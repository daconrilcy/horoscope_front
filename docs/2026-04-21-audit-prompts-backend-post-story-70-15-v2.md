# Audit backend génération de prompts LLM (post-story 70-15, AC18-AC70)

Date: 2026-04-21  
Dernière passe de review : 2026-04-22 (vérification post-modifs story 70-15 : imports canoniques confirmés sur `runtime/*` et `configuration/*`, dossier source `backend/app/llm_orchestration/` toujours absent, mais reliquats filesystem résiduels constatés sous `backend/app/prompts/` et `backend/app/domain/llm/legacy/`)  
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

**Aucun reliquat actif dans le code nominal scanné** : le dossier source `backend/app/llm_orchestration/` a bien été supprimé ; `legacy_prompt_runtime.py` n’existe plus ; les suites LLM vivent sous `backend/tests/llm_orchestration/` avec imports canoniques uniquement.

Reliquats filesystem encore visibles au 2026-04-22 :

- `backend/app/prompts/`
  - statut : **répertoire résiduel uniquement**
  - contenu observé : `tests/__init__.py` et `__pycache__/`
  - modules historiques `catalog`, `common_context`, `validators`, `exceptions` : **absents en source**
- `backend/app/domain/llm/legacy/`
  - statut : **répertoire résiduel uniquement**
  - contenu observé : `__pycache__/` seulement
  - fichiers source legacy (`bridge.py`, `__init__.py`) : **absents**

Dans `backend/app` et `backend/tests`, les seules occurrences textuelles restantes de `app.llm_orchestration`, `app.prompts` ou `app.domain.llm.legacy.*` relèvent des **garde-fous de tests** (`backend/tests/unit/test_story_70_14_transition_guards.py`) ou de la **documentation ops** (`backend/app/ops/llm/README.md`), pas d’imports nominaux exécutables.

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

Le **package applicatif historique** `backend/app/prompts` a été retiré de la surface nominale : plus de shims source `catalog` / `common_context` / `validators` / `exceptions` au chemin historique. Toute la surface correspondante est portée par **`app.domain.llm.prompting.*`** (catalogue, contexte, validators, exceptions, tests sous `app/domain/llm/prompting/tests/`).

À date du 2026-04-22, le répertoire **existe encore physiquement** mais uniquement comme reliquat filesystem (`tests/__init__.py` et `__pycache__/`) ; aucun module runtime source n’y subsiste.

### Constat actuel

- Aucun import `app.prompts` dans le backend Python applicatif scanné ; garde-fou optionnel dans `tests/unit/test_story_70_14_transition_guards.py` (préfixe interdit).
- Les tests de qualification de contexte vivent sous `app/domain/llm/prompting/tests/`.
- Le reliquat `backend/app/prompts/tests/` ne porte pas de point d’entrée canonique ; il ne remet pas en cause la migration runtime.

### Impact sur la lecture AC53-AC70 (passe en cours)

- Le runtime canonique est bien déplacé vers `app.domain.llm.*` / `app.application.llm.*`.
- `app.prompts` ne constitue plus un package de transition actif ; le reliquat observé est **structurel**, pas fonctionnel.
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

## Vérification ciblée du 2026-04-22

- Les modules `backend/app/domain/llm/runtime/composition.py`, `fallback.py`, `validation.py` n’importent que des modules canoniques `app.domain.llm.runtime.*`.
- Les modules `backend/app/domain/llm/configuration/assemblies.py`, `execution_profiles.py`, `prompt_versions.py` n’importent que des modules canoniques `app.domain.llm.configuration.*`.
- Le test modifié `backend/tests/integration/test_story_66_21_governance.py` consomme `app.domain.llm.runtime.contracts`, `FallbackGovernanceRegistry` et `LLMGateway`, sans retour à `app.llm_orchestration.*`.
- Aucun import nominal exécutable `app.llm_orchestration.*`, `app.prompts.*` ou `app.domain.llm.legacy.*` n’a été trouvé dans `backend/app`, `backend/tests` hors garde-fous et documentation.

### Suivi opérationnel (post-suppression `app/prompts`)

- `backend/app/domain/llm/prompting/context.py` — **Statut**: source de vérité prompting contexte — **Action suivante**: surveillance.
- `backend/app/domain/llm/prompting/tests/` — **Statut**: tests prompts (AC69) — **Action suivante**: maintenir imports canoniques uniquement.

### Ops LLM canonique (AC53, lot 2026-04-21)

- `app/ops/llm/release_service.py`, `eval_harness.py`, `replay_service.py`, `golden_regression_service.py`, `golden_regression_registry.py`, `prompt_lint.py`, `prompt_registry_v2.py`, `performance_qualification_service.py`, `performance_registry.py` portent les implementations reference pour les outils admin/ops.
- `app/ops/llm/services.py` reexporte uniquement depuis `app.ops.llm.*` (plus de chaine directe vers `llm_orchestration.services` pour ces symboles).
- `app/ops/llm/bootstrap/*` contient les seeds `use_cases_seed`, `seed_horoscope_narrator_assembly`, `seed_66_20_taxonomy` avec imports domaine (`schemas`, `narrator_contract`).

## Points de vigilance restants

- Conserver les garde-fous (conformité doc, tests 70.14, invariants sémantiques) pour éviter toute réintroduction de namespace `app.llm_orchestration.*` dans le code nominal `backend/app`.
- Nettoyer à l’occasion les reliquats filesystem `backend/app/prompts/` et `backend/app/domain/llm/legacy/` si l’objectif est une suppression physique stricte et non seulement logique.
- La liste d’échecs historiques dans ce document pour les suites lourdes peut être obsolète après campagne verte unifiée ; vérifier avant prochain audit.

## Conclusion

- La source de vérité runtime reste alignée sur `app.application.llm.*` + `app.domain.llm.*` ; les opérations LLM release/eval/replay/golden/qualification sont ancrées sous **`app.ops.llm.*`**.
- Le package runtime **`app.prompts` a été retiré de la surface nominale** ; toute évolution prompting nominale passe par `app.domain.llm.prompting.*`. Le répertoire résiduel encore présent ne porte pas de modules source runtime actifs.
- **AC54–AC55 / AC63–AC65 / AC64 / AC66** : plus de dossier source `backend/app/llm_orchestration/` ; plus de registre `TRANSITION_WRAPPERS.md` ; scans `backend/app` sans import nominal exécutable `app.llm_orchestration.*` ni `app.domain.llm.legacy.*` ; arborescence nominale lisible (`application` / `domain` / `infrastructure` / `ops`).
- **AC67** : validation complète tracée sur l’état final avec `ruff format .`, `ruff check .`, `pytest -q` verts (`2964 passed, 12 skipped`).
- **AC68 / AC70** : migration backend LLM clôturée au sens strict au niveau des imports et points d’entrée actifs ; il subsiste seulement des reliquats filesystem non nominaux à nettoyer si l’on veut une extinction physique parfaite.

## Annexe — État de l’arborescence liée à la génération de prompt

Convention de lecture :

- `actif` : fichier encore utilisé dans le flux nominal ou dans les outils d’admin/ops qui pilotent la génération de prompt.
- `inactif` : doublon, reliquat, placeholder, doc ou support non exécuté dans le flux nominal.
- Les répertoires `__pycache__/` sont exclus de cet inventaire.

### `backend/app/application/llm`

- `ai_engine_adapter.py` — **actif** — façade applicative consommée par les services métier ; construit les requêtes d’exécution et délègue au `LLMGateway`.

### `backend/app/domain/llm/prompting`

- `catalog.py` — **actif** — catalogue canonique des use cases, modèles, max tokens, schémas de sortie et fallback runtime.
- `context.py` — **actif** — construit le contexte commun et qualifié injecté dans les prompts à partir des données utilisateur/natales.
- `exceptions.py` — **actif** — exceptions de configuration prompting.
- `narrator_contract.py` — **actif** — contrat de sortie dédié au narrateur horoscope.
- `persona_boundary.py` — **actif** — garde-fous de contenu et validation des blocs de persona.
- `persona_composer.py` — **inactif** — doublon source de `personas.py` ; aucun import nominal relevé dans le scan courant.
- `personas.py` — **actif** — compose le bloc de persona canonique utilisé au runtime et en configuration.
- `placeholder_policy.py` — **actif** — définit la politique de placeholders autorisés/attendus dans les templates.
- `prompt_renderer.py` — **actif** — renderer canonique des prompts à partir des templates et variables autorisées.
- `schemas.py` — **actif** — schémas Pydantic des sorties structurées (`AstroResponse*`, `ChatResponse*`).
- `validation.py` — **inactif** — doublon/façade redondante de `validators.py` ; aucun import nominal relevé dans le scan courant.
- `validators.py` — **actif** — valide le contenu des templates, plan rules, naming de use case et cohérence catalogue/DB.
- `tests/conftest.py` — **actif** — support de tests unitaires prompting.
- `tests/test_qualified_context.py` — **actif** — tests de qualification du contexte prompting.

### `backend/app/domain/llm/runtime`

- `composition.py` — **actif** — façade canonique exportant les helpers de composition runtime.
- `context_quality_injector.py` — **actif** — enrichit la composition avec les métadonnées de qualité de contexte.
- `contracts.py` — **actif** — source de vérité des contrats runtime (requêtes, résultats, erreurs, observabilité).
- `crypto_utils.py` — **actif** — chiffrement utilitaire des snapshots d’entrée/logs runtime.
- `execution_profiles_types.py` — **actif** — types runtime liés aux profils d’exécution.
- `fallback_governance.py` — **actif** — gouvernance de fallback, métriques et décision de chemin dégradé.
- `fallback.py` — **actif** — façade canonique exportant la gouvernance de fallback.
- `gateway.py` — **actif** — orchestrateur central du pipeline de génération de prompt et d’appel provider.
- `hard_policy.py` — **actif** — règles runtime “dures” appliquées à l’exécution.
- `input_validation.py` — **actif** — façade canonique de validation d’entrée.
- `input_validator.py` — **actif** — validation JSON Schema des payloads d’entrée.
- `length_budget_injector.py` — **actif** — injecte les budgets de longueur/max tokens dans le plan résolu.
- `observability.py` — **actif** — façade canonique de télémétrie runtime.
- `observability_service.py` — **actif** — persistance et métriques des appels LLM, snapshots et événements de gouvernance.
- `output_validator.py` — **actif** — validation JSON/schéma/evidence des sorties provider.
- `policy.py` — **actif** — politiques runtime complémentaires utilisées par l’orchestration.
- `provider_parameter_mapper.py` — **actif** — normalise les paramètres d’exécution selon le provider/famille de modèle.
- `provider_runtime_manager.py` — **actif** — exécution provider avec résilience, retry, timeout et circuit breaker.
- `providers.py` — **actif** — helpers de support provider côté runtime.
- `repair.py` — **actif** — façade canonique de réparation de sortie invalide.
- `repair_prompter.py` — **actif** — construit le prompt de réparation envoyé au provider après échec de validation.
- `simulation.py` — **actif** — façade canonique pour la simulation d’incidents runtime.
- `simulation_context.py` — **actif** — `ContextVar` de simulation d’erreurs pour tests/qualification.
- `supported_providers.py` — **actif** — registre des providers supportés nominalement.
- `validation.py` — **actif** — façade canonique de validation de sortie.

### `backend/app/domain/llm/configuration`

- `active_release.py` — **actif** — accès à la release LLM active côté configuration.
- `admin_models.py` — **actif** — contrats Pydantic admin/configuration (assemblies, profils, preview, etc.).
- `assemblies.py` — **actif** — façade canonique d’entrée pour l’admin et la résolution d’assemblies.
- `assembly_admin_service.py` — **actif** — service admin CRUD/publish/rollback/preview des assemblies.
- `assembly_registry.py` — **actif** — lecture/résolution des assemblies actives depuis snapshot ou tables.
- `assembly_resolver.py` — **actif** — construit le prompt développeur final à partir des composants configurés.
- `coherence.py` — **actif** — façade de cohérence de configuration.
- `config_coherence_validator.py` — **actif** — valide la cohérence assembly/profile/schema/provider avant publication.
- `execution_profile_registry.py` — **actif** — lecture/résolution/caching des profils d’exécution actifs.
- `execution_profiles.py` — **actif** — façade canonique du registre des profils d’exécution.
- `prompt_version_lookup.py` — **actif** — lecture nominale de la version de prompt active pour un use case.
- `prompt_versions.py` — **actif** — façade canonique du lookup de version de prompt.

### `backend/app/ops/llm`

- `doc_conformity_manifest.py` — **actif** — manifeste des éléments documentaires qui doivent rester alignés avec le runtime prompting.
- `doc_conformity_validator.py` — **actif** — contrôle de conformité doc/code sur taxonomy, providers, fallback et invariants ops.
- `eval_harness.py` — **actif** — exécute les campagnes d’évaluation à partir de fixtures YAML.
- `golden_regression_registry.py` — **actif** — registre des paramètres et classifications des campagnes golden regression.
- `golden_regression_service.py` — **actif** — exécute et compare les campagnes golden.
- `ops_contract.py` — **actif** — contrats partagés des outils ops LLM.
- `performance_qualification.py` — **actif** — façade de qualification performance.
- `performance_qualification_service.py` — **actif** — calcule les rapports de qualification performance.
- `performance_registry.py` — **actif** — registres/SLO/SLA de performance ops.
- `prompt_lint.py` — **actif** — lint des prompts et vérification des placeholders attendus.
- `prompt_registry_v2.py` — **actif** — publication, rollback et résolution des prompts côté admin/ops.
- `README.md` — **inactif** — documentation du sous-système ops LLM.
- `release_service.py` — **actif** — construit, valide, active et historise les releases LLM.
- `replay_service.py` — **actif** — rejoue un appel LLM à partir des snapshots observabilité.
- `semantic_conformity_validator.py` — **actif** — contrôle sémantique automatisé des invariants d’architecture/story.
- `semantic_invariants_registry.py` — **actif** — registre des invariants sémantiques attendus.
- `services.py` — **actif** — façade d’agrégation des services ops utilisés par les routes admin et scripts.

### `backend/app/ops/llm/bootstrap`

- `seed_29_prompts.py` — **actif** — seed historique des prompts et schémas associés.
- `seed_30_14_chat_prompt.py` — **actif** — seed dédié aux prompts chat.
- `seed_30_8_v3_prompts.py` — **actif** — seed des prompts v3 plus denses/structurés.
- `seed_66_20_taxonomy.py` — **actif** — seed de la taxonomy feature/subfeature utilisée par la gouvernance.
- `seed_horoscope_narrator_assembly.py` — **actif** — seed de l’assembly narrateur horoscope et de ses dépendances.
- `use_cases_seed.py` — **actif** — seed du référentiel nominal des use cases.

### `backend/app/ops/llm/release`

- `build_golden_evidence.py` — **actif** — script de génération d’évidence golden pour un candidat de release.
- `build_qualification_evidence.py` — **actif** — script de génération d’évidence de qualification.
- `build_release_candidate.py` — **actif** — script de construction d’un release candidate LLM.
- `build_release_readiness_report.py` — **actif** — script de synthèse de readiness avant activation.
- `build_smoke_evidence.py` — **actif** — script de génération d’évidence smoke.

### Répertoires ou reliquats non nominaux

- `backend/app/ops/llm/legacy/__init__.py` — **inactif** — placeholder de namespace, sans implémentation active observée.
- `backend/app/ops/llm/migrations/__init__.py` — **inactif** — placeholder de namespace, sans implémentation active observée.
- `backend/app/prompts/` — **inactif** — reliquat filesystem ; pas de module source runtime encore actif.
- `backend/app/domain/llm/legacy/` — **inactif** — reliquat filesystem ; plus de source legacy active observée.
