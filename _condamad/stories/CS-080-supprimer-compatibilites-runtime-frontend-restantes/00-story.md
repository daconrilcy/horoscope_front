# Story CS-080 supprimer-compatibilites-runtime-frontend-restantes: Supprimer les compatibilites runtime frontend restantes

Status: done

## Objective

Supprimer les cinq surfaces frontend runtime/i18n qui gardent encore du
vocabulaire ou des branches de compatibilite. La decision utilisateur est
contraignante: aucun legacy ne doit rester, aucune compatibilite conservee ne
doit etre classee comme acceptable, et aucune AC ne peut finir en `PASS with
limitation`.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-1618/03-story-candidates.md#SC-002`
- Reason for change: `F-003` et `E-009` identifient cinq fichiers frontend avec
  vocabulaire ou branches explicites de compatibilite runtime sans condition de
  sortie.

## Domain Boundary

- Domain: `frontend-compatibility`
- In scope:
  - Inspecter et supprimer les cinq surfaces listees par `E-009`.
  - Remplacer les consommateurs internes par les contrats canoniques actuels.
  - Ajouter ou mettre a jour les tests/guards zero-hit pour le vocabulaire legacy supprime.
  - Produire un audit d'extinction prouvant que chaque surface est supprimee ou bloquee par decision utilisateur explicite.
- Out of scope:
  - Backend/API compatibility.
  - Routes admin legacy deja protegees par `RG-054`.
  - Migration des valeurs visuelles hardcodees couverte par `CS-079`.
  - Creation d'un registre de compatibilite autorisant des exceptions actives.
- Explicit non-goals:
  - Ne pas affaiblir `RG-050` ou `RG-053`.
  - Ne pas conserver de commentaire, symbole, mapper, parser, default export ou branche nommee legacy/compatibility.
  - Ne pas creer de fallback silencieux sous un nom canonique.
  - Ne pas accepter de `PASS with limitation`.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story retire les facades et branches runtime frontend qui preservent d'anciens contrats ou exports.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les contrats canoniques actuels doivent continuer a rendre les memes ecrans.
  - Les anciens payloads, codes, IDs, exports ou champs non canoniques ne doivent plus etre acceptes silencieusement.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: une surface est prouvee comme contrat externe actif; sans preuve externe, la decision "Aucun legacy ne doit rester" impose la suppression.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests frontend prouvent que les chemins canoniques restent executables. |
| Baseline Snapshot | yes | Les scans before/after bornent les cinq surfaces legacy. |
| Ownership Routing | yes | Chaque consommateur doit pointer vers le contrat canonique, pas vers une facade. |
| Allowlist Exception | yes | Le registre actif est une interdiction exacte: aucune surface legacy ne peut etre allowlistee. |
| Contract Shape | yes | Les payloads, codes i18n, exports et IDs de composants frontend peuvent etre touches. |
| Batch Migration | no | La suppression se fait par classification deterministe, pas par lot progressif. |
| Reintroduction Guard | yes | Les surfaces supprimees ne doivent pas revenir. |
| Persistent Evidence | yes | L'audit d'extinction et les scans zero-hit doivent rester consultables. |

## Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/design-system-guards.test.ts`
  - `frontend/src/tests/ConsultationMigration.test.tsx` if present after inspection
  - `frontend/src/tests/consultationStore.test.ts`
  - tests focalises `TurningPointsEnriched`, `DailyHoroscopePage` et `NatalInterpretation` s'ils existent.
- Secondary evidence:
  - scan exact `rg -n "Deprecated:|backwards compatibility|backward compatibility|legacy fallback|Legacy codes|aspectLegacy|compatibility" frontend/src`.
- Static scans alone are not sufficient because:
  - les payloads et composants canoniques doivent continuer a rendre les surfaces utilisateur.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-080-supprimer-compatibilites-runtime-frontend-restantes/frontend-runtime-compatibility-before.md`
- Comparison after implementation:
  - `_condamad/stories/CS-080-supprimer-compatibilites-runtime-frontend-restantes/frontend-runtime-compatibility-after.md`
- Expected invariant:
  - zero vocabulaire ou branche de compatibilite runtime frontend dans les cinq fichiers apres implementation, sauf blocker externe explicitement valide par l'utilisateur.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Chat page astrologer identity | contrat canonique actuellement consomme par `ChatPage` | champ deprecie `astrologerId` ou commentaire backwards compatibility |
| Daily summary shape | helper canonique de summary actuel | fallback `overall_summary` legacy |
| Prediction i18n codes | codes canoniques de `frontend/src/i18n/predictions.ts` | mapping `Legacy codes` |
| Daily insights export | import/export canonique du composant actif | default export conserve pour backward compatibility |
| Natal aspect IDs | IDs canoniques d'aspects natal | parser `aspectLegacy` |

## Allowlist / Exception Register

| File | Symbol / Route / Import | Reason | Expiry or permanence decision |
|---|---|---|---|
| `frontend/src/pages/ChatPage.tsx` | `Deprecated:`, `backwards compatibility` | Legacy chat identity branch. | Permanent deletion in this story. |
| `frontend/src/utils/dailySummaryHelper.ts` | `legacy fallback`, `overall_summary` | Legacy daily summary fallback. | Permanent deletion in this story. |
| `frontend/src/i18n/predictions.ts` | `Legacy codes` | Legacy prediction code mapping. | Permanent deletion in this story. |
| `frontend/src/components/DailyInsightsSection.tsx` | `backward compatibility`, default export alias | Legacy export facade. | Permanent deletion in this story. |
| `frontend/src/components/NatalInterpretation.tsx` | `aspectLegacy` | Legacy natal aspect parser. | Permanent deletion in this story. |

No allowed row may be added unless the user explicitly reverses the current
decision. This story must not mark any retained compatibility as acceptable.

## Contract Shape

Contract type:
- Frontend runtime payload, i18n code mapping, component export and natal aspect identifier contract.
Fields:
- `astrologerId`, `overall_summary`, legacy prediction codes, default export alias, `aspectLegacy`.
Required fields:
- Only current canonical fields and exports proven by active first-party tests.
Optional fields:
- Optional canonical fields already documented by existing types.
Status codes:
- Unchanged; no HTTP status is changed.
Serialization names:
- Legacy serialization names must be absent from runtime handling after deletion.
Frontend type impact:
- TypeScript callers may need to consume canonical fields only.
Generated contract impact:
- No generated client is expected; if generated fixtures/schemas exist, removed symbols must be absent.

## Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: les surfaces sont supprimees par audit d'extinction et scans exacts.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before compatibility baseline | `frontend-runtime-compatibility-before.md` | Inventorier les cinq surfaces, consommateurs et preuves initiales. |
| After compatibility evidence | `frontend-runtime-compatibility-after.md` | Prouver suppression, contrats canoniques et scans zero-hit. |
| Final validation evidence | `generated/10-final-evidence.md` | Persister commandes, resultats et risques residuels. |

## Reintroduction Guard

- Architecture guard against reintroduction: forbidden symbols fail if they are reintroduced.
- Required architecture guard against reintroduction: update `frontend/src/tests/design-system-guards.test.ts` or an equivalent AST guard.
- Required: architecture guard against reintroduction in `frontend/src/tests/design-system-guards.test.ts`.
- Deterministic source: forbidden symbols in frontend tests and exact scan over `frontend/src`.
- Required forbidden examples:
  - `Deprecated:`
  - `backwards compatibility`
  - `backward compatibility`
  - `legacy fallback`
  - `Legacy codes`
  - `aspectLegacy`
  - `compatibility`
- Guard evidence: `npm run test -- ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage design-system`.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-1618/02-finding-register.md#F-003`
  - cinq fichiers frontend contiennent encore des branches ou commentaires de compatibilite.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-1618/01-evidence-log.md#E-009`
  - scan FAIL sur le vocabulaire `Deprecated`, `backwards compatibility`, `Legacy codes`, `aspectLegacy`, `compatibility`.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-06-1618/00-audit-report.md#F-003`
  - liste exhaustive des cinq fichiers a modifier ou supprimer.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - `RG-050` et `RG-053` consultes avant cadrage.

## Target State

- Les cinq fichiers ne contiennent plus de vocabulaire ou branches legacy/compatibility.
- Les consommateurs frontend utilisent uniquement les contrats canoniques actuels.
- Aucun registre de compatibilite actif n'est cree, car la decision utilisateur interdit tout legacy restant.
- Les tests et scans prouvent zero retour silencieux.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-050` - les exceptions design-system doivent rester exactes et verifiees.
  - `RG-053` - les payloads historiques frontend ne doivent pas etre preserves par mapper, fallback, alias, builder ou vocabulaire legacy.
- Non-applicable invariants:
  - `RG-044` - aucun namespace CSS n'est dans le scope.
  - `RG-045` - aucune migration de literals visuels n'est dans le scope.
  - `RG-054` - aucune route admin legacy n'est dans le scope.
- Required regression evidence:
  - `npm run test -- ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage design-system`
  - scan zero-hit du vocabulaire `E-009` sur `frontend/src`.
- Allowed differences:
  - suppression du support silencieux des anciennes formes non canoniques.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Baseline exact des cinq surfaces `E-009`. | Command `rg -n $legacyPattern src`; before artifact. |
| AC2 | `ChatPage.tsx` sans commentaire compat. | Command `rg -n "Deprecated:|backwards compatibility" src/pages/ChatPage.tsx`. |
| AC3 | `dailySummaryHelper.ts` sans fallback legacy. | Command `rg -n "legacy fallback|overall_summary" src/utils/dailySummaryHelper.ts`. |
| AC4 | `predictions.ts` sans mapping legacy. | Command `rg -n "Legacy codes|compatibility|legacy" src/i18n/predictions.ts`. |
| AC5 | `DailyInsightsSection.tsx` sans export compat. | Command `rg -n "backward compatibility|export default" src/components/DailyInsightsSection.tsx`. |
| AC6 | `NatalInterpretation.tsx` sans `aspectLegacy`. | Command `rg -n "aspectLegacy|legacy|compatibility" src/components/NatalInterpretation.tsx`. |
| AC7 | Reintroduction legacy runtime bloquee. | Evidence profile: `reintroduction_guard`; AST guard and `npm run test -- ConsultationMigration consultationStore`. |
| AC8 | Aucun resultat final limite. | Command `rg -n "PASS with limitation|TODO|temporary" frontend-runtime-compatibility-after.md`. |

## Implementation Tasks

- [ ] Task 1 - Capturer le baseline complet des cinq surfaces `E-009`. (AC: AC1)
- [ ] Task 2 - Supprimer la compatibilite `ChatPage.tsx` et adapter les consommateurs au champ canonique. (AC: AC2, AC7)
- [ ] Task 3 - Supprimer le fallback legacy de `dailySummaryHelper.ts`. (AC: AC3, AC7)
- [ ] Task 4 - Supprimer les codes legacy de `predictions.ts` et garder seulement le mapping canonique. (AC: AC4, AC7)
- [ ] Task 5 - Supprimer l'export de compatibilite de `DailyInsightsSection.tsx` et migrer les imports internes. (AC: AC5, AC7)
- [ ] Task 6 - Supprimer la branche `aspectLegacy` de `NatalInterpretation.tsx` et couvrir le contrat canonique. (AC: AC6, AC7)
- [ ] Task 7 - Capturer l'after, les tests, le lint et les scans zero-hit sans limitation. (AC: AC7, AC8)

## Mandatory Reuse / DRY Constraints

- Reuse les types, helpers et exports canoniques existants; ne pas creer un deuxieme chemin de normalisation.
- Do not duplicate mapping i18n or aspect parsing logic to hide a removal.
- Shared abstraction allowed only if elle represente le contrat canonique actuel et remplace plusieurs consommateurs actifs.

## No Legacy / Forbidden Paths

- Forbidden: compatibility wrappers, transitional aliases, legacy imports, duplicate active implementations, silent fallback behavior.
- Forbidden symbols / paths:
  - `Deprecated:`
  - `backwards compatibility`
  - `backward compatibility`
  - `legacy fallback`
  - `Legacy codes`
  - `aspectLegacy`
  - `compatibility`
  - `frontend/src/styles/frontend-compatibility-registry.md` as an active exception registry.

## Removal Classification Rules

- `canonical-active`: contrat frontend actuel consomme par production.
- `external-active`: ancien payload/export prouve par doc publique, contrat client actif ou decision produit explicite.
- `historical-facade`: branche, mapper, export ou parser qui preserve une ancienne forme.
- `dead`: symbole sans consommateur actif apres scans.
- `needs-user-decision`: ambiguite restante apres scans; ne peut pas etre utilisee pour garder du legacy.

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `needs-user-decision` | Must block; cannot be kept silently because user decision forbids legacy. |
| `historical-facade` | `delete`, `replace-consumer` | Must be deleted or consumers migrated. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path:
- `_condamad/stories/CS-080-supprimer-compatibilites-runtime-frontend-restantes/frontend-runtime-compatibility-after.md`

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Chat astrologer identity | current canonical chat payload/type | deprecated `astrologerId` compatibility branch |
| Daily summary text | current canonical daily summary helper input | `overall_summary` legacy fallback |
| Prediction translation codes | current canonical i18n code table | `Legacy codes` mapping |
| Daily insights component ownership | named or canonical export used by internal imports | default export kept for backward compatibility |
| Natal aspect parsing | current canonical aspect IDs | `aspectLegacy` branch |

## Delete-Only Rule

Items classified as removable must be deleted, not repointed.
Forbidden: wrapper, compatibility alias, active deprecated path, silent fallback, re-export or soft-disable behavior.

## External Usage Blocker

- `external-active` items must not be deleted without an explicit user decision.
- If external evidence exists, implementation must stop and record the exact contract, consumer, deletion risk and requested decision.
- Without external proof, the existing user decision "Aucun legacy ne doit rester" applies and the surface must be deleted.

## Generated Contract Check

- OpenAPI path absence: no backend OpenAPI path may change for this frontend runtime story.
- Generated artifact absence: inspect generated frontend artifacts; prove removed fields/symbols are absent when such artifacts exist.
- Required evidence: scans for the `E-009` vocabulary in generated artifacts when present.

## Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-1618/00-audit-report.md`
- `_condamad/audits/frontend-design-system/2026-05-06-1618/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-06-1618/03-story-candidates.md`
- `frontend/src/pages/ChatPage.tsx`
- `frontend/src/utils/dailySummaryHelper.ts`
- `frontend/src/i18n/predictions.ts`
- `frontend/src/components/DailyInsightsSection.tsx`
- `frontend/src/components/NatalInterpretation.tsx`
- `frontend/src/tests/ConsultationMigration.test.tsx`
- `frontend/src/tests/consultationStore.test.ts`
- `frontend/src/tests/design-system-guards.test.ts`

## Expected Files to Modify

Likely files:
- `frontend/src/pages/ChatPage.tsx` - remove deprecated compatibility branch.
- `frontend/src/utils/dailySummaryHelper.ts` - remove legacy summary fallback.
- `frontend/src/i18n/predictions.ts` - remove legacy code mapping/comment.
- `frontend/src/components/DailyInsightsSection.tsx` - remove compatibility export and migrate imports.
- `frontend/src/components/NatalInterpretation.tsx` - remove `aspectLegacy` parsing branch.

Likely tests:
- `frontend/src/tests/ConsultationMigration.test.tsx` - ensure canonical consultation/chat behavior only if relevant.
- `frontend/src/tests/consultationStore.test.ts` - preserve canonical store behavior if touched.
- existing `DailyHoroscopePage`, `TurningPointsEnriched` or natal tests found by inspection - cover canonical prediction/natal paths.
- `frontend/src/tests/design-system-guards.test.ts` - add zero-hit guard if no exact guard already covers `E-009`.

Files not expected to change:
- `frontend/src/styles/token-namespace-registry.md` - no token namespace change.
- `frontend/src/tests/design-system-allowlist.ts` - no allowlist expansion is allowed.
- `frontend/package.json` - no dependency or script change is required.
- `backend/app/main.py` - no backend behavior is in scope.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage design-system
npm run lint
$legacyPattern = "Deprecated:|backwards compatibility|backward compatibility|legacy fallback|Legacy codes|aspectLegacy|compatibility"
rg -n $legacyPattern src/pages src/components src/utils src/i18n -g "*.ts" -g "*.tsx"
rg -n "astrologerId|overall_summary|aspectLegacy" src/pages/ChatPage.tsx src/utils/dailySummaryHelper.ts
rg -n "aspectLegacy" src/components/NatalInterpretation.tsx
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-080-supprimer-compatibilites-runtime-frontend-restantes/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Regression Risks

- Risk: une ancienne forme est encore emise par une surface externe inconnue.
  - Guardrail: External Usage Blocker avec decision utilisateur explicite obligatoire.
- Risk: un fallback est renomme en contrat canonique sans suppression reelle.
  - Guardrail: No Legacy scans, audit d'extinction et tests canoniques.
- Risk: suppression d'un default export casse un import interne.
  - Guardrail: lint TypeScript et tests frontend cibles.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- Do not create compatibility shims, aliases, fallbacks, wrappers, migration-only namespaces or re-exports.
- No PASS with limitation is accepted.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-1618/03-story-candidates.md#SC-002`
- `_condamad/audits/frontend-design-system/2026-05-06-1618/02-finding-register.md#F-003`
- `_condamad/audits/frontend-design-system/2026-05-06-1618/01-evidence-log.md#E-009`
- `_condamad/stories/regression-guardrails.md`
