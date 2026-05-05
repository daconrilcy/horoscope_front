# Story CS-041 convertir-styles-inline-statiques-restants-css: Convertir les styles inline statiques restants vers CSS

Status: done

## 1. Objective

Convertir les styles inline statiques restants du lot audite vers les fichiers CSS appropries.
Seules les exceptions dynamiques justifiees par le runtime, la geometrie calculee ou un bridge public restent inline.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-05-1748/03-story-candidates.md#SC-002`
- Reason for change: le finding `F-003` indique que 30 attributs `style` restent dans 17 fichiers TSX et que des entrees statiques sont encore preservees par l'allowlist.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src`
- In scope:
  - Inventorier les 30 attributs `style` restants.
  - Classer chaque occurrence touchee comme `static`, `dynamic-custom-property`, `runtime-geometry` ou `style-prop-bridge`.
  - Migrer toutes les occurrences `static` vers CSS.
  - Reduire `INLINE_STYLE_EXCEPTIONS` aux exceptions dynamiques justifiees.
  - Ajouter ou adapter les tests des surfaces touchees quand une classe ou structure visible change.
- Out of scope:
  - Migration des fallbacks CSS `var(--token, value)`.
  - Migration generale des hardcoded values hors styles inline.
  - Refonte visuelle des pages ou composants.
  - Changement d'API publique des composants.
- Explicit non-goals:
  - Ne pas affaiblir `RG-047` ou `RG-050`.
  - Ne pas ajouter de nouveau `style` statique.
  - Ne pas deplacer une decision statique vers une constante TSX au lieu de CSS.
  - Ne pas transformer un style dynamique en classe CSS si la valeur depend du runtime.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre un lot borne d'exceptions inline vers les surfaces CSS canoniques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le rendu attendu des surfaces touchees doit rester equivalent.
  - Les exceptions dynamiques peuvent rester inline uniquement avec classification et raison.
  - Les classes ajoutees doivent vivre dans les CSS existants ou adjacents appropries.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une occurrence ne peut pas etre classee sans arbitrage UX ou contrat public.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde Vitest inline-style observe les occurrences TSX effectives. |
| Baseline Snapshot | yes | Les 30 occurrences doivent etre comparees avant/apres. |
| Ownership Routing | yes | Les styles statiques doivent etre routes vers CSS, les dynamiques vers allowlist exacte. |
| Allowlist Exception | yes | Les exceptions inline restantes doivent etre exactes. |
| Contract Shape | no | Aucun contrat API, DTO, payload, export ou type public n'est modifie. |
| Batch Migration | yes | Le scope couvre plusieurs surfaces TSX auditees. |
| Reintroduction Guard | yes | Les styles inline statiques ne doivent pas revenir. |
| Persistent Evidence | yes | Les classifications before/after doivent etre persistantes. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard Vitest: `frontend/src/tests/inline-style-policy.test.ts`.
  - Allowlist executable: `frontend/src/tests/design-system-allowlist.ts`.
- Secondary evidence:
  - Scan `rg -n "style=\\{" src -g "*.tsx"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - La garde doit verifier que chaque occurrence restante est classee et allowlistee exactement.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-041-convertir-styles-inline-statiques-restants-css/inline-styles-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-041-convertir-styles-inline-statiques-restants-css/inline-styles-after.md`
- Expected invariant:
  - Toute occurrence statique du lot est supprimee de TSX et aucune occurrence non classee n'apparait.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Style statique de composant/page | fichier `.css` ou `.scss` approprie existant/adjacent | attribut `style` TSX |
| Valeur runtime dynamique | `style` allowliste dans `INLINE_STYLE_EXCEPTIONS` | classe CSS trompeuse |
| Garde inline-style | `frontend/src/tests/inline-style-policy.test.ts` | controle manuel |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/tests/design-system-allowlist.ts` | `INLINE_STYLE_EXCEPTIONS` dynamiques | Valeur runtime ou bridge public. | Permanent while the runtime input exists. |
| `frontend/src/tests/design-system-allowlist.ts` | anciennes exceptions statiques | Dette a migrer. | Doit disparaitre apres migration. |

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
| Inline style batch | `style={` static TSX | CSS adjacent | 17 TSX files | `npm run test -- inline-style design-system` | scan + allowlist diff | ambiguous classification |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before inventory | `_condamad/stories/CS-041-convertir-styles-inline-statiques-restants-css/inline-styles-before.md` | Classer les 30 occurrences avant edition. |
| After inventory | `inline-styles-after.md` | Prouver les suppressions, exceptions restantes et deltas. |
| Executable allowlist | `frontend/src/tests/design-system-allowlist.ts` | Documenter les exceptions dynamiques restantes. |

## 4i. Reintroduction Guard

- Guard target: `style={` statique non allowliste ou exception statique conservee.
- Architecture guard required: `frontend/src/tests/inline-style-policy.test.ts` doit echouer si une occurrence non classee ou statique reapparait.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- inline-style design-system`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-05-1748/02-finding-register.md#F-003` - 30 attributs `style` restent dans 17 fichiers TSX.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-05-1748/03-story-candidates.md#SC-002` - la liste des fichiers TSX candidats est fournie.
- Evidence 3: `frontend/src/tests/design-system-allowlist.ts` - `INLINE_STYLE_EXCEPTIONS` porte les exceptions executables.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les styles statiques du lot vivent dans des fichiers CSS appropries.
- `INLINE_STYLE_EXCEPTIONS` ne conserve que les exceptions dynamiques justifiees.
- Les scans et tests prouvent qu'aucun style inline statique non classe n'est actif.
- Les composants/pages touches gardent leur comportement et leur rendu attendu.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047` - les styles inline statiques sont interdits hors allowlist exacte.
  - `RG-050` - la suite anti-drift design-system doit rester executable.
- Non-applicable invariants:
  - `RG-044` - les tokens peuvent etre reutilises mais aucun namespace token n'est cree par defaut.
  - `RG-045` - les hardcoded values hors inline ne sont pas le domaine principal.
  - `RG-046` - la typographie n'est migree que si elle est dans un inline statique touche.
  - `RG-048` - les fallbacks CSS ne sont pas touches.
  - `RG-049` - aucun selecteur legacy n'est cree.
- Required regression evidence:
  - `npm run test -- inline-style design-system`, scan `rg -n "style=\\{" src -g "*.tsx"`, `npm run lint`.
- Allowed differences:
  - Retrait d'attributs `style` statiques et ajout de classes CSS equivalentes.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les 30 occurrences initiales ont une classification. | Evidence profile: `baseline_before_after_diff`; command: `rg -n "static|dynamic" inline-styles-before.md`. |
| AC2 | Les occurrences `static` du lot sont migrees vers CSS. | Evidence profile: `targeted_forbidden_symbol_scan`; command: `rg -n "style=\\{" src -g "*.tsx"`. |
| AC3 | Les exceptions restantes sont dynamiques. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- inline-style`; AST guard. |
| AC4 | Les CSS appropries reutilisent les variables/classes existantes. | Evidence profile: `component_behavior_test`; command: `npm run test -- inline-style design-system`. |
| AC5 | Aucun nouveau `style` non classe n'est introduit. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system inline-style`. |
| AC6 | Le frontend reste lintable. | Evidence profile: `frontend_typecheck_no_orphan`; `npm run lint`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer et classer les 30 occurrences initiales (AC: AC1)
- [ ] Task 2 - Migrer chaque occurrence `static` vers CSS adjacent ou existant (AC: AC2, AC4)
- [ ] Task 3 - Mettre a jour `INLINE_STYLE_EXCEPTIONS` pour retirer les statiques migrees et justifier les dynamiques restantes (AC: AC3)
- [ ] Task 4 - Adapter ou executer les tests des surfaces touchees (AC: AC4)
- [ ] Task 5 - Capturer l'inventaire after et les scans negatifs cibles (AC: AC2, AC3, AC5)
- [ ] Task 6 - Executer lint et guards frontend (AC: AC5, AC6)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Fichiers CSS existants des composants/pages touches.
  - Variables et classes existantes dans les feuilles de style locales.
  - `frontend/src/tests/inline-style-policy.test.ts`.
  - `frontend/src/tests/design-system-allowlist.ts`.
- Do not recreate:
  - Classes dupliquees pour une meme responsabilite visuelle.
  - Fichier CSS global opportuniste pour un style local.
  - Constante TSX contenant une valeur statique a la place du CSS.
- Shared abstraction allowed only if:
  - Au moins deux surfaces du meme domaine reutilisent exactement la meme responsabilite et qu'aucune classe existante ne convient.

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

- `style={` statique dans les fichiers touches.
- Entree `INLINE_STYLE_EXCEPTIONS` statique conservee sans blocker.
- Style inline ajoute pour contourner un CSS existant.
- Style dans une prop publique changee sans test ou decision explicite.

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Styles statiques | CSS adjacent ou feuille existante de la surface | attribut `style` |
| Exceptions inline dynamiques | `frontend/src/tests/design-system-allowlist.ts` | exception implicite dans TSX |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/tests/design-system-allowlist.ts`
- `frontend/src/tests/inline-style-policy.test.ts`
- `frontend/src/layouts/TwoColumnLayout.tsx`
- `frontend/src/components/DomainRankingCard.tsx`
- `frontend/src/components/NatalInterpretation.tsx`
- `frontend/src/components/TurningPointCard.tsx`
- `frontend/src/components/prediction/CategoryGrid.tsx`
- `frontend/src/components/prediction/DayPredictionCard.tsx`
- `frontend/src/components/prediction/DayTimelineSectionV4.tsx`
- `frontend/src/components/prediction/PeriodCard.tsx`
- `frontend/src/components/prediction/TimelineRail.tsx`
- `frontend/src/components/ui/Badge/Badge.tsx`
- `frontend/src/components/ui/Form/Form.tsx`
- `frontend/src/components/ui/Skeleton/Skeleton.tsx`
- `frontend/src/features/chat/components/AstrologerPickerModal.tsx`
- `frontend/src/features/chat/components/ChatLayout.tsx`
- `frontend/src/pages/AstrologerProfilePage.tsx`
- `frontend/src/pages/NotFoundPage.tsx`
- `frontend/src/pages/settings/AccountSettings.tsx`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/tests/design-system-allowlist.ts` - reduction et justification des exceptions.
- Les fichiers TSX listes dans `Files to Inspect First` - retrait des styles statiques identifies.
- Fichiers CSS adjacents des composants/pages touches - classes de remplacement.
- `_condamad/stories/CS-041-convertir-styles-inline-statiques-restants-css/inline-styles-before.md` - baseline.
- `_condamad/stories/CS-041-convertir-styles-inline-statiques-restants-css/inline-styles-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/inline-style-policy.test.ts` - garde principale.
- Tests existants des composants/pages touches si presents.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.
- `frontend/src/styles/css-fallback-allowlist.md` - hors scope sauf si un CSS adjacent expose une exception existante sans modification.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- inline-style design-system
rg -n "style=\\{" src -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-041-convertir-styles-inline-statiques-restants-css/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-041-convertir-styles-inline-statiques-restants-css/00-story.md
```

## 22. Regression Risks

- Risk: une occurrence dynamique est migree a tort en CSS.
  - Guardrail: classification obligatoire et blocker utilisateur si ambigu.
- Risk: une exception statique reste dans l'allowlist.
  - Guardrail: inventaire after et `npm run test -- inline-style`.
- Risk: une classe CSS duplique une responsabilite existante.
  - Guardrail: inspection des CSS adjacents avant edition.

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

- `_condamad/audits/frontend-design-system/2026-05-05-1748/03-story-candidates.md#SC-002` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-05-1748/02-finding-register.md#F-003` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-05-1748/00-audit-report.md` - fichier source des surfaces auditees.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
