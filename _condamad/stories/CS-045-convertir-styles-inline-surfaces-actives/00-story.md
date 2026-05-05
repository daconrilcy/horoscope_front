# Story CS-045 convertir-styles-inline-surfaces-actives: Convertir ou justifier 100% des styles inline actifs

Status: ready-to-dev

## 1. Objective

Traiter a 100% les 16 attributs `style=` actifs listes par l'audit `2026-05-05-1831`.
Chaque occurrence doit migrer vers CSS si elle est statique ou rester comme exception runtime exacte.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1831/03-story-candidates.md#SC-002`
- Reason for change: le finding `F-003` mesure 16 styles inline restants dans 10 fichiers, ce qui reste une exception a la regle projet "aucun style inline".

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src`
- In scope:
  - Traiter les 10 fichiers audites listes dans `F-003 - Inline Style Debt`.
  - Classer 100% des occurrences comme `static`, `dynamic-custom-property`, `runtime-geometry` ou `style-prop-bridge`.
  - Migrer toute occurrence `static` vers CSS adjacent ou existant.
  - Synchroniser `INLINE_STYLE_EXCEPTIONS` et les guards design-system.
- Out of scope:
  - Fallbacks CSS `var(--token, value)`.
  - Migration generale des hardcoded values hors attributs `style`.
  - Changement d'API publique des composants.
  - Refonte visuelle.
- Explicit non-goals:
  - Ne pas affaiblir `RG-047` ou `RG-050`.
  - Ne pas remplacer un style statique par une constante TSX.
  - Ne pas conserver un `style` statique sous pretexte d'allowlist.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot exhaustif d'occurrences inline actives vers CSS ou exceptions exactes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu doit rester equivalent.
  - Les valeurs runtime peuvent rester inline seulement avec classification et preuve.
  - Les composants touches ne changent pas d'API publique.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une occurrence ne peut pas etre classee sans arbitrage UX ou contrat public.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Le guard inline-style observe les occurrences TSX actives. |
| Baseline Snapshot | yes | Les 16 occurrences doivent etre comparees before/after. |
| Ownership Routing | yes | Les styles statiques doivent etre routes vers CSS, les dynamiques vers allowlist exacte. |
| Allowlist Exception | yes | Les exceptions restantes doivent etre exactes. |
| Contract Shape | no | Aucun API, DTO, payload, export ou type public n'est modifie. |
| Batch Migration | yes | Le scope couvre les 10 surfaces TSX auditees. |
| Reintroduction Guard | yes | Les styles inline statiques ne doivent pas revenir. |
| Persistent Evidence | yes | Les classifications before/after doivent etre persistantes. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/inline-style-policy.test.ts`
  - AST guard Vitest: `frontend/src/tests/design-system-guards.test.ts`
- Secondary evidence:
  - `frontend/src/tests/inline-style-allowlist.ts`
  - `frontend/src/tests/design-system-allowlist.ts`
  - Scan `rg -n "style=" src -g "*.tsx"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - Ils ne prouvent pas si une occurrence restante est statique ou runtime-driven.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-045-convertir-styles-inline-surfaces-actives/inline-styles-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-045-convertir-styles-inline-surfaces-actives/inline-styles-after.md`
- Expected invariant:
  - Les 16 occurrences initiales sont toutes classifiees et les statiques sont supprimees de TSX.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Style statique | CSS adjacent ou feuille existante de la surface | attribut `style` TSX |
| Valeur runtime dynamique | occurrence allowlistee exacte | classe CSS qui masque une valeur runtime |
| Garde inline-style | `inline-style-policy.test.ts` | verification manuelle seule |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/inline-style-allowlist.ts` | exceptions dynamiques | Valeur runtime, geometrie ou bridge public. | Permanent while runtime input exists. |
| `frontend/src/tests/design-system-allowlist.ts` | exceptions design-system | Parite executable globale. | Must match exact retained exceptions. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| Inline active surface | `style=` in 10 TSX files | CSS or exact exception | selected TSX/CSS | inline tests | scan + diff | ambiguous class |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `_condamad/stories/CS-045-convertir-styles-inline-surfaces-actives/inline-styles-before.md` | Classer les 16 occurrences avant edition. |
| After inventory | `_condamad/stories/CS-045-convertir-styles-inline-surfaces-actives/inline-styles-after.md` | Prouver les suppressions et exceptions restantes. |
| Executable allowlists | `frontend/src/tests/inline-style-allowlist.ts`, `frontend/src/tests/design-system-allowlist.ts` | Garder les exceptions exactes. |

## 4i. Reintroduction Guard

- Guard target: `style=` statique non allowliste ou exception statique conservee.
- Architecture guard against reintroduction required: `frontend/src/tests/inline-style-policy.test.ts` doit echouer si une occurrence non classee reapparait.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- inline-style design-system`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1831/02-finding-register.md#F-003` - 16 attributs `style=` restent dans 10 fichiers.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1831/00-audit-report.md#F-003---Inline-Style-Debt-10-Files` - liste exhaustive des fichiers candidats.
- Evidence 3: `frontend/src/tests/inline-style-allowlist.ts` - allowlist specialisee des styles inline.
- Evidence 4: `frontend/src/tests/design-system-allowlist.ts` - allowlist globale design-system.
- Evidence 5: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Aucune occurrence statique ne reste en style inline dans les 10 fichiers audites.
- Les exceptions restantes sont dynamiques, exactes et justifiees.
- Les CSS adjacents portent les styles statiques migres.
- Les tests prouvent que le guard inline-style reste strict.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - les styles inline statiques sont interdits hors allowlist exacte.
  - `RG-050` - la suite anti-drift design-system doit rester executable.
- Non-applicable invariants:
  - `RG-044` - aucun namespace token n'est cree par defaut.
  - `RG-045` - les hardcoded values hors inline ne sont pas le domaine principal.
  - `RG-046` - la typographie n'est touchee que si elle est inline statique.
  - `RG-048` - les fallbacks CSS ne sont pas touches.
  - `RG-049` - aucun selecteur legacy n'est cree.
- Required regression evidence:
  - `npm run test -- inline-style design-system`, scan `rg -n "style=" src -g "*.tsx"`, `npm run lint`.
- Allowed differences:
  - Retrait d'attributs `style` statiques et ajout de classes CSS equivalentes.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Baseline des 16 occurrences avec fichier exact. | Evidence profile: `baseline_before_after_diff`; `rg -n "frontend/src/.*\\.tsx" inline-styles-before.md`. |
| AC2 | Chaque occurrence a une classification finale. | Evidence: `rg -n "unclassified|TODO|TBD" inline-styles-after.md` zero-hit. |
| AC3 | Toutes les occurrences `static` migrent vers CSS adjacent ou existant. | Evidence profile: `targeted_forbidden_symbol_scan`; scan cible: `rg -n "style=" src -g "*.tsx"`. |
| AC4 | Les exceptions restantes sont synchronisees dans les allowlists. | Evidence profile: `allowlist_register_validated`; `npm run test -- inline-style design-system`. |
| AC5 | Aucun nouveau style inline non classe n'est introduit ailleurs. | Evidence: AST guard `inline-style-policy.test.ts`; `npm run test -- inline-style`. |
| AC6 | Le frontend reste lintable. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer et classer les 16 occurrences initiales (AC: AC1, AC2)
- [ ] Task 2 - Migrer toutes les occurrences `static` vers CSS adjacent ou existant (AC: AC3)
- [ ] Task 3 - Synchroniser `inline-style-allowlist.ts` et `design-system-allowlist.ts` avec les exceptions dynamiques restantes (AC: AC4)
- [ ] Task 4 - Adapter les CSS/tests des composants touches si une classe visible change (AC: AC3, AC6)
- [ ] Task 5 - Capturer l'inventaire after et les scans cibles (AC: AC2, AC3, AC5)
- [ ] Task 6 - Executer lint et guards frontend (AC: AC4, AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Fichiers CSS adjacents ou existants des composants/pages touches.
  - Variables CSS deja presentes avant d'en creer de nouvelles.
  - `frontend/src/tests/inline-style-policy.test.ts`.
  - `frontend/src/tests/inline-style-allowlist.ts`.
  - `frontend/src/tests/design-system-allowlist.ts`.
- Do not recreate:
  - Une deuxieme allowlist inline-style.
  - Des constantes TSX pour styles statiques.
  - Une classe globale pour un style strictement local.
- Shared abstraction allowed only if:
  - Elle supprime une duplication exacte entre plusieurs surfaces du meme domaine et reste documentee.

## 10. No Legacy / Forbidden Paths

Forbidden unless explicitly approved:

- compatibility wrappers
- transitional aliases
- legacy imports
- duplicate active implementations
- silent fallback behavior
- root-level service when canonical namespace exists
- preserving old path through re-export

Specific forbidden symbols / paths:

- `style=` statique dans les 10 fichiers audites.
- Entree d'allowlist statique conservee sans blocker explicite.
- Nouveau `style` ajoute dans un fichier hors lot.
- Style statique deplace vers constante TSX au lieu de CSS.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Styles statiques | CSS adjacent ou feuille existante de la surface | attribut `style` |
| Exceptions dynamiques | allowlists inline/design-system | exception implicite |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/tests/inline-style-allowlist.ts`
- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/components/DomainRankingCard.tsx`
- `frontend/src/components/prediction/CategoryGrid.tsx`
- `frontend/src/components/prediction/DayPredictionCard.tsx`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/prediction/TimelineRail.tsx`
- `frontend/src/components/TurningPointCard.tsx`
- `frontend/src/components/ui/Badge/Badge.tsx`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx`
- `frontend/src/features/chat/components/AstrologerPickerModal.tsx`
- `frontend/src/layouts/TwoColumnLayout.tsx`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/tests/inline-style-allowlist.ts` - reduction/synchronisation des exceptions.
- `frontend/src/tests/design-system-allowlist.ts` - synchronisation globale.
- Les 10 fichiers TSX listes dans `Files to Inspect First` - retrait des styles statiques.
- Fichiers CSS adjacents correspondants - classes de remplacement.
- `_condamad/stories/CS-045-convertir-styles-inline-surfaces-actives/inline-styles-before.md` - baseline.
- `_condamad/stories/CS-045-convertir-styles-inline-surfaces-actives/inline-styles-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/inline-style-policy.test.ts` - garde principale.
- `frontend/src/tests/design-system-guards.test.ts` - garde design-system.
- Tests composants existants des surfaces touchees si presents.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/styles/css-fallback-allowlist.md` - hors scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- inline-style design-system
rg -n "style=" src -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-045-convertir-styles-inline-surfaces-actives/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-045-convertir-styles-inline-surfaces-actives/00-story.md
```

## 22. Regression Risks

- Risk: une valeur runtime est migree a tort en CSS.
  - Guardrail: classification obligatoire et blocker si ambigu.
- Risk: une exception statique reste allowlistee.
  - Guardrail: AC2 et `npm run test -- inline-style`.
- Risk: la story reste partielle.
  - Guardrail: AC1 exige les 16 occurrences et AC2 interdit tout item non classe.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Respect the project rule: no inline style for static styling.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-05-1831/03-story-candidates.md#SC-002` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1831/02-finding-register.md#F-003` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1831/00-audit-report.md` - liste exhaustive des fichiers candidats.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
