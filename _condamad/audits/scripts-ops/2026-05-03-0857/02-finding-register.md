# Finding Register - scripts-ops

| ID | Severity | Confidence | Category | Domain | Evidence | Impact | Recommended action | Story candidate |
|---|---|---|---|---|---|---|---|---|
| F-001 | Medium | High | needs-user-decision | scripts-ops | E-002, E-004, E-012 | The Bash Stripe listener remains active beside the canonical PowerShell listener, which preserves a non-Windows dev path without a durable support decision. | needs-user-decision: either declare Git Bash / WSL support as intentional or remove the Bash listener and related docs/tests. | needs-user-decision |
| F-002 | Info | High | missing-canonical-owner | scripts-ops | E-002, E-004, E-005 | The prior flat-folder ownership risk is now controlled by exact registry coverage for every root file under `scripts/`. | Keep `RG-023` and `test_scripts_ownership.py` as mandatory guards for future script additions. | no |
| F-003 | Info | High | legacy-surface | scripts-ops | E-004, E-006, E-007 | The prior one-off route-removal validator is no longer an active root script, reducing story-specific legacy in `scripts/`. | No action; preserve the negative scan through the ownership guard. | no |
| F-004 | Info | High | missing-test-coverage | scripts-ops | E-002, E-004, E-008 | The local dev stack script is now documented, tested, and no longer requires Stripe for standard backend/frontend startup. | No action; keep `RG-024` and `test_start_dev_stack_script.py`. | no |
| F-005 | Info | High | runtime-contract-drift | scripts-ops | E-004, E-009 | The previous local absolute cache path was replaced by repo-relative cache resolution. | No action; keep `test_llm_release_readiness_script.py`. | no |
| F-006 | Info | High | duplicate-responsibility | scripts-ops | E-004, E-010 | Critical load responsibilities are grouped and destructive privacy load is opt-in, so the prior mixed-scope risk is materially reduced. | No action; keep manifest guards and explicit scenario group selection. | no |
| F-007 | Info | High | boundary-violation | scripts-ops | E-004, E-011 | The natal cross-tool report remains dev-only with runtime import and CI refusal guards. | No action; keep the dev-only contract tests. | no |

## Details

### F-001

- Severity: Medium
- Confidence: High
- Category: needs-user-decision
- Domain: scripts-ops
- Evidence: E-002, E-004, E-012.
- Expected rule: the repository target dev OS is Windows / PowerShell, so any parallel Bash implementation must be an explicit support policy rather than silent legacy.
- Actual state: `scripts/stripe-listen-webhook.sh` remains present, documented for Git Bash/WSL, tested for parity, and marked `needs-user-decision` in `scripts/ownership-index.md`.
- Impact: The Bash Stripe listener remains active beside the canonical PowerShell listener, which preserves a non-Windows dev path without a durable support decision.
- Recommended action: needs-user-decision: either declare Git Bash / WSL support as intentional or remove the Bash listener and related docs/tests.
- Story candidate: needs-user-decision
- Suggested archetype: legacy-facade-removal

### F-002

- Severity: Info
- Confidence: High
- Category: missing-canonical-owner
- Domain: scripts-ops
- Evidence: E-002, E-004, E-005.
- Expected rule: every root file under `scripts/` has exactly one visible owner, usage, support status, and validation command.
- Actual state: `scripts/ownership-index.md` covers the current `rg --files scripts` inventory and `test_scripts_ownership.py` passed.
- Impact: The prior flat-folder ownership risk is now controlled by exact registry coverage for every root file under `scripts/`.
- Recommended action: Keep `RG-023` and `test_scripts_ownership.py` as mandatory guards for future script additions.
- Story candidate: no
- Suggested archetype: none

### F-003

- Severity: Info
- Confidence: High
- Category: legacy-surface
- Domain: scripts-ops
- Evidence: E-004, E-006, E-007.
- Expected rule: story-specific validators do not remain as active root operational scripts after their one-off use ends.
- Actual state: `rg -n "validate_route_removal_audit.py" scripts backend frontend docs` has no hit; removal story evidence classifies the old root validator as `dead` and deleted.
- Impact: The prior one-off route-removal validator is no longer an active root script, reducing story-specific legacy in `scripts/`.
- Recommended action: No action; preserve the negative scan through the ownership guard.
- Story candidate: no
- Suggested archetype: none

### F-004

- Severity: Info
- Confidence: High
- Category: missing-test-coverage
- Domain: scripts-ops
- Evidence: E-002, E-004, E-008.
- Expected rule: standard local startup launches backend/frontend without requiring Stripe; Stripe startup is explicit and guarded.
- Actual state: `start-dev-stack.ps1` uses `[switch] $WithStripe`, docs show standard startup without Stripe, and the targeted guard passed.
- Impact: The local dev stack script is now documented, tested, and no longer requires Stripe for standard backend/frontend startup.
- Recommended action: No action; keep `RG-024` and `test_start_dev_stack_script.py`.
- Story candidate: no
- Suggested archetype: none

### F-005

- Severity: Info
- Confidence: High
- Category: runtime-contract-drift
- Domain: scripts-ops
- Evidence: E-004, E-009.
- Expected rule: release readiness scripts must be portable across repository clones.
- Actual state: `llm-release-readiness.ps1` derives the pytest cache path from `$root` and guard tests assert the old absolute path is absent.
- Impact: The previous local absolute cache path was replaced by repo-relative cache resolution.
- Recommended action: No action; keep `test_llm_release_readiness_script.py`.
- Story candidate: no
- Suggested archetype: none

### F-006

- Severity: Info
- Confidence: High
- Category: duplicate-responsibility
- Domain: scripts-ops
- Evidence: E-004, E-010.
- Expected rule: load-test scenarios are grouped by responsibility and destructive scenarios are not executed by default.
- Actual state: `load-test-critical.ps1` defines `smoke`, `llm`, `b2b`, `destructive-privacy`, and `stress-incidents`; default groups exclude `destructive-privacy`; tests assert old story and legacy markers are absent.
- Impact: Critical load responsibilities are grouped and destructive privacy load is opt-in, so the prior mixed-scope risk is materially reduced.
- Recommended action: No action; keep manifest guards and explicit scenario group selection.
- Story candidate: no
- Suggested archetype: none

### F-007

- Severity: Info
- Confidence: High
- Category: boundary-violation
- Domain: scripts-ops
- Evidence: E-004, E-011.
- Expected rule: a root diagnostic script that consumes test fixtures must be explicitly dev-only and must not leak that dependency into runtime backend modules.
- Actual state: tests assert `natal-cross-tool-report-dev.py` refuses CI execution and is the only runtime-adjacent golden fixture consumer.
- Impact: The natal cross-tool report remains dev-only with runtime import and CI refusal guards.
- Recommended action: No action; keep the dev-only contract tests.
- Story candidate: no
- Suggested archetype: none
