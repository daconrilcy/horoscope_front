# Story classify-converge-remaining-prompt-fallbacks: Classifier and converge remaining prompt fallback exceptions

Status: ready-for-dev

## 1. Objective

Classifier chaque cle restante de `PROMPT_FALLBACK_CONFIGS`.
Les prompts fallback canoniques doivent etre supprimes ou migres, sauf fixture
synthetique ou bootstrap non-prod strictement documente.
Le gateway doit continuer a refuser `missing_assembly` en production.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prompt-generation/2026-05-02-1452/03-story-candidates.md`
- Reason for change: F-001 constate que `PROMPT_FALLBACK_CONFIGS` reste un second
  proprietaire executable pour plusieurs use cases canoniques ou proches du nominal.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/domain/llm/prompting`
- In scope:
  - Inventorier les 8 cles citees par SC-001, dont `guidance_daily`,
    `event_guidance`, `test_natal` et `test_guidance`.
  - Classifier chaque cle avec une decision unique: `fixture`, `bootstrap-non-prod`, `migrate-to-assembly`, `delete` ou `needs-user-decision`.
  - Migrer ou supprimer les prompts fallback canoniques quand la decision n'est pas `fixture` ou `bootstrap-non-prod`.
  - Durcir les tests pour bloquer toute nouvelle cle canonique fallback sans decision auditee.
- Out of scope:
  - Changer les contrats HTTP admin LLM.
  - Refaire le renderer, le provider wrapper ou la taxonomie complete des use cases.
  - Modifier les prompts publies au-dela des assemblies/prompts necessaires a la convergence des cles inventoriees.
- Explicit non-goals:
  - Ne pas affaiblir `RG-018`: les familles supportees ne redeviennent pas proprietaires de prompt via fallback.
  - Ne pas affaiblir `RG-019`: les consignes durables `horoscope_daily/narration` restent dans l'assembly gouvernee.
  - Ne pas affaiblir `RG-020`: aucune famille `consultation` ou prompt durable issu de `prompt_content` ne doit apparaitre.
  - Ne pas creer de deuxieme registre runtime pour contourner `PROMPT_FALLBACK_CONFIGS`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: dead-code-removal
- Archetype reason: la story peut supprimer des prompts fallback classes `dead` ou remplaces par assembly, et doit interdire wrapper, alias ou fallback de remplacement.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les use cases canoniques ne doivent plus obtenir de prompt durable depuis `PROMPT_FALLBACK_CONFIGS` sauf decision `bootstrap-non-prod` exacte.
  - Les fixtures `test_natal` et `test_guidance` peuvent rester si elles sont separees du runtime nominal.
  - En production, l'absence d'assembly doit continuer a produire l'erreur `missing_assembly` attendue plutot qu'un fallback silencieux.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une cle canonique inventoriee ne peut pas etre classee `migrate-to-assembly`, `delete`, `fixture` ou `bootstrap-non-prod` avec preuve executable.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le comportement effectif vient du loaded config du catalogue et du gateway, pas d'un scan seul. |
| Baseline Snapshot | yes | La story doit capturer l'inventaire fallback avant/apres et documenter les differences autorisees. |
| Ownership Routing | no | Aucun deplacement de couche n'est requis hors domaine prompting. |
| Allowlist Exception | yes | Les exceptions restantes doivent etre exactes, justifiees et testables. |
| Contract Shape | no | Aucun DTO, schema HTTP, OpenAPI ou type frontend n'est modifie. |
| Batch Migration | no | Une seule surface de catalogue est ciblee; l'inventaire cle par cle suffit. |
| Reintroduction Guard | yes | Les prompts fallback canoniques ne doivent pas revenir sans decision. |
| Persistent Evidence | yes | L'audit de classification doit etre conserve dans le dossier de story. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated
contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - loaded config: `PROMPT_FALLBACK_CONFIGS` charge depuis `backend/app/domain/llm/prompting/catalog.py`.
  - `build_fallback_use_case_config` pour prouver qu'une cle ne cree plus de `UseCaseConfig` fallback quand elle est migree ou supprimee.
  - Tests gateway qui prouvent que `missing_assembly` reste le comportement production.
- Secondary evidence:
  - `rg -n "PROMPT_FALLBACK_CONFIGS|build_fallback_use_case_config" app tests`
  - Audit persistant `_condamad/stories/classify-converge-remaining-prompt-fallbacks/fallback-classification.md`.
- Static scans alone are not sufficient for this story because:
  - la presence d'une cle dans un fichier ne prouve pas si le gateway l'utilise comme fallback runtime.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/classify-converge-remaining-prompt-fallbacks/fallback-classification.md` must include a `Before inventory` table captured before code edits.
- After artifact after implementation:
  - `_condamad/stories/classify-converge-remaining-prompt-fallbacks/fallback-classification.md` must include an `After inventory` table captured after code edits.
- Comparison command or test:
  - `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py`
- Comparison after implementation:
  - compare `Before inventory` and `After inventory` in `fallback-classification.md`; only decisions `fixture` and `bootstrap-non-prod` may remain executable.
- Expected invariant:
  - every remaining fallback key is classified and allowed by exact decision.
- Allowed differences:
  - removal of entries classified `delete` or `migrate-to-assembly`; fixture and bootstrap exceptions only when exact.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: no responsibility moves or boundary rules are affected.

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `catalog.py` | `test_natal` | Fixture synthetique hors nominal | permanent if no production routing |
| `catalog.py` | `test_guidance` | Fixture synthetique hors nominal | permanent if no production routing |
| `catalog.py` | any `bootstrap-non-prod` key | Bootstrap base vide hors prod | expires when assembly seed exists |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Fallback classification audit | `fallback-classification.md` | Conserver decision, preuve et risque. |
| Final validation evidence | `generated/10-final-evidence.md` | Conserver commandes et resultats. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route,
field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the
removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- forbidden symbols or states

Required forbidden examples:

- `PROMPT_FALLBACK_CONFIGS["natal_interpretation_short"]` unless classified `bootstrap-non-prod`
- `PROMPT_FALLBACK_CONFIGS["guidance_daily"]` unless classified `bootstrap-non-prod`
- `PROMPT_FALLBACK_CONFIGS["guidance_weekly"]` unless classified `bootstrap-non-prod`
- `PROMPT_FALLBACK_CONFIGS["event_guidance"]` unless classified `bootstrap-non-prod`
- any new canonical fallback key without a row in `fallback-classification.md`

Guard evidence:

- Evidence profile: `reintroduction_guard`;
  `pytest -q tests/llm_orchestration/test_prompt_governance_registry.py`
  and `pytest -q tests/llm_orchestration/test_llm_legacy_extinction.py`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prompt-generation/2026-05-02-1452/02-finding-register.md` -
  F-001 lists remaining executable fallback exceptions.
- Evidence 2: `backend/app/domain/llm/prompting/catalog.py` -
  `PROMPT_FALLBACK_CONFIGS` contains the 8 keys listed by SC-001.
- Evidence 3: `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - current guard allows exactly those fallback keys.
- Evidence 4: `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - current guard blocks only the previously supported forbidden keys.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consulted before cadrage.

## 6. Target State

- Chaque cle fallback restante possede une decision auditable et une preuve.
- Les cles canoniques migrees ou supprimees ne construisent plus de fallback `UseCaseConfig`.
- Les seules exceptions executees sont des fixtures synthetiques ou un bootstrap non-prod explicitement borne.
- Le gateway conserve la preuve de rejet `missing_assembly` en production.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-018` - la story touche directement la surface `PROMPT_FALLBACK_CONFIGS` des familles supportees.
  - `RG-019` - la convergence ne doit pas ramener des consignes daily dans un builder ou fallback concurrent.
  - `RG-020` - les decisions guidance ne doivent pas creer une famille `consultation`.
- Non-applicable invariants:
  - `RG-010` - la story ne deplace pas les racines de tests backend.
  - `RG-016` - la story ne retablit pas `LLMNarrator`.
  - `RG-017` - la story ne touche pas le provider OpenAI direct.
- Required regression evidence:
  - Tests de gouvernance fallback.
  - Test production `missing_assembly`.
  - Scan cible des symboles fallback.
- Allowed differences:
  - Suppression ou migration des prompts fallback canoniques inventories.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `fallback-classification.md` liste les 8 cles imposees. | Evidence profile: `persistent_evidence`; pytest governance registry. |
| AC2 | Les cles migrees ou supprimees ne construisent plus de fallback config. | Evidence profile: `reintroduction_guard`; loaded config test in `test_llm_legacy_extinction.py`. |
| AC3 | Les cles `fixture` ou `bootstrap-non-prod` sont exactes. | Evidence profile: `allowlist_register_validated`; pytest governance registry. |
| AC4 | Aucune nouvelle cle canonique fallback n'est admise sans decision. | Evidence profile: `ast_architecture_guard`; pytest governance registry. |
| AC5 | Le gateway production conserve l'erreur `missing_assembly`. | Evidence profile: `runtime_contract`; pytest assembly resolution. |

## 8. Implementation Tasks

- [ ] Task 1 - Produire l'audit de classification cle par cle (AC: AC1)
  - [ ] Subtask 1.1 - Inspecter `catalog.py`, `gateway.py`, `canonical_use_case_registry.py` et les seeds bootstrap.
  - [ ] Subtask 1.2 - Ecrire `fallback-classification.md` avec les decisions autorisees.

- [ ] Task 2 - Converger les cles canoniques hors fallback (AC: AC2, AC5)
  - [ ] Subtask 2.1 - Migrer vers assembly/prompt gouverne ou supprimer les entrees classees.
  - [ ] Subtask 2.2 - Verifier que `build_fallback_use_case_config` ne produit plus de config pour ces cles.

- [ ] Task 3 - Borne les exceptions conservees (AC: AC3, AC4)
  - [ ] Subtask 3.1 - Encoder la liste exacte autorisee dans un test ou registre chargeable.
  - [ ] Subtask 3.2 - Faire echouer les ajouts de cle canonique sans decision.

- [ ] Task 4 - Executer et consigner la validation (AC: AC1, AC2, AC3, AC4, AC5)
  - [ ] Subtask 4.1 - Executer les tests cibles dans le venv.
  - [ ] Subtask 4.2 - Ecrire `generated/10-final-evidence.md`.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/domain/llm/prompting/catalog.py` comme surface unique du fallback existant.
  - `backend/app/domain/llm/runtime/gateway.py` pour le rejet `missing_assembly`.
  - `backend/app/domain/llm/configuration/canonical_use_case_registry.py` pour identifier les use cases canoniques.
  - `backend/app/ops/llm/bootstrap` pour prouver les prompts gouvernes deja seedes.
- Do not recreate:
  - Un second catalogue fallback.
  - Un fallback prompt par use case canonique.
  - Une exception implicite basee sur prefixe ou famille.
- Shared abstraction allowed only if:
  - Elle remplace une duplication reelle de decisions fallback et reste dans `backend/app/domain/llm/prompting`.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `PROMPT_FALLBACK_CONFIGS` entry for a canonical use case without `fallback-classification.md` decision.
- `build_fallback_use_case_config` returning a config for a `delete` or `migrate-to-assembly` key.
- Any new `developer_prompt` durable for `guidance`, `natal`, `chat`, `horoscope_daily` or `consultation` outside governed prompts/assemblies.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, generated links, OpenAPI clients, explicit audit evidence, or other known external surfaces.
- `historical-facade`: item delegates to a canonical assembly/prompt only to preserve older fallback behavior.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted; must become `needs-user-decision` if it remains a duplicate prompt owner. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions:

- `keep`
- `delete`
- `replace-consumer`
- `needs-user-decision`

Audit output path when applicable:

- `_condamad/stories/classify-converge-remaining-prompt-fallbacks/fallback-classification.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Durable prompt instructions | Governed prompts/assemblies | `PROMPT_FALLBACK_CONFIGS` developer prompts |
| Synthetic orchestration fixtures | Test-only fallback exceptions documented in `fallback-classification.md` | Production use-case routing through fixture keys |
| Production missing assembly behavior | `backend/app/domain/llm/runtime/gateway.py` | Silent fallback prompt generation |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to an equivalent fallback prompt;
- preserving a wrapper;
- adding a compatibility alias;
- keeping a deprecated fallback active;
- preserving the old prompt path through re-export;
- replacing deletion with soft-disable behavior.

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev
agent must stop or record an explicit user decision with external evidence and
deletion risk.

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/domain/llm/prompting/catalog.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/ops/llm/bootstrap/seed_29_prompts.py`
- `backend/app/ops/llm/bootstrap/seed_guidance_prompts.py`
- `backend/tests/llm_orchestration/test_prompt_governance_registry.py`
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/domain/llm/prompting/catalog.py` - retirer ou borner les entrees fallback selon classification.
- `_condamad/stories/classify-converge-remaining-prompt-fallbacks/fallback-classification.md` - audit persistant des decisions.
- `_condamad/stories/classify-converge-remaining-prompt-fallbacks/generated/10-final-evidence.md` - preuve finale.

Likely tests:

- `backend/tests/llm_orchestration/test_prompt_governance_registry.py` - verifier decisions exactes et blocage des nouvelles cles.
- `backend/tests/llm_orchestration/test_llm_legacy_extinction.py` - verifier absence de configs fallback interdites.
- `backend/tests/llm_orchestration/test_assembly_resolution.py` - verifier `missing_assembly` production.

Files not expected to change:

- `frontend/src` - aucune surface frontend n'est dans le scope.
- `backend/app/api/v1/routers` - aucune route API n'est dans le scope.
- `backend/pyproject.toml` - aucune dependance nouvelle n'est autorisee.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\classify-converge-remaining-prompt-fallbacks\00-story.md
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\classify-converge-remaining-prompt-fallbacks\00-story.md
pytest -q tests/llm_orchestration/test_prompt_governance_registry.py tests/llm_orchestration/test_llm_legacy_extinction.py tests/llm_orchestration/test_assembly_resolution.py
rg -n "PROMPT_FALLBACK_CONFIGS|build_fallback_use_case_config" app tests
ruff check .
```

## 22. Regression Risks

- Risk: une cle canonique conserve un prompt durable hors assembly.
  - Guardrail: classification persistante + test comparant `PROMPT_FALLBACK_CONFIGS` aux decisions.
- Risk: la production retombe sur un fallback silencieux quand une assembly manque.
  - Guardrail: test `missing_assembly` dans `test_assembly_resolution.py`.
- Risk: les fixtures de test deviennent consommables par un chemin nominal.
  - Guardrail: audit `fixture` + test de non-routage production.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Run every Python command after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/prompt-generation/2026-05-02-1452/00-audit-report.md` - conclusion de re-audit et dette residuelle.
- `_condamad/audits/prompt-generation/2026-05-02-1452/01-evidence-log.md` - E-004, E-010, E-011, E-012.
- `_condamad/audits/prompt-generation/2026-05-02-1452/02-finding-register.md` - F-001.
- `_condamad/audits/prompt-generation/2026-05-02-1452/03-story-candidates.md` - SC-001.
- `_condamad/stories/regression-guardrails.md` - RG-018, RG-019, RG-020.
