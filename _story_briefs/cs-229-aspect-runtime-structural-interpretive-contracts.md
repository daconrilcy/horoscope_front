# CS-229 — Aspect Runtime Structural / Interpretive Contracts

## Résumé

CS-229 formalise la séparation entre runtime structurel et runtime interprétatif pour les aspects astrologiques.

Aujourd’hui, `AspectRuntimeData` mélange des faits calculatoires :

```text
identité
participants
orbe
force technique
modifiers factuels
```

avec des indices semi-interprétatifs :

```text
default_valence
interpretive_valence
energy_type
interpretive_weight
```

Cette story ne migre pas encore tous les consommateurs. Elle crée d’abord les contrats cibles et la doctrine d’architecture qui permettront aux stories suivantes de déplacer les champs interprétatifs hors du runtime structurel.

La cible est :

```text
AspectStructuralRuntimeData
→ faits géométriques, calculatoires et structurels

AspectInterpretiveRuntimeData / AspectInterpretiveHints
→ valence, energy type, axes sémantiques, poids interprétatifs
```

---

## Contexte

Les stories CS-217 à CS-228 ont convergé vers un runtime astrologique plus canonique :

```text
NatalResult.chart_objects
aspects runtime
dignities runtime
dominance runtime
fixed stars runtime
chart interpretation input
calculation graph
```

Cette convergence a déjà réduit le risque de surfaces parallèles. Mais le runtime d’aspects reste hybride.

Exemples actuels :

```python
AspectRuntimeData(
    aspect=...,
    participants=...,
    orb=...,
    strength=...,
    interpretation=AspectInterpretationRuntimeData(
        default_valence="positive",
        interpretive_valence="harmonious",
        energy_type="harmonious_flow",
    ),
    modifiers=(...),
)
```

Le bloc `interpretation` n’est pas narratif, mais il n’est déjà plus purement structurel. Il encode une première lecture du fait astrologique.

---

## Problème à résoudre

Sans frontière formelle, le code peut évoluer vers :

```text
aspect calculator
→ valence
→ energy_type
→ prompt hint
→ poids interprétatif
→ rendu produit
```

dans la même surface runtime.

Risques :

- confusion entre fait astrologique et pré-interprétation ;
- difficulté à prouver qu’un calculateur reste déterministe et structurel ;
- duplication future entre `AspectRuntimeData`, `ChartInterpretationInputRuntimeData` et les profils éditoriaux ;
- propagation de champs comme `positive`, `negative`, `harmonious`, `challenging` dans des couches qui ne devraient pas les connaître ;
- impossibilité de nettoyer proprement les surfaces legacy d’aspects.

CS-229 doit définir les contrats et les règles avant la migration.

---

## Objectifs

### Objectif fonctionnel

Créer des contrats explicites pour distinguer :

```text
runtime structurel
runtime interprétatif
projection publique legacy
```

### Objectif architectural

Installer la règle suivante :

```text
Un calculateur structurel ne produit que des faits structurels.
Les indices interprétatifs sont produits par un adapter ou resolver dédié,
à partir du runtime structurel et du référentiel interprétatif.
```

---

## Périmètre inclus

CS-229 couvre :

1. La définition de la terminologie officielle : structural runtime, interpretive runtime, public projection, legacy projection.
2. La création ou préparation de contrats dédiés aux aspects structurels.
3. La création ou préparation de contrats dédiés aux hints interprétatifs d’aspects.
4. La documentation du statut des champs `default_valence`, `interpretive_valence`, `energy_type` et `interpretive_weight`.
5. La clarification du statut du référentiel d’aspects : définition structurelle vs profil interprétatif.
6. La clarification du rôle de `AspectStrengthRuntimeData`.
7. La clarification du rôle de la dominance d’aspect.
8. La clarification du rôle des modifiers factuels.
9. La clarification du statut des consommateurs prediction qui utilisent déjà `default_valence` et `energy_type`.
10. Les tests unitaires de validation des nouveaux contrats.
11. Une documentation d’architecture courte.

---

## Hors périmètre

CS-229 ne doit pas :

- supprimer immédiatement `AspectRuntimeData.interpretation` ;
- casser le JSON public natal ;
- modifier la doctrine astrologique ;
- modifier les valeurs des profils d’aspects ;
- modifier les prompts ;
- modifier le frontend ;
- supprimer les tables DB de valence ;
- changer les scores de prédiction ;
- migrer tous les consommateurs d’un coup.

---

## Contrats attendus

### Référentiel d’aspects

Le référentiel doit être explicitement séparé en deux vues, même si les données restent temporairement chargées depuis les mêmes tables.

Vue structurelle :

```python
AspectStructuralDefinitionRuntimeData
```

Champs autorisés :

```python
code
name
angle
family
is_enabled
is_major
is_minor
default_orb_deg
system_code
legacy_orb_fields
```

Vue interprétative :

```python
AspectInterpretiveProfileRuntimeData
```

Champs possibles :

```python
aspect_code
system_code
default_valence
interpretive_valence
energy_type
semantic_axes
growth_axes
shadow_axes
relationship_axes
source_profile_code
reference_version
```

Règle :

```text
Un calculateur structurel ne reçoit que la vue structurelle.
Un resolver interprétatif reçoit la vue interprétative.
```

### Runtime structurel d’aspect

Créer ou préparer un contrat structurel.

Nom recommandé :

```python
AspectStructuralRuntimeData
```

Champs attendus :

```python
aspect: AspectIdentityRuntimeData
participants: AspectParticipantsRuntimeData
orb: AspectOrbRuntimeData
metadata: AspectMetadataRuntimeData
strength: AspectStrengthRuntimeData
phase: AspectPhaseRuntimeData | None
modifiers: tuple[AspectStructuralModifierRuntimeData, ...]
```

Règle :

```text
Aucun champ de valence, energy type, prompt, meaning, narrative ou theme éditorial.
```

### Hints interprétatifs d’aspect

Créer ou préparer un contrat séparé.

Nom recommandé :

```python
AspectInterpretiveHintsRuntimeData
```

Champs possibles :

```python
aspect_code: str
default_valence: str
interpretive_valence: str
energy_type: str
semantic_axes: tuple[str, ...]
growth_axes: tuple[str, ...]
shadow_axes: tuple[str, ...]
relationship_axes: tuple[str, ...]
interpretive_weight: float | None
source_profile_code: str | None
source_codes: tuple[str, ...]
```

Règle :

```text
Ces hints ne sont pas des textes narratifs.
Ils restent des indices d’interprétation typés et sourcés.
```

### Modifier structurel

Renommer ou borner le contrat existant pour éviter l’ambiguïté.

Le modifier structurel peut porter :

```python
modifier_type
source
intensity
reason
applies_to
```

Il ne doit pas porter :

```python
interpretive_weight
prompt_hint
meaning
narrative
```

Si un poids interprétatif est nécessaire, il doit vivre dans le contrat de hints interprétatifs.

---

## Documentation attendue

Mettre à jour ou créer :

```text
docs/architecture/astrology-runtime-surfaces.md
```

Ajouter une section :

```text
Aspect runtime layers
```

Elle doit préciser :

| Couche | Contenu | Owner | Consommateurs autorisés |
|---|---|---|---|
| Structural aspect runtime | géométrie, orbe, participants, force technique, modifiers factuels | astrology runtime | calculateurs, dominance, graph |
| Interpretive aspect runtime | valence, energy type, axes, poids interprétatifs | interpretation adapter | prompts, interpretation input |
| Public aspect projection | contrat API stable | chart json builder | front/API |
| Legacy aspect projection | compatibilité historique | adapters allowlistés | transition uniquement |

Ajouter aussi une note sur les consommateurs prediction :

```text
Le domaine prediction peut continuer à utiliser des valences ou energy types,
mais via ses contrats de prediction ou via les hints interprétatifs,
jamais via le runtime structurel d’aspects.
```

---

## Tests attendus

Ajouter ou préparer des tests qui prouvent :

1. Le contrat structurel refuse les champs interprétatifs.
2. Le contrat interprétatif accepte les hints sourcés.
3. Les modifiers structurels ne portent pas de poids interprétatif.
4. Le référentiel structurel d’aspects ne contient pas les champs de valence.
5. Les termes interdits ne sont pas présents dans les modules structurels :

```text
default_valence
interpretive_valence
energy_type
interpretive_weight
meaning
narrative
prompt
llm
```

6. La documentation liste explicitement les deux couches.

---

## Critères d’acceptation

### AC1 — Doctrine explicite

Une documentation d’architecture définit clairement :

```text
structural runtime
interpretive runtime
public projection
legacy projection
```

### AC2 — Contrats séparés

Les contrats dédiés existent ou sont préparés avec une nomenclature claire.

### AC3 — Référentiel scindé par responsabilité

Le brief ou le code distingue la définition structurelle d’aspect du profil interprétatif d’aspect.

### AC4 — Aucun nouveau mélange

Aucun nouveau champ interprétatif n’est ajouté à un contrat structurel.

### AC5 — Modifiers bornés

Les modifiers structurels ne contiennent plus de poids interprétatif, ou ce poids est explicitement marqué comme legacy à migrer en CS-230.

### AC6 — Tests de frontière

Des tests d’architecture empêchent le retour des champs interprétatifs dans les modules structurels ciblés.

---

## Validation recommandée

PowerShell, après activation du venv :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py backend/tests/unit/domain/astrology/test_aspect_modifiers.py backend/tests/architecture/test_chart_interpretation_input_boundary.py
```

Ajouter les tests spécifiques créés par la story à cette commande ciblée.

---

## Risques et points d’attention

Le principal risque est de renommer les contrats trop tôt et de casser beaucoup de consommateurs.

Approche recommandée :

```text
1. créer les nouveaux contrats ;
2. garder des alias temporaires si nécessaire ;
3. migrer les consommateurs dans CS-230 ;
4. supprimer les alias dans CS-231 ou CS-232.
```

Le second risque est de déplacer les champs sans déplacer la responsabilité. La migration n’est réussie que si les calculateurs structurels ne dépendent plus du référentiel interprétatif.

Le troisième risque est d’oublier le domaine prediction. Les usages prediction de `default_valence` et `energy_type` sont légitimes, mais ils doivent être alimentés par un contrat prediction ou par les hints interprétatifs, pas par un runtime structurel hybride.
