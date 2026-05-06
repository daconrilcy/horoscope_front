# Final Evidence - CS-081

## Story status

- Validation outcome: PASS
- Ready for review: yes
- Story key: CS-081-migrer-cluster-chat-valeurs-visuelles-hardcodees
- Source story: `_condamad/stories/CS-081-migrer-cluster-chat-valeurs-visuelles-hardcodees/00-story.md`
- Capsule path: `_condamad/stories/CS-081-migrer-cluster-chat-valeurs-visuelles-hardcodees/`

## Preflight

- Repository root: `c:\dev\horoscope_front`
- Initial `git status --short`: pre-existing changes in `_condamad/stories/regression-guardrails.md`, `_condamad/stories/story-status.md`, audit folder `2026-05-06-2139`, and CS-081 capsule.
- AGENTS.md considered: root `AGENTS.md`.
- Capsule generated: yes, missing `generated/` files created.
- Frontend contract: applied directly in main session; no implementation subagent used because current tool policy requires explicit delegation wording.

## Capsule validation

| File | Required | Present | Status | Notes |
|---|---:|---:|---|---|
| `00-story.md` | yes | yes | PASS | Human story preserved. |
| `generated/01-execution-brief.md` | yes | yes | PASS | Created. |
| `generated/03-acceptance-traceability.md` | yes | yes | PASS | All ACs mapped. |
| `generated/04-target-files.md` | yes | yes | PASS | Created. |
| `generated/06-validation-plan.md` | yes | yes | PASS | Created. |
| `generated/07-no-legacy-dry-guardrails.md` | yes | yes | PASS | Created. |
| `generated/10-final-evidence.md` | yes | yes | PASS | Created. |

## AC validation

| AC | Implementation evidence | Validation evidence | Status | Notes |
|---|---|---|---|---|
| AC1 | Scope limited to chat CSS, token registry, design-system guard, story artifacts and status registry. | `hardcoded-values-before.md`, `git diff --stat`. | PASS | No TSX, hook, API or backend runtime changes. |
| AC2 | `--chat-*` owner and consumer migration recorded in `hardcoded-values-after.md`. | Scan on `hardcoded-values-after.md` for forbidden incomplete wording returned no hits. | PASS | Existing avatar replacement names classified. |
| AC3 | `--chat-*` row added to `token-namespace-registry.md`; consumers use tokens/roles. | `npm run test -- theme-tokens design-system` via guarded subset passed. | PASS | Namespace registry guard passes. |
| AC4 | No allowlist widened; CSS variable default scan has no hit. | `npm run test -- css-fallback inline-style legacy-style` passed. | PASS | |
| AC5 | React unchanged; visual smoke suite retained. | `npm run test -- visual-smoke design-system` passed. | PASS | |
| AC6 | New CS-081 guard in `design-system-guards.test.ts`. | `npm run test -- design-system` passed. | PASS | |
| AC7 | All AC rows complete with PASS. | Final evidence scan returned no incomplete status wording. | PASS | |

## Files changed

| File | Change type | Purpose | Related AC |
|---|---|---|---|
| `frontend/src/pages/ChatPage.css` | modified | Add semantic `--chat-*` owner and migrate page consumers. | AC2, AC3 |
| `frontend/src/features/chat/components/ChatComposer.css` | modified | Consume chat tokens and typographic roles. | AC2, AC3 |
| `frontend/src/features/chat/components/ChatPageHeader.css` | modified | Consume chat tokens and typographic roles. | AC2, AC3 |
| `frontend/src/features/chat/components/ChatQuotaBanner.css` | modified | Replace pill radius literals with chat token. | AC2, AC3 |
| `frontend/src/features/chat/components/ChatWindow.css` | modified | Consume chat tokens for header, chip, bubbles, errors and scrollbars. | AC2, AC3 |
| `frontend/src/features/chat/components/ConversationItem.css` | modified | Consume chat tokens and typographic roles. | AC2, AC3 |
| `frontend/src/features/chat/components/ConversationList.css` | modified | Consume chat tokens and typographic roles. | AC2, AC3 |
| `frontend/src/styles/token-namespace-registry.md` | modified | Document `--chat-*`. | AC3 |
| `frontend/src/tests/design-system-guards.test.ts` | modified | Add CS-081 reintroduction guard. | AC4, AC6 |
| `_condamad/stories/CS-081-migrer-cluster-chat-valeurs-visuelles-hardcodees/hardcoded-values-before.md` | added | Baseline artifact. | AC1 |
| `_condamad/stories/CS-081-migrer-cluster-chat-valeurs-visuelles-hardcodees/hardcoded-values-after.md` | added | Final decisions artifact. | AC2 |
| `_condamad/stories/CS-081-migrer-cluster-chat-valeurs-visuelles-hardcodees/generated/*.md` | added | CONDAMAD capsule evidence. | AC7 |

## Files deleted

None.

## Tests added or updated

- Updated `frontend/src/tests/design-system-guards.test.ts` with CS-081 chat cluster guard.

## Commands run

| Command | Working directory | Result | Exit status | Evidence summary |
|---|---|---|---:|---|
| `npm run test -- design-system` | `frontend/` | PASS | 0 | Final run: 1 file, 12 tests passed. |
| `npm run test -- design-system theme-tokens css-fallback inline-style legacy-style visual-smoke` | `frontend/` | PASS | 0 | 6 files, 134 tests passed. |
| `npm run lint` | `frontend/` | PASS | 0 | TypeScript lint configs passed. |
| `npm run build` | `frontend/` | PASS | 0 | Production build passed; Vite emitted chunk-size warning. |
| `npm run test` | `frontend/` | FAIL | 1 | 114 files passed; `src/tests/predictionBands.test.ts` has 2 failures in prediction label/category expectations outside the chat CSS scope. |
| `rg -n "#[0-9A-Fa-f]{3,8}\|rgba?\(\|hsla?\(" src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"` | `frontend/` | PASS | 0 | Hits confined to documented `--chat-*` owner. |
| `rg -n "font-size:\|font-weight:\|line-height:\|letter-spacing:" src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"` | `frontend/` | PASS | 0 | Consumers use tokens or `--chat-*` roles. |
| `rg -n "box-shadow:\|border-radius:\|var\(\s*--[a-zA-Z0-9_-]+\s*," src/pages/ChatPage.css src/features/chat/components -g "*.css" -g "*.tsx"` | `frontend/` | PASS | 0 | Consumers use tokens; no CSS variable literal default. |
| `rg -n "legacy\|Legacy\|alias\|compat\|compatibility\|shim\|fallback\|migration-only" src/pages/ChatPage.css src/features/chat/components` | `frontend/` | PASS | 0 | Existing avatar replacement names and shimmer names classified. |
| After-artifact forbidden vocabulary scan from AC2 | repo root | PASS | 1 | No hits. |
| Final-evidence incomplete-status scan from AC7 | repo root | PASS | 1 | No hits before recording final review metadata. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-081-migrer-cluster-chat-valeurs-visuelles-hardcodees/00-story.md` | repo root | PASS | 0 | CONDAMAD story validation passed with venv active. |
| `.\.venv\Scripts\Activate.ps1; python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-081-migrer-cluster-chat-valeurs-visuelles-hardcodees/00-story.md` | repo root | PASS | 0 | CONDAMAD story lint passed with venv active. |
| `git diff --check` | repo root | PASS | 0 | No whitespace errors; line-ending warnings only. |
| `npm run dev -- --host 127.0.0.1 --port 5176` | `frontend/` | PASS | 0 | Dev server started on `http://127.0.0.1:5176` after port 5173 was occupied. |
| `Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5176 -TimeoutSec 5` | repo root | PASS | 0 | HTTP 200 returned. |

## Commands skipped or blocked

None.

## DRY / No Legacy evidence

- One semantic owner for chat visual values: `.chat-page-container`.
- Namespace `--chat-*` documented in `token-namespace-registry.md`.
- No CSS variable literal default introduced.
- No React, hook, route, API or backend behavior changed.
- Existing avatar replacement class names are non-transitional UI labels.

## Diff review

- Scope reviewed via `git diff --stat` and targeted diff inspection.
- Story changes are limited to expected frontend CSS/test/registry files and CS-081 evidence files, plus status update.
- Pre-existing unrelated dirty files preserved.

## Final worktree status

Final `git status --short`:

```text
 M _condamad/stories/regression-guardrails.md
 M _condamad/stories/story-status.md
 M frontend/src/features/chat/components/ChatComposer.css
 M frontend/src/features/chat/components/ChatPageHeader.css
 M frontend/src/features/chat/components/ChatQuotaBanner.css
 M frontend/src/features/chat/components/ChatWindow.css
 M frontend/src/features/chat/components/ConversationItem.css
 M frontend/src/features/chat/components/ConversationList.css
 M frontend/src/pages/ChatPage.css
 M frontend/src/styles/token-namespace-registry.md
 M frontend/src/tests/design-system-guards.test.ts
?? _condamad/audits/frontend-design-system/2026-05-06-2139/
?? _condamad/stories/CS-081-migrer-cluster-chat-valeurs-visuelles-hardcodees/
```

Notes:

- `_condamad/stories/regression-guardrails.md`, the audit folder and the CS-081
  capsule were already dirty at preflight.
- `story-status.md` was synchronized to `done` for CS-081 during closure.

## Remaining risks

- No story-specific risk identified.
- Repository broad `npm run test` currently has unrelated failures in `src/tests/predictionBands.test.ts`; targeted CS-081 validations and chat tests passed.

## Suggested reviewer focus

- Verify that `--chat-*` is the correct permanent owner for chat-specific glass, message and elevation roles.
- Verify that the CS-081 guard remains strict enough while allowing the owner block.
