# Dev Log

## Preflight

- Initial `git status --short` showed pre-existing dirty entries:
  `_condamad/stories/regression-guardrails.md`,
  `_condamad/audits/prompt-generation/`,
  `_condamad/stories/converge-horoscope-daily-narration-assembly/`, and
  `_condamad/stories/formalize-consultation-guidance-prompt-ownership/`.
- `AGENTS.md` read and applied.
- Regression guardrails read; `RG-006`, `RG-016`, `RG-017`, and `RG-019` treated
  as applicable evidence.
- `condamad_prepare.py` initially generated a title-derived duplicate capsule; its
  generated files were copied into the requested capsule and the duplicate folder was
  removed.

## Implementation notes

- Captured `_condamad/stories/converge-horoscope-daily-narration-assembly/prompt-builder-before.md`.
- Removed durable narration instructions from `AstrologerPromptBuilder`.
- Added `HOROSCOPE_DAILY_NARRATION_PROMPT` and `HOROSCOPE_DAILY_PLAN_RULES` to
  `seed_horoscope_narrator_assembly.py`.
- Added `horoscope_daily_free_narration` and `horoscope_daily_premium_narration`
  to `PLAN_RULES_REGISTRY`.
- Captured `_condamad/stories/converge-horoscope-daily-narration-assembly/prompt-builder-after.md`.
- `pytest -q` modified `backend/horoscope.db`; it was restored because it was a
  validation side effect and outside story scope.

## Validation notes

- Targeted tests passed.
- Ruff format/check passed after formatting three touched files.
- Full `pytest -q` initially timed out after 10 minutes in the Codex run, then
  the user provided a successful rerun: `3496 passed, 12 skipped in 737.63s`.
  Completion is now `PASS`.
- A post-implementation story status change to `ready-for-review` made the local
  CONDAMAD story validator fail because this story format requires
  `Status: ready-for-dev`; the status field was restored and the final review
  status is recorded in `10-final-evidence.md`.
