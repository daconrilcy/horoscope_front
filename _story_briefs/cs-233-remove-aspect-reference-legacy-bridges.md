# CS-233 — Remove Aspect Reference Legacy Bridges

## Résumé

CS-233 supprime les surfaces de transition restantes après CS-229 à CS-232.

Les stories précédentes ont correctement séparé :

```text
AspectStructuralRuntimeData
AspectInterpretiveHintsRuntimeData
AspectStructuralDefinitionRuntimeData
AspectInterpretiveProfileRuntimeData
```

et les calculateurs d’aspects consomment désormais la vue structurelle.

Il reste cependant plusieurs bridges explicitement marqués `Temporary` :

```text
AspectReferenceData.default_valence
AspectReferenceData.interpretive_valence
AspectReferenceData.energy_type
AspectDefinitionRuntimeData
natal_calculation_nodes._aspect_definition
AspectResult.default_valence
AspectResult.interpretive_valence
AspectResult.energy_type
json_builder fallback sur les champs plats d'aspect
AspectRuntimeWeightTaxonomy mention legacy d'interpretive_weight
```

CS-233 doit fermer ces transitions pour que la séparation ne soit plus seulement protégée par allowlist.

---

## Contexte

Après l’implémentation CS-229 à CS-232, l’état cible est largement atteint :

- `AspectCalculationResult` ne porte plus de champs interprétatifs ;
- `calculate_major_aspects` reçoit `AspectStructuralDefinitionRuntimeData` ;
- `build_aspect_structural_runtime_data` produit un runtime structurel ;
- `AspectInterpretiveHintResolver` produit les hints depuis un profil dédié ;
- `json_builder` privilégie `aspect_interpretive_hints` ;
- les tests d’architecture documentent les exceptions.

Mais les exceptions temporaires sont encore présentes dans :

```text
backend/app/domain/astrology/runtime/runtime_reference.py
backend/app/domain/astrology/runtime/aspect_calculation_contracts.py
backend/app/domain/astrology/runtime/natal_calculation_nodes.py
backend/app/domain/astrology/natal_calculation.py
backend/app/services/chart/json_builder.py
backend/tests/architecture/test_astrology_runtime_boundary.py
docs/architecture/astrology-runtime-surfaces.md
```

Cette story transforme les exceptions temporaires en contrats définitifs ou les supprime.

---

## Problème à résoudre

Tant que `AspectReferenceData` reste hybride, le référentiel runtime continue à mélanger :

```text
definition géométrique
profil interprétatif
```

Tant que `AspectDefinitionRuntimeData` existe, les nouvelles implémentations peuvent continuer à construire une définition legacy puis appeler :

```python
definition.structural_definition()
definition.interpretive_profile()
```

Ce bridge est acceptable pendant la migration, mais il devient une nouvelle surface legacy s’il reste durablement.

Tant que `AspectResult` accepte les champs plats :

```text
default_valence
interpretive_valence
energy_type
```

les serializers publics peuvent encore fonctionner sans hints explicites.

CS-233 doit supprimer ces raccourcis.

---

## Objectifs

### Objectif fonctionnel

Rendre les hints interprétatifs obligatoires pour produire les champs publics interprétatifs d’un aspect.

### Objectif architectural

Remplacer le pipeline temporaire :

```text
AspectReferenceData hybride
→ AspectDefinitionRuntimeData legacy
→ structural_definition() + interpretive_profile()
```

par un pipeline explicite :

```text
AspectReferenceSet.structural_definitions
AspectReferenceSet.interpretive_profiles
→ calculateur structurel
→ resolver de hints
→ projection publique
```

---

## Périmètre inclus

CS-233 couvre :

1. La suppression de `AspectDefinitionRuntimeData` si plus aucun consommateur interne ne l’exige.
2. La suppression des champs interprétatifs de `AspectReferenceData`, ou leur confinement dans une structure dédiée.
3. L’ajout de vues explicites dans `AspectReferenceSet`, par exemple :

```python
structural_definitions: tuple[AspectStructuralDefinitionRuntimeData, ...]
interpretive_profiles: tuple[AspectInterpretiveProfileRuntimeData, ...]
```

4. La migration de `AstrologyRuntimeReferenceMapper` pour construire ces vues séparées.
5. La migration de `natal_calculation_nodes._aspect_runtime_rules` pour ne plus passer par `AspectDefinitionRuntimeData`.
6. La suppression de `_aspect_definition` si elle ne sert plus qu’au bridge legacy.
7. La suppression de `AspectResult.default_valence`, `AspectResult.interpretive_valence` et `AspectResult.energy_type`.
8. La suppression du fallback `json_builder` sur les champs plats d’aspect.
9. La mise à jour des tests d’architecture pour retirer les allowlists temporaires.
10. La mise à jour de `docs/architecture/astrology-runtime-surfaces.md`.

---

## Hors périmètre

CS-233 ne doit pas :

- supprimer les tables DB de valence ;
- modifier les valeurs de `astral_aspect_profiles.json` ;
- modifier la doctrine astrologique ;
- modifier les scores prediction ;
- supprimer les champs publics `interpretive_valence` et `energy_type` du JSON natal ;
- changer le frontend sauf si un test prouve un usage direct d’un champ supprimé ;
- refondre le domaine prediction.

Le domaine prediction peut continuer à utiliser ses contrats propres :

```text
AspectProfileData.default_valence
AspectProfileData.energy_type
```

mais il ne doit pas dépendre d’un runtime structurel astrology hybride.

---

## Design cible

### Référentiel d’aspects

Option préférée :

```python
@dataclass(frozen=True, slots=True)
class AspectReferenceSet:
    structural_definitions: tuple[AspectStructuralDefinitionRuntimeData, ...]
    interpretive_profiles: tuple[AspectInterpretiveProfileRuntimeData, ...]
    orb_rules: tuple[AspectOrbRuleReferenceData, ...]
```

Option acceptable si compatibilité interne nécessaire :

```python
@dataclass(frozen=True, slots=True)
class AspectReferenceSet:
    items: tuple[AspectStructuralDefinitionRuntimeData, ...]
    interpretive_profiles: tuple[AspectInterpretiveProfileRuntimeData, ...]
    orb_rules: tuple[AspectOrbRuleReferenceData, ...]
```

Dans les deux cas :

```text
les calculateurs lisent uniquement les définitions structurelles ;
les resolvers lisent uniquement les profils interprétatifs ;
aucun objet référentiel unique ne force les deux.
```

### Graphe natal

`_aspect_runtime_rules` doit construire directement :

```python
tuple[AspectStructuralDefinitionRuntimeData, ...]
dict[str, AspectInterpretiveProfileRuntimeData]
```

sans créer `AspectDefinitionRuntimeData`.

### AspectResult

`AspectResult` ne doit porter que :

```text
aspect_code
planet_a
planet_b
angle
orb
orb_used
orb_max
family
is_major
is_minor
aspect_interpretive_hints
aspect_runtime
```

Interdit :

```text
default_valence
interpretive_valence
energy_type
```

### Projection publique

`json_builder` doit résoudre :

```python
hints = aspect.aspect_interpretive_hints
```

Si les hints manquent pour un aspect publié, le comportement doit être explicite :

```text
erreur de contrat
ou champ public None uniquement si le mode dégradé est documenté
```

Pas de fallback silencieux sur `aspect.interpretive_valence` ou `aspect.energy_type`.

---

## Tests attendus

### Tests unitaires

Mettre à jour ou ajouter :

```text
test_aspect_calculation_contracts.py
test_aspect_interpretive_hint_resolver.py
test_natal_calculation_graph_execution.py
test_chart_json_builder.py
test_astrology_runtime_reference_repository.py
```

Prouver que :

1. `AspectDefinitionRuntimeData` n’est plus nécessaire au calcul natal.
2. `AspectReferenceSet` expose une vue structurelle et une vue interprétative séparées.
3. `AspectResult` refuse ou ignore les champs plats de valence.
4. `json_builder` utilise les hints comme source unique des champs publics interprétatifs.
5. L’absence de hints est détectée explicitement.

### Tests d’architecture

Mettre à jour :

```text
test_astrology_runtime_boundary.py
test_structural_runtime_boundary.py
test_aspect_runtime_boundary.py
test_api_contract_neutrality.py
```

Supprimer les allowlists temporaires pour :

```text
AspectDefinitionRuntimeData
AspectReferenceData.default_valence
AspectReferenceData.interpretive_valence
AspectReferenceData.energy_type
natal_calculation_nodes._aspect_definition
AspectRuntimeWeightTaxonomy interpretive_weight legacy
```

Ajouter une assertion :

```text
aucune exception Temporary ne reste pour les champs interprétatifs aspectuels.
```

### Tests de compatibilité publique

Conserver :

```text
interpretive_valence
energy_type
```

dans le JSON public, mais vérifier qu’ils viennent des hints.

---

## Critères d’acceptation

### AC1 — Plus de définition legacy

`AspectDefinitionRuntimeData` est supprimé ou n’est plus importé par les chemins de calcul natal.

### AC2 — Référentiel non hybride

`AspectReferenceData` ne force plus les champs `default_valence`, `interpretive_valence` et `energy_type` dans la même structure que l’angle et l’orbe.

### AC3 — Graphe direct

Le graphe natal consomme directement les définitions structurelles et les profils interprétatifs séparés.

### AC4 — AspectResult propre

`AspectResult` ne contient plus de champs plats interprétatifs, même exclus du JSON schema.

### AC5 — Projection publique par hints

`json_builder` ne lit plus `aspect.interpretive_valence` ou `aspect.energy_type` comme fallback.

### AC6 — Allowlists nettoyées

Les allowlists `Temporary` liées aux champs interprétatifs aspectuels sont supprimées.

### AC7 — Prediction isolée

Les tests confirment que prediction utilise ses propres profils ou projections, pas le runtime structurel astrology.

---

## Validation recommandée

PowerShell, après activation du venv :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q backend/tests/architecture backend/tests/unit/domain/astrology/test_aspect_calculation_contracts.py backend/tests/unit/domain/astrology/test_aspect_interpretive_hint_resolver.py backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py backend/tests/unit/domain/astrology/test_natal_calculation_graph_execution.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py
```

Compléter avec les tests prediction ciblés :

```powershell
pytest -q backend/app/tests/unit/test_astrology_prediction_boundary.py backend/app/tests/unit/test_public_projection.py backend/app/tests/unit/test_contribution_calculator.py
```

---

## Risques et points d’attention

Le risque principal est de casser des fixtures ou tests qui construisent encore un aspect avec des champs plats de valence. Ces fixtures doivent être migrées vers :

```text
AspectInterpretiveProfileRuntimeData
AspectInterpretiveHintsRuntimeData
```

Le second risque est de casser le JSON public en supprimant le fallback trop vite. La sortie publique doit rester stable, mais sa source doit devenir strictement `aspect_interpretive_hints`.

Le troisième risque est de déplacer les champs hybrides dans un dictionnaire libre. La séparation doit rester typée.

