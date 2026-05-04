# Story CS-026 canonicaliser-source-verite-tokens-design-frontend: Canonicaliser la source de verite des tokens de design frontend

Status: ready-to-dev

## 1. Objective

Etablir `frontend/src/styles/design-tokens.css` comme source canonique des decisions de design frontend.
Classer les autres couches comme extension semantique, alias de compatibility ou dette de migration documentee.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-001`
- Reason for change: le finding `F-001` montre que plusieurs namespaces de tokens peuvent prendre la meme decision visuelle sans ownership canonique.

## 3. Domain Boundary

This story belongs to exactly one domain:

- Domain: `frontend/src/styles`
- In scope:
  - Classer les tokens de `design-tokens.css`, `theme.css`, `premium-theme.css`, `LandingLayout.css`, `Settings.css` et `DailyHoroscopePage.css`.
  - Definir la carte des namespaces canoniques, semantiques, compatibility et migration-only.
  - Ajouter un registre persistant de classification des tokens frontend.
  - Ajouter une garde qui bloque un nouveau namespace non classe.
- Out of scope:
  - Migrer les valeurs hardcodees des pages.
  - Changer la hierarchie typographique.
  - Revoir le rendu produit premium.
- Explicit non-goals:
  - Ne pas modifier les invariants backend `RG-001` a `RG-043`.
  - Ne pas fusionner `--premium-*` dans les tokens canoniques sans decision produit explicite.
  - Ne pas creer de second fichier canonique concurrent a `design-tokens.css`.

## 4. Operation Contract

- Operation type: converge
- Primary archetype: namespace-convergence
- Archetype reason: la story converge plusieurs namespaces CSS vers une classification canonique sans supprimer de surface runtime.
- Behavior change allowed: no
- Behavior change constraints:
  - Le rendu visuel doit rester equivalent.
  - Les imports CSS existants restent fonctionnels.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: le statut du namespace `--premium-*` ne peut pas etre classe comme extension semantique sans changer le rendu ou le contrat produit.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde AST/CSS doit inspecter les fichiers frontend reels comme source de verite executable. |
| Baseline Snapshot | yes | Les namespaces de tokens doivent etre captures avant et apres classification. |
| Ownership Routing | yes | Chaque namespace doit avoir un owner canonique ou une classification explicite. |
| Allowlist Exception | no | Les exceptions sont traitees comme lignes de classification, pas comme allowlist separee. |
| Contract Shape | no | Aucun API, DTO, OpenAPI ou type frontend n'est modifie. |
| Batch Migration | yes | Les namespaces non canoniques doivent etre mappes vers une surface canonique ou migration-only. |
| Reintroduction Guard | yes | La garde doit bloquer les namespaces non classes. |
| Persistent Evidence | yes | Le registre de tokens est l'artefact durable de preuve. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard CSS et inventaire disque des variables sous `frontend/src/**/*.css`.
  - Commande cible: `npm run test -- theme-tokens`.
- Secondary evidence:
  - `rg -n "--[a-z0-9-]+\\s*:" src -g "*.css"` depuis `frontend`.
- Static scans alone are not sufficient for this story because:
  - La garde doit comparer les namespaces trouves au registre de classification.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-026-canonicaliser-source-verite-tokens-design-frontend/token-namespace-inventory-before.md`
- Comparison after implementation: `_condamad/stories/CS-026-canonicaliser-source-verite-tokens-design-frontend/token-namespace-inventory-after.md`
- Expected invariant: chaque variable CSS frontend est rattachee a une classification explicite.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Token canonique | `frontend/src/styles/design-tokens.css` | page CSS locale |
| Extension premium | `frontend/src/styles/premium-theme.css` avec statut documente | alias implicite dans page CSS |
| Alias de compatibility | `frontend/src/styles/theme.css` avec cible canonique | alias sans cible |
| Token page migration-only | registre `frontend/src/styles/token-namespace-registry.md` | nouveau namespace non classe |

## 4e. Allowlist / Exception Register

- Allowlist / exception register: not applicable
- Reason: aucune exception flottante n'est autorisee; tout namespace conserve doit etre une entree exacte du registre de classification.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

| Batch | Old surface | Canonical surface | Consumers changed | Tests adapted | No-shim proof | Blocker condition |
|---|---|---|---|---|---|---|
| 1 | `theme.css` aliases | `design-tokens.css` targets | none | `theme-tokens.test.ts` | every alias points to a canonical token | alias target unknown |
| 2 | `premium-theme.css` | semantic premium extension | none | token namespace guard | premium role documented | product rejects premium layer |
| 3 | page namespaces | registry classification | none | token namespace guard | no unclassified namespace | page token owner ambiguous |

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Token namespace registry | `frontend/src/styles/token-namespace-registry.md` | Classer chaque namespace et alias de tokens frontend. |
| Baseline inventory | `token-namespace-inventory-before.md` | Capturer les namespaces avant changement. |
| After inventory | `token-namespace-inventory-after.md` | Prouver la couverture finale du registre. |

## 4i. Reintroduction Guard

- Guard target: nouveau namespace `--*` dans `frontend/src/**/*.css` absent du registre.
- Guard evidence: Evidence profile: `reintroduction_guard`; `npm run test -- theme-tokens`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md#E-002` - les couches `design-tokens.css`, `theme.css` et `premium-theme.css` coexistent.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-04-2238/02-finding-register.md#F-001` - les namespaces audites n'ont pas de statut commun.
- Evidence 3: `frontend/src/tests/theme-tokens.test.ts` - des tests de valeurs existent deja mais ne classent pas la consommation.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.

## 6. Target State

- `design-tokens.css` est declare source canonique des decisions globales.
- `theme.css` ne contient que des aliases de compatibility cibles et testes.
- `premium-theme.css` est classe comme extension semantique ou bloque pour decision produit.
- Les tokens page-scoped sont classes comme migration-only ou converges dans le registre.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-044` - les namespaces de tokens frontend doivent rester classes et gardes.
- Non-applicable invariants:
  - `RG-001` a `RG-043` - ces invariants protegent des surfaces backend, docs, scripts, LLM, DB ou prediction.
- Required regression evidence:
  - Inventaire des namespaces, test de garde token, `npm run lint`.
- Allowed differences:
  - Ajout du registre, de la garde et de classifications sans changement visuel attendu.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | `design-tokens.css` est documente comme source canonique des tokens globaux. | `frontend/src/styles/token-namespace-registry.md`; command: `npm run test -- theme-tokens`. |
| AC2 | Chaque namespace de token audite possede une classification exacte. | Evidence profile: `allowlist_register_validated`; command: `npm run test -- theme-tokens`. |
| AC3 | Les aliases de compatibility pointent vers des tokens canoniques existants. | Evidence profile: `targeted_forbidden_symbol_scan`; command: `npm run test -- theme-tokens`. |
| AC4 | Aucun nouveau namespace CSS non classe n'est accepte. | Evidence profile: `reintroduction_guard`; `npm run test -- theme-tokens`. |
| AC5 | Le rendu premium reste bloque sans decision si sa classification change. | Evidence profile: `baseline_before_after_diff`; command: `npm run test -- theme-tokens`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'inventaire initial des namespaces CSS (AC: AC1, AC2)
- [ ] Task 2 - Creer le registre de classification des tokens frontend (AC: AC1, AC2, AC5)
- [ ] Task 3 - Ajouter ou etendre la garde `theme-tokens` pour valider namespaces et aliases (AC: AC2, AC3, AC4)
- [ ] Task 4 - Capturer l'inventaire final et documenter les differences autorisees (AC: AC2, AC5)
- [ ] Task 5 - Executer lint, tests cibles et validation de story (AC: AC3, AC4)

## 9. Mandatory Reuse / DRY Constraints

- Reuse:
  - `frontend/src/styles/design-tokens.css` comme source de tokens globaux.
  - `frontend/src/tests/theme-tokens.test.ts` comme point d'ancrage des gardes.
- Do not recreate:
  - Un second fichier global de tokens.
  - Une carte de namespaces dupliquee hors du registre.
- Shared abstraction allowed only if:
  - Elle sert a parser le registre dans les tests sans modifier le runtime frontend.

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

- nouveau namespace CSS sans ligne exacte dans `frontend/src/styles/token-namespace-registry.md`
- alias de compatibility sans cible canonique
- variable locale presentee comme token global

## 11. Removal Classification Rules

- Removal classification: not applicable

## 12. Removal Audit Format

- Removal audit: not applicable

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Tokens globaux frontend | `frontend/src/styles/design-tokens.css` | tokens globaux declares dans CSS de page |
| Classification des namespaces | `frontend/src/styles/token-namespace-registry.md` | commentaires disperses |
| Garde de consommation token | `frontend/src/tests/theme-tokens.test.ts` | scan manuel d'audit |

## 14. Delete-Only Rule

- Delete-only rule: not applicable

## 15. External Usage Blocker

- External usage blocker: not applicable

## 17. Generated Contract Check

- Generated contract check: not applicable
- Reason: no generated API, route manifest, schema, public contract, or generated client is affected.

## 18. Files to Inspect First

- `frontend/src/styles/design-tokens.css`
- `frontend/src/styles/theme.css`
- `frontend/src/styles/premium-theme.css`
- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/DailyHoroscopePage.css`
- `frontend/src/tests/theme-tokens.test.ts`
- `_condamad/stories/regression-guardrails.md`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/styles/token-namespace-registry.md` - nouveau registre de classification.
- `frontend/src/tests/theme-tokens.test.ts` - garde namespace et aliases.
- `_condamad/stories/CS-026-canonicaliser-source-verite-tokens-design-frontend/token-namespace-inventory-before.md` - baseline.
- `_condamad/stories/CS-026-canonicaliser-source-verite-tokens-design-frontend/token-namespace-inventory-after.md` - preuve finale.

Likely tests:

- `frontend/src/tests/theme-tokens.test.ts` - tests de classification.

Files not expected to change:

- `backend/app` - aucun impact backend.
- `frontend/package.json` - aucune dependance nouvelle.
- `frontend/src/app/routes.tsx` - aucune route frontend.

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
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-026-canonicaliser-source-verite-tokens-design-frontend/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-026-canonicaliser-source-verite-tokens-design-frontend/00-story.md
```

## 22. Regression Risks

- Risk: un namespace page devient source de verite implicite.
  - Guardrail: registre exact et test anti-namespace non classe.
- Risk: un alias de compatibility diverge de sa cible.
  - Guardrail: test qui valide la cible canonique.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.
- Keep CSS changes in `.css` files and reuse existing style variables before creating new ones.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-04-2238/03-story-candidates.md#SC-001` - candidate source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/02-finding-register.md#F-001` - finding source.
- `_condamad/audits/frontend-design-system/2026-05-04-2238/01-evidence-log.md` - preuves d'audit.
- `_condamad/stories/regression-guardrails.md` - invariants consultes.
