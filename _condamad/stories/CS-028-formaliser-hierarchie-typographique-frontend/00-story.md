# Story CS-028 formaliser-hierarchie-typographique-frontend: Formaliser la hierarchie typographique frontend

Status: ready-to-dev

## 1. Objective

Creer une echelle typographique semantique pour les pages et composants React, puis migrer les declarations typographiques repetees vers des roles de texte reutilisables.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-003`
- Reason for change: le finding `F-003` montre que la hierarchie texte est encodee par des literals locaux de taille, poids, line-height et letter-spacing.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Definir les roles `page-title`, `section-title`, `card-title`, `body`, `body-muted`, `metadata`, `label`, `eyebrow`, `cta` et `numeric`.
  - Ajouter les tokens ou classes CSS necessaires.
  - Migrer les repetitions les plus frequentes dans les fichiers du lot choisi.
  - Ajouter une garde contre les nouveaux literals typographiques non classes.
- Out of scope:
  - Modifier la copy produit.
  - Redessiner la landing marketing.
  - Migrer les couleurs et espacements traites par `CS-027`.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas imposer une normalisation px-to-rem sur les surfaces marketing sans decision.
  - Ne pas ajouter de style inline.

## 4. Operation Contract

- Operation type: migrate
- Primary archetype: batch-migration
- Archetype reason: la story migre par lot des declarations typographiques locales vers des roles semantiques.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les roles peuvent normaliser des repetitions exactes.
  - Une difference visuelle marketing exige une decision utilisateur.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: une normalisation px-to-rem ou landing-scale change une taille visible.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | La typographie est gouvernee par CSS statique. |
| Baseline Snapshot | yes | Les literals typographiques doivent etre comptes avant/apres. |
| Ownership Routing | no | Le domaine reste `frontend/src/styles` sans routage multi-owner. |
| Allowlist Exception | no | Les exceptions sont listees dans l'artefact de migration. |
| Contract Shape | no | Aucun contrat API ou type frontend n'est touche. |
| Batch Migration | yes | La migration doit etre faite en lot controle. |
| Reintroduction Guard | yes | Une garde bloque les nouveaux literals non classes. |
| Persistent Evidence | yes | Les roles et comptes avant/apres doivent persister. |

## 4b. Runtime Source of Truth

- Runtime source of truth: not applicable
- Reason: aucun comportement runtime ou contrat genere n'est touche par les roles CSS.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-028-formaliser-hierarchie-typographique-frontend/typography-literals-before.md`
- Comparison after implementation: `_condamad/stories/CS-028-formaliser-hierarchie-typographique-frontend/typography-literals-after.md`
- Expected invariant: les declarations typographiques migrees diminuent dans le lot et chaque exception restante est classee.

## 4d. Ownership Routing Rule

- Ownership routing: not applicable
- Reason: les roles typographiques appartiennent a la couche styles frontend unique.

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: les exceptions sont documentees dans l'artefact de migration avec une cible exacte et une decision de permanence.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | repeated font weights | semantic text roles | CSS declarations in selected files | typography guard | local literals decrease | role conflicts with component contract |
| 2 | repeated font sizes | semantic text roles | CSS declarations in selected files | typography guard | no duplicate role value | px-to-rem decision needed |
| 3 | line-height and letter-spacing | semantic text roles | selected CSS | typography guard | exact exceptions | landing scale decision |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Typography role registry | `frontend/src/styles/typography-roles.md` | Decrire les roles et leurs usages. |
| Before counts | `typography-literals-before.md` | Capturer les declarations initiales. |
| After counts | `typography-literals-after.md` | Prouver les changements du lot. |

## 4i. Reintroduction Guard

- Guard target: nouveaux `font-size`, `font-weight`, `line-height` et `letter-spacing` literals hors registre.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- design-system`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md#E-005` - 1393 declarations typographiques non tokenisees.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-04-2238/02-finding-register.md#F-003` - poids `700`, `600`, `500` et tailles px/rem sont repetes.
- Evidence 3: `frontend/src/tests/theme-tokens.test.ts` - il existe une base de tests styles a etendre.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Les roles typographiques semantiques existent dans la couche styles.
- Les composants et pages du lot consomment ces roles.
- Les literals restants sont classes ou bloques pour decision.
- Un test statique detecte les nouveaux literals hors politique.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les ajouts de tokens doivent respecter la source canonique frontend.
  - `RG-046` - les roles typographiques doivent rester la voie canonique.
- Non-applicable invariants:
  - `RG-001` a `RG-043` - hors surface frontend styles.
- Required regression evidence:
  - Comptes avant/apres, garde typographique, `npm run lint`.
- Allowed differences:
  - Normalisation des repetitions exactes uniquement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les roles typographiques requis sont documentes. | `frontend/src/styles/typography-roles.md`; command: `npm run test -- design-system`. |
| AC2 | Les declarations typographiques repetees du lot utilisent les roles. | Evidence profile: `targeted_forbidden_symbol_scan`; command: `npm run test -- design-system`. |
| AC3 | Les exceptions restantes ont une entree exacte. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- design-system`. |
| AC4 | Les nouveaux literals typographiques non classes echouent en test. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system`. |
| AC5 | Les differences visuelles non exactes sont bloquees pour decision. | Evidence profile: `baseline_before_after_diff`; command: `npm run test -- design-system`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'inventaire typographique initial (AC: AC2, AC5)
- [ ] Task 2 - Definir les roles typographiques et leur registre (AC: AC1)
- [ ] Task 3 - Migrer le lot de declarations repetees (AC: AC2)
- [ ] Task 4 - Classer les exceptions restantes (AC: AC3)
- [ ] Task 5 - Ajouter la garde et capturer l'inventaire final (AC: AC4, AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css` pour les variables globales.
  - Les classes utilitaires existantes dans `frontend/src/styles/utilities.css` quand elles conviennent.
- Do not recreate:
  - Un role par composant.
  - Une echelle marketing concurrente sans decision.
- Shared abstraction allowed only if:
  - Elle est consommee par au moins deux surfaces du lot.

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

- nouveau literal typographique non classe
- role semantique duplique sous un autre nom
- style inline pour taille, poids ou line-height

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Roles typographiques | `frontend/src/styles/typography-roles.md` et CSS styles | declarations locales non classees |
| Garde typographique | `frontend/src/tests/theme-tokens.test.ts` ou test design-system dedie | scan manuel |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/utilities.css`
- `frontend/src/App.css`
- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/pages/landing/LandingPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/tests/theme-tokens.test.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/design-tokens.css` - roles ou variables typographiques.
- `frontend/src/styles/utilities.css` - classes de role reutilisables.
- `frontend/src/styles/typography-roles.md` - registre durable.
- `frontend/src/tests/theme-tokens.test.ts` - garde typographique.
- `frontend/src/App.css` - migration du lot.
- `frontend/src/pages/settings/Settings.css` - migration du lot.

Likely tests:

- `frontend/src/tests/theme-tokens.test.ts` - garde statique.

Files not expected to change:

- `backend/app` - hors scope.
- `frontend/package.json` - aucune dependance.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run lint
npm run test -- theme-tokens
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-028-formaliser-hierarchie-typographique-frontend/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-028-formaliser-hierarchie-typographique-frontend/00-story.md
```

## 22. Regression Risks

- Risk: la landing perd son echelle expressive.
  - Guardrail: decision requise avant normalisation non exacte.
- Risk: les roles deviennent trop nombreux.
  - Guardrail: registre fini et garde anti-literal.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Keep typography styling in CSS files and reuse existing variables before adding roles.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-003` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/02-finding-register.md#F-003` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
