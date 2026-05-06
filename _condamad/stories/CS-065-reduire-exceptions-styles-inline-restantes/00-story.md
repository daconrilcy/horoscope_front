# Story CS-065 reduire-exceptions-styles-inline-restantes: Reduire les exceptions de styles inline restantes

Status: ready-to-dev

## Objective

Reduire les styles inline restants qui peuvent devenir CSS, custom properties typees ou variantes.
Le pass-through `Skeleton.style` reste un contrat public sauf decision explicite de changement d'API.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-0705/03-story-candidates.md#SC-002`
- Reason for change: diminuer les exceptions inline restantes et garder une allowlist exacte.

## Domain Boundary

- Domain: `frontend/src/components`
In scope:
- Classer chaque style inline actuel comme geometrie runtime, pont custom-property, pont couleur ou pass-through style-prop.
- Convertir les styles convertibles dans les CSS existants des composants et layouts cibles.
- Preserver `Skeleton.style` tant que l'API publique ne change pas.
- Synchroniser `frontend/src/tests/inline-style-allowlist.ts` et `frontend/src/tests/design-system-allowlist.ts`.

Out of scope:
- Refonte globale des composants UI.
- Suppression du prop public `style` de `Skeleton`.
- Migration des fallbacks CSS, selectors legacy ou valeurs hardcodees hors styles inline cibles.

Explicit non-goals:
  - Ne pas changer `RG-047` ni `RG-050`.
  - Ne pas remplacer un style inline par un autre style inline equivalent.
  - Ne pas ajouter de logique metier dans les composants UI.

## Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: les exceptions inline doivent etre traitees par lots independants avec mapping old surface vers surface canonique.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les largeurs, couleurs et custom properties runtime doivent produire le meme rendu observable.
  - Les seules differences autorisees sont la baisse des exceptions inline et la mise a jour des allowlists.
- Deletion allowed: yes
- Replacement allowed: yes
- User decision required if: la reduction exige de supprimer ou modifier le contrat public `Skeleton.style`.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | l'AST guard Vitest est la source runtime-equivalente des exceptions inline actives |
| Baseline Snapshot | yes | un inventaire before/after est requis pour chaque exception inline |
| Ownership Routing | no | aucun ownership cross-layer n'est deplace; les CSS composants restent owners |
| Allowlist Exception | yes | les exceptions inline restantes doivent rester exactes dans les allowlists |
| Contract Shape | no | aucun type public ne doit changer; `Skeleton.style` est preserve |
| Batch Migration | yes | chaque style inline convertible doit etre mappe vers CSS, variable typee ou variante |
| Reintroduction Guard | yes | le guard inline-style doit bloquer les styles statiques non classes |
| Persistent Evidence | yes | le classement before/after des exceptions doit rester dans le dossier de story |

## Runtime Source of Truth

- Primary source of truth:
  - AST guard `frontend/src/tests/inline-style-policy.test.ts` execute par Vitest.
  - AST guard `frontend/src/tests/design-system-guards.test.ts` execute par Vitest.
- Secondary evidence:
  - `rg -n "style=\\{" src -g "*.tsx"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - les styles inline restants doivent etre compares aux allowlists executables.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-065-reduire-exceptions-styles-inline-restantes/inline-styles-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-065-reduire-exceptions-styles-inline-restantes/inline-styles-after.md`
- Expected invariant:
  - les cas conserves doivent etre classes avec raison exacte; le nombre d'exceptions convertibles doit baisser.

## Ownership Routing Rule

- Ownership routing: not applicable
- Reason: the story keeps each component/layout CSS as owner and does not move responsibilities across application layers.

## Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/inline-style-allowlist.ts` | `style-prop` | API publique `Skeleton.style` | permanent tant que le contrat public `SkeletonProps.style` existe |
| `frontend/src/tests/inline-style-allowlist.ts` | dynamic CSS property bridge | valeurs runtime par props | sortie: migration CSS/variant sans perte dynamique |
| `frontend/src/tests/design-system-allowlist.ts` | mirrored inline exceptions | garde design-system exact | condition de sortie: suppression quand l'entree source disparait |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected. `Skeleton.style` must remain unchanged.

## Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| sidebar width | `TwoColumnLayout.tsx` | CSS bridge/class | `TwoColumnLayout` | `npm run test -- inline-style` | scan `style={` | width not preserved |
| score width | `DomainRankingCard.tsx` | CSS bridge/class | `DomainRankingCard` | `npm run test -- inline-style` | scan `style={` | dynamic width lost |
| period accent | `DayTimelineSectionV4.tsx` | CSS variable if dynamic | timeline section | `npm run test -- inline-style` | exact allowlist | accent is runtime |
| badge color | `Badge.tsx` | variant or CSS variable | `Badge` | `npm run test -- inline-style` | no inline background | public API needs inline |
| skeleton style | `Skeleton.tsx` | preserve style-prop | `Skeleton` | `npm run test -- inline-style` | exact allowlist | API change required |

## Persistent Evidence Artifacts

The implementation must persist these evidence artifacts:

| Artifact | Path | Purpose |
|---|---|---|
| inline baseline | `_condamad/stories/CS-065-reduire-exceptions-styles-inline-restantes/inline-styles-before.md` | classifier chaque style inline avant migration |
| inline result | `_condamad/stories/CS-065-reduire-exceptions-styles-inline-restantes/inline-styles-after.md` | prouver les conversions et exceptions restantes |

## Reintroduction Guard

The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.

Required forbidden examples:

- style inline statique non allowliste
- `style={{ background: color }}` si `Badge` est migre vers CSS/variable
- `style={{ width: value }}` si `DomainRankingCard` est migre vers CSS/variable

Guard evidence:

- Evidence profile: `reintroduction_guard`; `npm run test -- inline-style design-system` checks exact inline exceptions.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-0705/03-story-candidates.md#SC-002` - demande la classification de chaque style inline restant.
- Evidence 2: `frontend/src/tests/inline-style-allowlist.ts` - allowlist dynamique exacte actuelle.
- Evidence 3: `frontend/src/tests/design-system-allowlist.ts` - miroir executable des exceptions inline.
- Evidence 4: `frontend/src/components/DomainRankingCard.tsx`, `frontend/src/components/ui/Badge/Badge.tsx` - styles inline detectes.
- Evidence 5: `frontend/src/components/ui/Skeleton/Skeleton.tsx`, `frontend/src/layouts/TwoColumnLayout.tsx` - styles inline detectes.
- Evidence 6: `_condamad/stories/regression-guardrails.md` - invariants `RG-047` et `RG-050` consultes avant cadrage.

## Target State

- Les styles inline convertibles sont deplaces dans les CSS existants ou exprimes par ponts custom properties exacts.
- Les exceptions restantes sont classees et justifiees dans les deux allowlists.
- Le contrat `Skeleton.style` reste disponible sans migration implicite de l'API publique.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - les styles inline statiques sont interdits hors exceptions exactes.
  - `RG-050` - les allowlists design-system restent executees.
- Non-applicable invariants:
  - `RG-048` - aucun fallback CSS n'est cible.
  - `RG-049` - aucun selector legacy n'est cible.
- Required regression evidence:
  - `npm run test -- inline-style design-system`
  - scan `rg -n "style=\\{" src -g "*.tsx"`
- Allowed differences:
  - le nombre d'exceptions inline peut baisser; les exceptions dynamiques restantes doivent rester exactes.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline classe chaque style inline restant. | Evidence profile: `baseline_before_after_diff`; AST guard `npm run test -- inline-style` + scan `style={` |
| AC2 | Les styles convertibles migrent vers CSS ou variante. | Evidence profile: `batch_migration_mapping`; AST guard `npm run test -- inline-style design-system` |
| AC3 | `Skeleton.style` reste preserve ou bloque pour decision API. | Evidence profile: `frontend_typecheck_no_orphan`; AST guard `npm run test -- inline-style design-system` |
| AC4 | Les deux allowlists ne gardent que les exceptions exactes. | Evidence profile: `allowlist_register_validated`; `npm run test -- inline-style design-system` |
| AC5 | Aucun nouveau style inline statique non classe n'est introduit. | Evidence profile: `reintroduction_guard`; `rg -n "style=\\{" src` + `npm run test -- inline-style` |

## Implementation Tasks

- [ ] Task 1 - Capturer et classifier l'inventaire before des styles inline. (AC: AC1)
- [ ] Task 2 - Migrer les lots convertibles vers les CSS existants ou des custom properties typees. (AC: AC2)
- [ ] Task 3 - Preserver ou documenter explicitement les exceptions runtime `Skeleton` sans changer son API publique. (AC: AC3)
- [ ] Task 4 - Synchroniser les deux allowlists apres les changements de code. (AC: AC4)
- [ ] Task 5 - Capturer l'inventaire after et executer les guards inline/design-system. (AC: AC1, AC4, AC5)

## Mandatory Reuse / DRY Constraints

- Reuse:
  - les fichiers CSS existants `TwoColumnLayout.css`, `DomainRankingCard.css`, `DayTimelineSectionV4.css`, `Badge.css`, `Skeleton.css`.
  - `frontend/src/tests/inline-style-allowlist.ts` et `frontend/src/tests/design-system-allowlist.ts`.
- Do not recreate:
  - un registre parallele de styles inline.
  - une variante locale de `Badge` ou `Skeleton` qui duplique le composant existant.
- Shared abstraction allowed only if:
  - au moins deux composants partagent une responsabilite identique et aucun composant UI existant ne couvre ce besoin.

## No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- duplicate active implementations
- silent fallback behavior
- preserving old path through re-export

Specific forbidden symbols / paths:

- nouveau `style={{ value }}` statique non allowliste.
- suppression silencieuse de `SkeletonProps.style`.
- nouvelle surface legacy ou compatibility pour contourner la migration CSS.

## Removal Classification Rules

- Removal classification: not applicable

## Removal Audit Format

- Removal audit: not applicable

## Canonical Ownership

- Canonical ownership: not applicable

## Delete-Only Rule

- Delete-only rule: not applicable

## External Usage Blocker

- External usage blocker: not applicable

## Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## Files to Inspect First

- `frontend/src/layouts/TwoColumnLayout.tsx`
- `frontend/src/layouts/TwoColumnLayout.css`
- `frontend/src/components/DomainRankingCard.tsx`
- `frontend/src/components/DomainRankingCard.css`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/prediction/DayTimelineSectionV4.css`
- `frontend/src/components/ui/Badge/Badge.tsx`
- `frontend/src/components/ui/Badge/Badge.css`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx`
- `frontend/src/components/ui/Skeleton/Skeleton.css`
- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-allowlist.ts`

## Expected Files to Modify

Likely files:

- `frontend/src/layouts/TwoColumnLayout.tsx` - reduire ou reclasser le pont `--sidebar-width`.
- `frontend/src/layouts/TwoColumnLayout.css` - porter la regle CSS associee.
- `frontend/src/components/DomainRankingCard.tsx` - remplacer la largeur inline si faisable.
- `frontend/src/components/DomainRankingCard.css` - porter la largeur score.
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx` - reclasser ou reduire `--period-accent`.
- `frontend/src/components/prediction/DayTimelineSectionV4.css` - porter les styles de periode.
- `frontend/src/components/ui/Badge/Badge.tsx` - migrer `background` vers variante ou variable si faisable.
- `frontend/src/components/ui/Badge/Badge.css` - porter le style badge.
- `frontend/src/components/ui/Skeleton/Skeleton.tsx` - ne modifier que si le pont `--skeleton-gap` peut etre type sans changer l'API.
- `frontend/src/components/ui/Skeleton/Skeleton.css` - porter les styles skeleton.
- `frontend/src/tests/inline-style-allowlist.ts` - synchroniser les exceptions.
- `frontend/src/tests/design-system-allowlist.ts` - synchroniser le miroir.

Likely tests:

- `frontend/src/tests/inline-style-policy.test.ts` - guard principal.
- `frontend/src/tests/design-system-guards.test.ts` - synchronisation allowlists.

Files not expected to change:

- `backend/` - aucun contrat backend n'est touche.
- `frontend/src/styles/css-fallback-allowlist.md` - aucun fallback CSS n'est dans le scope.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- inline-style design-system
npm run lint
rg -n "style=\{" src -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-065-reduire-exceptions-styles-inline-restantes/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-065-reduire-exceptions-styles-inline-restantes/00-story.md
```

## Regression Risks

- Risk: perte de comportement dynamique pour largeur, couleur ou accent runtime.
  - Guardrail: batch evidence before/after et tests inline/design-system.
- Risk: modification involontaire de l'API publique `Skeleton`.
  - Guardrail: AC3 bloque la suppression sans decision explicite.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-0705/03-story-candidates.md#SC-002` - source du candidat.
- `_condamad/stories/regression-guardrails.md` - invariants `RG-047` et `RG-050`.
- `frontend/src/tests/inline-style-allowlist.ts` - allowlist inline.
- `frontend/src/tests/design-system-allowlist.ts` - miroir design-system.
