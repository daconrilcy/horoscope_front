# Story CS-076 supprimer-compatibilites-runtime-frontend-restantes: Supprimer les compatibilites runtime frontend restantes

Status: ready-to-dev

## Objective

Supprimer les chemins runtime frontend qui conservent des payloads ou libelles
legacy pour les consultations et les predictions. La decision produit fournie
est stricte: aucun legacy ne doit rester.

Les fonctions `isLegacy`, `mapLegacyConsultationKey`, `buildLegacyBlocks` et les
mappers d'anciens payloads doivent etre supprimes ou renommes vers un contrat
canonique uniquement si le comportement reste actif sans semantique legacy.

## Trigger / Source

- Source type: audit
- Source reference: `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md#SC-003`
- Reason for change: `F-006` identifie des chemins de compatibilite consultation
  et prediction actifs sans condition de sortie; la decision utilisateur impose
  leur extinction.

## Domain Boundary

- Domain: `frontend-compatibility`
- In scope:
  - Supprimer ou renommer les symboles runtime legacy listes par `E-012` et `E-014`.
  - Retirer les tests qui valident explicitement des payloads historiques, ou les convertir vers le contrat canonique.
  - Ajouter un registre d'extinction frontend pour prouver les decisions de suppression, sans conserver de compat active.
  - Ajouter des scans zero-hit pour vocabulaire et symboles legacy runtime.
- Out of scope:
  - Routes admin legacy, couvertes par `CS-077`.
  - Backend/API compatibility.
  - Refonte UX des consultations ou predictions.
- Explicit non-goals:
  - Ne pas affaiblir `RG-049` ou `RG-050`.
  - Ne pas creer de compatibility registry qui autorise des chemins legacy restants.
  - Ne pas accepter de `PASS with limitation`.

## Operation Contract

- Operation type: remove
- Primary archetype: legacy-facade-removal
- Archetype reason: la story retire les facades runtime frontend conservees pour anciens payloads.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Les payloads canoniques actuels doivent continuer a rendre les memes ecrans.
  - Les payloads historiques non canoniques ne doivent plus etre pris en charge silencieusement.
- Deletion allowed: yes
- Replacement allowed: no
- User decision required if: un payload historique est prouve comme contrat externe actif; sinon la decision utilisateur bloque toute conservation legacy.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | yes | Les tests ConsultationMigration, consultationStore et prediction prouvent le runtime frontend. |
| Baseline Snapshot | yes | Les scans before/after bornent les symboles legacy supprimes. |
| Ownership Routing | yes | Les contrats canoniques doivent remplacer les chemins legacy. |
| Allowlist Exception | no | Aucune compatibilite legacy restante n'est autorisee. |
| Contract Shape | yes | Les types frontend de consultation/prediction et payload shapes sont touches. |
| Batch Migration | no | La suppression est pilotee par audit de surfaces legacy. |
| Reintroduction Guard | yes | Les symboles legacy ne doivent pas revenir. |
| Persistent Evidence | yes | L'audit d'extinction et les scans doivent etre persistants. |

## Runtime Source of Truth

- Primary source of truth:
  - AST guard in `frontend/src/tests/ConsultationMigration.test.tsx`
  - `frontend/src/tests/consultationStore.test.ts`
  - tests prediction existants autour des mappers et composants enrichis.
- Secondary evidence:
  - scans `rg` sur `frontend/src/types`, `frontend/src/pages`, `frontend/src/features/consultations`, `frontend/src/utils` et `frontend/src/components/prediction`.
- Static scans alone are not sufficient because:
  - les payloads canoniques doivent rester rendus par les tests runtime.

## Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/stories/CS-076-supprimer-compatibilites-runtime-frontend-restantes/frontend-runtime-legacy-before.md`.
- Comparison after implementation: `_condamad/stories/CS-076-supprimer-compatibilites-runtime-frontend-restantes/frontend-runtime-legacy-after.md`.
- Expected invariant: zero chemin runtime frontend conserve pour payload legacy apres implementation.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Consultation type key | contrat canonique `ConsultationType` | mapper `mapLegacyConsultationKey` |
| Consultation result blocks | structure resultat canonique | builder `buildLegacyBlocks` |
| Prediction enriched cards | mappers canoniques des payloads actuels | fallback older API versions / legacy maps |

## Allowlist / Exception Register

- Allowlist / Exception Register: not applicable
- Reason: aucune exception legacy runtime frontend n'est autorisee.

## Contract Shape

Contract type:
- Frontend runtime payload and TypeScript model.
Fields:
- Consultation keys, consultation result block shapes, prediction enriched-card fields.
Required fields:
- Only current canonical fields supported by active API/frontend tests.
Optional fields:
- Optional current payload fields documented by existing types only.
Status codes:
- Unchanged; no HTTP status is changed.
Serialization names:
- Legacy serialization names must be absent unless they are proven canonical by current types.
Frontend type impact:
- `frontend/src/types/consultation.ts` and prediction mapper types may change.
Generated contract impact:
- No generated client expected; repo inspection must prove no generated legacy field remains.

## Batch Migration Plan

- Batch Migration Plan: not applicable
- Reason: les surfaces sont supprimees par classification et scans exacts, pas par batch de valeurs.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Before runtime legacy baseline | `frontend-runtime-legacy-before.md` | Inventorier symboles, consommateurs et tests legacy. |
| After runtime legacy evidence | `frontend-runtime-legacy-after.md` | Prouver suppression, contrats canoniques et scans zero-hit. |
| Final validation evidence | `generated/10-final-evidence.md` | Persister commandes, resultats et risques residuels. |

## Reintroduction Guard

- Architecture guard against reintroduction: les symboles et commentaires de compatibilite runtime legacy echouent s'ils sont reintroduced.
- Deterministic source: forbidden symbols in tests frontend et scans `rg`.
- Required forbidden examples:
  - `isLegacy`
  - `mapLegacyConsultationKey`
  - `buildLegacyBlocks`
  - `normalizeLegacy`
  - `legacyMap`
  - `Fallback for older API versions`
- Guard evidence: `npm run test -- ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage design-system`.

## Current State Evidence

- Evidence 1: `_condamad/audits/frontend-design-system/2026-05-06-1031/02-finding-register.md#F-006` - compatibilites runtime restantes.
- Evidence 2: `_condamad/audits/frontend-design-system/2026-05-06-1031/01-evidence-log.md#E-012` - symboles consultation legacy actifs.
- Evidence 3: `_condamad/audits/frontend-design-system/2026-05-06-1031/01-evidence-log.md#E-014` - mappers prediction anciens payloads actifs.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - `RG-049` et `RG-050` consultes avant cadrage.

## Target State

- Les chemins runtime frontend ne contiennent plus de symboles, commentaires ou tests legacy.
- Les payloads canoniques actuels restent couverts.
- Les anciens payloads non canoniques ne sont plus normalises silencieusement.
- Les validations passent sans limitation.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-049` - toute surface legacy frontend restante doit etre retiree ou gardee contre retour.
  - `RG-050` - les guards anti-drift frontend doivent rester exacts.
- Non-applicable invariants:
  - `RG-044` - aucun namespace CSS n'est dans le scope attendu.
  - `RG-047` - aucun style inline n'est dans le scope attendu.
- Required regression evidence:
  - `npm run test -- ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage design-system`
  - scans zero-hit des symboles legacy runtime.
- Allowed differences:
  - suppression du support silencieux des payloads historiques non canoniques.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le baseline inventorie `E-012`. | Evidence profile: `baseline_before_after_diff`; command `rg -e mapLegacyConsultationKey -e isLegacy src`. |
| AC2 | Les symboles consultation legacy sont absents. | Command `rg -e isLegacy -e mapLegacyConsultationKey src/types src/pages`. |
| AC3 | Les mappers prediction n'ont plus de fallback legacy. | Evidence profile: `targeted_forbidden_symbol_scan`; command `rg -e normalizeLegacy -e legacyMap src/utils`. |
| AC4 | Les tests valident le contrat canonique. | Evidence profile: `runtime_guard`; command `npm run test -- ConsultationMigration consultationStore`. |
| AC5 | Le legacy runtime ne revient pas. | Evidence profile: `reintroduction_guard`; command `npm run test -- frontend/src/tests/ConsultationMigration.test.tsx`. |

## Implementation Tasks

- [ ] Task 1 - Capturer baseline des symboles et consommateurs legacy runtime. (AC: AC1)
- [ ] Task 2 - Supprimer les mappers/builders consultation legacy et adapter les consommateurs au contrat canonique. (AC: AC2, AC4)
- [ ] Task 3 - Supprimer les fallbacks/mappers anciens payloads prediction. (AC: AC3, AC4)
- [ ] Task 4 - Mettre a jour les tests pour prouver le contrat canonique sans vocabulaire legacy. (AC: AC4, AC5)
- [ ] Task 5 - Capturer after, scans zero-hit, lint et validations. (AC: AC2, AC3, AC5)

## Mandatory Reuse / DRY Constraints

- Reuse les types et mappers canoniques existants; ne pas creer un deuxieme chemin de normalisation.
- Do not duplicate payload conversion logic between pages and components.
- Shared abstraction allowed only if elle represente le contrat canonique actuel, pas une facade d'ancien payload.

## No Legacy / Forbidden Paths

- Forbidden: compatibility wrappers, transitional aliases, legacy imports, duplicate active implementations, silent fallback behavior.
- Forbidden symbols / paths:
  - `isLegacy`
  - `mapLegacyConsultationKey`
  - `buildLegacyBlocks`
  - `normalizeLegacy`
  - `legacyMap`
  - comments `Fallback for older API versions`, `Legacy codes`, `Fallback Legacy`

## Removal Classification Rules

- `canonical-active`: contrat frontend actuel consomme par production.
- `external-active`: ancien payload prouve par doc publique ou contrat client actif; bloque suppression silencieuse.
- `historical-facade`: mapper ou fallback qui preserve un ancien payload.
- `dead`: symbole sans consommateur actif.
- `needs-user-decision`: ambiguite restante apres scans; ne peut pas etre utilisee pour garder du legacy.

| Classification | Allowed decisions | Rule |
|---|---|---|
| `canonical-active` | `keep` | Must not be deleted. |
| `external-active` | `keep`, `needs-user-decision` | Must not be deleted without explicit user decision. |
| `historical-facade` | `delete`, `replace-consumer` | Must be deleted or consumers migrated. |
| `dead` | `delete` | Must be deleted. |
| `needs-user-decision` | `needs-user-decision` | Must block implementation until decision. |

## Removal Audit Format

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|

Allowed decisions: `keep`, `delete`, `replace-consumer`, `needs-user-decision`.

Audit output path:
- `_condamad/stories/CS-076-supprimer-compatibilites-runtime-frontend-restantes/frontend-runtime-legacy-after.md`

## Canonical Ownership

| Responsibility | Canonical owner | Non-canonical surfaces |
|---|---|---|
| Consultation payload shape | `frontend/src/types/consultation.ts` canonical types | legacy key mappers and legacy block builders |
| Prediction display payloads | current mapper contracts in `frontend/src/utils/*Mapper.ts` | older API fallback maps |
| Runtime validation evidence | focused Vitest tests | compatibility comments or manual assumptions |

## Delete-Only Rule

Items classified as removable must be deleted, not repointed.
Forbidden: wrapper, compatibility alias, active deprecated path, silent fallback, re-export or soft-disable behavior.

## External Usage Blocker

- `external-active` items must not be deleted without a user decision.
- If an item is classified as `external-active`, implementation must stop and
  record exact evidence, affected payload, and deletion risk. Without such proof,
  the user decision "Aucun legacy ne doit rester" applies.

## Generated Contract Check

- OpenAPI path absence: no backend OpenAPI path may change for this frontend runtime story.
- Generated artifact absence: if a generated frontend client, schema snapshot,
  route manifest or generated payload fixture exists after inspection, prove
  removed legacy fields and symbols are absent.
- Required evidence: scans for `isLegacy`, `mapLegacyConsultationKey`, `buildLegacyBlocks`, `normalizeLegacy`, `legacyMap` in generated artifacts when present.

## Files to Inspect First

- `_condamad/audits/frontend-design-system/2026-05-06-1031/01-evidence-log.md`
- `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md`
- `frontend/src/types/consultation.ts`
- `frontend/src/pages/ConsultationWizardPage.tsx`
- `frontend/src/pages/ConsultationResultPage.tsx`
- `frontend/src/features/consultations/components/ConsultationTypeStep.tsx`
- `frontend/src/features/consultations/components/ConsultationFormStep.tsx`
- `frontend/src/utils/bestWindowCardMapper.ts`
- `frontend/src/utils/domainRankingCardMapper.ts`
- `frontend/src/utils/dayClimateHeroMapper.ts`
- `frontend/src/utils/predictionI18n.ts`
- `frontend/src/utils/turningPointCardMapper.ts`
- `frontend/src/components/prediction/DayTimeline.tsx`
- `frontend/src/components/prediction/TurningPointsList.tsx`
- `frontend/src/tests/ConsultationMigration.test.tsx`
- `frontend/src/tests/consultationStore.test.ts`

## Expected Files to Modify

Likely files:
- `frontend/src/types/consultation.ts` - supprimer symboles legacy ou renommer en contrat canonique.
- `frontend/src/pages/ConsultationWizardPage.tsx` - consommer contrat canonique.
- `frontend/src/pages/ConsultationResultPage.tsx` - supprimer build legacy.
- `frontend/src/features/consultations/components/ConsultationTypeStep.tsx` - adapter types canoniques.
- `frontend/src/features/consultations/components/ConsultationFormStep.tsx` - adapter types canoniques.
- `frontend/src/utils/bestWindowCardMapper.ts` - retirer fallback older payload.
- `frontend/src/utils/domainRankingCardMapper.ts` - retirer fallback older payload.
- `frontend/src/utils/dayClimateHeroMapper.ts` - retirer fallback older payload.
- `frontend/src/utils/predictionI18n.ts` - retirer legacy codes.
- `frontend/src/utils/turningPointCardMapper.ts` - retirer fallback older payload.
- `frontend/src/components/prediction/DayTimeline.tsx` - consommer contrat canonique.
- `frontend/src/components/prediction/TurningPointsList.tsx` - consommer contrat canonique.

Likely tests:
- `frontend/src/tests/ConsultationMigration.test.tsx` - convertir vers contrat canonique ou supprimer assertions legacy.
- `frontend/src/tests/consultationStore.test.ts` - idem.
- tests prediction existants trouves par inspection - ajouter no-return coverage.

Files not expected to change:
- `frontend/src/app/routes.tsx` - routes admin couvertes par `CS-077`.
- `backend/app/main.py` - aucun backend dans le scope.
- `frontend/package.json` - aucune dependance requise.

## Dependency Policy

- New dependencies: none
- Dependency changes allowed only if explicitly listed here with justification.

## Validation Plan

```powershell
Push-Location frontend
npm run test -- ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage design-system
npm run lint
rg -n "isLegacy|mapLegacyConsultationKey|buildLegacyBlocks" src/types src/pages src/features src/tests
rg -n "Fallback for older API versions|Legacy codes|normalizeLegacy|legacyMap|buildTimelineFallbackSummary|Fallback Legacy" src/utils src/components/prediction -g "*.ts" -g "*.tsx"
rg -n "legacy|Legacy|compatibility|older API" src/types src/pages src/features/consultations src/utils src/components/prediction src/tests -g "*.ts" -g "*.tsx"
Pop-Location
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-076-supprimer-compatibilites-runtime-frontend-restantes/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Regression Risks

- Risk: suppression casse un payload encore emis par l'API courante.
  - Guardrail: tests runtime sur payload canonique et inspection des types.
- Risk: ancien support remplace par un fallback renomme.
  - Guardrail: scans zero-hit et No Legacy strict.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies unless explicitly listed.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not perform unrelated cleanup.
- No PASS with limitation is accepted.
- Respect the repository rule: every Python command must run after `.\.venv\Scripts\Activate.ps1`.

## References

- `_condamad/audits/frontend-design-system/2026-05-06-1031/03-story-candidates.md#SC-003`
- `_condamad/audits/frontend-design-system/2026-05-06-1031/02-finding-register.md#F-006`
- `_condamad/stories/regression-guardrails.md`
