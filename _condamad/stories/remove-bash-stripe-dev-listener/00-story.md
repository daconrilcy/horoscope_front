# Story remove-bash-stripe-dev-listener: Retirer le listener Stripe Bash et figer le support dev PowerShell

Status: ready-for-dev

## 1. Objective

Supprimer la variante Bash `scripts/stripe-listen-webhook.sh` et faire de
`scripts/stripe-listen-webhook.ps1` l'unique script supporte pour l'ecoute
Stripe locale. Le client Stripe CLI reste un outil de developpement local
uniquement, sous Windows / PowerShell, et ne doit pas etre documente ou garde
comme surface Git Bash, WSL, CI, production ou deploiement.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/scripts-ops/2026-05-03-0857/02-finding-register.md` (`F-001`)
- User decision: le client Stripe doit etre utilise en mode dev uniquement, avec support uniquement PowerShell sous Windows, l'environnement de dev cible.
- Reason for change: l'audit a laisse `scripts/stripe-listen-webhook.sh` en `needs-user-decision`; la decision utilisateur tranche ce support comme non canonique et removable.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `scripts/`
- In scope:
  - Supprimer `scripts/stripe-listen-webhook.sh`.
  - Mettre a jour `scripts/ownership-index.md` pour retirer la ligne Bash et conserver uniquement la ligne PowerShell.
  - Mettre a jour la documentation locale Stripe pour ne proposer que PowerShell/Windows et pour qualifier la Stripe CLI comme dev-only.
  - Adapter les tests d'ownership et de docs/scripts Stripe pour refuser la reintroduction du script Bash.
  - Persister un scan avant/apres des references Bash dans ce dossier de story.
- Out of scope:
  - Modifier `backend/app/services/billing/stripe_webhook_service.py` ou la logique runtime des webhooks Stripe.
  - Modifier les evenements Stripe supportes par le backend.
  - Ajouter un support Linux, WSL, Git Bash, CI ou production pour la Stripe CLI locale.
  - Modifier `scripts/start-dev-stack.ps1` au-dela des references directes necessaires si un test ou une doc pointe vers le script Bash.
- Explicit non-goals:
  - Ne pas affaiblir `RG-023`: chaque fichier racine restant sous `scripts/` doit rester couvert par `scripts/ownership-index.md`.
  - Ne pas affaiblir `RG-024`: Stripe doit rester optionnel via `-WithStripe` pour le demarrage local, et jamais requis pour backend/frontend standard.
  - Ne pas creer de wrapper, alias, fallback, re-export ou nouveau script shell pour remplacer `scripts/stripe-listen-webhook.sh`.
  - Ne pas transformer le listener Stripe local en surface CI, production ou deploiement.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: le script Bash est une surface de compatibilite non canonique qui duplique le script PowerShell deja designe comme variante de reference.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le comportement local PowerShell doit rester identique: memes evenements standardises et meme `--forward-to http://localhost:8001/v1/billing/stripe-webhook`.
  - Les docs doivent retirer Git Bash/WSL comme chemins supportes et declarer explicitement le mode dev-only.
  - Aucun comportement backend Stripe ne doit changer.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une preuve externe actuelle impose un support Git Bash/WSL non mentionne par l'audit ou par la decision utilisateur.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le script PowerShell et les guards de fichiers sont la source de verite du support local Stripe. |
| Baseline Snapshot | yes | Un scan avant/apres doit prouver la disparition des references Bash et la conservation PowerShell. |
| Ownership Routing | yes | `scripts/ownership-index.md` doit router l'ownership vers le script PowerShell uniquement. |
| Allowlist Exception | no | Aucune exception n'est autorisee pour conserver Bash, Git Bash ou WSL. |
| Contract Shape | no | Aucun contrat API, DTO, OpenAPI ou type frontend n'est touche. |
| Batch Migration | no | Il n'y a pas de migration par lots; une seule surface non canonique est supprimee. |
| Reintroduction Guard | yes | Un guard doit echouer si `scripts/stripe-listen-webhook.sh`, Git Bash ou WSL redeviennent support nominal. |
| Persistent Evidence | yes | Les scans avant/apres et l'audit de suppression doivent rester dans le dossier de story. |

## 4b. Runtime Source of Truth

Use when the story changes API routes, config, runtime registration, generated
contracts, persistence behavior, or architecture rules.

- Primary source of truth:
  - AST guard and file guard over `scripts/stripe-listen-webhook.ps1` and absence of `scripts/stripe-listen-webhook.sh`.
  - AST guard in `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py` plus `scripts/ownership-index.md` exact registry coverage for current `rg --files scripts`.
- Secondary evidence:
  - Targeted `rg` scans for `stripe-listen-webhook.sh`, `Git Bash`, `WSL`, and Bash listener commands.
  - Tests under `backend/app/tests/unit/`.
- Static scans alone are not sufficient for this story because:
  - The durable rule must fail from tests if the Bash file or Bash support documentation returns.

## 4c. Baseline / Before-After Rule

Use for refactor, convergence, migration, route restructuring, API contract
changes, or behavior-preserving changes.

- Baseline artifact before implementation:
  - `_condamad/stories/remove-bash-stripe-dev-listener/reference-baseline.txt`
    generated by the baseline scan from section 21.
- Comparison after implementation:
  - `_condamad/stories/remove-bash-stripe-dev-listener/reference-after.txt` generated by the same command.
- Expected invariant:
  - Active scripts, docs and tests no longer support Bash/Git Bash/WSL for the local Stripe listener; historical audit references may remain under `_condamad/audits/**`.

## 4d. Ownership Routing Rule

Use for boundary, namespace, service, API, core, domain, or infra refactors.

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Local Stripe webhook listener script | `scripts/stripe-listen-webhook.ps1` | `scripts/stripe-listen-webhook.sh`, any new `.sh`, `.bash`, WSL or Git Bash listener |
| Root script ownership decision | `scripts/ownership-index.md` | Implicit support status, `needs-user-decision` for the removed Bash path |
| Local Stripe validation runbook | `docs/billing-webhook-local-testing.md` | Git Bash/WSL instructions or production/CI use of Stripe CLI listener |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: no exception is allowed by this story.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: no multi-surface or multi-consumer migration is required.

## 4h. Persistent Evidence Artifacts

Use when the story requires audit, snapshot, baseline, OpenAPI diff, migration
mapping, allowlist register, or exception register evidence.

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| Reference baseline | `_condamad/stories/remove-bash-stripe-dev-listener/reference-baseline.txt` | Prouver les references Bash/Git Bash/WSL avant suppression. |
| Reference after-scan | `_condamad/stories/remove-bash-stripe-dev-listener/reference-after.txt` | Prouver l'absence de support nominal Bash apres suppression. |
| Removal audit | `_condamad/stories/remove-bash-stripe-dev-listener/removal-audit.md` | Classifier `scripts/stripe-listen-webhook.sh` et documenter la decision utilisateur. |

## 4i. Reintroduction Guard

Use when the story removes, forbids, or converges away from a legacy route,
field, import, module, prefix, OpenAPI path, frontend route, or status.

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

The guard must check at least one deterministic source:

- forbidden symbols or states
- importable Python modules
- frontend route table
- generated OpenAPI paths
- registered router prefixes

Required forbidden examples:

- `scripts/stripe-listen-webhook.sh`
- `stripe-listen-webhook.sh`
- `Git Bash`
- `WSL`
- `#!/usr/bin/env bash` in root Stripe listener assets

Guard evidence:

- Evidence profile: `reintroduction_guard`.
- Command: `pytest -q app/tests/unit/test_scripts_ownership.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/unit/test_start_dev_stack_script.py`.
- Expected result: forbidden Bash support fails, while PowerShell/Windows dev behavior remains preserved.

## 5. Current State Evidence

The current codebase or audit indicates:

- Evidence 1: `_condamad/audits/scripts-ops/2026-05-03-0857/02-finding-register.md` -
  `F-001` marks `scripts/stripe-listen-webhook.sh` as the only remaining issue.
- Evidence 2: `scripts/stripe-listen-webhook.ps1` - PowerShell listener already forwards standardized billing events to `http://localhost:8001/v1/billing/stripe-webhook`.
- Evidence 3: `scripts/stripe-listen-webhook.sh` - Bash listener duplicates the PowerShell listener.
- Evidence 4: `scripts/ownership-index.md` - Bash listener row is `needs-user-decision` / `blocked-support-decision`; PowerShell row is `supported` / `keep`.
- Evidence 5: `docs/billing-webhook-local-testing.md` - current runbook says Bash remains available for Git Bash or WSL.
- Evidence 6: `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py` - current guard expects both PowerShell and Bash listener assets.
- Evidence 7: `_condamad/stories/regression-guardrails.md` - invariants consulted before scope, especially `RG-023` and `RG-024`.
- Evidence 8: user decision in this conversation - Stripe CLI listener is dev-only and supported only through PowerShell on Windows.

## 6. Target State

After implementation:

- `scripts/stripe-listen-webhook.sh` no longer exists.
- `scripts/stripe-listen-webhook.ps1` remains the only supported local Stripe listener script.
- `scripts/ownership-index.md` covers every remaining root script and has no row for the removed Bash listener.
- `docs/billing-webhook-local-testing.md` documents Windows / PowerShell only and states that Stripe CLI listener usage is local dev-only.
- Tests fail if Bash/Git Bash/WSL support is reintroduced as a nominal path.
- `scripts/start-dev-stack.ps1 -WithStripe` continues to use the PowerShell listener only.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-023` - this story removes one root script and must keep `scripts/ownership-index.md` exactly aligned with `rg --files scripts`.
  - `RG-024` - this story touches the local Stripe listener used by `start-dev-stack.ps1 -WithStripe`; standard backend/frontend startup must remain Stripe-free.
- Non-applicable invariants:
  - `RG-004` - no API error envelope is modified.
  - `RG-010` - backend test topology is not reorganized.
  - `RG-021` - prompt fallback governance is not touched.
- Required regression evidence:
  - `pytest -q app/tests/unit/test_scripts_ownership.py app/tests/unit/test_start_dev_stack_script.py app/tests/unit/test_stripe_webhook_local_dev_assets.py`
  - Negative scan for `stripe-listen-webhook.sh`, `Git Bash`, and `WSL` in active scripts/docs/tests.
  - Before/after reference snapshots persisted in this story folder.
- Allowed differences:
  - Delete `scripts/stripe-listen-webhook.sh`.
  - Remove Bash/Git Bash/WSL instructions and tests.
  - Keep historical references under `_condamad/audits/**` and this story's baseline evidence.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Bash listener removal follows `removal-audit.md` classification. | Evidence: `removal-audit.md`; `rg --files scripts \| rg "stripe-listen-webhook\\.sh"` has no hit. |
| AC2 | `scripts/ownership-index.md` covers root scripts without the Bash row. | Evidence: `pytest -q app/tests/unit/test_scripts_ownership.py`; targeted `rg`. |
| AC3 | The local Stripe runbook states dev-only Windows / PowerShell support. | Evidence: `pytest -q app/tests/unit/test_stripe_webhook_local_dev_assets.py`; docs `rg`. |
| AC4 | PowerShell listener command remains the canonical local target. | Evidence: `pytest -q app/tests/unit/test_stripe_webhook_local_dev_assets.py`; `.ps1` scan. |
| AC5 | `start-dev-stack.ps1 -WithStripe` targets PowerShell. | Evidence: `pytest -q app/tests/unit/test_start_dev_stack_script.py`. |
| AC6 | Persistent after-scan proves no compatibility path remains. | Evidence: baseline file; after file; final `rg` scan from section 21. |

## 8. Implementation Tasks

- [ ] Task 1 - Capture removal evidence before editing (AC: AC1, AC6)
  - [ ] Subtask 1.1 - Generate `reference-baseline.txt` with the baseline scan from section 4c.
  - [ ] Subtask 1.2 - Create `removal-audit.md` with the required classification table and record the user decision.

- [ ] Task 2 - Remove the non-canonical Bash surface (AC: AC1, AC2)
  - [ ] Subtask 2.1 - Delete `scripts/stripe-listen-webhook.sh`.
  - [ ] Subtask 2.2 - Remove the Bash row and `blocked-support-decision` meaning from `scripts/ownership-index.md` if no remaining row uses that decision.

- [ ] Task 3 - Update docs and tests to enforce PowerShell-only dev support (AC: AC3, AC4, AC5)
  - [ ] Subtask 3.1 - Update `docs/billing-webhook-local-testing.md` so the runbook says local dev-only, Windows / PowerShell only, and no Git Bash/WSL path.
  - [ ] Subtask 3.2 - Update `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py` to assert the Bash file is absent and the PowerShell script remains canonical.
  - [ ] Subtask 3.3 - Update `backend/app/tests/unit/test_scripts_ownership.py` to remove the blocked Bash decision assertion and keep inventory coverage.
  - [ ] Subtask 3.4 - Keep or tighten `backend/app/tests/unit/test_start_dev_stack_script.py` so `-WithStripe` still invokes only `stripe-listen-webhook.ps1`.

- [ ] Task 4 - Validate and persist after-state evidence (AC: AC2, AC3, AC4, AC5, AC6)
  - [ ] Subtask 4.1 - Generate `reference-after.txt` with the same scan as baseline.
  - [ ] Subtask 4.2 - Run targeted tests and negative scans from the validation plan.
  - [ ] Subtask 4.3 - Record any historical-only remaining hits in `removal-audit.md`; do not keep active docs/tests hits.

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `scripts/stripe-listen-webhook.ps1` as the only local Stripe listener implementation.
  - `scripts/ownership-index.md` as the canonical root script ownership registry.
  - Existing tests `test_scripts_ownership.py`, `test_stripe_webhook_local_dev_assets.py`, and `test_start_dev_stack_script.py`.
- Do not recreate:
  - A Bash, Git Bash, WSL, `.cmd`, `.bat`, Node, Python, or secondary listener script for the same local Stripe responsibility.
  - A second ownership register or alternate support decision table.
- Shared abstraction allowed only if:
  - It removes real duplication inside an existing test file; it must not add a new production helper.

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

- `scripts/stripe-listen-webhook.sh`
- `stripe-listen-webhook.sh`
- `Git Bash`
- `WSL`
- `#!/usr/bin/env bash` for a Stripe listener under `scripts/`
- `blocked-support-decision` for the removed Bash listener

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
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

Audit output path:

- `_condamad/stories/remove-bash-stripe-dev-listener/removal-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Local Stripe webhook listener for development | `scripts/stripe-listen-webhook.ps1` | `scripts/stripe-listen-webhook.sh`, Git Bash/WSL listener docs |
| Local Stripe startup from dev stack | `scripts/start-dev-stack.ps1 -WithStripe` | Any unconditional Stripe startup or Bash listener invocation |
| Root script ownership registry | `scripts/ownership-index.md` | Any implicit script support status or stale row for deleted files |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

For this story, the user decision already rejects Git Bash/WSL support. Only a new, concrete, first-party external requirement discovered during implementation may block deletion.

## 17. Generated Contract Check

- Generated contract check: active for absence proof.
- Required generated-contract evidence:
  - `rg -n "stripe-listen-webhook\\.sh|Git Bash|WSL" frontend backend/app docs scripts`
    proves no generated client, frontend route, backend contract, public docs or script surface still exposes the removed Bash listener.
  - No OpenAPI path absence is required because the removed surface is a local script, not an API route.
  - No generated TypeScript client/schema absence is required because no generated client is affected; the scan above is the generated/public artifact absence proxy for this story.

## 18. Files to Inspect First

Codex must inspect before editing:

- `scripts/stripe-listen-webhook.ps1`
- `scripts/stripe-listen-webhook.sh`
- `scripts/ownership-index.md`
- `scripts/start-dev-stack.ps1`
- `docs/billing-webhook-local-testing.md`
- `docs/local-dev-stack.md`
- `docs/development-guide-backend.md`
- `backend/app/tests/unit/test_scripts_ownership.py`
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py`
- `backend/app/tests/unit/test_start_dev_stack_script.py`
- `_condamad/audits/scripts-ops/2026-05-03-0857/02-finding-register.md`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `scripts/stripe-listen-webhook.sh` - delete the non-canonical Bash listener.
- `scripts/ownership-index.md` - remove the Bash row and stale blocked decision.
- `docs/billing-webhook-local-testing.md` - document dev-only Windows / PowerShell support.
- `_condamad/stories/remove-bash-stripe-dev-listener/removal-audit.md` - persist classification and user decision.
- `_condamad/stories/remove-bash-stripe-dev-listener/reference-baseline.txt` - persist before scan.
- `_condamad/stories/remove-bash-stripe-dev-listener/reference-after.txt` - persist after scan.

Likely tests:

- `backend/app/tests/unit/test_scripts_ownership.py` - update ownership expectations after deletion.
- `backend/app/tests/unit/test_stripe_webhook_local_dev_assets.py` - replace Bash parity test with Bash absence and PowerShell-only dev support tests.
- `backend/app/tests/unit/test_start_dev_stack_script.py` - keep or tighten PowerShell-only `-WithStripe` assertion.

Files not expected to change:

- `backend/app/services/billing/stripe_webhook_service.py` - webhook runtime behavior and event handling are out of scope.
- `backend/app/api/**` - no API route, OpenAPI, or HTTP contract changes are in scope.
- `frontend/**` - no frontend behavior is in scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
.\.venv\Scripts\Activate.ps1
Push-Location backend
pytest -q app/tests/unit/test_scripts_ownership.py app/tests/unit/test_stripe_webhook_local_dev_assets.py app/tests/unit/test_start_dev_stack_script.py
Pop-Location
rg -n "stripe-listen-webhook\\.sh|Git Bash|WSL|#!/usr/bin/env bash" scripts docs backend/app/tests
rg --files scripts
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/remove-bash-stripe-dev-listener/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/remove-bash-stripe-dev-listener/00-story.md
```

Expected scan notes:

- The negative scan must have no active hits in `scripts`, `docs`, or `backend/app/tests`.
- Historical hits under `_condamad/audits/**` or this story's `reference-baseline.txt` are allowed only if recorded in `removal-audit.md`.

## 22. Regression Risks

- Risk: deleting the Bash listener also weakens coverage of the PowerShell event list.
  - Guardrail: `test_stripe_webhook_local_dev_assets.py` must assert the PowerShell standardized event list directly.
- Risk: docs still imply Git Bash/WSL support even after file deletion.
  - Guardrail: targeted docs scan for `Git Bash`, `WSL`, bash code fences, and `stripe-listen-webhook.sh`.
- Risk: root script ownership drifts after deletion.
  - Guardrail: `RG-023` and `test_scripts_ownership.py` must compare registry rows against `rg --files scripts`.
- Risk: standard local startup becomes Stripe-dependent.
  - Guardrail: `RG-024` and `test_start_dev_stack_script.py` must keep `-WithStripe` opt-in.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not perform unrelated cleanup.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Keep Stripe CLI listener usage local-dev-only and Windows / PowerShell-only.

## 24. References

- `_condamad/audits/scripts-ops/2026-05-03-0857/02-finding-register.md` - source finding `F-001`.
- `_condamad/audits/scripts-ops/2026-05-03-0857/05-executive-summary.md` - confirms the only remaining issue is the Bash Stripe listener decision.
- `_condamad/stories/regression-guardrails.md` - shared invariants `RG-023` and `RG-024`.
- `scripts/ownership-index.md` - current ownership and support decision registry.
- `docs/billing-webhook-local-testing.md` - current local Stripe validation runbook.

## 25. Audit Finding Coverage

| Finding | Coverage in this story | Scope decision |
|---|---|---|
| `F-001` | Primary implementation target: remove Bash Stripe listener and keep PowerShell-only dev support. | in scope |
| `F-002` | Preserved through `RG-023`, AC2, and `test_scripts_ownership.py`. | non-regression guard |
| `F-003` | No action required; the route-removal validator is already absent and remains outside this Stripe-only story. | closed finding |
| `F-004` | Preserved through `RG-024`, AC5, and `test_start_dev_stack_script.py`. | non-regression guard |
| `F-005` | No action required; LLM readiness portability is already guarded by its dedicated tests. | closed finding |
| `F-006` | No action required; critical load scenario grouping is already guarded by its dedicated tests. | closed finding |
| `F-007` | No action required; natal cross-tool dev-only behavior is already guarded by its dedicated tests. | closed finding |
