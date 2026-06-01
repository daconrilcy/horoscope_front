# CS-426 Source Alignment

Commentaire global: cette preuve relie le brief source aux artefacts d'inventaire livres pour CS-426.

## Source

- Story: `_condamad/stories/CS-426-freeze-inventory-legacy-generation-natal-bigbang/00-story.md`
- Brief: `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md`
- Tracker: `_condamad/stories/story-status.md`, row `CS-426`

## Brief Coverage

| Brief primitive | Implementation artifact | Status |
|---|---|---|
| Public, admin, and dev natal generation endpoints | `evidence/legacy-generation-map.md` maps public natal routes, profile routes, internal QA, services, runtime, scripts, tests, reports, and frontend rows. | covered |
| Services, gateways, seeds, prompts, schemas, tests, mocks, and frontend components | `evidence/legacy-generation-map.md` and `evidence/legacy-surface-classification.md` classify each covered surface, including API contracts and runtime adapter. | covered |
| Required vocabulary `delete`, `replace`, `readonly`, `keep`, `needs-decision` | `legacy-surface-classification.md` uses the same classification vocabulary and architecture guard checks it. | covered |
| Legacy active generation versus readonly readback | Map rows distinguish `active-generation`, `readonly`, `bootstrap`, `test-only`, `admin-only`, and `historical`. | covered |
| Named primitives and trigger fields | Map and scans cover `natal_interpretation_short`, `natal_long_free`, `natal_interpretation`, `use_case_level`, `variant_code`, `forceRefresh`, fallback, and persistence tokens. | covered |
| Initial scans for later blocking evidence | `evidence/initial-scans.txt` preserves VC1 through VC6 outputs. | covered |
| `_condamad/run-state.json` out of scope | `initial-scans.txt`, `10-final-evidence.md`, and review evidence record it as non-story-owned and unchanged by CS-426 edits. | covered |

## Guardrail Alignment

Applicable guardrails are recorded in `00-story.md` and tied to VC evidence:
`RG-001`, `RG-002`, `RG-005`, `RG-018`, `RG-021`, `RG-149`, `RG-150`, `RG-152`, `RG-157`, `RG-171`, and `RG-172`.

The implementation adds only an architecture guard and evidence artifacts. It does not edit runtime route, service, gateway, prompt, DB,
script, migration, or frontend source files.

## Accepted Assumptions

- `delete` is only a future classification in this inventory story; no physical code deletion is performed here.
- `needs-decision` entries are intentionally retained for follow-up ownership decisions, with owner and expected decision recorded.
- `_condamad/run-state.json` is already dirty in the worktree and remains outside CS-426 ownership.

## Alignment correction on 2026-06-01

- Added missing real-code surfaces found by targeted generation scans:
  `public/users.py`, `internal/llm/qa.py`, public/internal API contracts, `runtime/adapter.py`, and two dev debug scripts.
- No functional code was changed; only CS-426 evidence and the architecture guard were updated.
