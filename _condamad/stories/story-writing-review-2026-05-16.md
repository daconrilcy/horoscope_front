# Review redactionnelle des stories CS-175 a CS-178

Date: 2026-05-16

## Scope

- `_condamad/stories/CS-175-creer-runtime-canonique-signes/00-story.md`
- `_condamad/stories/CS-176-calculer-signature-balance-theme/00-story.md`
- `_condamad/stories/CS-177-finaliser-i18n-astrologique-backend/00-story.md`
- `_condamad/stories/CS-178-documenter-zodiaque-ayanamsa-runtime/00-story.md`
- `_condamad/stories/story-status.md`

## Review Cycle 1

Findings:

- Contract sections marked active still contained not-applicable wording.
- Some AC evidence was too vague.
- CS-177 removed local mappings and therefore had to use a removal archetype.
- CS-178 needed a baseline and persistent evidence for the documentation guard.

Corrections:

- Rewrote active contract sections.
- Added concrete pytest and `rg` evidence.
- Reclassified CS-177 as `dead-code-removal`.
- Added baseline artifacts to CS-178.

## Review Cycle 2

Findings:

- Strict lint detected template placeholders, long lines and optional vague wording.
- Removal guard in CS-177 needed deterministic forbidden-symbol evidence.
- Some AC rows were compound.

Corrections:

- Removed placeholder syntax and ellipses.
- Split long lines.
- Added `forbidden symbols` to CS-177 reintroduction guard.
- Simplified AC requirements to one invariant per row.

## Final Verdict

No remaining redaction issue found after validation.

Required final checks:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py <story>
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict <story>
```
