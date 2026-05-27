# Validation Extinction Legacy Injection LLM Natale

<!-- Commentaire global: ce rapport cloture l'audit des anciens carriers d'injection LLM natale. -->

## Resume de l'etat final

Statut: done apres review d'implementation.

Le chemin LLM natal actif est ownerise par `llm_astrology_input_v1`. Les contrats natals modernes declares dans
`canonical_use_case_registry.py` exposent uniquement `llm_astrology_input_v1` comme entree requise, et le runtime
`LLMGateway` retire `chart_json` et `natal_data` des variables de rendu pour les use cases natals.

Les occurrences restantes de `chart_json`, `natal_data`, `evidence_catalog`, `legacy`, `fallback` et
`transition-condition` sont classees ci-dessous. Aucune occurrence inspectee ne prouve un second chemin actif
d'injection du prompt LLM natal.

## Surfaces legacy supprimees

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| Placeholder natal `chart_json` | runtime/config | garde-negative | Use cases `natal_interpretation`, `natal_interpretation_short` | `llm_astrology_input_v1` | keep | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` lignes 183-210; test `test_modern_natal_contracts_only_expose_llm_astrology_input_v1` | Aucun risque de suppression: il n'est plus declare par les contrats natals modernes. |
| Variables de rendu `chart_json` / `natal_data` | runtime | garde-negative | `LLMGateway` | `llm_astrology_input_v1` | keep | `backend/app/domain/llm/runtime/gateway.py` lignes 1391-1393; test `test_natal_user_payload_ignores_legacy_carriers_when_modern_input_exists` | Risque faible: garde de regression ajoutee. |
| Schema de validation natal avec anciens carriers | runtime/test | garde-negative | `LLMGateway._build_validation_payload` | `llm_astrology_input_v1` | keep | `backend/app/domain/llm/runtime/gateway.py` lignes 1927-1933; test `test_natal_validation_payload_ignores_declared_legacy_carriers` | Risque faible: le test echoue si un ancien carrier est reinjecte. |

## Tests et mocks legacy supprimes

Aucun test de compatibilite legacy n'a ete conserve comme comportement nominal. Les tests ajoutes sont des guards
negatifs: ils prouvent que les carriers legacy declares ou fournis en contexte ne nourrissent pas le chemin natal.

Tests de preuve:

- `backend/tests/integration/test_llm_legacy_extinction.py::test_modern_natal_contracts_only_expose_llm_astrology_input_v1`
- `backend/tests/integration/test_llm_legacy_extinction.py::test_natal_user_payload_ignores_legacy_carriers_when_modern_input_exists`
- `backend/tests/integration/test_llm_legacy_extinction.py::test_natal_validation_payload_ignores_declared_legacy_carriers`

## References restantes et justification

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `build_chart_json` et `chart_json_dict` dans le service natal | non-LLM ownerise | hors-chemin-llm-ownerise | Projection publique/audit natal hors carrier prompt | `llm_astrology_input_v1` pour le prompt LLM | keep | `backend/app/services/llm_generation/natal/interpretation_service.py` construit ensuite `_build_llm_astrology_input_v1` et passe `llm_astrology_input_v1` au gateway | Risque faible si un futur patch rebranche `chart_json_dict` au prompt; guards runtime couvrent ce cas. |
| `event_guidance` avec `chart_json` | configuration non natale | hors-chemin-llm-ownerise | Use case `event_guidance`, pas chemin LLM natal | Hors scope CS-338 | keep | `backend/app/domain/llm/configuration/canonical_use_case_registry.py` lignes 231-247 | Risque de confusion documentaire; laisse hors scope car non natal. |
| `ExecutionContext.chart_json` / `natal_data` | contrat runtime partage | hors-chemin-llm-ownerise | Runtime LLM generique et tests negatifs | `llm_astrology_input_v1` pour les use cases natals | keep | `backend/app/domain/llm/runtime/contracts.py` lignes 114-120; `LLMGateway` ignore ces champs pour validation/rendu natal | Risque residuel: champ partage existant pour surfaces non natales; garde natal ajoutee. |
| `evidence_catalog` | validation output | hors-chemin-llm-ownerise | `output_validator.py`, flags de validation | `llm_astrology_input_v1.evidence.evidence_refs` pour audit natal | keep | `backend/app/domain/llm/runtime/output_validator.py` normalise/sanitise les preuves de sortie, pas le prompt natal | Risque faible: role validation-only a surveiller. |
| Termes `legacy`, `fallback`, `transition-condition` dans `_condamad` et `_story_briefs` | documentation historique | archive-documentaire | Audits, briefs, capsules et rapports CONDAMAD | Rapport final CS-338 | keep | `legacy-scan-before.txt` et `legacy-scan-after.txt` conservent les occurrences documentaires pour audit | Risque faible: presence textuelle volumineuse; le rapport distingue texte historique et execution runtime. |
| Tests contenant `chart_json` / `natal_data` | tests | garde-negative | Guards de non-regression ou tests non-LLM | `llm_astrology_input_v1` pour le chemin natal | keep | `backend/tests/integration/test_llm_legacy_extinction.py`, `backend/app/tests/unit/test_gateway_input_validation_payload.py`, `backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py` | Risque faible: reviewer doit verifier que ces tests restent negatifs. |

## Preuves du chemin unique llm_astrology_input_v1

- `list_modern_natal_use_case_contracts()` ne retient que les contrats natals dont le schema requiert
  `llm_astrology_input_v1`.
- `LLMGateway.build_user_payload()` rend le bloc `llm_astrology_input_v1` et ne bascule vers `chart_json` que pour
  les use cases non natals.
- `LLMGateway.execute_request()` supprime `chart_json` et `natal_data` des variables de rendu quand le use case est
  natal.
- `LLMGateway._build_validation_payload()` ignore `chart_json`, `natal_data` et `evidence_catalog` pour les schemas
  de validation natals, meme si ces proprietes sont declarees.

## Commandes de validation executees

Les commandes Python ont ete lancees apres activation de `.\.venv\Scripts\Activate.ps1`.

| Commande | Resultat |
|---|---|
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_prepare.py --repair-generated-only _condamad\stories\CS-338-cloturer-extinction-legacy-injection-llm-natale --root . --with-optional` | PASS |
| `python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-338-cloturer-extinction-legacy-injection-llm-natale` | PASS |
| `cd backend; ruff format tests\integration\test_llm_legacy_extinction.py` | PASS |
| `cd backend; ruff check .` | PASS |
| `cd backend; python -B -m pytest -q --long tests\integration\test_llm_legacy_extinction.py --tb=short` | PASS, 7 tests |
| `cd backend; python -B -m pytest -q --long tests\integration\test_llm_runtime_suppression.py --tb=short` | PASS, 8 tests |
| `cd backend; python -B -m pytest -q app\tests\unit\test_gateway_input_validation_payload.py --tb=short` | PASS, 2 tests |
| `cd backend; pytest --long tests` | PASS, 1420 passed, 9 skipped |
| `rg -n "chart_json\|natal_data\|evidence_catalog\|legacy\|fallback\|transition-condition" backend\app backend\tests _condamad _story_briefs` | PASS avec occurrences classees |
| `rg -n "llm_astrology_input_v1" backend\app backend\tests _condamad _story_briefs` | PASS, chemin moderne present |

## Risques residuels

- Les scans documentaires `_condamad` / `_story_briefs` restent volumineux car ils contiennent les briefs et audits
  historiques. Ce n'est pas un blocker tant que ces occurrences restent archive-documentaire.
- `ExecutionContext` conserve des champs generiques `chart_json` et `natal_data` pour le runtime partage. Le risque de
  rebranchement natal est couvert par les guards ajoutes dans `test_llm_legacy_extinction.py`.
- Aucun blocker externe actif n'a ete identifie; aucune `decision-utilisateur-requise` n'est ouverte.
