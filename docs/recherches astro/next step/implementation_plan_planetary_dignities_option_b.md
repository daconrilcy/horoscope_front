# Implémentation détaillée — Exploitation runtime des dignités planétaires (Option B)

## 1. Objectif

L'objectif est de faire évoluer le moteur astrologique d'un simple référentiel statique de dignités vers un système réellement exploité dans :

- le calcul du thème astral,
- le scoring des prédictions,
- les calculs de sensibilité natale,
- les signaux de transit,
- l'interprétation éditoriale,
- les futurs systèmes de restitution UX.

Le modèle SQL est désormais en place avec :

- `astral_planets`
- `astral_planet_sign_dignities`
- `astral_systems`
- `astral_dignity_types`

La prochaine étape consiste à exploiter ces données dans le runtime.

Le choix retenu est :

# OPTION B

Les dignités influencent réellement les calculs numériques et les scores.

Une planète forte doit produire un effet plus puissant.
Une planète affaiblie doit produire un effet réduit ou déséquilibré.

---

# 2. Vision fonctionnelle

## Principe astrologique

Une planète ne s'exprime pas avec la même efficacité selon le signe dans lequel elle se trouve.

Exemples :

| Cas | Interprétation |
|---|---|
| Mars en Bélier | planète forte, directe, efficace |
| Mars en Cancer | planète affaiblie, indirecte, émotionnelle |
| Soleil en Bélier | énergie solaire renforcée |
| Soleil en Balance | expression solaire diminuée |

Le moteur doit désormais refléter cette logique.

---

# 3. Périmètre fonctionnel

Les dignités devront influencer :

| Composant | Impact |
|---|---|
| NatalSensitivity | pondération des planètes natales |
| ContributionCalculator | intensité des contributions |
| TransitSignalBuilder | modulation des signaux continus |
| Daily predictions | qualité du score final |
| Interprétation éditoriale | vocabulaire et nuances |
| UX | affichage planète forte/faible |

Les dignités ne doivent PAS :

- modifier les positions astronomiques,
- modifier les maisons,
- modifier les aspects,
- modifier les orbes,
- modifier les calculs d'éphémérides.

Elles modulent uniquement l'expression symbolique d'une planète.

---

# 4. Architecture cible

## 4.1 Nouveau service runtime

Créer un service dédié :

```python
PlanetDignityEvaluator
```

Responsabilités :

- résoudre les dignités d'une planète dans un signe,
- calculer un multiplicateur numérique,
- produire des métadonnées interprétatives,
- centraliser toute la logique métier des dignités.

---

# 5. Contrat runtime attendu

## Entrée

```python
resolve_dignity(
    planet_code: str,
    sign_code: str,
    system: str = "traditional",
)
```

---

## Sortie

```python
PlanetDignityResult(
    dignity_type="domicile",
    weight=1.0,
    score_modifier=1.15,
    polarity="reinforced",
    is_positive=True,
    is_major=True,
)
```

---

# 6. Multiplicateurs métier recommandés

## Table canonique

| Dignité | Weight DB | Multiplicateur runtime |
|---|---:|---:|
| domicile | 1.0 | 1.15 |
| exaltation | 0.8 | 1.10 |
| detriment | -1.0 | 0.85 |
| fall | -0.8 | 0.90 |
| aucune | 0 | 1.00 |

---

## Pourquoi des multiplicateurs faibles

Les dignités ne doivent pas écraser :

- les aspects,
- les maisons,
- les orbes,
- les angles,
- les transits.

Elles sont un modulateur secondaire.

Le moteur doit rester principalement piloté par :

- les événements,
- les aspects,
- les maisons,
- les catégories.

---

# 7. Nouvelle structure runtime

## DTO recommandé

```python
@dataclass(slots=True)
class PlanetDignityResult:
    dignity_type: str | None
    weight: float
    score_modifier: float
    polarity: str
    is_positive: bool
    is_major: bool
```

---

# 8. Repository

## Méthode à ajouter

```python
get_planet_sign_dignities(
    system: str = "traditional"
)
```

Retour recommandé :

```python
dict[
    tuple[str, str],
    PlanetDignityData
]
```

clé :

```python
(planet_code, sign_code)
```

---

# 9. PredictionContext

Ajouter :

```python
planet_sign_dignities
```

Exemple :

```python
{
    ("mars", "aries"): PlanetDignityData(...),
    ("sun", "aries"): PlanetDignityData(...),
}
```

---

# 10. ContextLoader

## Étapes

### Charger les dignités

```python
context.planet_sign_dignities = (
    repository.get_planet_sign_dignities(
        system="traditional"
    )
)
```

---

## Validation obligatoire

Ajouter dans :

```python
PredictionContextLoader._validate_context
```

Validation :

```python
if not context.planet_sign_dignities:
    raise MissingPredictionReferenceError(...)
```

---

# 11. Exploitation dans NatalSensitivity

## Objectif

Une planète natale forte doit avoir plus d'impact.

Exemple :

```text
Mars en Bélier
=> activation énergétique plus forte
```

```text
Mars en Cancer
=> activation plus instable/faible
```

---

## Intégration

Lors du calcul :

```python
planet_weight
```

appliquer :

```python
planet_weight *= dignity.score_modifier
```

---

# 12. Exploitation dans ContributionCalculator

## Objectif

Un transit impliquant une planète forte doit produire un impact supérieur.

---

## Exemple

Avant :

```python
final_score = (
    w_planet
    * w_aspect
    * f_orb
    * f_phase
)
```

Après :

```python
final_score = (
    w_planet
    * dignity_modifier
    * w_aspect
    * f_orb
    * f_phase
)
```

---

# 13. Exploitation dans TransitSignalBuilder

## Objectif

Moduler les signaux continus.

Exemple :

```text
Vénus exaltée
=> signaux affectifs fluides et amplifiés
```

```text
Saturne en chute
=> signaux structurels plus faibles ou rigides
```

---

# 14. Exploitation éditoriale

## Nouveau champ interprétatif

Ajouter dans les payloads :

```json
{
  "planet": "mars",
  "sign": "aries",
  "dignity": {
    "type": "domicile",
    "strength": "strong"
  }
}
```

---

## Utilisation future

Les prompts LLM pourront produire :

```text
Mars agit ici avec force et spontanéité.
```

ou :

```text
L'énergie martienne semble freinée ou intériorisée.
```

---

# 15. Ne PAS coder en dur

Interdiction de faire :

```python
if planet == "mars" and sign == "aries":
```

Toute la logique doit venir du référentiel SQL.

Le runtime ne doit connaître que :

- les codes,
- les poids,
- les types,
- les multiplicateurs.

---

# 16. Gestion des systèmes astrologiques

## Canonique actuel

Le moteur runtime doit rester :

```text
traditional
```

pour éviter :

```text
scorpio -> pluto
pisces -> neptune
aquarius -> uranus
```

---

## Règle d'architecture

| Système | Usage |
|---|---|
| traditional | moteur canonique |
| modern | enrichissement éditorial optionnel |
| hellenistic | futur |
| medieval | futur |

---

# 17. Compatibilité future

Le système doit permettre plus tard :

- dignités mineures,
- décans,
- termes,
- triplicités,
- gestion diurne/nocturne,
- dignités cumulatives,
- score astrologique global.

---

# 18. Ce qu'il ne faut PAS faire

## Ne pas mélanger

- scoring prédictif
- positions astronomiques
- dignités
- aspects

Les responsabilités doivent rester séparées.

---

## Ne pas versionner

`astral_planet_sign_dignities`

reste une taxonomie stable.

Les multiplicateurs runtime peuvent évoluer.

---

## Ne pas sur-amplifier

Une dignité ne doit jamais doubler un score.

Les multiplicateurs doivent rester modérés.

---

# 19. Refactorings recommandés

## Ajouter un package dédié

```text
backend/app/domain/astrology/dignities/
```

Contenu :

```text
planet_dignity_evaluator.py
planet_dignity_models.py
planet_dignity_resolver.py
```

---

# 20. Tests obligatoires

## Repository

Vérifier :

- chargement des 50 lignes,
- unicité,
- mapping planète/signe,
- filtres système.

---

## Runtime

Vérifier :

```text
Mars en Bélier => 1.15
Mars en Cancer => 0.90
```

---

## Non-régression

Vérifier :

- aucune dépendance à astral_sign_rulerships,
- PredictionContext valide,
- scores cohérents,
- absence de crash sans dignité.

---

# 21. Observabilité

Ajouter dans les snapshots/debug :

```json
{
  "planet": "mars",
  "sign": "aries",
  "dignity_modifier": 1.15,
  "dignity_type": "domicile"
}
```

---

# 22. API / DTO publics

Prévoir plus tard :

```json
{
  "planet": "mars",
  "sign": "aries",
  "dignity": {
    "type": "domicile",
    "label": "Mars est en domicile",
    "strength": "strong"
  }
}
```

---

# 23. Priorités de mise en œuvre

## PHASE 1 — Runtime minimal

Objectif :

- charger les dignités,
- produire les multiplicateurs,
- injecter dans les calculateurs.

---

## PHASE 2 — Interprétation

Objectif :

- enrichir les payloads,
- enrichir les prompts,
- améliorer la restitution.

---

## PHASE 3 — Astrologie avancée

Objectif :

- décans,
- triplicités,
- termes,
- score essentiel global.

---

# 24. État cible final

À terme, le moteur devra être capable de dire :

```json
{
  "planet": "mars",
  "sign": "aries",
  "dignity": {
    "type": "domicile",
    "score_modifier": 1.15,
    "strength": "strong"
  },
  "interpretation": {
    "energy": "direct",
    "expression": "assertive",
    "stability": "high"
  }
}
```

sans aucune logique hardcodée.

