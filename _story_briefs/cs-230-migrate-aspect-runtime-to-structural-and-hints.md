# CS-230 — Migrate Aspect Runtime To Structural Runtime And Interpretive Hints

## Résumé

CS-230 migre le runtime d’aspects vers la séparation définie en CS-229.

La cible est que le calculateur et le builder structurel d’aspects ne produisent plus directement :

```text
default_valence
interpretive_valence
energy_type
interpretive_weight
```

Ces champs doivent être déplacés vers un resolver ou adapter interprétatif dédié, construit à partir :

```text
AspectStructuralRuntimeData
référentiel d’aspects
profils sémantiques/interprétatifs
```

Cette story doit préserver les sorties publiques existantes via une projection contrôlée.

---

## Contexte

CS-229 a défini deux couches :

```text
structural runtime
interpretive runtime / interpretive hints
```

Le code actuel transporte encore les champs interprétatifs dès les contrats de calcul :

```python
AspectDefinitionRuntimeData.default_valence
AspectDefinitionRuntimeData.interpretive_valence
AspectDefinitionRuntimeData.energy_type
AspectCalculationResult.default_valence
AspectCalculationResult.interpretive_valence
AspectCalculationResult.energy_type
AspectRuntimeData.interpretation
```

Cela signifie que la couche structurelle sait déjà si un aspect est `positive`, `negative`, `harmonious` ou `dynamic_challenging`.

CS-230 doit déplacer cette connaissance hors du runtime structurel.

---

## Problème à résoudre

Aujourd’hui, le chemin est :

```text
aspect reference
→ aspect definition runtime
→ aspect calculation result
→ aspect runtime
→ chart JSON
→ interpretation input / prediction
```

Le même objet transporte à la fois :

- la géométrie de l’aspect ;
- l’orbe ;
- la force technique ;
- la valence ;
- l’énergie interprétative.

La frontière entre calcul et interprétation n’est donc pas prouvable par les types.

---

## Objectifs

### Objectif fonctionnel

Faire en sorte qu’un aspect structurel puisse être calculé sans champs de valence.

Exemple cible :

```python
runtime = build_aspect_structural_runtime_data(aspect_result)
hints = aspect_interpretive_hint_resolver.resolve(runtime, reference)
```

### Objectif architectural

Installer une responsabilité claire :

```text
calculateur d’aspects
→ détecte une relation géométrique

builder structurel
→ enrichit force technique, orbe, metadata, modifiers factuels

resolver interprétatif
→ ajoute valence, energy_type, axes, poids interprétatifs
```

---

## Périmètre inclus

CS-230 couvre :

1. La migration de `AspectDefinitionRuntimeData` pour séparer définition structurelle et profil interprétatif.
2. La migration de `AspectCalculationResult` pour ne plus porter de champs interprétatifs dans sa forme structurelle cible.
3. La création d’un resolver de hints interprétatifs d’aspects.
4. La migration de `build_aspect_runtime_data` vers un builder structurel.
5. La préservation temporaire d’une façade compatible si des consommateurs attendent encore `aspect_runtime.interpretation`.
6. La migration de `ChartInterpretationInputBuilder` pour consommer les hints interprétatifs plutôt que le runtime structurel hybride.
7. La migration de `json_builder` pour construire les champs publics `interpretive_valence` et `energy_type` depuis les hints ou une projection dédiée.
8. La migration de `natal_calculation_nodes` et des mappers de référentiel pour fournir deux vues : structurelle et interprétative.
9. La vérification des consommateurs `dominant_aspects`, `pattern_runtime` et `prediction` qui encapsulent ou lisent les aspects.
10. La mise à jour des tests unitaires et d’intégration ciblés.
11. Les recherches anti-régression sur les champs déplacés.

---

## Hors périmètre

CS-230 ne doit pas :

- supprimer les champs publics du JSON natal ;
- supprimer les tables DB de valence ;
- modifier les valeurs de `astral_aspect_profiles.json` ;
- changer les scores ou la doctrine astrologique ;
- modifier le frontend ;
- réécrire le moteur de prédiction ;
- supprimer toutes les surfaces legacy du `NatalResult` ;
- migrer les transits ou la synastrie sauf si un test ciblé l’exige.

---

## Design cible

### Calcul structurel

Le calculateur d’aspects doit retourner uniquement des faits structurels.

Champs autorisés :

```text
aspect_code
planet_a
planet_b
chart_a
chart_b
angle
orb
orb_used
orb_max
family
is_major
is_minor
```

Champs interdits dans le résultat structurel :

```text
default_valence
interpretive_valence
energy_type
prompt_hint
meaning
narrative
```

### Hints interprétatifs

Créer un resolver.

Nom recommandé :

```python
AspectInterpretiveHintResolver
```

Responsabilités :

- recevoir un aspect structurel ;
- retrouver le profil interprétatif par `aspect_code` et système ;
- produire un contrat typé de hints ;
- ne pas calculer d’orbe ;
- ne pas modifier la force technique ;
- ne pas écrire de texte narratif long.

Entrées recommandées :

```python
runtime: AspectStructuralRuntimeData
profile: AspectInterpretiveProfileRuntimeData
```

ou :

```python
runtime: AspectStructuralRuntimeData
reference: AstrologyRuntimeReference
```

à condition que le resolver ne transmette jamais la vue interprétative au calculateur structurel.

### Projection publique

Le JSON public peut continuer à exposer :

```text
interpretive_valence
energy_type
```

mais ces champs doivent être documentés comme projection publique interprétative, non comme runtime structurel.

---

## Compatibilité temporaire

Si le delta est trop large, autoriser une façade temporaire :

```python
AspectRuntimeData.interpretation
```

mais uniquement si :

1. elle est documentée comme legacy compatibility ;
2. elle est alimentée depuis le resolver interprétatif ;
3. elle n’est plus produite par le calculateur structurel ;
4. une story de suppression explicite existe.

Même règle pour les objets plats historiques :

```python
AspectCalculationResult.default_valence
AspectCalculationResult.interpretive_valence
AspectCalculationResult.energy_type
```

Ils peuvent rester uniquement comme projection legacy si un consommateur externe l’exige, mais ils ne doivent plus être nécessaires à la construction du runtime structurel.

---

## Consommateurs à auditer explicitement

Auditer au minimum :

```text
backend/app/domain/astrology/runtime/natal_calculation_nodes.py
backend/app/domain/astrology/builders/aspect_runtime_builder.py
backend/app/domain/astrology/runtime/aspect_calculation_contracts.py
backend/app/domain/astrology/calculators/aspects.py
backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py
backend/app/domain/astrology/interpretation/aspect_interpretation_facts.py
backend/app/domain/astrology/interpretation/aspect_interpretation_builder.py
backend/app/domain/astrology/interpretation/dominant_aspects.py
backend/app/domain/astrology/runtime/dominant_aspect_runtime_data.py
backend/app/domain/astrology/runtime/pattern_runtime_data.py
backend/app/services/chart/json_builder.py
backend/app/domain/prediction/**
backend/app/services/prediction/**
backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py
backend/app/infra/db/repositories/reference_repository.py
```

Pour chaque hit, décider :

```text
structurel
hint interprétatif
projection publique
prediction contract
legacy temporaire
test/fixture
```

---

## Tests attendus

### Tests unitaires

Ajouter ou mettre à jour :

```text
test_aspect_calculation_contracts.py
test_aspect_runtime_builder.py
test_aspect_interpretive_hint_resolver.py
test_chart_interpretation_input_builder.py
test_chart_json_builder.py
test_natal_calculation_graph_execution.py
test_dominant_aspects.py
test_pattern_runtime_contract.py
```

Prouver que :

1. le calculateur d’aspects ne retourne plus de valence dans le contrat structurel cible ;
2. le builder structurel ne crée pas de bloc interprétatif ;
3. le resolver interprétatif retrouve les hints attendus ;
4. le JSON public conserve les champs historiques ;
5. l’input interprétatif reçoit les hints depuis la couche dédiée ;
6. aucun recalcul géométrique n’est fait dans le resolver interprétatif.
7. la dominance d’aspects ne dépend pas des hints interprétatifs ;
8. le domaine prediction reçoit les valences via son contrat, pas via le runtime structurel.

### Tests d’architecture

Ajouter un test qui scanne les modules structurels :

```text
backend/app/domain/astrology/runtime/aspect_calculation_contracts.py
backend/app/domain/astrology/calculators/aspects.py
backend/app/domain/astrology/builders/aspect_runtime_builder.py
```

Interdire :

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

Prévoir une allowlist temporaire uniquement si un alias de compatibilité est nécessaire.

---

## Critères d’acceptation

### AC1 — Calculateur structurel

Le calculateur d’aspects peut produire un résultat sans champs interprétatifs.

### AC2 — Runtime structurel propre

Le runtime structurel d’aspects ne contient plus de bloc `interpretation` comme source primaire.

### AC3 — Resolver interprétatif dédié

Un resolver ou adapter produit les hints interprétatifs d’aspects.

### AC4 — Compatibilité publique

Le JSON natal public reste compatible pour `interpretive_valence` et `energy_type`.

### AC5 — Input interprétatif branché

L’input interprétatif consomme les hints depuis la couche dédiée, pas depuis le runtime structurel.

### AC6 — Guardrails

Les tests d’architecture empêchent la réintroduction des champs interprétatifs dans les modules structurels.

### AC7 — Prediction non cassée

Les usages prediction de `default_valence` et `energy_type` restent alimentés par une projection ou un contrat dédié.

### AC8 — Graph runtime aligné

Les nodes du graphe natal ne transmettent pas de vue interprétative aux calculateurs structurels.

---

## Validation recommandée

PowerShell, après activation du venv :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py backend/tests/unit/domain/astrology/test_aspect_interpretation_facts.py backend/app/tests/unit/test_chart_json_builder.py backend/tests/unit/domain/astrology/interpretation/test_chart_interpretation_input_builder.py backend/tests/architecture/test_chart_interpretation_input_boundary.py
```

Ajouter les nouveaux tests créés par la story.

---

## Risques et points d’attention

Le risque principal est de casser les consommateurs historiques qui lisent directement :

```python
aspect.default_valence
aspect.interpretive_valence
aspect.energy_type
aspect.aspect_runtime.interpretation
```

La migration doit donc être progressive :

```text
1. créer les nouveaux contrats ;
2. alimenter les hints ;
3. migrer les consommateurs internes ;
4. conserver la projection publique ;
5. supprimer les alias dans une story dédiée.
```

Ne pas déplacer les champs dans un dictionnaire libre. La séparation doit être typée, testée et documentée.

Ne pas oublier les mappers de référentiel : si `AstrologyRuntimeReference.aspects` continue à exposer uniquement une structure hybride, la migration sera cosmétique. La séparation doit exister au moins dans les vues consommées par les calculateurs et par le resolver.
