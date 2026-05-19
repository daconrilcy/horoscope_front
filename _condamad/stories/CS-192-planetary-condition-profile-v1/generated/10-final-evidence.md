<!-- Evidence finale CS-192. -->

# CS-192 Final Evidence

Status: done

## Summary

CS-192 ajoute une couche backend `PlanetConditionProfile` derivee des
`PlanetDignityResult`. Les axes conditionnels sont transportes par le runtime
reference depuis les poids de dignites, puis exposes dans
`NatalResult.condition_profiles` et dans le JSON public sous
`planet_condition_profiles`.

## AC Validation

Tous les AC1 a AC9 sont `PASS`; voir `generated/03-acceptance-traceability.md`.

## Files Changed

- `backend/migrations/versions/20260519_0130_add_condition_axes_to_dignity_weights.py`
- `backend/app/infra/db/models/dignity_reference.py`
- `backend/app/infra/db/repositories/dignity_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/condition/contracts.py`
- `backend/app/domain/astrology/condition/planet_condition_profile_service.py`
- `backend/app/domain/astrology/condition/__init__.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/services/chart/json_builder.py`
- Tests backend cibles et factories runtime associes.
- Evidence CS-192 sous `evidence/`.

## Commands Run

- `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py backend/app/tests/integration/test_reference_data_migrations.py` - PASS, 43 passed, 5 deselected.
- `ruff format <fichiers CS-192>` - PASS.
- `ruff check <fichiers CS-192>` - PASS.
- `rg -n "Session|select\(|from app\.infra|from app\.services|from app\.api|from app\.domain\.prediction|from app\.services\.prediction" backend/app/domain/astrology/condition -g "*.py"` - PASS, zero hit.
- `rg -n "OpenAI|AIEngineAdapter|chat\.completions|prompt|interpretation|micro_note" backend/app/domain/astrology/condition -g "*.py"` - PASS, zero hit.
- `rg -n "VISIBILITY_WEIGHTS|CONDITION_SCORES|CONDITION_LEVELS|astral_chart_planet_condition_profiles" backend/app backend/migrations backend/tests -g "*.py"` - PASS, zero hit.
- `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -c "from app.main import app; print(app.title)"` - PASS, `horoscope-backend`.

## Commands Not Run / Limitations

- `ruff check .` a ete lance sous venv et echoue hors perimetre CS-192 sur des
  templates de skills dans `.agent/.agents/.claude/.gemini` avec noms de
  placeholder et imports inutilises preexistants. Le lint cible des fichiers
  CS-192 passe.
- Une premiere verification d'import backend a ete lancee depuis `backend/`
  avec un chemin relatif d'activation incorrect; elle a ete reexecutee depuis
  la racine avec activation venv correcte et a passe.
- Aucun demarrage applicatif local durable n'a ete lance; story backend pure
  couverte par tests de calcul, projection et persistance.

## Legacy / DRY Evidence

- Aucun import DB/API/services/prediction/LLM dans
  `backend/app/domain/astrology/condition/**`.
- Aucun mapping local `VISIBILITY_WEIGHTS`, `CONDITION_SCORES` ou
  `CONDITION_LEVELS`.
- Aucune table `astral_chart_planet_condition_profiles`.
- Le mapper refuse un payload de poids incomplet au lieu de neutraliser un axe
  absent.

## Review Findings Fixed

- Public `planet_condition_profiles` complete desormais chaque entree planete
  avec `planet_code`, `score_profile`, `tradition`, `reference_version` et
  `sect`.
- Le mapper runtime exige les cinq axes conditionnels.
- Les attributs du contrat runtime domaine ne portent plus le symbole produit
  interdit `visibility_weight`; le mapper infra traduit les colonnes DB
  `*_weight` vers `condition_visibility`, `condition_stability`,
  `condition_coherence`, `condition_support` et `condition_constraint`.
- Les snapshots et la traceability ont ete mis a jour.
- La passe review finale du 2026-05-19 a synchronise le statut et les cases de
  `00-story.md` avec le registre `story-status.md`, deja marque `done`.
- La passe de revue independante demandee par `condamad-dev-review-fix-story`
  a corrige les snapshots avant/apres trop etroits et incoherents: les champs
  chart existants sont maintenant presents dans les deux snapshots, et le
  breakdown conditionnel inclut les contributions `domicile` et
  `angular_house` coherentes avec les dignites source.
- La mention de classe de cloture dans `generated/11-code-review.md` a ete
  clarifiee: CS-192 est une architecture decision, pas une story issue d'audit.

## Review Loop Validation

- Iteration 1: findings deja corriges dans l'evidence existante
  (`planet_condition_profiles` incomplet, mapper runtime permissif, evidence
  incomplete).
- Iteration 2: la suite complete a trouve la garde
  `test_astrology_domain_does_not_carry_product_symbols` en echec sur
  `visibility_weight` dans le domaine astrology; correction appliquee par
  renommage du contrat runtime domaine.
- Iteration 3: review fraiche du 2026-05-19 sans finding restant; seule
  incoherence d'evidence corrigee dans `00-story.md`, puis validations finales.
- Iteration 4: revue independante post-demande utilisateur; corrections
  acceptees sur la coherence des snapshots, le fixture chart JSON et la
  formulation de cloture. Finding rejete/documente: les seuils locaux de
  `condition_level` sont une discretisation deterministe requise par la story,
  pas un mapping de poids conditionnels DB-backed.
- Commande: `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py backend/app/tests/integration/test_reference_data_migrations.py` - PASS, 43 passed, 5 deselected.
- Commande: `pytest -q backend/tests/unit/domain/astrology/test_planet_condition_profile_service.py backend/tests/unit/domain/astrology/test_natal_result_contract.py backend/app/tests/unit/test_chart_json_builder.py backend/app/tests/unit/test_chart_result_service.py backend/app/tests/unit/test_astrology_runtime_reference_repository.py backend/app/tests/unit/test_astrology_runtime_reference_guard.py backend/app/tests/integration/test_reference_data_migrations.py backend/app/tests/unit/test_astrology_prediction_boundary.py::test_astrology_domain_does_not_carry_product_symbols` - PASS, 44 passed, 5 deselected.
- Commande: `pytest -q` - PASS, 2693 passed, 1 skipped, 1177 deselected.
- Commande: `pytest -q` - revue fraiche post-demande utilisateur du
  2026-05-19 - PASS, 2693 passed, 1 skipped, 1177 deselected en 182.39s.
- Commande: `pytest -q` - premier relancement dans cette session interrompu
  par timeout a 304 secondes, relancee ensuite avec timeout plus long - PASS,
  2693 passed, 1 skipped, 1177 deselected en 317.22s.
- Commande: `ruff check <fichiers CS-192>` - PASS.
- Commande: `ruff format --check <fichiers CS-192>` - PASS, 19 files already formatted.
- Commande: `ruff check backend _condamad/stories/CS-192-planetary-condition-profile-v1/00-story.md`
  - PASS.
- Commande: `ruff check .` - FAIL hors perimetre CS-192 sur les templates de
  skills `.agent/.agents/.claude/.gemini` deja documentes.
- Commande: `git diff --check` - PASS.
- Commande: `.\.venv\Scripts\Activate.ps1; Set-Location backend; python -c "from app.main import app; print(app.title)"` - PASS, `horoscope-backend`.
- Scans RG-119: PASS, zero hit sur imports DB/API/services/prediction,
  LLM/prompt/interpretation et table/mappings interdits.

## Remaining Risks

- Aucun risque restant identifie dans le perimetre CS-192.
