# Story CS-031 classer-surfaces-css-legacy-frontend: Classer les surfaces CSS legacy frontend

Status: ready-to-dev

## 1. Objective

Inventorier les selecteurs CSS legacy et aliases de compatibility actifs.
Creer un registre d'ownership avec owner canonique, statut de migration et garde anti-croissance.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-006`
- Reason for change: le finding `F-006` montre que des selecteurs et aliases legacy restent actifs sans classification durable.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Inventorier `*-legacy`, aliases de `theme.css` et aliases locaux de pages.
  - Classer chaque surface comme canonical-active, compatibility, migration-only ou needs-user-decision.
  - Ajouter une garde contre de nouveaux selecteurs legacy non classes.
  - Produire un registre de selector ownership.
- Out of scope:
  - Refactorer les composants chat entiers.
  - Changer les routes frontend.
  - Traiter les fallbacks CSS, couverts par `CS-030`.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas renommer un selecteur actif sans test composant cible.
  - Ne pas conserver un alias sans owner et condition de sortie.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story classe les facades CSS legacy et impose que les surfaces prouvees migration-only soient traitees par suppression controlee, pas par nouveau shim.
- Behavior change allowed: no
- Behavior change constraints:
  - Les selecteurs actifs restent fonctionnels tant que leur migration n'est pas couverte par une autre story.
  - Toute classification ambiguë bloque l'implementation.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un selecteur legacy est encore consommé par un composant actif mais aucun owner canonique ne peut etre etabli.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde AST/CSS doit inspecter les fichiers frontend reels. |
| Baseline Snapshot | yes | Les selecteurs legacy doivent etre captures avant/apres classification. |
| Ownership Routing | yes | Chaque surface legacy doit avoir owner, statut et cible. |
| Allowlist Exception | yes | Les surfaces conservees sont des exceptions exactes. |
| Contract Shape | no | Aucun contrat API ou type frontend n'est touche. |
| Batch Migration | no | La story classifie; les migrations visuelles futures auront leurs lots. |
| Reintroduction Guard | yes | Une garde bloque les nouveaux selecteurs legacy non classes. |
| Persistent Evidence | yes | Le registre d'ownership et l'audit de classification doivent persister. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard CSS/TSX qui inventorie selecteurs et usages sous `frontend/src`.
  - Commande cible: `npm run test -- legacy-style`.
- Secondary evidence:
  - `rg -n "legacy|--text-main|--text-1|--glass|--primary" src -g "*.css"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - La garde doit comparer les surfaces detectees au registre d'ownership.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-031-classer-surfaces-css-legacy-frontend/legacy-style-surfaces-before.md`
- Comparison after implementation: `_condamad/stories/CS-031-classer-surfaces-css-legacy-frontend/legacy-style-surfaces-after.md`
- Expected invariant: chaque surface legacy detectee est presente dans le registre final.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Selecteur actif chat | composant `frontend/src/features/chat/components` correspondant | selecteur legacy non classe |
| Alias de theme | `frontend/src/styles/theme.css` avec cible canonique | alias sans cible |
| Alias local page | fichier CSS de page avec statut migration-only | token local presente comme canonique |
| Garde legacy | test legacy-style-policy | scan manuel |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/features/chat/components/ConversationList.css` | `conversation-item-legacy` | Surface active classee. | Until component migration. |
| `frontend/src/styles/theme.css` | compatibility token alias | Alias historique mappe vers token canonique. | Until token namespace registry marks alias retired. |
| `frontend/src/pages/DailyHoroscopePage.css` | local alias variable | Dette migration-only documentee. | Until canonical token exists and consumers migrate. |

Rules:

- no selector family wildcard without exact selector;
- no alias without canonical target;
- no compatibility alias without permanence or exit condition;
- every exception must be validated by test.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch migration plan: not applicable
- Reason: cette story classe les surfaces et bloque la croissance; les remplacements de composants seront des stories separees.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Legacy style registry | `frontend/src/styles/legacy-style-surface-registry.md` | Classer les surfaces legacy et leur owner. |
| Removal audit | `_condamad/stories/CS-031-classer-surfaces-css-legacy-frontend/legacy-style-removal-audit.md` | Documenter les decisions keep/delete/blocker. |
| Before inventory | `legacy-style-surfaces-before.md` | Capturer les surfaces initiales. |
| After inventory | `legacy-style-surfaces-after.md` | Prouver la classification finale. |

## 4i. Reintroduction Guard

- Guard target: architecture guard against reintroduced forbidden symbols such as `conversation-item-legacy` when absent from the registry.
- Deterministic source: forbidden symbols from CSS/TSX inventory.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- legacy-style`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md#E-009` - les plus gros fichiers CSS concentrent le risque.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md#E-012` - plusieurs selecteurs et variables legacy sont detectes.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-04-2238/02-finding-register.md#F-006` - les aliases et noms legacy ne sont pas rattaches a une migration.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- Un registre `legacy-style-surface-registry.md` classe chaque surface legacy detectee.
- Les selecteurs actifs ont un owner composant et une cible canonique.
- Les aliases conserves ont une condition de sortie.
- Une garde Vitest bloque toute croissance non classee.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les aliases token doivent rester classes par le registre frontend.
  - `RG-049` - les surfaces CSS legacy doivent rester inventories.
- Non-applicable invariants:
  - `RG-001` a `RG-043` - hors surface frontend CSS.
- Required regression evidence:
  - Registre legacy, test legacy-style, inventaire avant/apres.
- Allowed differences:
  - Ajout de classifications et de garde sans changement visuel.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Les surfaces legacy detectees sont inventories avant changement. | Evidence profile: `baseline_before_after_diff`; command: `npm run test -- legacy-style`. |
| AC2 | Chaque surface legacy finale possede une entree de registre. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- legacy-style`. |
| AC3 | Les aliases de compatibility ont une cible canonique. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- legacy-style`. |
| AC4 | Un nouveau selecteur legacy non classe fait echouer la garde. | Evidence profile: `reintroduction_guard`; `npm run test -- legacy-style`. |
| AC5 | Les fichiers CSS actifs restent sans changement de rendu attendu. | Evidence profile: `baseline_before_after_diff`; command: `npm run test -- legacy-style`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'inventaire initial des surfaces legacy (AC: AC1)
- [ ] Task 2 - Creer le registre d'ownership legacy style (AC: AC2, AC3)
- [ ] Task 3 - Classer les aliases `theme.css` et locaux (AC: AC2, AC3)
- [ ] Task 4 - Ajouter la garde legacy-style (AC: AC4)
- [ ] Task 5 - Capturer l'inventaire final et executer lint (AC: AC5)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - Le registre token de `CS-026` pour les aliases CSS variables.
  - Les tests frontend existants pour ajouter la garde.
- Do not recreate:
  - Un registre legacy par composant.
  - Un alias canonicalise dans plusieurs fichiers.
- Shared abstraction allowed only if:
  - Elle parse CSS pour les gardes legacy et token sans duplication.

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

- selecteur `*-legacy` sans ligne de registre
- alias de compatibility sans cible canonique
- statut `unknown`, `misc` ou `later`

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: item is referenced by first-party production code or is the canonical owner.
- `external-active`: item is referenced by public docs, email templates, generated links, clients, or audit evidence.
- `historical-facade`: item delegates to a canonical implementation only to preserve an old surface.
- `dead`: item has zero references in production code, tests, docs, generated contracts, and known external surfaces.
- `needs-user-decision`: ambiguity remains after required scans and must block deletion.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

Required audit table:

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `conversation-item-legacy` | selector | needs-user-decision | chat components | canonical selector | needs-user-decision | `npm run test -- legacy-style` | visual |
| `--text-1` | alias | historical-facade | `theme.css` | canonical token | delete | `npm run test -- legacy-style` | drift |
| `chat-layout` | CSS selector | canonical-active | chat runtime components | same selector | keep | `npm run test -- legacy-style` | none |
| `old-local-alias` | CSS variable alias | dead | none after scan | canonical token | delete | `npm run test -- legacy-style` | none |
| `ambiguous-compat-class` | selector | external-active | unknown docs | canonical selector | keep or replace-consumer | `npm run test -- legacy-style` | external |

Audit output path when applicable:

- `_condamad/stories/CS-031-classer-surfaces-css-legacy-frontend/legacy-style-removal-audit.md`

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Classification legacy CSS | `frontend/src/styles/legacy-style-surface-registry.md` | audit ponctuel |
| Garde legacy CSS | test `legacy-style` | scan manuel |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- redirecting to the canonical endpoint
- preserving a wrapper
- adding a compatibility alias
- keeping a deprecated route active
- preserving the old path through re-export
- replacing deletion with soft-disable behavior

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted. The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

## 17. Generated Contract Check

- Generated contract check: required for this CSS legacy facade story.
- OpenAPI path absence: unchanged because this CSS story has no OpenAPI producer.
- generated client/schema absence: `npm run test -- legacy-style` must prove no generated frontend contract consumes the classified facade.
- route manifest absence: `npm run test -- legacy-style` must prove no frontend route manifest registers a classified legacy CSS surface.

## 18. Files to Inspect First

- `frontend/src/styles/theme.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/features/chat/components/ChatLayout.tsx`
- `frontend/src/features/chat/components/ConversationItem.tsx`
- `frontend/src/features/chat/components/ConversationList.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/pages/settings/Settings.css`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/legacy-style-surface-registry.md` - registre d'ownership.
- `frontend/src/tests/legacy-style-policy.test.ts` - garde legacy.
- `frontend/src/styles/theme.css` - annotations ou ajustements d'aliases si requis.

Likely tests:

- `frontend/src/tests/legacy-style-policy.test.ts` - couverture principale.
- `frontend/src/tests/theme-tokens.test.ts` - couverture des aliases token.

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
npm run test -- legacy-style
rg -n "legacy|--text-main|--text-1|--glass|--primary" src -g "*.css"
Pop-Location
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-031-classer-surfaces-css-legacy-frontend/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-031-classer-surfaces-css-legacy-frontend/00-story.md
```

## 22. Regression Risks

- Risk: un selecteur actif est classe sans owner reel.
  - Guardrail: registre exige owner composant et cible.
- Risk: une exception legacy devient permanente par oubli.
  - Guardrail: condition de sortie obligatoire.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Treat ambiguous active selectors as blockers, not silent exceptions.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-006` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/02-finding-register.md#F-006` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
