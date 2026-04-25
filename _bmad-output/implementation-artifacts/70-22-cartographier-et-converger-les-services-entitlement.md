# Story 70-22: Cartographier et converger les services entitlement

Status: review

## Story

As a Platform Architect,  
I want cartographier puis converger les services entitlement sous `backend/app/services`,  
so that la frontiere canonique entre runtime gates, resolution effective, quotas, B2B et `canonical_entitlement/` soit explicite, DRY et sans legacy.

## Objectif

- produire une cartographie canonique des responsabilites entitlement ;
- creer un namespace dedie `backend/app/services/entitlement/` pour les runtime gates B2C, la resolution effective partagee, les types communs et le registre de scope ;
- deplacer les huit fichiers entitlement actuellement a plat vers ce namespace dedie ;
- realigner les imports production/tests et les patch targets ;
- verifier qu aucun chemin legacy ou doublon structurel ne subsiste entre la racine `services/`, `entitlement/` et `canonical_entitlement/` ;
- ajouter des garde-fous structurels nominativement fondes sur cette cartographie.

## Acceptance Criteria

1. Une cartographie explicite couvre au minimum les familles suivantes :
   - runtime gates ;
   - effective entitlement resolution ;
   - quota usage ;
   - quota window resolution ;
   - types partages ;
   - B2B plan, usage et repair ;
   - mutation, audit, alerting, suppression et coherence dans `canonical_entitlement/`.
2. Un namespace dedie `backend/app/services/entitlement/` est cree pour les runtime gates B2C, la resolution effective partagee, les types communs et le registre de scope. Il porte au minimum :
   - `chat_entitlement_gate.py` ;
   - `thematic_consultation_entitlement_gate.py` ;
   - `natal_chart_long_entitlement_gate.py` ;
   - `horoscope_daily_entitlement_gate.py` ;
   - `effective_entitlement_resolver_service.py` ;
   - `effective_entitlement_gate_helpers.py` ;
   - `entitlement_types.py` ;
   - `feature_scope_registry.py`.
3. Les huit fichiers ci-dessus n existent plus a la racine de `backend/app/services/` apres implementation.
4. Chaque fichier entitlement existant sous `backend/app/services/` est classe avec une decision explicite :
   - conserver ;
   - deplacer ;
   - fusionner ;
   - supprimer ;
   - documenter comme follow-up.
5. Tous les imports de production et de tests, ainsi que les patch targets string-based, sont migres vers les nouveaux chemins `app.services.entitlement.*` pour les huit modules deplaces.
6. Aucun alias, wrapper, re-export ou chemin legacy entitlement n est maintenu par inertie.
7. Les garde-fous structurels entitlement sont nominatifs et s appuient sur une allowlist ou un registre canonique, sans pretendre detecter automatiquement des duplications semantiques implicites. Ils echouent si l un des huit fichiers entitlement migres reapparait a la racine de `backend/app/services/`.

## Tasks / Subtasks

- [x] **Task 1: Cartographier le perimetre entitlement reel**  
  AC: 1, 4  
  - [x] Lister les fichiers entitlement et quota presents a la racine de `backend/app/services/`.
  - [x] Lister le sous-arbre `backend/app/services/canonical_entitlement/`.
  - [x] Classer chaque fichier par famille de responsabilite canonique.
  - [x] Prendre une decision explicite par fichier : conserver, deplacer, fusionner, supprimer ou follow-up.

- [x] **Task 2: Creer le namespace entitlement dedie et y deplacer les modules runtime**  
  AC: 2, 3, 4  
  - [x] Creer `backend/app/services/entitlement/`.
  - [x] Deplacer les quatre runtime gates B2C dans ce namespace.
  - [x] Deplacer `effective_entitlement_resolver_service.py`, `effective_entitlement_gate_helpers.py`, `entitlement_types.py` et `feature_scope_registry.py` dans ce namespace.
  - [x] Laisser a la racine uniquement les modules entitlement hors de ce perimetre canonique.

- [x] **Task 3: Realigner tous les imports et patch targets**  
  AC: 5, 6  
  - [x] Migrer les imports de production vers `app.services.entitlement.*`.
  - [x] Migrer les imports de tests vers `app.services.entitlement.*`.
  - [x] Migrer les patch targets string-based des tests vers les nouveaux chemins.
  - [x] Verifier qu aucun alias ou re-export legacy n est ajoute pour amortir le deplacement.

- [x] **Task 4: Ajouter des garde-fous structurels nominatifs**  
  AC: 6, 7  
  - [x] Ajouter une allowlist des modules entitlement autorises a la racine de `backend/app/services/`.
  - [x] Ajouter une allowlist fermee du sous-arbre `backend/app/services/entitlement/`.
  - [x] Ajouter une allowlist fermee du sous-arbre `canonical_entitlement/`.
  - [x] Ajouter un test qui echoue si un des huit fichiers entitlement migres reapparait a la racine.
  - [x] Ajouter un test qui echoue si un ancien chemin legacy entitlement est reintroduit.

- [x] **Task 5: Valider dans le venv**  
  AC: 5, 6, 7  
  - [x] Activer le venv avant toute commande Python.
  - [x] Executer `ruff format` sur le namespace entitlement, les imports touches et le garde-fou ajoute.
  - [x] Executer `ruff check` sur le namespace entitlement, les imports touches et le garde-fou ajoute.
  - [x] Executer `pytest -q` sur le garde-fou 70-22 et sur un sous-ensemble cible des tests entitlement directement impactes.

## Dev Notes

### Cartographie canonique retenue

- Runtime gates B2C, resolution effective partagee, types et registre dans `entitlement/`:
  - `chat_entitlement_gate.py`
  - `thematic_consultation_entitlement_gate.py`
  - `natal_chart_long_entitlement_gate.py`
  - `horoscope_daily_entitlement_gate.py`
  - `effective_entitlement_resolver_service.py`
  - `effective_entitlement_gate_helpers.py`
  - `entitlement_types.py`
  - `feature_scope_registry.py`
- Runtime gates B2B conserves a la racine:
  - `b2b_api_entitlement_gate.py`
- Quotas runtime:
  - `quota_usage_service.py`
  - `enterprise_quota_usage_service.py`
  - `quota_window_resolver.py`
- B2B plan, usage et repair:
  - `b2b_canonical_plan_resolver.py`
  - `b2b_canonical_usage_service.py`
  - `b2b_entitlement_repair_service.py`
- `canonical_entitlement/`:
  - `alert/*`
  - `audit/*`
  - `shared/*`
  - `suppression/*`

### Decisions par fichier

- Deplacer vers `backend/app/services/entitlement/`:
  - `chat_entitlement_gate.py` ;
  - `thematic_consultation_entitlement_gate.py` ;
  - `natal_chart_long_entitlement_gate.py` ;
  - `horoscope_daily_entitlement_gate.py` ;
  - `effective_entitlement_resolver_service.py` ;
  - `effective_entitlement_gate_helpers.py` ;
  - `entitlement_types.py` ;
  - `feature_scope_registry.py`.
- Conserver a la racine:
  - `b2b_api_entitlement_gate.py` ;
  - `quota_usage_service.py` ;
  - `enterprise_quota_usage_service.py` ;
  - `quota_window_resolver.py` ;
  - `b2b_canonical_plan_resolver.py` ;
  - `b2b_canonical_usage_service.py` ;
  - `b2b_entitlement_repair_service.py`.
- Conserver dans `canonical_entitlement/`:
  - tous les services de mutation, audit, alerting, suppression et coherence.
- Supprimer ou maintenir absents comme legacy interdit:
  - `entitlement_service.py`
  - `quota_service.py`
  - tous les anciens fichiers plats `canonical_entitlement_*`.
- Follow-up:
  - aucun deplacement physique supplementaire n est impose dans 70-22 au-dela des huit modules entitlement migres.

## Dev Agent Record

### Completion Notes

- Cartographie implementee:
  - creation de `backend/app/services/entitlement/` comme namespace dedie aux runtime gates B2C, a la resolution effective partagee, aux types communs et au registre de scope ;
  - deplacement des huit fichiers suivants vers ce namespace :
    - `chat_entitlement_gate.py` ;
    - `thematic_consultation_entitlement_gate.py` ;
    - `natal_chart_long_entitlement_gate.py` ;
    - `horoscope_daily_entitlement_gate.py` ;
    - `effective_entitlement_resolver_service.py` ;
    - `effective_entitlement_gate_helpers.py` ;
    - `entitlement_types.py` ;
    - `feature_scope_registry.py` ;
  - conservation a la racine des services quota et B2B ;
  - confirmation du sous-arbre `backend/app/services/canonical_entitlement/` comme sous-domaine ferme pour mutation, audit, alerting, suppression et coherence.
- Realignement complet:
  - les imports production ont ete migres vers `app.services.entitlement.*` ;
  - les imports et patch targets de tests ont ete migres vers `app.services.entitlement.*` ;
  - aucun alias ou re-export legacy n a ete ajoute pour amortir le deplacement.
- Legacy interdit confirme:
  - aucun fichier `entitlement_service.py`, `quota_service.py` ou `canonical_entitlement_*` plat n existe sous `backend/app/services/` ;
  - les huit fichiers deplaces n existent plus a la racine de `backend/app/services/` ;
  - `backend/app/services/__init__.py` ne reexporte aucun chemin legacy entitlement.
- Garde-fous ajoutes:
  - nouveau test `backend/app/tests/unit/test_story_70_22_entitlement_structure_guard.py` avec :
    - allowlist racine ;
    - allowlist fermee `entitlement/` ;
    - allowlist fermee `canonical_entitlement/` ;
    - interdiction des anciens fichiers legacy ;
    - interdiction des anciens imports legacy ;
    - interdiction nominative du retour des huit modules a la racine.

### Validation Evidence

- Commandes executees dans le venv:
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend ; ruff format app/services/entitlement app/api/v1/routers/chat.py app/api/v1/routers/consultations.py app/api/v1/routers/entitlements.py app/api/v1/routers/internal/llm/qa.py app/api/v1/routers/natal_interpretation.py app/api/v1/routers/predictions.py app/services/b2b_api_entitlement_gate.py app/services/feature_registry_consistency_validator.py app/services/llm_generation/chat/chat_guidance_service.py app/services/llm_generation/guidance/guidance_service.py app/services/llm_generation/natal/interpretation_service.py app/tests/unit/test_story_70_22_entitlement_structure_guard.py`
  - `cd backend ; ruff check app/services/entitlement app/api/v1/routers/chat.py app/api/v1/routers/consultations.py app/api/v1/routers/entitlements.py app/api/v1/routers/internal/llm/qa.py app/api/v1/routers/natal_interpretation.py app/api/v1/routers/predictions.py app/services/b2b_api_entitlement_gate.py app/services/feature_registry_consistency_validator.py app/services/llm_generation/chat/chat_guidance_service.py app/services/llm_generation/guidance/guidance_service.py app/services/llm_generation/natal/interpretation_service.py app/tests/unit/test_story_70_22_entitlement_structure_guard.py`
  - `cd backend ; pytest -q app/tests/unit/test_story_70_22_entitlement_structure_guard.py app/tests/unit/test_chat_entitlement_gate.py app/tests/unit/test_thematic_consultation_entitlement_gate.py app/tests/unit/test_natal_chart_long_entitlement_gate.py app/tests/unit/test_horoscope_daily_entitlement_gate.py app/tests/unit/test_effective_entitlement_resolver_service.py`
  - `cd backend ; ruff format app/services/entitlement app/services/b2b_api_entitlement_gate.py app/services/b2b_canonical_usage_service.py app/services/b2b_audit_service.py app/services/enterprise_quota_usage_service.py app/services/feature_registry_consistency_validator.py app/services/quota_usage_service.py app/services/llm_generation/chat/chat_guidance_service.py app/services/llm_generation/guidance/guidance_service.py app/api/v1/routers/admin_users.py app/api/v1/routers/chat.py app/api/v1/routers/entitlements.py app/tests/unit/test_story_70_22_entitlement_structure_guard.py app/tests/unit/test_feature_scope_registry.py app/tests/unit/test_feature_registry_consistency_validator.py app/tests/unit/test_quota_usage_service.py app/tests/unit/test_enterprise_quota_usage_service.py app/tests/unit/test_effective_entitlement_resolver_service.py`
  - `cd backend ; ruff check app/services/entitlement app/services/b2b_api_entitlement_gate.py app/services/b2b_canonical_usage_service.py app/services/b2b_audit_service.py app/services/enterprise_quota_usage_service.py app/services/feature_registry_consistency_validator.py app/services/quota_usage_service.py app/services/llm_generation/chat/chat_guidance_service.py app/services/llm_generation/guidance/guidance_service.py app/api/v1/routers/admin_users.py app/api/v1/routers/chat.py app/api/v1/routers/entitlements.py app/tests/unit/test_story_70_22_entitlement_structure_guard.py app/tests/unit/test_feature_scope_registry.py app/tests/unit/test_feature_registry_consistency_validator.py app/tests/unit/test_quota_usage_service.py app/tests/unit/test_enterprise_quota_usage_service.py app/tests/unit/test_effective_entitlement_resolver_service.py`
  - `cd backend ; pytest -q app/tests/unit/test_story_70_22_entitlement_structure_guard.py app/tests/unit/test_feature_scope_registry.py app/tests/unit/test_feature_registry_consistency_validator.py app/tests/unit/test_quota_usage_service.py app/tests/unit/test_enterprise_quota_usage_service.py app/tests/unit/test_effective_entitlement_resolver_service.py app/tests/unit/test_chat_entitlement_gate.py app/tests/unit/test_thematic_consultation_entitlement_gate.py app/tests/unit/test_natal_chart_long_entitlement_gate.py app/tests/unit/test_horoscope_daily_entitlement_gate.py`
  - `cd backend ; python -c "from app.main import app; print(app.title)"`
- Resultats:
  - `ruff format` OK
  - `ruff check` OK
  - `pytest -q` entitlement phase 1 OK, `45 passed`
  - `pytest -q` entitlement phase 2 OK, `88 passed`
  - smoke import backend OK, sortie `horoscope-backend`

### File List

- backend/app/services/entitlement/__init__.py
- backend/app/services/entitlement/chat_entitlement_gate.py
- backend/app/services/entitlement/thematic_consultation_entitlement_gate.py
- backend/app/services/entitlement/natal_chart_long_entitlement_gate.py
- backend/app/services/entitlement/horoscope_daily_entitlement_gate.py
- backend/app/services/entitlement/effective_entitlement_resolver_service.py
- backend/app/services/entitlement/effective_entitlement_gate_helpers.py
- backend/app/services/entitlement/entitlement_types.py
- backend/app/services/entitlement/feature_scope_registry.py
- backend/app/services/b2b_api_entitlement_gate.py
- backend/app/services/b2b_audit_service.py
- backend/app/services/b2b_canonical_usage_service.py
- backend/app/services/billing_service.py
- backend/app/services/canonical_entitlement/audit/mutation_service.py
- backend/app/services/canonical_entitlement/shared/db_consistency_validator.py
- backend/app/services/enterprise_quota_usage_service.py
- backend/app/services/feature_registry_consistency_validator.py
- backend/app/services/quota_usage_service.py
- backend/app/main.py
- backend/app/api/v1/routers/admin_users.py
- backend/app/api/v1/routers/chat.py
- backend/app/api/v1/routers/consultations.py
- backend/app/api/v1/routers/entitlements.py
- backend/app/api/v1/routers/internal/llm/qa.py
- backend/app/api/v1/routers/natal_interpretation.py
- backend/app/api/v1/routers/predictions.py
- backend/app/services/llm_generation/chat/chat_guidance_service.py
- backend/app/services/llm_generation/guidance/guidance_service.py
- backend/app/services/llm_generation/natal/interpretation_service.py
- backend/app/tests/unit/test_story_70_22_entitlement_structure_guard.py
- backend/app/tests/unit/test_chat_entitlement_gate.py
- backend/app/tests/unit/test_thematic_consultation_entitlement_gate.py
- backend/app/tests/unit/test_natal_chart_long_entitlement_gate.py
- backend/app/tests/unit/test_horoscope_daily_entitlement_gate.py
- backend/app/tests/unit/test_effective_entitlement_resolver_service.py
- backend/app/tests/unit/test_feature_scope_registry.py
- backend/app/tests/unit/test_feature_registry_consistency_validator.py
- backend/app/tests/unit/test_quota_usage_service.py
- backend/app/tests/unit/test_enterprise_quota_usage_service.py
- _bmad-output/implementation-artifacts/70-22-cartographier-et-converger-les-services-entitlement.md

## References

- [Source: _bmad-output/implementation-artifacts/70-21-analyser-factoriser-et-deplacer-les-services-llm-residuels-sous-services.md]
- [Source: _bmad-output/implementation-artifacts/70-19-entitlement-mutation-refactor.md]
