# No Legacy / DRY Guardrails

<!-- Garde No Legacy et DRY appliquee a la restauration visuelle /astrologers. -->

## Canonical Owners

| Responsibility | Canonical owner |
|---|---|
| Route composition | `frontend/src/pages/AstrologersPage.tsx` |
| Card markup | `frontend/src/features/astrologers/components/AstrologerCard.tsx` |
| Compact card material | `frontend/src/styles/app/cards.css` |
| Avatar and media relief | `frontend/src/styles/app/media.css` |
| Person/people tokens | `frontend/src/styles/app/tokens.css` |
| Static guards | `frontend/src/tests/design-system-guards.test.ts` |
| Render smoke proof | `frontend/src/tests/visual-smoke.test.tsx` |

## Forbidden Patterns

- active selector or token declaration in `frontend/src/App.css`;
- `.astrologer-card`, `.astrologer-grid`, `.astrologer-card-avatar`, `.astrologer-card-specialties`;
- `compat`, `compatibility`, `legacy`, `alias`, `shim` in active touched frontend style/component surfaces;
- inline `style=`;
- new module under `frontend/src/styles/app/`;
- duplicated card implementation or route behavior changes;
- broad allowlist or wildcard exception.

## Required Negative Evidence

| Pattern | Scope | Expected |
|---|---|---|
| `person-card|people-page|astrologer` | `frontend/src/App.css` | zero hits |
| `astrologer-card|astrologer-grid|compat|compatibility|legacy|alias|shim` | `frontend/src/styles/app frontend/src/pages frontend/src/features/astrologers` | zero active hits |
| `style=` | route and astrologer components | zero hits |
| `rg --files src/styles/app` | app CSS modules | approved filenames only |

## Applicable Guardrails

- `RG-044`, `RG-045`, `RG-047`, `RG-048`, `RG-049`, `RG-050`, `RG-061`, `RG-075`, `RG-076`, `RG-078`, `RG-079`.

## Review Checklist

- One canonical CSS owner per visual responsibility.
- No new selector aliases.
- No `App.css` pollution.
- No duplicated card/component logic.
- Every AC has code and validation evidence.
