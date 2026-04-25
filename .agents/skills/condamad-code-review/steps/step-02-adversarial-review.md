<!-- Etape de revue multi-couches sans modification applicative. -->

# Step 2 - Adversarial Review

## Objective

Run independent adversarial layers against the same evidence. Subagents are
optional and read-only; the main Codex session owns final judgment.

## Layers

### Layer A - Blind Diff Integrity

Review the diff without trusting story intent.

Look for:

- unrelated or surprising files;
- risky deletions;
- database/cache/generated artifacts;
- secrets;
- broad formatting churn;
- accidental public API changes;
- conflict markers or broken syntax.

### Layer B - Acceptance Auditor

For every AC:

- map implementation evidence;
- map validation evidence;
- flag missing, contradicted, or weak proof;
- check non-goals and scope boundaries.

### Layer C - Edge Case Hunter

Inspect changed code and nearby callers for:

- empty collections, nulls, malformed input;
- missing permissions;
- duplicate or stale state;
- transaction boundaries;
- idempotency;
- timezone/date handling;
- frontend loading/error/empty states;
- external-client failures and timeouts.

### Layer D - DRY / No Legacy Hunter

Search and inspect for:

- duplicate active implementations;
- shims, aliases, re-exports, compatibility wrappers;
- fallback behavior;
- old imports or registry keys;
- tests/docs that keep legacy paths nominal.

Use story-specific `rg` searches when relevant.

### Layer E - Validation Skeptic

Audit claimed validation:

- Were commands actually run?
- Were Python commands run with the venv activated when applicable?
- Do tests target the changed behavior?
- Are skipped checks justified?
- Is `git diff --check` or equivalent covered?
- Are full regression gaps documented honestly?

### Layer F - Security and Data Reviewer

Check:

- authn/authz boundaries;
- CORS, secrets, and environment defaults;
- sensitive logs/errors;
- input validation;
- injection/path risks;
- persistence/migration safety.

## Subagent Option

If the current user explicitly authorized parallel/subagent review, split these
layers into read-only subagent tasks. Otherwise run all layers yourself.

## Output to Step 3

Produce raw candidate findings with:

- layer;
- title;
- severity guess;
- location;
- evidence;
- suspected bucket;
- suggested fix.

