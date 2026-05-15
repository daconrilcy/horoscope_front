# Story: daily-house-system-runtime-convergence

Status: draft

---

# 1. Objective

Rendre le moteur de prédiction quotidienne (`daily`) pleinement piloté par le système de maisons demandé (`house_system_requested` / `house_system_id`) au lieu du comportement historique codé en dur :

```text
Placidus -> fallback Porphyry
```

L’objectif est d’aligner totalement le runtime daily avec la référence canonique `astral_house_systems`, déjà utilisée par :

- le moteur natal,
- les rulesets,
- les baselines,
- les analytics,
- les traces runtime.

Après cette convergence :

- le daily devra réellement calculer les cuspides courantes avec le système demandé ;
- les stratégies de fallback devront devenir explicites et pilotées ;
- les traces runtime devront permettre d’expliquer précisément :

```text
requested_system
-> effective_system
-> fallback_reason
```

Le moteur daily ne devra plus dépendre implicitement de Placidus comme système universel.

---

# 2. Contexte actuel

## État actuel du moteur natal

Le moteur natal supporte déjà :

- `placidus`
- `equal`
- `whole_sign`
- `porphyry`

Le calcul passe par :

```text
houses_provider.calculate_houses
-> swe.houses_ex
```

avec un mapping canonique :

```python
SWISS_HOUSE_SYSTEM_BYTES = {
    HouseSystemCode.PLACIDUS: b"P",
    HouseSystemCode.EQUAL: b"E",
    HouseSystemCode.WHOLE_SIGN: b"W",
    HouseSystemCode.PORPHYRY: b"O",
}
```

## État actuel du moteur daily

Le moteur daily (`AstroCalculator`) :

- ignore encore `house_system_requested` ;
- tente systématiquement :

```text
Placidus
-> fallback Porphyry
```

Exemple actuel :

```python
return self._run_house_calculation(ut_jd, b"P", HOUSE_SYSTEM_PLACIDUS)
```

puis :

```python
return self._run_house_calculation(ut_jd, b"O", HOUSE_SYSTEM_PORPHYRY)
```

Conséquence :

- `equal` et `whole_sign` existent comme références canoniques ;
- les rulesets peuvent les demander ;
- les baselines peuvent les tracer ;
- MAIS les cuspides courantes daily ne les utilisent pas réellement.

---

# 3. Problème d’architecture actuel

Aujourd’hui :

```text
ruleset
-> house_system_requested = whole_sign
```

mais runtime :

```text
daily
-> calcule toujours Placidus
-> ou Porphyry
```

Cela crée :

- une divergence entre intention et runtime ;
- une ambiguïté analytics ;
- des baselines potentiellement incohérentes ;
- des interprétations daily incompatibles avec certains systèmes ;
- une difficulté future pour expliquer les résultats utilisateur.

Le système actuel est encore acceptable tant qu’il est documenté.

Mais il devient insuffisant dès que :

- l’utilisateur choisit explicitement un système ;
- des abonnements avancés apparaissent ;
- des comparaisons cross-system sont nécessaires ;
- des analytics par système deviennent importantes.

---

# 4. Objectifs fonctionnels détaillés

## 4.1 Objectif principal

Faire dépendre les cuspides courantes daily du système demandé.

Avant :

```text
ruleset -> ignoré
```

Après :

```text
ruleset.house_system_requested
-> AstroCalculator
-> système runtime réel
```

---

## 4.2 Objectif secondaire

Rendre les fallbacks explicites.

Exemple attendu :

```text
requested = placidus
latitude = 72°
placidus impossible
-> fallback porphyry
```

et non plus :

```text
fallback implicite interne
```

---

## 4.3 Objectif analytics

Permettre :

- analytics par système ;
- taux de fallback ;
- régions problématiques ;
- diagnostics runtime ;
- monitoring qualité.

---

# 5. Architecture cible

## 5.1 Nouveau flux runtime

Architecture cible :

```text
prediction_ruleset
    -> house_system_id
        -> astral_house_systems
            -> AstroCalculator
                -> runtime house strategy
                    -> effective system
                        -> cusp calculation
                            -> tracing
```

---

## 5.2 Stratégie runtime explicite

Créer une stratégie runtime dédiée.

Exemple :

```text
HouseSystemRuntimeResolver
```

Responsabilités :

- recevoir le système demandé ;
- vérifier la compatibilité géographique ;
- vérifier les limites astronomiques ;
- appliquer les règles de fallback ;
- retourner le système effectif ;
- retourner la raison éventuelle du fallback.

---

# 6. Nouveau contrat runtime recommandé

Créer une structure dédiée.

Exemple :

```python
@dataclass(slots=True)
class HouseSystemResolution:
    requested_system: str
    effective_system: str
    fallback_reason: str | None
    fallback_applied: bool
```

Exemple runtime :

```python
HouseSystemResolution(
    requested_system="placidus",
    effective_system="porphyry",
    fallback_reason="polar_region_unsupported",
    fallback_applied=True,
)
```

---

# 7. Stratégie de fallback recommandée

## 7.1 Principe

Le fallback ne doit plus être codé en dur.

Il doit être piloté :

- par la référence `astral_house_systems` ;
- par une stratégie runtime explicite.

---

## 7.2 Exemple recommandé

| Requested | Cas | Effective |
| --- | --- | --- |
| placidus | latitude normale | placidus |
| placidus | région polaire | porphyry |
| whole_sign | région polaire | whole_sign |
| equal | région polaire | equal |
| porphyry | région polaire | porphyry |

---

## 7.3 Point important

`whole_sign` et `equal` ne devraient probablement jamais fallback sur Porphyry.

Sinon :

```text
l’utilisateur demande un système sign-based
-> runtime produit un système quadrant
```

ce qui change profondément la logique astrologique.

---

# 8. Évolution SQL recommandée

## 8.1 Option minimale

Ne rien ajouter.

Continuer à utiliser :

```text
daily_prediction_runs.house_system_effective_id
```

et enrichir seulement le runtime mémoire.

---

## 8.2 Option recommandée

Ajouter une table runtime dédiée.

Exemple :

```sql
CREATE TABLE house_system_runtime_resolutions (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    requested_house_system_id BIGINT NOT NULL,
    effective_house_system_id BIGINT NOT NULL,

    fallback_reason VARCHAR(100),
    fallback_applied BOOLEAN NOT NULL DEFAULT FALSE,

    latitude DOUBLE PRECISION,
    longitude DOUBLE PRECISION,

    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_requested_house_system
        FOREIGN KEY (requested_house_system_id)
        REFERENCES astral_house_systems(id),

    CONSTRAINT fk_effective_house_system
        FOREIGN KEY (effective_house_system_id)
        REFERENCES astral_house_systems(id)
);
```

---

# 9. Fallback reasons recommandées

Créer un enum ou constantes.

Exemples :

```python
class HouseSystemFallbackReason:
    POLAR_REGION_UNSUPPORTED = "polar_region_unsupported"
    INVALID_COORDINATES = "invalid_coordinates"
    SWISSEPH_FAILURE = "swisseph_failure"
    NUMERICAL_INSTABILITY = "numerical_instability"
```

---

# 10. Refactoring AstroCalculator

## 10.1 Situation actuelle

`AstroCalculator` choisit lui-même :

```text
Placidus
-> Porphyry
```

Ce comportement doit disparaître.

---

## 10.2 Architecture cible

`AstroCalculator` ne choisit plus.

Il reçoit :

```python
HouseSystemResolution
```

et exécute uniquement :

```python
_run_house_calculation(...)
```

avec :

```python
effective_system
```

---

# 11. Évolution des baselines

Aujourd’hui :

```text
baseline
-> séparée par effective_house_system_id
```

Ce comportement doit être conservé.

Mais il faudra garantir :

```text
requested_system != effective_system
```

n’introduit pas :

- collisions ;
- pollution cross-system ;
- agrégats incohérents.

---

# 12. Impacts interprétatifs majeurs

Cette story n’est pas seulement technique.

Changer le système de maisons change :

- les cuspides ;
- les maisons occupées ;
- les activations ;
- les événements ;
- les routages catégorie ;
- les timelines ;
- les scores ;
- les turning points ;
- les maîtrises de maisons.

Le daily deviendra réellement multi-systèmes.

---

# 13. Compatibilité historique

## 13.1 Important

Les anciens runs daily peuvent avoir été :

```text
requested = whole_sign
effective = placidus
```

sans trace explicite.

Il ne faut PAS réécrire l’historique.

---

## 13.2 Contrat recommandé

Considérer :

```text
avant convergence = legacy runtime behavior
```

---

# 14. Tests obligatoires

## 14.1 Tests unitaires

Ajouter :

- résolution runtime ;
- stratégie de fallback ;
- régions polaires ;
- conservation du système demandé ;
- mapping SwissEph ;
- non-régression Placidus.

---

## 14.2 Tests d’intégration

Tester :

```text
ruleset whole_sign
-> daily whole_sign réel
```

Tester :

```text
ruleset equal
-> daily equal réel
```

Tester :

```text
ruleset placidus + latitude extrême
-> fallback porphyry
```

---

## 14.3 Tests analytics

Vérifier :

- requested_system correctement tracé ;
- effective_system correctement persisté ;
- fallback_reason correctement remonté.

---

# 15. Guardrails architecture

## 15.1 Interdictions

Interdire :

```python
b"P"
```

hardcodé directement dans le runtime hors resolver.

---

## 15.2 Interdire

Interdire :

```python
if placidus fails:
    use porphyry
```

hors stratégie centralisée.

---

## 15.3 Interdire

Interdire le retour de :

```text
house_system = 'placidus'
```

comme string relationnelle SQL.

Le garde-fou actuel doit être conservé.

---

# 16. Étapes de migration recommandées

## Phase 1

Créer :

```text
HouseSystemRuntimeResolver
```

sans modifier le comportement runtime.

---

## Phase 2

Faire dépendre :

```text
AstroCalculator
```

du resolver.

---

## Phase 3

Activer :

```text
equal
whole_sign
```

comme systèmes daily réels.

---

## Phase 4

Ajouter analytics et fallback tracing.

---

# 17. Risques principaux

## Risque 1

Explosion des différences de résultats.

Le daily changera réellement.

---

## Risque 2

Baselines incompatibles.

---

## Risque 3

Comparaisons historiques difficiles.

---

## Risque 4

SwissEph peut produire des comportements différents selon les systèmes.

---

# 18. Décisions importantes à prendre avant implémentation

## Décision 1

Les systèmes daily doivent-ils tous être officiellement supportés ?

ou :

```text
supported_for_natal_only
```

pour certains ?

---

## Décision 2

Les fallbacks doivent-ils être automatiques ou bloquants ?

Exemple :

```text
whole_sign demandé
-> impossible ?
-> erreur ?
-> fallback ?
```

---

## Décision 3

Les analytics doivent-elles distinguer :

```text
requested
vs
actual
```

sur tous les dashboards ?

---

# 19. Résultat final attendu

Après convergence complète :

```text
ruleset
-> house_system_requested
-> runtime resolver
-> effective system
-> daily cuspides
-> routing
-> events
-> scores
-> analytics
-> tracing
```

sans logique implicite Placidus globale.

Le moteur daily deviendra réellement :

```text
multi-house-system aware
```

avec :

- runtime explicite ;
- traçabilité ;
- analytics cohérentes ;
- architecture canonique alignée avec les références SQL.
