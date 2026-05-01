# Story converge-horoscope-daily-narration-assembly: Move daily narration instructions to assembly

Status: ready-for-dev

## 1. Objective

Faire converger les consignes durables `horoscope_daily/narration` vers l'assembly gouvernee.
`AstrologerPromptBuilder` doit rester un constructeur de payload contextuel quotidien,
pas un proprietaire de style, longueur, format ou interdictions narratives.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/prompt-generation/2026-04-30-1810`
- Reason for change: F-003 identifie des consignes durables dans `AstrologerPromptBuilder`.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `backend/app/services/llm_generation/horoscope_daily`
- In scope:
  - Deplacer les consignes narratives stables vers l'assembly `horoscope_daily/narration`.
  - Limiter `AstrologerPromptBuilder` au contexte metier quotidien.
  - Verifier les couches admin observables avec les vraies consignes envoyees.
  - Conserver la validation metier post-gateway sur `daily_synthesis`.
- Out of scope:
  - Recrire les prompts natal, chat ou guidance.
  - Changer `AIEngineAdapter` au-dela des appels existants.
  - Modifier le contrat JSON public horoscope daily.
- Explicit non-goals:
  - Ne pas compenser par une logique narrative dans `AIEngineAdapter`.
  - Ne pas recreer une assembly parallele.
  - Ne pas changer les invariants `RG-004`, `RG-005`, `RG-006`, `RG-016`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: ownership-routing-refactor
- Archetype reason: la story route les consignes durables vers leur proprietaire canonique.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les consignes de format, longueur, style et interdiction viennent de l'assembly.
  - Le payload conserve les faits astrologiques du jour.
  - Le seuil de validation post-gateway reste dans le service quotidien.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: le texte exact a migrer n'est pas identifiable depuis la seed ou l'assembly existante.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde AST prouve que les instructions durables ne sont plus dans le builder. |
| Baseline Snapshot | yes | Le prompt avant/apres doit prouver que seules les consignes changent de proprietaire. |
| Ownership Routing | yes | Les responsabilites payload versus instructions doivent etre classees. |
| Allowlist Exception | yes | Aucune exception durable hors assembly n'est autorisee. |
| Contract Shape | no | Le schema JSON de sortie n'est pas modifie. |
| Batch Migration | no | Une seule feature est concernee. |
| Reintroduction Guard | yes | Les phrases durables ne doivent pas revenir dans le builder. |
| Persistent Evidence | yes | Le baseline prompt builder avant/apres doit rester consultable. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard over `backend/app/prediction/astrologer_prompt_builder.py`.
  - Loaded config evidence for `horoscope_daily/narration` assembly.
- Secondary evidence:
  - `rg -n "Format attendu|Interdiction|daily_synthesis : strictement" backend/app/prediction/astrologer_prompt_builder.py`
- Static scans alone are not sufficient for this story because:
  - la preuve doit confirmer que l'assembly chargee porte les consignes.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/converge-horoscope-daily-narration-assembly/prompt-builder-before.md`
- Comparison after implementation:
  - `_condamad/stories/converge-horoscope-daily-narration-assembly/prompt-builder-after.md`
- Expected invariant:
  - Le payload contextuel reste present.
- Allowed differences:
  - Les consignes durables quittent le builder pour l'assembly.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Daily context payload | `backend/app/prediction/astrologer_prompt_builder.py` | assembly seed |
| Durable narration instruction | `backend/app/domain/llm/configuration` | context builder |
| Horoscope generation use case | `backend/app/services/llm_generation/horoscope_daily` | `AIEngineAdapter` |

## 4e. Allowlist / Exception Register

Use when a broad rule has allowed exceptions.

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `backend/app/prediction/astrologer_prompt_builder.py` | factual context labels | Payload metier non durable | permanent as context only |
| `backend/app/services/llm_generation/horoscope_daily/narration_service.py` | correction sentence count | Validation post-gateway | permanent |

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
| Prompt builder before | `_condamad/stories/converge-horoscope-daily-narration-assembly/prompt-builder-before.md` | Capturer les consignes avant migration. |
| Prompt builder after | `_condamad/stories/converge-horoscope-daily-narration-assembly/prompt-builder-after.md` | Prouver leur absence du builder. |

## 4i. Reintroduction Guard

The implementation must add or update deterministic guards that fail if:

- `Format attendu` revient dans `backend/app/prediction/astrologer_prompt_builder.py`;
- `Interdiction` revient dans `backend/app/prediction/astrologer_prompt_builder.py`;
- `daily_synthesis : strictement` revient dans `backend/app/prediction/astrologer_prompt_builder.py`;
- une consigne durable est ajoutee dans `AIEngineAdapter`.

Required architecture guard against reintroduction:
- Deterministic source: forbidden symbols.
- Evidence profile: `reintroduction_guard`; `pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py` checks `Format attendu`.
- The guard must fail when durable instructions are reintroduced.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/prompt-generation/2026-04-30-1810/01-evidence-log.md` - E-010 signale les consignes dans le builder.
- Evidence 2: `backend/app/prediction/astrologer_prompt_builder.py` - le builder contient `Format attendu`, `daily_synthesis` et `Interdiction`.
- Evidence 3: `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py` - la seed porte deja une assembly horoscope daily.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- L'assembly `horoscope_daily/narration` porte les consignes de rendu.
- Le builder ne produit que les donnees contextuelles du jour.
- L'admin detail expose les couches contenant les consignes migrees.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-016` - le chemin narratif ne doit pas redevenir consommateur de `LLMNarrator`.
  - `RG-006` - les services ne doivent pas importer `app.api`.
- Non-applicable invariants:
  - `RG-001` - aucune facade route n'est modifiee.
  - `RG-009` - aucun package schema API legacy n'est touche.
- Required regression evidence:
  - Tests builder.
  - Tests seed assembly.
  - Tests admin detail des couches observables.
- Allowed differences:
  - Le texte durable apparait dans l'assembly au lieu du builder.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Builder payload only. | Evidence profile: `targeted_forbidden_symbol_scan`; `pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py`. |
| AC2 | Assembly owns instructions. | Evidence profile: `json_contract_shape`; `pytest -q tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py`. |
| AC3 | Admin layers expose migrated text. | Evidence profile: `ast_architecture_guard`; `pytest -q tests/llm_orchestration/test_prompt_admin_catalog_detail.py`. |
| AC4 | Narration behavior preserved. | Evidence profile: `reintroduction_guard`; `pytest -q tests/llm_orchestration/test_narrator_migration.py`. |

## 8. Implementation Tasks

- [x] Task 1 - Capturer le prompt builder avant migration (AC: AC1)
- [x] Task 2 - Migrer les consignes durables vers la seed assembly (AC: AC2)
- [x] Task 3 - Reduire le builder au payload contextuel (AC: AC1)
- [x] Task 4 - Adapter les tests builder et seed (AC: AC1, AC2)
- [x] Task 5 - Verifier les couches admin observables (AC: AC3)
- [x] Task 6 - Executer la regression narration dans le venv (AC: AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py` pour les consignes versionnees.
  - `backend/app/domain/llm/configuration` pour la configuration canonique.
  - `backend/app/services/llm_generation/horoscope_daily/narration_service.py` pour la validation post-gateway.
- Do not recreate:
  - Un prompt durable dans `AstrologerPromptBuilder`.
  - Une logique narrative dans `AIEngineAdapter`.
  - Une source admin separee du runtime.
- Shared abstraction allowed only if:
  - Elle se limite a assembler le contexte metier quotidien reutilise par le service.

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

- `Format attendu` in `backend/app/prediction/astrologer_prompt_builder.py`
- `Interdiction` in `backend/app/prediction/astrologer_prompt_builder.py`
- `daily_synthesis : strictement` in `backend/app/prediction/astrologer_prompt_builder.py`
- `backend/app/services/ai_engine_adapter.py`
- `app.services.ai_engine_adapter`

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Context payload | `backend/app/prediction/astrologer_prompt_builder.py` | assembly text duplication |
| Durable prompt instruction | `backend/app/domain/llm/configuration` | builder hard-coded text |
| Daily narration execution | `backend/app/services/llm_generation/horoscope_daily` | adapter narrative logic |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

Codex must inspect before editing:

- `backend/app/prediction/astrologer_prompt_builder.py`
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py`
- `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py`
- `backend/tests/unit/prediction/test_astrologer_prompt_builder.py`
- `backend/tests/llm_orchestration/test_narrator_migration.py`

## 19. Expected Files to Modify

Likely files:

- `backend/app/prediction/astrologer_prompt_builder.py` - retirer les consignes durables.
- `backend/app/ops/llm/bootstrap/seed_horoscope_narrator_assembly.py` - porter les consignes migrees.
- `backend/app/services/llm_generation/horoscope_daily/narration_service.py` - ajuster le payload si requis.

Likely tests:

- `backend/tests/unit/prediction/test_astrologer_prompt_builder.py` - verifier payload only.
- `backend/tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py` - verifier assembly.
- `backend/tests/llm_orchestration/test_narrator_migration.py` - verifier runtime.

Files not expected to change:

- `frontend/src` - aucun changement UI.
- `backend/app/api/v1/routers` - aucune route API.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_validate.py ..\_condamad\stories\converge-horoscope-daily-narration-assembly\00-story.md
python -B ..\.agents\skills\condamad-story-writer\scripts\condamad_story_lint.py --strict ..\_condamad\stories\converge-horoscope-daily-narration-assembly\00-story.md
pytest -q tests/unit/prediction/test_astrologer_prompt_builder.py
pytest -q tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py
pytest -q tests/llm_orchestration/test_narrator_migration.py
rg -n "Format attendu|Interdiction|daily_synthesis : strictement" app/prediction/astrologer_prompt_builder.py
ruff check .
```

## 22. Regression Risks

- Risk: perte de contexte metier quotidien.
  - Guardrail: tests builder.
- Risk: admin affichant une source differente du runtime.
  - Guardrail: tests detail catalog.

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

- `_condamad/audits/prompt-generation/2026-04-30-1810/03-story-candidates.md` - SC-003.
- `_condamad/audits/prompt-generation/2026-04-30-1810/01-evidence-log.md` - E-010.
- `_bmad-output/implementation-artifacts/70-12*.md` - couches observables admin.
- `_bmad-output/implementation-artifacts/70-20.md` - adapter minimal.
