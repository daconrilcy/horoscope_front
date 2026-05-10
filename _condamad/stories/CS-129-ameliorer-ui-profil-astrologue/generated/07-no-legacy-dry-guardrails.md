# No Legacy / DRY Guardrails

## Applicable guardrails

- `RG-044` through `RG-050`: token namespaces, visual literals, inline styles, CSS fallbacks, legacy styles and design-system guards must remain intact.
- `RG-064`: page architecture guards must remain valid.
- `RG-068`: route ownership must remain under the existing layout hierarchy.
- `RG-078`: `frontend/src/App.css` must not receive profile-specific styles.
- `RG-079`: `/astrologers` compact list relief must not regress.
- `RG-080`: `/astrologers/:id` profile invariant must be established and preserved.

## Forbidden patterns

- Active profile-specific styles in `frontend/src/App.css`.
- Inline `style=` in `AstrologerProfilePage.tsx` or `AstrologerProfileSections.tsx`.
- `overflow-x: hidden` as a blunt fix in `AstrologerProfilePage.css`.
- Compatibility wrapper, alias, shim, fallback, legacy route or duplicate profile component.
- New `astrologer-card` or `astrologer-grid` selectors for this profile story.
- API, route or payload changes.

## Required negative evidence

- Zero hit for `rg -n "AstrologerProfile|profile-" src/App.css`.
- Zero hit for `rg -n "style=" src/pages/AstrologerProfilePage.tsx src/features/astrologers/components/AstrologerProfileSections.tsx`.
- Zero hit for `rg -n "overflow-x:\s*hidden" src/pages/AstrologerProfilePage.css`.
- Bounded zero active hit for `astrologer-card|astrologer-grid|compat|compatibility|legacy|alias|shim` in touched profile files.

## DRY stance

- Reuse `handleConsultationCta`, `handleChatCta`, `handleNatalCta`.
- Extend existing profile section components instead of creating duplicate sections.
- Reuse existing `Button`, lucide icons, page-local `--profile-*` variables and global tokens.
- Keep new visible strings in `frontend/src/i18n/astrologers.ts`.

## Review checklist

- CTA destinations are unchanged.
- Empty public reviews do not display a primary non-zero public rating with `0 avis`.
- Metrics use one value/label/helper structure.
- Mobile CTA is quickly reachable without App.css or inline styles.
- Tests and scans cover the new invariant.
