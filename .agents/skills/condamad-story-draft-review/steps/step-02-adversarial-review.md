<!-- Etape de revue redactionnelle multi-couches sans revue de code applicatif. -->

# Step 2 - Adversarial Story Review

## Objective

Run adversarial layers against the drafted story contract. The main Codex
session owns final judgment.

## Layers

### Layer A - Source Alignment

Check whether the story preserves the source brief, audit finding, or user
request:

- objective and expected outcome;
- exact domain boundary;
- source constraints and non-goals;
- expected files, tests, and review artifact path.

### Layer B - Acceptance Criteria Auditor

For every AC:

- verify it is atomic and testable;
- verify it has validator-recognized evidence;
- flag compound requirements, vague wording, or missing proof;
- check that tasks map back to ACs.

### Layer C - Validation Skeptic

Audit the validation plan:

- story validator and strict lint are runnable;
- expected implementation checks are concrete;
- skipped checks have bounded reasons;
- runtime/API claims use runtime evidence, not only text search.

### Layer D - Guardrail and No Legacy Auditor

Check that the story:

- uses only scoped guardrail IDs;
- records registry gaps without modifying the registry;
- forbids fallback, shim, alias, wrapper, and legacy routes;
- includes negative scans or runtime absence checks where relevant.

### Layer E - Story Completeness Auditor

Check for:

- valid status line;
- dependency policy and justification;
- files to inspect and expected files to modify;
- repository structure alerts when roots are absent;
- review artifact path aligned to `generated/11-code-review.md`.

## Output to Step 3

Produce raw candidate findings with:

- layer;
- title;
- severity guess;
- story/capsule location;
- evidence;
- suspected bucket;
- suggested story-artifact fix.
