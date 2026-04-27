# Story Candidates

## SC-001 LLM Observability Router Convergence

- Source finding: F-001
- Suggested story title: Converger les endpoints admin LLM observability vers leur routeur canonique
- Suggested archetype: legacy-facade-removal
- Primary domain: backend/app/api
- Required contracts: api-adapter-audit-contract.md, no-legacy-dry-audit-contract.md
- Draft objective: Faire de `admin.llm.observability` l'unique propriétaire runtime des endpoints d'observabilité LLM.
- Must include: Montage via registre, suppression des handlers dupliqués dans `prompts.py`, test OpenAPI des paths conservés, test d'absence de duplication.
- Validation hints: `pytest backend/app/tests/integration/test_admin_llm_config_api.py -q` et test d'architecture ciblé routeur.
- Blockers: Vérifier que les services `app.services.llm_observability.admin_observability` couvrent exactement le contrat actuel de `prompts.py`.

## SC-002 API Persistence Boundary Extraction

- Source finding: F-002
- Suggested story title: Extraire l'orchestration SQL des routeurs API les plus denses
- Suggested archetype: api-adapter-boundary-convergence
- Primary domain: backend/app/api
- Required contracts: api-adapter-audit-contract.md
- Draft objective: Réduire la responsabilité des routeurs à l'adaptation HTTP pour un premier lot de routes à forte densité DB.
- Must include: Sélection d'un lot borné, services applicatifs avec tests unitaires, maintien des contrats OpenAPI, aucun changement de payload non documenté.
- Validation hints: Tests d'intégration des routes concernées, `ruff check .`, `pytest -q` dans le venv backend.
- Blockers: Décision de lot initial recommandée entre `admin/llm/prompts.py`, `admin/content.py` et `ops/entitlement_mutation_audits.py`.

## SC-003 Route Registration Exception Registry

- Source finding: F-003
- Suggested story title: Formaliser les exceptions de montage API hors registre v1
- Suggested archetype: route-architecture-convergence
- Primary domain: backend/app/api
- Required contracts: api-adapter-audit-contract.md
- Draft objective: Rendre explicites et testables les routes hors registre canonique sans dépendre d'exceptions ad hoc dans `main.py`.
- Must include: Inventaire des routes hors registre, justification de condition ou préfixe, test runtime OpenAPI et test d'architecture.
- Validation hints: Comparaison AST routeurs déclarés contre registre plus exceptions déclarées.
- Blockers: Décision utilisateur sur le statut cible de `/api/email/unsubscribe` et des routes internes QA.

## SC-004 API Router SQL Guard

- Source finding: F-004
- Suggested story title: Ajouter une garde d'architecture contre SQLAlchemy dans les routeurs API
- Suggested archetype: architecture-guard-hardening
- Primary domain: backend/app/api
- Required contracts: api-adapter-audit-contract.md, no-legacy-dry-audit-contract.md
- Draft objective: Empêcher la réintroduction non contrôlée de logique SQL dans les routeurs API.
- Must include: Garde AST, allowlist temporaire documentée, message d'échec actionnable, trajectoire de réduction de l'allowlist.
- Validation hints: Test unitaire d'architecture qui échoue sur `db.commit`, `db.execute`, imports `app.infra.db.models` et imports SQLAlchemy hors exceptions.
- Blockers: Dépend de la stratégie d'extraction retenue pour éviter un test bloquant trop large dès le premier commit.
