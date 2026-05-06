# CS-063 - Legacy style after

No deletion performed.

Reason:
- Admin prompt selectors are still classified `external-active` in `frontend/src/styles/legacy-style-surface-registry.md`; the story forbids deleting them without an explicit user/product decision.
- Compatibility aliases `--text-*`, `--glass*`, and `--primary*` still have broad active consumers in `frontend/src/App.css`; deleting them would exceed the bounded route-specific scope and break runtime styling.

Final classification:
- `.admin-prompts-legacy*`: kept, external-active.
- `.admin-prompts-modal--legacy-rollback`: kept, external-active.
- `--text-*`: kept, compatibility with active consumers.
- `--glass*`: kept, compatibility with active consumers.
- `--primary*`: kept, compatibility with active consumers.

Recommended next story:
- Migrate `App.css` aliases to `--color-*` in a dedicated app-shell token convergence story.
- Then revisit alias deletion and registry shrink.
