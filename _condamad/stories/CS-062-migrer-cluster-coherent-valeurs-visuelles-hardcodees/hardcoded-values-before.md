# CS-062 - Hardcoded values before

Chosen cluster: `frontend/src/components/prediction/PeriodCard.css`.

Reason: prediction card cluster is listed by the story, bounded to one CSS file, and already uses some design tokens.

Representative local values before:
- hardcoded rgba surfaces and borders;
- hardcoded typography sizes `0.7rem`, `0.9rem`, `0.65rem`;
- hardcoded spacing `4px`, `8px`;
- tone colors `#27ae60`, `#d4921a`, `#cc8822`, `#2eaabb`.

Decision: migrate eligible declarations to existing tokens (`--color-*`, `--type-*`, `--space-*`) and `color-mix()` with existing tokens. No new token or role introduced.
