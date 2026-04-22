# Audit backend génération de prompts LLM (post-story 70-15, AC18-AC52)

Date: 2026-04-21  
Dernière passe de review : 2026-04-21 (clôture AC54–AC55, AC63–AC70 : suppression physique `backend/app/llm_orchestration/`, retrait `TRANSITION_WRAPPERS.md`, extinction `legacy_prompt_runtime.py`, tests déplacés sous `backend/tests/llm_orchestration/`, logger gateway `app.domain.llm.runtime.gateway`)  
Périmètre : backend, flux runtime prompting/persona/configuration/gateway, consommateurs métier.

## Source de vérité canonique (état visé)

- Adaptateur applicatif: `app.application.llm.ai_engine_adapter`
- Runtime gateway : `app.domain.llm.runtime.gateway`
- Prompt renderer officiel : `app.domain.llm.prompting.prompt_renderer`
- Persona composer officiel : `app.domain.llm.prompting.personas`
- Données runtime et fallback borné : `app.domain.llm.prompting.catalog` (bridge `domain.llm.legacy` et `legacy_prompt_runtime.py` supprimés, AC57/AC68)

## Preuve d’adoption canonique (scan imports)

### Imports historiques supprimés ou bornés

- `app.llm_orchestration.services.persona_composer`
  - usage nominal runtime/configuration: **0**
  - usages restants : **0 (fichier supprimé)**
- `app.domain.llm.prompting.renderer`
  - usage nominal: **0**
  - statut : **supprimé**
- `app.llm_orchestration.legacy_prompt_runtime`
  - usage nominal direct: **0** (contenu absorbé par `domain.llm.prompting.catalog`)

### Imports canoniques vérifiés

- `app.domain.llm.prompting.personas` consommé par :
  - `app.domain.llm.runtime.gateway`
  - `app.domain.llm.configuration.assembly_resolver`
- `app.domain.llm.prompting.prompt_renderer` consommé par :
  - `app.domain.llm.runtime.gateway`
  - `app.domain.llm.configuration.assembly_resolver`
  - `app.api.v1.routers.admin_llm`
- `app.application.llm.ai_engine_adapter` consommé par les services métier :
  - guidance/chat/natal/prediction (+ routes nominales associées)

## Reliquats de compatibilité tolérés (état courant)

**Aucun reliquat actif** : le dossier `backend/app/llm_orchestration/` a été supprimé ; `backend/app/domain/llm/prompting/legacy_prompt_runtime.py` n’existe plus ; les suites LLM vivent sous `backend/tests/llm_orchestration/` avec imports canoniques uniquement. Les seules occurrences textuelles de `app.llm_orchestration` ou `legacy_prompt_runtime` dans le périmètre tests sont des **littéraux de garde-fou** (`test_story_70_14_transition_guards.py`, préfixes interdits), pas des imports exécutables.

## Safe to delete next (AC30) — statut post AC31-AC40

1. `backend/app/domain/llm/prompting/renderer.py`
   - statut : **supprimé**

2. `backend/app/services/ai_engine_adapter.py`
   - statut : **supprimé**

3. `backend/app/llm_orchestration/services/persona_composer.py`
   - statut : **supprimé**

4. `backend/app/llm_orchestration/services/prompt_renderer.py`
   - statut : **supprimé**

## Validation de la passe AC31-AC40

- AC31 confirmé : les trois suppressions candidates ont bien été exécutées.
- AC32/AC33/AC36/AC37 confirmés : aucun import `backend/app` vers `app.llm_orchestration.services.prompt_renderer` ; tests et patches historiques migrés vers `app.domain.llm.prompting.prompt_renderer`.
- AC34/AC35/AC39/AC40 confirmés : registre wrappers et audit alignés sur la suppression effective du shim renderer ; phase de migration renderer explicitement clôturée.
- Import canonique confirmé : `app.domain.llm.prompting.prompt_renderer` est la référence runtime/config/admin.
- Aucun import nominal vers `app.services.ai_engine_adapter`.
- Aucun import nominal vers `app.llm_orchestration.services.persona_composer`.
- Les dépendances vers les données runtime/fallback passent par `domain.llm.prompting.catalog` (plus de `domain.llm.legacy.bridge`, plus de `legacy_prompt_runtime.py`).

## Validation de la passe AC41-AC52

- AC41/AC44/AC45 : phase wrappers namespace historique **clôturée** ; le fichier `backend/app/ops/llm/TRANSITION_WRAPPERS.md` a été **supprimé** (AC63) faute de shims restants à inventorier.
- AC42 confirmé (delta nominal) : les points d’entrée canoniques runtime/configuration migrés vers des imports `app.domain.llm.*` directs pour `composition`, `validation`, `fallback`, `assemblies`, `execution_profiles`, et imports internes `gateway`/`assembly_admin_service`.
- AC43/AC46/AC47 : aucune nouvelle dépendance tests/patches au renderer historique ; les migrations antérieures restent effectives. Les reliquats de tests historiques hors renderer sont explicitement traités comme dette bornée.
- AC48 confirmé (partiel ciblé) : les modules canoniques touchés n’utilisent plus les wrappers historiques simples quand un module canonique existe ; les outils restant en historique sont maintenus avec justification de compatibilité.
- AC49/AC50 : documentation de transition alignée sur l’état final ; plus de couche `llm_orchestration` dans l’arborescence `backend/app` (AC54–AC55, AC65).
- AC52 confirmé : la phase "wrappers namespace historiques" est clôturée comme stratégie diffuse ; les reliquats restants sont listés comme dette isolée et datée.

## Package `backend/app/prompts` (AC58 — lot 2026-04-21)

Le dossier **`backend/app/prompts/` a été supprimé** : plus de shims `catalog` / `common_context` / `validators` au chemin historique. Toute la surface correspondante est portée par **`app.domain.llm.prompting.*`** (catalogue, contexte, validators, exceptions, tests sous `app/domain/llm/prompting/tests/`).

### Constat actuel

- Aucun import `app.prompts` dans le backend Python applicatif ; garde-fou optionnel dans `tests/unit/test_story_70_14_transition_guards.py` (préfixe interdit).
- Les tests de qualification de contexte vivent sous `app/domain/llm/prompting/tests/`.

### Impact sur la lecture AC53-AC70 (passe en cours)

- Le dossier `app.prompts` confirme l’état "migration contrôlée" : le runtime canonique est bien déplacé vers `app.domain.llm.*` / `app.application.llm.*`, mais ce package conserve des **points d’entrée de transition**.
- Les dépendances legacy observées dans `app.prompts` sont conformes à la stratégie AC41-AC52 : explicites, traçables, limitées à la compatibilité, et non utilisées comme nouvelle voie nominale.
- Aucune contradiction relevée avec la suppression effective des shims renderer/persona/adapter déjà actée.
- Mise à jour passe AC53-AC70 : `app.prompts.common_context` et `app.domain.llm.prompting.context` n importent plus `app.llm_orchestration.services.fallback_governance` ni `get_legacy_use_case_name`.
- Mise à jour passe AC53-AC70 (lot taxonomy) : création de `app.domain.llm.governance.feature_taxonomy` et migration des imports nominaux critiques hors `app.llm_orchestration.feature_taxonomy`.
- Mise à jour passe AC53-AC70 (lot persona boundary) : création de `app.domain.llm.prompting.persona_boundary` et migration des imports nominaux runtime/admin hors `app.llm_orchestration.persona_boundary`.
- Mise à jour passe AC53-AC70 (lot contracts) : `gateway.py` et `admin_llm.py` n importent plus directement `app.llm_orchestration.models` / `app.llm_orchestration.admin_models` ; convergence via facades canoniques `app.domain.llm.runtime.contracts` et `app.domain.llm.configuration.admin_models`.
- Mise à jour passe AC53-AC70 (lot wrappers inverses) : `llm_orchestration.feature_taxonomy` et `llm_orchestration.persona_boundary` sont devenus des shims vers le canonique ; les builders de contexte consomment `FallbackType` via `app.domain.llm.runtime.contracts`.
- Mise à jour passe AC53-AC70 (lot natal/main/config) : `assembly_resolver`, service/route/schemas natal et `main` consomment désormais les façades canoniques (`runtime.contracts`, `prompting.schemas`, `configuration.admin_models`) pour les symboles migrés.
- Mise à jour passe AC53-AC70 (lot utilitaires runtime) : `gateway`, `fallback_governance`, `assembly_admin_service`, `assembly_resolver` consomment désormais les façades canoniques runtime pour policy/input/observability/repair/providers.
- Mise à jour passe AC53-AC70 (lot services nominaux) : `ai_engine_adapter`, `natal_interpretation_service`, `openai_responses_client`, `provider_runtime_manager`, `legacy_residual_registry`, `length_budget_injector` migrés vers `runtime.contracts`, `prompting.schemas` et `configuration.admin_models`.
- Mise à jour passe AC53-AC70 (lot routes admin/ops) : `admin_llm_assembly` et `ops_monitoring` ne dépendent plus directement de `app.llm_orchestration.*` ; elles consomment les façades canoniques.
- Mise à jour passe AC53-AC70 (lot admin/ops complémentaire) : `admin_llm`, `admin_llm_release` et les scripts ops bootstrap/release passent par les façades canoniques `domain.llm.runtime.*` et `ops.llm.services`.
- Mise à jour passe AC53-AC70 (lot coherence/performance) : la validation de cohérence startup/DB et `build_qualification_evidence` passent par `configuration.coherence`, `runtime.contracts` et `ops.llm.performance_qualification`.
- Mise à jour passe AC53-AC70 (lot provider runtime) : `provider_runtime_manager` n importe plus directement `llm_orchestration.providers.*` ni `llm_orchestration.simulation_context` ; convergence via `infrastructure.providers.llm.circuit_breaker` et `domain.llm.runtime.simulation`.
- Mise à jour passe AC53-AC70 (lot renderer/bootstrap) : `prompt_renderer` et `main` n importent plus directement `llm_orchestration.placeholder_policy` ni `llm_orchestration.seeds.use_cases_seed` ; convergence via `domain.llm.prompting.placeholder_policy` et `ops.llm.bootstrap.use_cases_seed`.
- Mise à jour passe AC53-AC70 (lot governance/ops/bootstrap) : `main`, `llm_ops_monitoring_service`, `provider_parameter_mapper` et `prompt_governance_registry` convergent vers `domain.llm.runtime.simulation`, `ops.llm.bootstrap.seed_*`, `ops.llm.ops_contract`, `domain.llm.runtime.execution_profiles_types` et `domain.llm.prompting.placeholder_policy`.
- Mise à jour passe AC53-AC70 (lot inversion interne des façades) : `domain.llm.runtime.execution_profiles_types`, `domain.llm.prompting.placeholder_policy` et `ops.llm.ops_contract` portent désormais la logique canonique ; les modules legacy homologues (`llm_orchestration/*`) sont passés en shims inverses.
- Mise à jour passe AC53-AC70 (lot schemas) : `domain.llm.prompting.schemas` devient source de vérité des schémas natal/chat ; `llm_orchestration.schemas` est réduit à un shim de compatibilité.
- Mise à jour passe AC53-AC70 (lot admin models) : `domain.llm.configuration.admin_models` devient source de vérité des contrats admin ; `llm_orchestration.admin_models` est réduit à un shim de compatibilité.
- Mise à jour passe AC53-AC70 (lot runtime contracts partiel) : `domain.llm.runtime.contracts` porte désormais nativement `FallbackStatus`, `FallbackType`, `ExecutionPathKind`, `ContextCompensationStatus`, `MaxTokensSource`, `is_reasoning_model` et `EVIDENCE_ID_REGEX`; les schémas prompting n importent plus `llm_orchestration.models`.
- Mise à jour passe AC53-AC70 (lot runtime contracts étape 2) : `UsageInfo`, `GatewayMeta` et `GatewayResult` sont portés nativement par `domain.llm.runtime.contracts`; les erreurs runtime conservent une compatibilité stricte via alias explicites vers `llm_orchestration.models`.
- Mise à jour passe AC53-AC70 (lot runtime contracts étape 3) : `UseCaseConfig` est porté nativement par `domain.llm.runtime.contracts`; `ResponseFormatConfig` reste transitoirement en alias legacy tant que `ResolvedExecutionPlan` n est pas convergé.
- Mise à jour passe AC53-AC70 (lot runtime contracts étape 4) : `ResponseFormatConfig` et `ResolvedExecutionPlan` sont désormais portés nativement par `domain.llm.runtime.contracts`, y compris la validation perimeter supportée via taxonomy canonique.
- Mise à jour passe AC53-AC70 (lot runtime contracts étape 5) : les contrats d entrée/runtime (`Execution*`, `LLMExecutionRequest`, `NatalExecutionInput`) et `RecoveryResult` sont désormais portés nativement par `domain.llm.runtime.contracts`.
- Mise à jour passe AC53-AC70 (lot runtime contracts étape 6) : `ExecutionObservabilitySnapshot` et `PerformanceQualificationReport` sont portés nativement par `domain.llm.runtime.contracts`; les flux gateway/ops restent stables en validation ciblée.
- Mise à jour passe AC53-AC70 (lot prompts étape 1) : `domain.llm.prompting.catalog` devient source canonique du catalog ; `app.prompts.catalog` est réduit en shim et les consommateurs nominaux `domain/*` ciblent désormais le chemin canonique.
- Mise à jour passe AC53-AC70 (lot prompts étape 2) : `domain.llm.prompting.validators` devient source canonique ; `app.prompts.validators` est réduit en shim de compatibilité et `assembly_resolver` nominal consomme désormais le validateur canonique.
- Mise à jour passe AC53-AC70 (lot prompts étape 3) : `domain.llm.prompting.exceptions` est introduit ; les consommateurs nominaux (`runtime.gateway`, route `predictions`, `astrologer_prompt_builder`) ciblent désormais `domain.llm.prompting.context`; les imports `app.prompts.*` restants sont bornés aux tests/historique.
- Mise à jour passe AC53-AC70 (lot legacy.bridge étape 1) : les dépendances `DEPRECATED_USE_CASE_MAPPING`/`resolve_model`/`get_legacy_max_tokens` convergent vers `domain.llm.prompting.catalog` ; l import nominal direct de `domain.llm.legacy.bridge` est désormais borné à `runtime.gateway`.
- Mise à jour passe AC53-AC70 (lot legacy.bridge étape 2) : `runtime.gateway` converge aussi `build_legacy_compat_use_case_config`, `get_legacy_output_schema` et `get_legacy_prompt_runtime_entry` vers `domain.llm.prompting.catalog`; aucun import nominal `domain.llm.legacy.bridge` ne subsiste dans `backend/app`.
- Mise à jour passe AC53-AC70 (lot legacy.bridge étape 3) : suppression physique de `domain/llm/legacy/bridge.py` (et `domain/llm/legacy/__init__.py`) ; le point d accès legacy transitoire est `domain.llm.prompting.catalog`.
- Mise à jour passe AC53-AC70 (lot prompts tests étape 4) : les tests unitaires prompts/gateway consomment les chemins canoniques `domain.llm.prompting.*`; les imports `app.prompts.*` restants sont bornés au package historique `llm_orchestration` et au shim `app.prompts.__init__`.
- Mise à jour passe AC53-AC70 (lot prompts étape 5) : extinction des derniers reliquats `app.prompts.*` dans `backend/app` (services `llm_orchestration`, patch targets tests intégration/unitaires, et `app.prompts.__init__`), avec convergence complète des imports vers `domain.llm.prompting.*`.
- Mise à jour passe AC53-AC70 (lot runtime contracts étape 7) : migration massive des tests et services de test de `app.llm_orchestration.models` vers `domain.llm.runtime.contracts` + reroutage `is_reasoning_model` dans `llm_orchestration/services/assembly_resolver`; reliquat côté `app/tests` réduit au seul `EvalReport`.
- Mise à jour passe AC53-AC70 (lot runtime contracts étape 8) : migration complète des imports `app.llm_orchestration.models` dans `llm_orchestration/tests/*` vers `domain.llm.runtime.contracts`.
- Mise à jour passe AC53-AC70 (lot runtime contracts étape 9) : ajout d alias de compatibilité runtime (`ReplayResult`, `Eval*`, `Performance*`, `GoldenRegression*`) puis reroutage des services legacy et seeds ; résultat net : plus aucun import direct `from app.llm_orchestration.models import ...` dans `backend/app` hors `domain.llm.runtime.contracts`.
- Mise à jour passe AC53-AC70 (lot prompts étape 6) : suppression physique de `llm_orchestration/legacy_prompt_runtime.py`, puis absorption du runtime data/fallback legacy dans `domain.llm.prompting.catalog` ; `domain.llm.prompting.catalog` devient le point d entrée canonique unique.
- Mise à jour passe AC53-AC70 (lot runtime contracts étape 10) : `domain.llm.runtime.contracts` est désormais autonome (plus d import depuis `llm_orchestration.models`) et `llm_orchestration/models.py` devient un shim de compatibilité minimal.
- Mise à jour passe AC53-AC70 (lot clôture étape 11) : derniers shims `llm_orchestration` retirés avant suppression du dossier ; tests legacy ajustés au comportement cible de rejet des use_case supprimés (`daily_prediction`, `chat`).
- Mise à jour passe AC53-AC70 (lot validation backend étape 12 puis clôture AC67–AC70) : campagne complète backend exécutée dans le venv avec `ruff format .`, `ruff check .`, `pytest -q` ; résultat final `2964 passed, 12 skipped`. `STRUCTURAL_FILES` ne référence plus de chemins sous `app/llm_orchestration/`.

### Suivi opérationnel (post-suppression `app/prompts`)

- `backend/app/domain/llm/prompting/context.py` — **Statut**: source de vérité prompting contexte — **Action suivante**: surveillance.
- `backend/app/domain/llm/prompting/tests/` — **Statut**: tests prompts (AC69) — **Action suivante**: maintenir imports canoniques uniquement.

### Ops LLM canonique (AC53, lot 2026-04-21)

- `app/ops/llm/release_service.py`, `eval_harness.py`, `replay_service.py`, `golden_regression_service.py`, `golden_regression_registry.py`, `prompt_lint.py`, `prompt_registry_v2.py`, `performance_qualification_service.py`, `performance_registry.py` portent les implementations reference pour les outils admin/ops.
- `app/ops/llm/services.py` reexporte uniquement depuis `app.ops.llm.*` (plus de chaine directe vers `llm_orchestration.services` pour ces symboles).
- `app/ops/llm/bootstrap/*` contient les seeds `use_cases_seed`, `seed_horoscope_narrator_assembly`, `seed_66_20_taxonomy` avec imports domaine (`schemas`, `narrator_contract`).

## Points de vigilance restants

- Conserver les garde-fous (conformité doc, tests 70.14, invariants sémantiques) pour éviter toute réintroduction de namespace `app.llm_orchestration.*` dans le code nominal `backend/app`.
- La liste d’échecs historiques dans ce document pour les suites lourdes peut être obsolète après campagne verte unifiée ; vérifier avant prochain audit.

## Conclusion

- La source de vérité runtime reste alignée sur `app.application.llm.*` + `app.domain.llm.*` ; les opérations LLM release/eval/replay/golden/qualification sont ancrées sous **`app.ops.llm.*`**.
- Le package **`app.prompts` a été retiré** ; toute évolution prompting nominale passe par `app.domain.llm.prompting.*`.
- **AC54–AC55 / AC63–AC65 / AC64 / AC66** : plus de dossier `backend/app/llm_orchestration/` ; plus de registre `TRANSITION_WRAPPERS.md` ; scans `backend/app` sans import `app.llm_orchestration.*` ni `app.domain.llm.legacy.*` ; arborescence nominale lisible (`application` / `domain` / `infrastructure` / `ops`).
- **AC67** : validation complète tracée sur l’état final avec `ruff format .`, `ruff check .`, `pytest -q` verts (`2964 passed, 12 skipped`).
- **AC68 / AC70** : migration backend LLM clôturée au sens strict ; plus aucun module ou point d’entrée transitoire actif n’est maintenu pour la compatibilité historique runtime.
