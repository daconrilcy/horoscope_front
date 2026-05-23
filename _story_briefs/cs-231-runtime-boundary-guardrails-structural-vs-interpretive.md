# CS-231 — Runtime Boundary Guardrails Structural Vs Interpretive

## Résumé

CS-231 ajoute des guardrails d’architecture pour empêcher le retour du mélange entre runtime structurel et runtime interprétatif.

Après CS-229 et CS-230, le code doit pouvoir prouver que :

```text
les calculateurs structurels ne produisent pas de pré-interprétation ;
les adapters interprétatifs ne recalculent pas les faits structurels ;
les projections publiques restent isolées ;
les surfaces legacy sont allowlistées et bornées.
```

Cette story est une story de verrouillage. Elle ne change pas la doctrine astrologique et ne supprime pas encore toutes les surfaces historiques.

---

## Contexte

Le dépôt possède déjà des tests d’architecture pour :

- éviter les lectures directes de surfaces legacy depuis `NatalResult` ;
- éviter les branches métier par `object_type` ;
- éviter les builders spécialisés par famille d’objet ;
- protéger l’input interprétatif contre les champs narratifs.

Mais il manque une garde explicite :

```text
structural runtime ↔ interpretive runtime
```

Sans cette garde, les champs déplacés en CS-230 peuvent revenir dans les calculateurs à la faveur d’une future story.

---

## Problème à résoudre

Les mots suivants sont des signaux d’interprétation ou de projection produit :

```text
default_valence
interpretive_valence
energy_type
interpretive_weight
meaning
narrative
prompt
llm
OpenAI
AIEngineAdapter
```

Ils peuvent être légitimes dans :

```text
interpretation adapters
prompt builders
public projections
prediction domain
tests/fixtures
```

mais pas dans :

```text
calculators
structural runtime contracts
structural runtime builders
calculation graph nodes structurels
dominance structurelle
fixed-star structural calculators
```

CS-231 doit rendre cette frontière testable.

---

## Objectifs

### Objectif fonctionnel

Ajouter des tests d’architecture qui échouent dès qu’un champ interprétatif est introduit dans une couche structurelle.

### Objectif architectural

Définir une matrice simple :

| Zone | Champs structurels | Hints interprétatifs | Textes narratifs | Providers LLM |
|---|---:|---:|---:|---:|
| calculators | oui | non | non | non |
| runtime structural contracts | oui | non | non | non |
| interpretation adapters | lecture | oui | non | non |
| prompt / LLM services | lecture | oui | oui | oui |
| public JSON builder | projection | projection contrôlée | non | non |
| prediction domain | selon contrat dédié | selon contrat dédié | non | non |

---

## Périmètre inclus

CS-231 couvre :

1. L’ajout d’un test d’architecture `test_structural_runtime_does_not_expose_interpretive_fields`.
2. L’ajout d’un test d’architecture `test_interpretive_adapters_do_not_recalculate_structural_facts`.
3. L’ajout d’une allowlist explicite pour les projections publiques et les adapters legacy.
4. La mise à jour de `docs/architecture/astrology-runtime-surfaces.md`.
5. La documentation des chemins autorisés pour `default_valence`, `interpretive_valence`, `energy_type` et `interpretive_weight`.
6. La vérification que les tests ne scannent pas les fixtures de manière trop bruyante.
7. La vérification que les tests protègent les futurs calculateurs.

---

## Hors périmètre

CS-231 ne doit pas :

- migrer les contrats d’aspects si CS-230 ne l’a pas fait ;
- supprimer les champs publics ;
- supprimer les tables DB ;
- modifier les prompts ;
- modifier les scores ;
- changer le frontend ;
- ajouter une dépendance de lint externe.

---

## Zones structurelles à protéger

Chemins recommandés :

```text
backend/app/domain/astrology/calculators/**
backend/app/domain/astrology/runtime/**
backend/app/domain/astrology/builders/**
backend/app/domain/astrology/dominance/**
backend/app/domain/astrology/fixed_stars/**
backend/app/domain/astrology/dignities/**
backend/app/domain/astrology/planetary_conditions/**
backend/app/domain/astrology/advanced_conditions/**
```

Exceptions possibles :

```text
runtime/reference contracts
legacy compatibility adapters
public projection builders
tests
fixtures
```

Attention particulière :

```text
backend/app/domain/astrology/runtime/runtime_reference.py
backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py
backend/app/infra/db/repositories/reference_repository.py
```

Ces fichiers peuvent charger des données DB hybrides pendant la transition, mais ils doivent exposer des vues séparées aux consommateurs structurels et interprétatifs.

Toute exception doit avoir :

```text
chemin
champ autorisé
raison
date/story de sortie si temporaire
```

---

## Zones interprétatives autorisées

Chemins recommandés :

```text
backend/app/domain/astrology/interpretation/**
backend/app/domain/astrology/interpretation_adapters/**
backend/app/services/llm_generation/**
backend/app/domain/prediction/**
backend/app/services/prediction/**
backend/app/services/chart/json_builder.py
```

Attention :

`json_builder.py` est une projection publique, pas une source métier. Son usage doit rester en lecture/projection.

---

## Tests attendus

### Test 1 — Champs interprétatifs interdits dans le structurel

Scanner les fichiers structurels pour interdire :

```text
default_valence
interpretive_valence
energy_type
interpretive_weight
meaning
narrative
prompt
llm
OpenAI
AIEngineAdapter
```

Les allowlists doivent être minimales et justifiées.

Le test doit éviter un faux positif bloquant sur :

```text
AspectInterpretiveProfileRuntimeData
AspectInterpretiveHintsRuntimeData
docs
fixtures
tests dédiés à la compatibilité legacy
```

### Test 2 — Adapters interprétatifs sans recalcul

Scanner les adapters interprétatifs pour interdire les appels à :

```text
calculate_major_aspects
calculate_interchart_aspects
resolve_orb
PlanetDominanceEngine.calculate
FixedStarConjunctionCalculator
EssentialDignityCalculator
AccidentalDignityCalculator
```

Le but est de garantir :

```text
adapter interprétatif = projection / enrichissement sémantique
pas recalcul structurel
```

### Test 3 — Documentation synchronisée

Vérifier que les documents d’architecture mentionnent :

```text
structural runtime
interpretive runtime
public projection
legacy projection
```

### Test 4 — Référentiel sans vue hybride obligatoire

Vérifier que les calculateurs structurels ne reçoivent pas un contrat qui oblige à fournir :

```text
default_valence
interpretive_valence
energy_type
```

Ce test peut être fait par AST, par import ciblé ou par test unitaire du contrat.

---

## Critères d’acceptation

### AC1 — Guardrail structurel

Un test échoue si un champ de valence ou d’énergie interprétative revient dans un module structurel non allowlisté.

### AC2 — Guardrail interprétatif

Un test échoue si un adapter interprétatif rappelle un calculateur structurel.

### AC3 — Allowlist explicite

Chaque exception est nommée, justifiée et bornée.

### AC4 — Documentation alignée

La documentation reflète la matrice des couches.

### AC5 — Tests stables

Les guardrails ne dépendent pas de l’ordre des fichiers et n’échouent pas sur les fixtures volontairement historiques.

### AC6 — Référentiel protégé

Les contrats de référentiel consommés par les calculateurs structurels ne forcent pas les champs interprétatifs.

---

## Validation recommandée

PowerShell, après activation du venv :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q backend/tests/architecture
```

Compléter avec les tests d’aspects ciblés si CS-230 a modifié les contrats :

```powershell
pytest -q backend/tests/unit/domain/astrology/test_aspect_runtime_builder.py backend/app/tests/unit/test_chart_json_builder.py
```

---

## Risques et points d’attention

Le risque principal est de faire un test trop large qui bloque des zones légitimes comme le domaine prediction.

Préférer :

```text
scan par zones structurelles explicites
allowlists minimales
messages d’erreur actionnables
```

Le second risque est de scanner uniquement les noms de champs et de rater les imports indirects. Les tests peuvent combiner recherche texte et AST selon le besoin.

Le troisième risque est inverse : bloquer les contrats interprétatifs légitimes parce que leur nom contient `interpretive`. Les tests doivent cibler les zones structurelles, pas tout le dépôt.
