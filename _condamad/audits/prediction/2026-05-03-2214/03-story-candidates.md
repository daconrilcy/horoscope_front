<!-- Propositions de stories issues de l'audit CONDAMAD prediction. -->

# Story Candidates

## SC-001

- Candidate ID: SC-001
- Source finding: F-001
- Suggested story title: Converger le namespace racine `app.prediction`
- Suggested archetype: namespace-convergence
- Primary domain: `backend/app/prediction`
- Required contracts: no-legacy-dry-audit-contract, domain-purity-audit-contract, service-boundary-audit-contract
- Draft objective: Classer chaque fichier de `backend/app/prediction` et definir son proprietaire canonique cible avant de deplacer le code.
- Must include: mapping fichier vers `domain`, `services`, `infra`, `api/contracts`, `ops`; liste des imports consommateurs; ordre de migration; non-goals LLM narrator.
- Validation hints: `rg --files backend/app/prediction`; scan imports `app.prediction`; tests prediction existants; consultation RG-016 a RG-019.
- Blockers: Choisir si le moteur pur vit sous `backend/app/domain/prediction` ou sous un sous-package metier dedie autorise explicitement.

## SC-002

- Candidate ID: SC-002
- Source finding: F-002
- Suggested story title: Extraire les dependances infra hors prediction
- Suggested archetype: service-boundary-refactor
- Primary domain: `backend/app/prediction/context_loader.py`, `backend/app/prediction/persistence_service.py`
- Required contracts: service-boundary-audit-contract, data-model-boundary-audit
- Draft objective: Deplacer le chargement DB et la persistence dans des owners `services/prediction` et `infra/db`, en gardant les contrats purs accessibles au moteur.
- Must include: ports ou interfaces minimalistes, migration des imports, tests de persistence inchanges, aucun nouveau dossier racine sous `backend/`.
- Validation hints: scans zero-hit SQLAlchemy dans le futur domaine pur; tests `test_context_loader.py`, `test_prediction_persistence.py`, `test_engine_persistence_e2e.py`.
- Blockers: Determiner le nom canonique du service de chargement contexte et du service de persistence.

## SC-003

- Candidate ID: SC-003
- Source finding: F-003
- Suggested story title: Classer et reduire les compatibilites legacy prediction restantes
- Suggested archetype: legacy-facade-removal
- Primary domain: `backend/app/prediction/schemas.py`, `engine_orchestrator.py`, `persistence_service.py`, `public_projection.py`
- Required contracts: no-legacy-dry-audit-contract
- Draft objective: Produire un registre des surfaces legacy restantes et supprimer celles qui n'ont plus de consommateur actif.
- Must include: classification `keep-temporary`, `delete`, `migrate`, `needs-user-decision`; remplacement canonique; guard anti-reintroduction.
- Validation hints: `rg -n "legacy|backward|compat|retrocompat|engine_output" backend/app/prediction`; tests V3/V4; RG-016 a RG-019.
- Blockers: Fixer une politique de compatibilite pour le payload public `categories`.

## SC-004

- Candidate ID: SC-004
- Source finding: F-004
- Suggested story title: Separer projection publique et enrichissement LLM
- Suggested archetype: ownership-routing-refactor
- Primary domain: `backend/app/prediction/public_projection.py`, `backend/app/services/llm_generation/horoscope_daily`
- Required contracts: api-adapter-audit-contract, service-boundary-audit-contract
- Draft objective: Faire de la projection publique un assemblage deterministe et deplacer l'appel LLM dans un use-case/service explicite.
- Must include: conservation OpenAPI/payload, injection request_id/trace_id, aucun retour vers `LLMNarrator`.
- Validation hints: integration `test_daily_prediction_api.py`, variant narration tests, scans `AIEngineAdapter` hors projection.
- Blockers: Choisir si le payload public final est construit par `services/api_contracts` ou `services/prediction/public_predictions.py`.

## SC-005

- Candidate ID: SC-005
- Source finding: F-005
- Suggested story title: Corriger la resolution des evenements `astro_foundation`
- Suggested archetype: bugfix-contract-preservation
- Primary domain: `backend/app/prediction/public_projection.py`
- Required contracts: contract-shape-audit, test-guard-coverage-audit
- Draft objective: Aligner `PublicAstroFoundationPolicy` sur les sources d'evenements canoniques et les types d'aspects exacts.
- Must include: fallback `detected_events`, support `aspect_exact_to_angle|luminary|personal`, tests unitaires, aucun changement de schema public hors remplissage attendu.
- Validation hints: `pytest -q tests/unit/prediction/test_public_astro_foundation.py`; tests API V4 concernes.
- Blockers: Aucun identifie.

## SC-006

- Candidate ID: SC-006
- Source finding: F-006
- Suggested story title: Supprimer le partage de session DB dans le calcul threade prediction
- Suggested archetype: robustness-hardening
- Primary domain: `backend/app/services/prediction/compute_runner.py`, `backend/app/prediction/context_loader.py`
- Required contracts: service-boundary-audit-contract, data-integrity-risk
- Draft objective: Garantir que le timeout de calcul ne laisse pas une session SQLAlchemy partagee avec un thread en arriere-plan.
- Must include: session worker dediee ou contexte precharge; test de timeout; documentation du comportement.
- Validation hints: tests `test_daily_prediction_service.py`, nouveau test runner timeout, scan commentaire non-thread-safe supprime ou remplace par preuve.
- Blockers: Choisir entre abandon du thread timeout ou session factory dediee.

## SC-007

- Candidate ID: SC-007
- Source finding: F-007
- Suggested story title: Ajouter une garde anti-croissance pour `app.prediction`
- Suggested archetype: architecture-guard-hardening
- Primary domain: `backend/app/tests/unit`
- Required contracts: no-legacy-dry-audit-contract, dependency-direction-audit
- Draft objective: Bloquer les nouveaux fichiers/imports interdits dans `backend/app/prediction` pendant la convergence.
- Must include: allowlist exacte des fichiers actuels, interdiction nouveaux imports infra/API/LLM dans le futur domaine pur, exceptions documentees.
- Validation hints: nouveau test AST; `rg --files backend/app/prediction`; scans imports.
- Blockers: Accepter une allowlist temporaire avant migration.

## SC-008

- Candidate ID: SC-008
- Source finding: F-008
- Suggested story title: Propager les IDs de correlation vers la narration horoscope
- Suggested archetype: observability-guard-hardening
- Primary domain: `backend/app/api/v1/routers/public/predictions.py`, `backend/app/services/prediction`, `backend/app/services/llm_generation/horoscope_daily`
- Required contracts: observability-audit, service-boundary-audit-contract
- Draft objective: Remplacer les UUID locaux de projection par les IDs de trace/requete du chemin API/service.
- Must include: source canonique request_id/trace_id, tests de propagation, logs/metrics conserves.
- Validation hints: tests variant narration et API prediction; scan `uuid.uuid4()` dans `public_projection.py`.
- Blockers: Identifier le standard actuel de request id backend.
