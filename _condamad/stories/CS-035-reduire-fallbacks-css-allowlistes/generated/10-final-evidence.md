<!-- Preuve finale CONDAMAD pour CS-035. -->

# CS-035 Final Evidence

Status: done

AC status:

- AC1 PASS: lot inventorie dans `css-fallbacks-before.md`.
- AC2 PASS: fallbacks de tokens requis retires du lot.
- AC3 PASS: `css-fallback-allowlist.md` clarifie l'exception `--color-bg-surface`.
- AC4 PASS: `CSS_FALLBACK_EXCEPTIONS` synchronise avec le scan reel.
- AC5 PASS: guards css-fallback/design-system passent.
- AC6 PASS: lint frontend passe.

Files changed:

- `frontend/src/components/ui/Select/Select.css`
- `frontend/src/components/ui/UserMenu/UserMenu.css`
- `frontend/src/styles/css-fallback-allowlist.md`
- `frontend/src/tests/design-system-allowlist.ts`
- `_condamad/stories/CS-035-reduire-fallbacks-css-allowlistes/css-fallbacks-before.md`
- `_condamad/stories/CS-035-reduire-fallbacks-css-allowlistes/css-fallbacks-after.md`

Validation:

- `rg -n "var\(\s*--[A-Za-z0-9_-]+\s*," src/components/ui/Select/Select.css src/components/ui/UserMenu/UserMenu.css` - PASS, seulement deux exceptions classees.
- `npm run test -- inline-style css-fallback design-system` - PASS.
- `npm run lint` - PASS.
- `npm run test` - PASS.

Legacy / DRY:

- Pas de nouvelle allowlist parallele.
- Pas de fallback literal pour token requis conserve dans `UserMenu.css`.

Remaining risks:

- Aucun risque restant identifie.
