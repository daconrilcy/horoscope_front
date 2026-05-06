# Story CS-083 fermer-garde-no-legacy-vocabulaire-css-actif: Fermer la garde No Legacy sur le vocabulaire CSS actif

Status: done

## 1. Objective

Supprimer le vocabulaire No Legacy non classe de `AdminPromptsPage.css`.
Durcir la garde frontend afin qu'un commentaire CSS actif ne conserve plus
`legacy`, `compatibility`, `alias`, `fallback` ou `migration-only` sans classification.
Aucun legacy ne doit rester et aucune AC ne peut etre acceptee en `PASS with limitation`.

## 2. Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-2320/03-story-candidates.md#SC-002`
- Reason for change: `F-003` signale que `AdminPromptsPage.css:1792`
  contient encore `Route legacy : investigation hors catalogue`.
  La garde actuelle classe surtout les selectors et aliases.

## 3. Domain Boundary

- Domain: `frontend-design-system`
- In scope:
  - Supprimer ou renommer le commentaire CSS stale dans `AdminPromptsPage.css` vers un vocabulaire canonique non legacy.
  - Etendre la garde design-system pour scanner le vocabulaire No Legacy dans les commentaires CSS actifs.
  - Conserver les exceptions exactes existantes uniquement dans les registres explicites ou tests de garde.
  - Persister un audit before/after du vocabulaire CSS actif.
- Out of scope:
  - Renommer les concepts metier legitimes de fallback prompt si leur vocabulaire est produit et deja classe.
  - Modifier les selectors, routes, composants, API ou comportements Admin Prompts.
  - Migrer les hardcoded visual values de `AdminPromptsPage.css`, hors correction du commentaire vise.
- Explicit non-goals:
  - Ne pas affaiblir `RG-049`, `RG-050`, `RG-052`, `RG-057` ou `RG-060`.
  - Ne pas ajouter d'exception large, wildcard, alias, shim, fallback, compatibility wrapper ou vocabulaire legacy conserve.
  - Ne pas conserver de dette sous forme de TODO, exception large, limitation acceptee ou `PASS with limitation`.

## 4. Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story supprime un vocabulaire legacy actif et ajoute une garde anti-retour pour empecher sa conservation comme facade historique non classee.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Le texte du commentaire peut changer ou disparaitre.
  - Les selectors, styles effectifs, routes, labels visibles, API et comportements Admin Prompts restent inchanges.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: le vocabulaire `legacy` est revendique comme vocabulaire produit canonique et doit etre conserve avec owner, cible et condition de sortie.

## 4a. Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | La garde Vitest/AST guard est la source executable de la politique No Legacy frontend. |
| Baseline Snapshot | yes | Les scans before/after prouvent le commentaire cible et l'absence finale de limitation. |
| Ownership Routing | yes | Tout vocabulaire conserve doit etre route vers un registre explicite, pas vers un commentaire CSS actif. |
| Allowlist Exception | yes | Les exceptions doivent rester exactes; aucune exception large n'est autorisee. |
| Contract Shape | no | Aucun contrat API, DTO, route, payload ou client genere n'est modifie. |
| Batch Migration | no | La story ferme une garde ciblee, pas un lot multi-fichiers. |
| Reintroduction Guard | yes | Le vocabulaire No Legacy CSS actif ne doit pas revenir silencieusement. |
| Persistent Evidence | yes | L'audit before/after et la preuve finale doivent rester consultables. |

## 4b. Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/design-system-guards.test.ts` or `frontend/src/tests/legacy-style-policy.test.ts` with deterministic CSS comment vocabulary scan.
- Secondary evidence:
  - scans `rg` cibles sur `frontend/src/**/*.css`.
- Static scans alone are not sufficient because:
  - la politique doit echouer automatiquement dans Vitest si un commentaire CSS actif reintroduit du vocabulaire No Legacy non classe.

## 4c. Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-083-fermer-garde-no-legacy-vocabulaire-css-actif/css-no-legacy-vocabulary-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-083-fermer-garde-no-legacy-vocabulaire-css-actif/css-no-legacy-vocabulary-after.md`
- Expected invariant:
  - aucun commentaire CSS actif ne conserve `legacy`, `compatibility`, `alias`, `shim`, `fallback` ou `migration-only` hors registre explicite et classification exacte.

## 4d. Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Vocabulaire legacy/compat CSS | `frontend/src/styles/legacy-style-surface-registry.md` si une exception explicite est approuvee | commentaire CSS actif non classe |
| Garde No Legacy executable | `frontend/src/tests/design-system-guards.test.ts` ou `legacy-style-policy.test.ts` | scan manuel non teste |
| Commentaire Admin Prompts cible | vocabulaire canonique non legacy ou suppression | `Route legacy` ou libelle equivalent |

## 4e. Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/styles/legacy-style-surface-registry.md` | exact selector families | Existing registry. | Rows with owner, target and exit condition only. |

Rules:

- no wildcard;
- no folder-wide exception;
- no implicit exception;
- every exception must be validated by test or scan;
- no new exception is allowed for `Route legacy : investigation hors catalogue` unless the user explicitly approves product vocabulary retention.

## 4f. Contract Shape

- Contract shape: not applicable
- Reason: no API, error, payload, export, DTO, OpenAPI contract, generated client, or frontend type is affected.

## 4g. Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: this is a targeted guard hardening and source cleanup story, not a batch migration.

## 4h. Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before vocabulary audit | `css-no-legacy-vocabulary-before.md` | Classer le hit initial et les exceptions. |
| After vocabulary audit | `css-no-legacy-vocabulary-after.md` | Prouver l'absence de vocabulaire CSS actif non classe. |
| Final validation | `_condamad/stories/CS-083-fermer-garde-no-legacy-vocabulaire-css-actif/generated/10-final-evidence.md` | Persister commandes et resultats. |

## 4i. Reintroduction Guard

- The implementation must add or update an architecture guard that fails if the removed or forbidden surface is reintroduced.
- Architecture guard against reintroduction: les commentaires CSS actifs echouent s'ils contiennent du vocabulaire No Legacy non classe.
- Deterministic source: forbidden symbols extracted by an AST guard or bounded Vitest scan over CSS comments.
- Required forbidden examples:
  - `Route legacy : investigation hors catalogue`.
  - `legacy`, `compatibility`, `alias`, `shim`, `migration-only` in active CSS comments.
  - `fallback` in active CSS comments unless classified as product vocabulary with exact owner.
- Guard evidence: `npm run test -- design-system legacy-style`.

## 5. Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-2320/02-finding-register.md#F-003`
  - la garde No Legacy ne couvre pas completement le vocabulaire des commentaires CSS.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-2320/01-evidence-log.md#E-013`
  - `AdminPromptsPage.css:1792` contient `Route legacy : investigation hors catalogue`.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-06-2320/03-story-candidates.md#SC-002` - demande le nettoyage source et l'extension de garde.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - `RG-049`, `RG-050`, `RG-052`, `RG-057` et `RG-060` consultes avant cadrage.
- Evidence 5: scan local du 2026-05-06 - `rg` confirme le hit `legacy` cible dans `AdminPromptsPage.css`.

## 6. Target State

- Le commentaire `Route legacy : investigation hors catalogue` est supprime ou remplace par un vocabulaire canonique non legacy.
- Une garde Vitest echoue si un commentaire CSS actif reintroduit du vocabulaire No Legacy non classe.
- Les registres existants restent exacts; aucune exception large ou retention legacy n'est ajoutee.
- Les validations frontend passent sans limitation et les preuves sont persistantes.

## 6a. Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-049` - toute surface CSS legacy restante doit avoir owner, cible et condition de sortie.
  - `RG-050` - la suite anti-drift design-system doit rester executable.
  - `RG-052` - aucun namespace migration-only ou alias stale ne doit revenir.
  - `RG-057` - les mots compatibility/legacy ne doivent pas revenir comme vocabulaire runtime non classe.
  - `RG-060` - les commentaires CSS actifs ne doivent pas conserver du vocabulaire No Legacy non classe.
- Non-applicable invariants:
  - `RG-044`, `RG-045`, `RG-046` - la story ne migre pas de tokens ou typographie.
  - `RG-047`, `RG-048` - aucun style inline ou fallback CSS literal n'est modifie.
  - `RG-051`, `RG-055`, `RG-056`, `RG-058`, `RG-059` - les clusters HelpPage, prediction, UI, chat et App ne sont pas modifies.
- Required regression evidence:
  - `npm run test -- design-system legacy-style`.
  - scan cible du vocabulaire No Legacy CSS actif.
  - `npm run lint`.
- Allowed differences:
  - suppression ou reformulation non legacy du commentaire cible uniquement.

## 7. Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le hit CSS initial est capture. | Evidence profile: `baseline_before_after_diff`; command `rg -n "Route legacy|legacy" AdminPromptsPage.css`. |
| AC2 | `AdminPromptsPage.css` ne contient plus le commentaire legacy. | Evidence profile: `runtime_guard`; AST guard plus `npm run test -- design-system legacy-style`. |
| AC3 | Une garde executable couvre les commentaires CSS actifs. | Evidence profile: `reintroduction_guard`; `npm run test -- design-system legacy-style`. |
| AC4 | Les exceptions restent exactes. | Evidence profile: `allowlist_register_validated`; command `rg -n "\*|glob|folder-wide" legacy-style-surface-registry.md`. |
| AC5 | Admin Prompts reste inchange hors commentaire cible. | Evidence profile: `ast_architecture_guard`; `npm run test -- AdminPromptsPage design-system legacy-style`. |
| AC6 | L'after prouve zero vocabulaire non classe. | Evidence profile: `repo_wide_negative_scan`; command `rg -n "migration-only|compatibility|legacy|alias" frontend/src`. |
| AC7 | Aucun livrable n'a d'AC partielle. | Evidence profile: `persistent_evidence`; command `rg -n "PASS with limitation|PARTIAL|TODO" generated/10-final-evidence.md`. |

## 8. Implementation Tasks

- [ ] Task 1 - Capturer l'audit before du vocabulaire No Legacy CSS actif. (AC: AC1)
- [ ] Task 2 - Supprimer ou reformuler le commentaire `Route legacy : investigation hors catalogue` sans garder de vocabulaire legacy. (AC: AC2, AC5)
- [ ] Task 3 - Ajouter une garde Vitest deterministe des commentaires CSS actifs. (AC: AC3, AC6)
- [ ] Task 4 - Verifier que les exceptions existantes restent exactes et sans wildcard. (AC: AC4)
- [ ] Task 5 - Capturer l'audit after et la preuve finale sans limitation. (AC: AC6, AC7)
- [ ] Task 6 - Executer les validations frontend ciblees. (AC: AC3, AC5, AC6, AC7)

## 9. Mandatory Reuse / DRY Constraints

- Reuse les helpers de tests design-system existants dans `frontend/src/tests/design-system-guards.test.ts` ou le fichier de garde equivalent.
- Reuse `frontend/src/styles/legacy-style-surface-registry.md` comme registre canonique des exceptions legacy style.
- Do not recreate a second registry for CSS comment vocabulary unless it is a narrow section in the existing registry with owner, canonical target and exit condition.
- Shared abstraction allowed only if elle remplace une logique de scan deja dupliquee dans les tests design-system.

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

- `Route legacy : investigation hors catalogue`.
- `legacy`, `Legacy`, `alias`, `compat`, `compatibility`, `shim`, `migration-only` dans les commentaires CSS actifs hors registre explicite.
- nouvelle exception wildcard ou dossier complet dans `frontend/src/styles/legacy-style-surface-registry.md`.
- modification de selectors Admin Prompts pour contourner la garde.

## 11. Removal Classification Rules

Classification must be deterministic:

- `canonical-active`: vocabulaire produit non legacy ou registre explicite avec owner.
- `external-active`: documentation publique ou decision produit impose le vocabulaire legacy et bloque la suppression.
- `historical-facade`: commentaire ou libelle actif conserve uniquement pour expliquer une surface ancienne.
- `dead`: commentaire stale sans consommateur runtime.
- `needs-user-decision`: ambiguite apres scans et preuve d'usage externe.

Classification decision matrix:

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `needs-user-decision` | Must be deleted when no external blocker remains. Must not be repointed. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## 12. Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Audit output path when applicable:

- `_condamad/stories/CS-083-fermer-garde-no-legacy-vocabulaire-css-actif/css-no-legacy-vocabulary-after.md`

Allowed decisions: `delete`, `keep`, `replace-consumer`, `needs-user-decision`.

## 13. Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| CSS legacy vocabulary exceptions | `frontend/src/styles/legacy-style-surface-registry.md` | unclassified active CSS comments |
| CSS comment guard | `frontend/src/tests/design-system-guards.test.ts` or `legacy-style-policy.test.ts` | manual-only scan |
| Admin Prompts CSS section label | canonical neutral wording or no comment | `Route legacy` |

## 14. Delete-Only Rule

Items classified as removable must be deleted, not repointed.

Forbidden:

- preserving a wrapper;
- adding a compatibility alias;
- keeping deprecated vocabulary active;
- preserving the old wording through re-export;
- preserving the old wording through a near-synonym containing `legacy`;
- replacing deletion with an allowlist wildcard.

## 15. External Usage Blocker

If an item is classified as `external-active`, it must not be deleted.
The dev agent must stop or record an explicit user decision with external evidence and deletion risk.

## 17. Generated Contract Check

- OpenAPI path absence: no backend OpenAPI path is added, removed or renamed.
- Generated client/schema absence: no generated client or schema is affected.
- Route manifest absence: no frontend route manifest or generated artifact may change.
- Required evidence: `git diff -- frontend/src/pages/admin/AdminPromptsPage.css frontend/src/tests` remains limited to CSS comment cleanup and guard tests.

## 18. Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-2320/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-06-2320/02-finding-register.md`
- `_condamad/audits/frontend-design-system/2026-05-06-2320/03-story-candidates.md`
- `_condamad/stories/regression-guardrails.md`
- `frontend/src/pages/admin/AdminPromptsPage.css`
- `frontend/src/tests/design-system-guards.test.ts`
- `frontend/src/tests/legacy-style-policy.test.ts`
- `frontend/src/styles/legacy-style-surface-registry.md`
- `frontend/src/tests/design-system-allowlist.ts`

## 19. Expected Files to Modify

Likely files:

- `frontend/src/pages/admin/AdminPromptsPage.css` - supprimer ou reformuler le commentaire cible.
- `frontend/src/tests/design-system-guards.test.ts` - ajouter la garde No Legacy des commentaires CSS actifs.
- `frontend/src/tests/legacy-style-policy.test.ts` - alternative acceptable si cette garde est l'owner local.
- `frontend/src/styles/legacy-style-surface-registry.md` - uniquement si une exception explicite est approuvee avec owner, cible et condition de sortie.

Likely tests:

- `frontend/src/tests/design-system-guards.test.ts` - couverture anti-retour du vocabulaire CSS actif.
- `frontend/src/tests/legacy-style-policy.test.ts` - couverture legacy-style si c'est l'owner choisi.

Files not expected to change:

- `frontend/package.json` - aucune dependance ou script nouveau.
- `frontend/src/pages/admin/AdminPromptsPage.tsx` - comportement Admin Prompts hors scope.
- `frontend/src/App.css` - cluster visual values couvert par `CS-082`.
- `backend/app/main.py` - aucun backend dans ce scope.

## 20. Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## 21. Validation Plan

Run or justify why skipped:

```powershell
Push-Location frontend
npm run test -- design-system legacy-style AdminPromptsPage
npm run lint
rg -n --glob "*.css" -- "--default_dropshadow|migration-only|compatibility|legacy|alias" src
rg -n "Route legacy|PASS with limitation" ../_condamad/stories/CS-083-fermer-garde-no-legacy-vocabulaire-css-actif
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-083-fermer-garde-no-legacy-vocabulaire-css-actif/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## 22. Regression Risks

- Risk: la garde bloque du vocabulaire produit legitime `fallback` deja classe.
  - Guardrail: AC4 impose exceptions exactes avec owner et condition.
- Risk: le commentaire est supprime mais la garde ne couvre pas les commentaires futurs.
  - Guardrail: AC3 impose une garde Vitest deterministe.
- Risk: une exception large masque une future reintroduction legacy.
  - Guardrail: `RG-049`, `RG-050`, `RG-060` et scan No Legacy.
- Risk: une AC partiellement satisfaite est acceptee.
  - Guardrail: AC7 interdit `PASS with limitation` et impose evidence finale sans limitation.

## 23. Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not create compatibility shims, aliases, fallbacks, wrappers, migration-only namespaces or re-exports.
- No legacy may remain in the implemented surface.
- No AC may be accepted as `PASS with limitation`.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## 24. References

- `_condamad/audits/frontend-design-system/2026-05-06-2320/03-story-candidates.md#SC-002` - source de la story.
- `_condamad/audits/frontend-design-system/2026-05-06-2320/02-finding-register.md#F-003` - constat principal.
- `_condamad/audits/frontend-design-system/2026-05-06-2320/01-evidence-log.md#E-013` - preuve du hit CSS.
- `_condamad/stories/regression-guardrails.md` - invariants applicables.
