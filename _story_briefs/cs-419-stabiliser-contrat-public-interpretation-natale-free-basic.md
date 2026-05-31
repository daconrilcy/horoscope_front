# CS-419 - Stabiliser Le Contrat Public D'interpretation Natale Free Et Basic

<!-- Commentaire global: ce brief cadre la stabilisation backend du contrat public des lectures natales free et Basic. -->

## Resume

Clarifier et tester le contrat public retourne par `/v1/natal/interpretation` pour les deux
formats actuellement exposes a la page `/natal`:

- Free / short: `meta.level=short`, `use_case=natal_interpretation_short`,
  `interpretation` au format `AstroFreeResponseV1`.
- Basic / complete: `meta.level=complete`, `schema_version=basic_natal_interpretation_v2`,
  `basic_natal_interpretation_v2` au format `BasicNatalInterpretationV2`.

La story doit empecher qu'une lecture free courte soit classee comme lecture complete obsolete,
et garantir que la lecture Basic V2 dispose d'un payload public complet, lisible et sans fuite
technique.

## Contexte

L'exemple utilisateur `daconrilcy@hotmail.com` montre que l'endpoint retourne une interpretation
courte valide:

- `use_case=natal_interpretation_short`
- `meta.level=short`
- `interpretation.title`, `summary`, `sections`, `highlights`, `advice`, `disclaimers`
- `narrative_natal_reading_v1=null`
- `basic_natal_interpretation_v2=null`

La page `/natal` affiche pourtant un message de lecture complete a regenerer, car le frontend ne
dispose pas d'un contrat suffisamment explicite pour distinguer les surfaces free short, Basic V2
et complete legacy.

## Objectif

Garantir cote backend un contrat public non ambigu:

```text
Free / short
=> AstroFreeResponseV1 public lisible
=> aucune exigence narrative_natal_reading_v1
=> aucune erreur "complete obsolete"

Basic / complete
=> basic-natal-reading-v1
=> basic_natal_interpretation_v2 public non nul
=> contenu structure, auditable, sans marqueurs techniques
```

## Perimetre Inclus

1. Auditer la projection publique de `NatalInterpretationResponse` pour les lectures free short
   et Basic complete.
2. Ajouter des tests backend prouvant que `natal_interpretation_short` est un format public valide,
   pas une complete obsolete.
3. Ajouter des tests backend prouvant qu'une lecture Basic complete compatible expose
   `basic_natal_interpretation_v2` avec ses versions et son contenu public.
4. Verifier que `data.interpretation` reste present et coherent pour la retrocompatibilite free,
   sans imposer au frontend de le traiter comme une lecture complete.
5. Verifier que `disclaimers` sont disponibles au niveau racine et/ou dans le payload public sans
   duplication incoherente.
6. Ajouter un snapshot JSON avant/apres base sur le profil utilisateur exemple ou une fixture
   equivalente non sensible.
7. Documenter les differences attendues entre free short, Basic V2 et complete legacy.

## Hors Perimetre

- Refaire le rendu React de `/natal` (traite par CS-420).
- Modifier les droits commerciaux ou les quotas.
- Declencher un appel provider live dans les tests automatises.
- Migrer toutes les anciennes interpretations persistees.
- Reintroduire des cartes factuelles legacy ou des champs techniques publics.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/00-story.md`
- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/00-story.md`
- `_condamad/stories/CS-418-integrer-basic-natal-v2-persistance-cache-qa/evidence/basic-v2-runtime-after.json`
- `backend/app/services/api_contracts/public/natal_interpretation.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/stored_interpretation_payload.py`
- `backend/app/domain/astrology/reading/basic_natal_contracts.py`
- `backend/tests/integration/test_basic_natal_v2_pipeline.py`
- Pieces jointes utilisateur: reponse `/v1/natal/interpretation`, reponse
  `/v1/users/me/natal-chart/`, DOM actuel de `/natal`.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-150` - les payloads rejetes restent exclus des routes publiques.
  - `RG-152` - les lectures publiques ne doivent pas exposer `chart_json`, audit ou signaux internes.
  - `RG-154` - les marqueurs techniques ne doivent pas atteindre le DOM public via le contrat.
  - `RG-155` - pas de padding semantique ni de sources publiques vides pour les lectures completes.
  - `RG-164` - la selection Basic reste portee par `BasicNatalReadingPlan`.
  - `RG-165` - le payload Basic provider/public exclut PII, scores, chemins et IDs bruts.
  - `RG-166` - les drafts Basic acceptes restent conformes au plan.
  - `RG-167` - Basic complete persiste et relit uniquement `basic-natal-reading-v1`.
  - `RG-168` - `BasicNatalInterpretationV2` reste le contrat public canonique Basic V2.
- Required regression evidence:
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/integration/test_natal_interpretation_public_free_basic_contract.py --tb=short`
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py --tb=short`
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/integration/test_basic_natal_v2_cache_invalidation.py --tb=short`
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/unit/test_basic_natal_reading_contracts.py tests/architecture/test_basic_natal_reading_contract_boundaries.py --tb=short`
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/unit/test_natal_interpretation_stored_payload.py tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short`
  - Depuis la racine repo: `rg -n "ranking_score|condition_axis|score_profile|weighted_score|prompt_hint|audit_input|chart_json|natal_data" backend/app/services/api_contracts backend/app/services/llm_generation/natal backend/app/domain/astrology/reading`
  - Les hits `rg` sont autorises uniquement dans les constantes denylist, validateurs, tests de rejet ou assertions de garde; tout hit dans une serialisation publique acceptee est bloquant.
- Registry enrichment expected:
  - Non attendu si la story ne fait que stabiliser les invariants existants.
- Allowed differences:
  - Les reponses publiques peuvent devenir plus explicites dans `meta.schema_version` ou dans les
    tests snapshot.
  - Une lecture free short reste rendable sans `narrative_natal_reading_v1`.

## Criteres D'acceptation

1. Une reponse free short similaire a l'exemple utilisateur est validee par test d'integration.
2. Free short expose `title`, `summary`, au moins une section, des highlights/advice optionnels
   lisibles et les disclaimers canoniques.
3. Free short ne contient pas `basic_natal_interpretation_v2` et n'exige pas
   `narrative_natal_reading_v1`.
4. Basic complete compatible expose `basic_natal_interpretation_v2` non nul avec `locale`,
   `level=basic`, `engine_version=basic-natal-reading-v1`,
   `schema_version=basic_natal_interpretation_v2`, versions de taxonomie/salience/prompt/validator.
5. Basic complete expose `basic_natal_interpretation_v2.interpretation` avec `title`,
   `introduction`, `themes`, `conclusion`, `public_evidence`, `limitations` et
   `disclaimers` publics; `data.interpretation` peut rester un resume de compatibilite mais ne
   doit pas etre le contrat canonique Basic.
6. Aucune reponse publique acceptee ne contient les champs techniques interdits.
7. Les snapshots avant/apres prouvent que les differences attendues sont uniquement contractuelles.
8. Les tests documentent clairement quelle branche doit etre rendue par le frontend.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration/test_natal_interpretation_public_free_basic_contract.py --tb=short
python -B -m pytest -q tests/integration/test_basic_natal_v2_pipeline.py --tb=short
python -B -m pytest -q tests/integration/test_basic_natal_v2_cache_invalidation.py --tb=short
python -B -m pytest -q tests/unit/test_basic_natal_reading_contracts.py tests/architecture/test_basic_natal_reading_contract_boundaries.py --tb=short
python -B -m pytest -q tests/unit/test_natal_interpretation_stored_payload.py tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short
```

Scans:

```powershell
rg -n "ranking_score|condition_axis|score_profile|weighted_score|prompt_hint|audit_input|chart_json|natal_data" backend/app/services/api_contracts backend/app/services/llm_generation/natal backend/app/domain/astrology/reading
```

Les hits de scan doivent etre classes: denylist, validateur, test de rejet ou fuite bloquante.

## Dependances

- CS-416.
- CS-417.
- CS-418.

## Risques

Le risque principal est de corriger seulement le frontend alors que l'API reste ambigue. Cette
story doit produire un contrat executable que le frontend peut brancher sans heuristique fragile.
