# Brief détaillé — prochaines stories autour de `astral_house_interpretation_profiles`

## Contexte

La couche `astral_house_interpretation_profiles` existe désormais dans le modèle SQL et le vocabulaire éditorial initial des 12 maisons est seedé.

Références actuelles :

- vocabulaire maisons : `astral_house_interpretation_profiles.json`
- documentation maisons : `tables-maisons-et-roles.md`
- documentation planètes : `tables-planetes-et-roles.md`

État actuel confirmé :

- séparation astrologie runtime / scoring produit déjà mise en œuvre ;
- runtime natal enrichi (`HouseRuntimeData`) déjà disponible ;
- maîtres de maisons runtime déjà calculés ;
- `astral_house_interpretation_profiles` déjà versionnée et reliée à `astral_systems` ;
- vocabulaire éditorial des 12 maisons déjà seedé ;
- `HouseStrength` déjà typé et normalisé.

Le prochain enjeu n’est donc plus la structure SQL.

Le prochain enjeu est :

```text
faire de house_interpretation_profiles
la source éditoriale canonique
consommée par le moteur narratif et LLM.
```

Le but est d’éviter :

- prompts hardcodés ;
- connaissances astrologiques dupliquées ;
- logique narrative dispersée ;
- contradictions entre UI, prompts et projections publiques ;
- dérive éditoriale selon les features.

---

# Vision cible

Pipeline cible :

```text
astral_houses
→ référentiel canonique des maisons

HouseRuntimeData
→ réalité astrologique calculée du thème

astral_house_interpretation_profiles
→ vocabulaire interprétatif contrôlé

planet/sign interpretation profiles
→ vocabulaire complémentaire

LLM Context Builder
→ assemble runtime + vocabulaire + guards

Narrative Engine / Prompt Engine
→ produit l’interprétation finale
```

Important :

```text
house_interpretation_profiles
ne calcule jamais.
```

Cette couche :

- ne décide pas des scores ;
- ne décide pas des maisons activées ;
- ne modifie pas la vérité astrologique ;
- ne modifie pas le runtime.

Elle fournit uniquement :

```text
le vocabulaire contrôlé
pour parler astrologiquement d’une maison.
```

---

# STORY 1 — Contrat runtime canonique `HouseInterpretationProfileData`

## Objectif

Créer le contrat runtime canonique utilisé partout dans l’application pour transporter le vocabulaire interprétatif maison.

Aujourd’hui :

- les données existent en SQL ;
- mais il manque un DTO/domain contract stable.

Il faut éviter :

- dictionnaires libres ;
- accès JSON dynamiques ;
- parsing dispersé ;
- duplication de logique de normalisation.

---

## À créer

### Nouveau contrat runtime

Fichier cible :

```text
backend/app/domain/astrology/interpretation/house_interpretation_profile.py
```

Créer :

```python
HouseInterpretationProfileData
```

Structure recommandée :

```python
@dataclass(frozen=True)
class HouseInterpretationProfileData:
    house_number: int
    language: str
    system: str

    title: str
    short_label: str | None
    summary: str
    micro_note: str | None

    core_keywords: tuple[str, ...]
    shadow_keywords: tuple[str, ...]
    psychological_keywords: tuple[str, ...]
    material_keywords: tuple[str, ...]
    relationship_keywords: tuple[str, ...]
    career_keywords: tuple[str, ...]
    health_keywords: tuple[str, ...]
    spiritual_keywords: tuple[str, ...]

    body_parts: tuple[str, ...]
    archetypes: tuple[str, ...]
    life_areas: tuple[str, ...]

    dos: tuple[str, ...]
    donts: tuple[str, ...]
    prompt_hints: tuple[str, ...]
```

---

## Règles importantes

### Tous les JSON doivent être normalisés

Interdire :

```python
list
set
None
mixed types
```

Le runtime doit toujours exposer :

```python
tuple[str, ...]
```

---

### Contrat immuable

Le DTO doit être :

```python
frozen=True
```

pour empêcher les mutations runtime.

---

### Aucun champ astrologique runtime

Interdire dans ce contrat :

- cusp_sign
- ruler
- occupants
- house_kind
- strength
- activation score
- dominance

Ce contrat est éditorial uniquement.

---

## Acceptance Criteria

### AC-1

Le repository retourne uniquement `HouseInterpretationProfileData`.

### AC-2

Aucun `dict[str, Any]` ne sort du repository.

### AC-3

Tous les tableaux JSON sont normalisés en tuples.

### AC-4

Tests de parsing invalides :

- JSON null ;
- mauvais type ;
- liste mixte ;
- JSON cassé.

### AC-5

Architecture guard :

```text
prediction/
ne doit pas définir
HouseInterpretationProfileData
```

Le contrat appartient à :

```text
domain/astrology/interpretation
```

---

# STORY 2 — Repository canonique des profils d’interprétation

## Objectif

Créer une couche repository stable.

Aujourd’hui le seed existe.

Mais il manque :

```text
la lecture runtime canonique.
```

---

## À créer

### Repository dédié

Fichier cible :

```text
backend/app/infra/db/repositories/house_interpretation_repository.py
```

API cible :

```python
get_house_interpretation_profiles(
    reference_version_id: int,
    language: str,
    system: str,
) -> dict[int, HouseInterpretationProfileData]
```

Retour attendu :

```python
{
    1: HouseInterpretationProfileData(...),
    2: HouseInterpretationProfileData(...),
}
```

clé = numéro canonique de maison.

---

## Règles critiques

### Pas de fallback silencieux

Interdire :

```python
if not found:
    return {}
```

Le repository doit échouer si :

- une maison manque ;
- plusieurs profils concurrents existent ;
- une langue est incomplète.

---

### Validation stricte des 12 maisons

Le runtime doit garantir :

```text
12 maisons interprétatives
pour chaque combinaison
(reference_version, language, system)
```

---

### Résolution par numéro canonique

Le runtime ne doit jamais dépendre des IDs SQL.

Retour :

```python
house_number -> profile
```

et pas :

```python
house_id -> profile
```

---

## Acceptance Criteria

### AC-1

Le repository retourne exactement 12 maisons.

### AC-2

Une duplication SQL déclenche une erreur.

### AC-3

Une maison manquante déclenche une erreur.

### AC-4

Le repository ne retourne jamais de SQLAlchemy model.

### AC-5

Architecture guard :

```text
domain/astrology
ne doit pas importer SQLAlchemy.
```

---

# STORY 3 — Injection dans `PredictionContext` et `NatalContext`

## Objectif

Rendre les profils éditoriaux accessibles au moteur narratif.

Aujourd’hui :

- le runtime connaît les maisons ;
- mais le contexte ne connaît pas encore leur vocabulaire.

---

## À mettre en œuvre

Ajouter :

```python
house_interpretation_profiles: dict[int, HouseInterpretationProfileData]
```

Dans :

- `PredictionContext`
- `NatalInterpretationContext`
- ou un nouveau `NarrativeContext`

selon l’architecture retenue.

---

## Règle majeure

Le contexte :

```text
ne doit pas enrichir
ni transformer
les données éditoriales.
```

Il transporte.

Le mapping doit rester passif.

---

## Anti-pattern interdit

Interdire :

```python
if house == 10:
    keywords = ["career", "status"]
```

Toute connaissance métier doit venir du référentiel SQL.

---

## Acceptance Criteria

### AC-1

Les prompts ne contiennent plus de mapping hardcodé maison → keywords.

### AC-2

Le contexte expose :

```python
context.house_interpretation_profiles[10]
```

### AC-3

Les builders runtime ne modifient pas les profils.

### AC-4

Guardrail anti-hardcode :

scan regex :

```text
house == 10
career
reputation
public role
```

à proximité des prompts.

---

# STORY 4 — Builder narratif maison → contexte LLM

## Objectif

Créer une couche dédiée qui transforme :

```text
HouseRuntimeData
+
HouseInterpretationProfileData
```

vers :

```text
LLM-ready narrative context.
```

C’est probablement la story la plus importante.

---

## Nouveau composant

Fichier cible :

```text
backend/app/domain/astrology/interpretation/house_narrative_builder.py
```

API cible :

```python
build_house_narrative_context(
    runtime_house,
    interpretation_profile,
) -> HouseNarrativeContext
```

---

## Contrat cible

Exemple :

```python
@dataclass(frozen=True)
class HouseNarrativeContext:
    house_number: int

    title: str
    summary: str

    runtime_sign: str
    runtime_ruler: str | None
    runtime_ruler_house: int | None

    core_keywords: tuple[str, ...]
    shadow_keywords: tuple[str, ...]

    dominant_themes: tuple[str, ...]

    prompt_hints: tuple[str, ...]
    dos: tuple[str, ...]
    donts: tuple[str, ...]
```

---

## Important

Cette couche :

```text
assemble.
```

Elle ne calcule pas l’astrologie.

Le runtime reste propriétaire de :

- ruler ;
- occupants ;
- strength ;
- sign ;
- house kind.

Le profil reste propriétaire de :

- vocabulaire ;
- nuances ;
- guardrails ;
- tonalité.

---

## Acceptance Criteria

### AC-1

Aucun prompt ne lit directement SQLAlchemy.

### AC-2

Le LLM consomme uniquement `HouseNarrativeContext`.

### AC-3

Le builder ne recalcule jamais :

- maîtres ;
- maisons ;
- angularité ;
- scores.

### AC-4

Les `donts` sont propagés dans le contexte prompt.

---

# STORY 5 — Guardrails narratifs et anti-dérive

## Objectif

Empêcher les dérives narratives.

Exemples dangereux :

- maison 8 = mort ;
- maison 12 = folie ;
- maison 6 = maladie ;
- maison 10 = succès garanti.

Le référentiel doit devenir :

```text
la source qualité canonique.
```

---

## À mettre en œuvre

### Prompt policy layer

Créer :

```text
house_prompt_guardrails.py
```

qui applique automatiquement :

- dos ;
- donts ;
- restrictions ;
- tonalité.

---

## Exemple

Pour maison 8 :

```json
"donts": [
  "Do not reduce the eighth house to death.",
  "Avoid deterministic or frightening interpretations."
]
```

Le moteur doit injecter automatiquement ces protections.

---

## Acceptance Criteria

### AC-1

Tous les prompts maison incluent `donts`.

### AC-2

Les maisons sensibles ont des tests snapshot.

### AC-3

Créer une liste de maisons sensibles :

- 6
- 8
- 12

### AC-4

Tests anti-pattern :

interdire :

```text
fatalistic
certain death
incurable
```

---

# STORY 6 — Internationalisation éditoriale

## Objectif

Préparer le multi-langue réel.

Aujourd’hui :

- vocabulaire anglais uniquement.

Demain :

- français ;
- italien ;
- espagnol ;
- astrologues/personas localisés.

---

## À mettre en œuvre

### Validation de complétude

Créer un validator :

```python
validate_house_interpretation_completeness()
```

qui garantit :

- 12 maisons ;
- tous les champs critiques ;
- cohérence des langues.

---

## Important

Interdire :

```text
fallback implicite EN → FR
```

pour éviter les prompts hybrides.

---

## Acceptance Criteria

### AC-1

Le runtime échoue si une langue est incomplète.

### AC-2

Les prompts ne mélangent jamais plusieurs langues.

### AC-3

Le validator produit un rapport détaillé.

---

# STORY 7 — Couche complémentaire planètes/signes

## Objectif

Répliquer exactement la même architecture pour :

- planètes ;
- signes.

Car aujourd’hui :

```text
les maisons sont éditorialisées
mais pas encore les planètes ni les signes.
```

---

## Futures tables attendues

### `astral_planet_interpretation_profiles`

Structure analogue :

```text
planet_id
reference_version_id
language
astral_system_id
...
```

---

### `astral_sign_interpretation_profiles`

Même logique.

---

## Important

Le futur moteur narratif doit pouvoir assembler :

```text
house vocabulary
+
planet vocabulary
+
sign vocabulary
+
aspect vocabulary
```

sans hardcode.

---

## Acceptance Criteria

### AC-1

Architecture alignée avec les maisons.

### AC-2

Aucun mapping planète → keywords hardcodé.

### AC-3

Même philosophie :

```text
runtime facts
≠
editorial vocabulary
```

---

# STORY 8 — Projection publique UI / cartes pédagogiques

## Objectif

Réutiliser le référentiel éditorial côté UI.

Aujourd’hui :

- beaucoup de labels simplifiés sont hardcodés.

Demain :

- la UI doit lire le même vocabulaire que le LLM.

---

## À mettre en œuvre

Créer un projector public :

```text
PublicHouseInterpretationProjector
```

capable d’exposer :

```json
{
  "title": "Career and Public Role",
  "summary": "...",
  "keywords": [...],
  "micro_note": "..."
}
```

---

## Important

La projection publique :

- ne doit pas exposer les `donts` ;
- ne doit pas exposer les prompt hints internes ;
- ne doit pas exposer les guardrails système.

---

## Acceptance Criteria

### AC-1

La UI ne possède plus ses propres labels maison.

### AC-2

Le projector filtre les champs internes.

### AC-3

Tests snapshot API.

---

# STORY 9 — Canonical narrative engine

## Objectif long terme

Créer un moteur narratif déterministe.

Le LLM ne doit plus :

```text
inventer l’astrologie.
```

Il doit :

```text
rédiger
à partir d’un contexte déjà structuré.
```

---

## Vision cible

Pipeline final :

```text
runtime astrology
→ faits réels

interpretation profiles
→ vocabulaire maîtrisé

narr
