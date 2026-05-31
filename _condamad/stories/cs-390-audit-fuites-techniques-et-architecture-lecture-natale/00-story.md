# Story CS-390 audit-fuites-techniques-et-architecture-lecture-natale: Auditer La Lecture Natale Publique
Status: done

## Trigger / Source

- Source type: audit
- Source reference: `_story_briefs/cs-390-audit-fuites-techniques-et-architecture-lecture-natale.md`
- Reason for change: la page `/natal` mélangeait narration publique, justification astrologique et détails experts.

## Objective

Produire un audit fini de `/natal` et une architecture cible en trois couches pour guider CS-391 à CS-395.

## Target State

- Le rapport inventorie chaque bloc public et ses états.
- Chaque surface est classée par lecteur cible et décision.
- Les cinq chapitres narratifs et les owners cibles sont documentés.
- La preuve navigateur est rattachée au rapport CS-390 et à la QA CS-395.

## Current State Evidence

- Evidence 1: `_story_briefs/cs-390-audit-fuites-techniques-et-architecture-lecture-natale.md` - brief source lu.
- Evidence 2: `_condamad/reports/cs-390-audit-architecture-lecture-natale.md` - rapport d'audit produit.
- Evidence 3: `_condamad/stories/regression-guardrails.md` - invariants consultés avant cadrage.
- Evidence 4: `_condamad/stories/story-status.md` - tracker consulté pour le numéro `CS-390`.

## Domain Boundary

- Domain: natal-public-reading-audit
- In scope:
  - Audit documentaire de la composition publique `/natal`.
  - Classification des fuites techniques et architecture cible.
  - Carte de dépendances CS-391 à CS-395.
- Out of scope:
  - Code React, CSS, prompts, schémas backend, calculs astrologiques et entitlements.
- Explicit non-goals:
  - Aucun delta applicatif.
  - Aucun changement de calcul astrologique.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: aucun archétype supporté ne couvre exactement un audit documentaire de composition publique.
- Behavior change allowed: no
- Behavior change constraints:
  - Produire uniquement le rapport d'audit.
- Deletion allowed: no
- Replacement allowed: no
- User decision required if: une décision produit de lecteur cible reste ambiguë.

Additional validation rules:
- Conserver le rapport d'audit versionné et vérifier les scans de vocabulaire public.

## Required Contracts

| Contract | Required | Reason |
|---|---:|---|
| Runtime Source of Truth | no | L'audit décrit le baseline avant delta applicatif. |
| Baseline Snapshot | no | Le rapport décrit l'état observé sans créer de mesure comparative durable. |
| Ownership Routing | no | Le rapport n'introduit aucune règle de routage. |
| Allowlist Exception | no | Aucun allowlist n'est requis. |
| Contract Shape | no | Le rapport consomme le contrat public sans le modifier. |
| Batch Migration | no | Aucune migration n'est autorisée. |
| Reintroduction Guard | yes | Les scans empêchent le retour des termes interdits. |
| Persistent Evidence | yes | Le rapport doit rester versionné. |

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Chaque bloc public possède une décision. | Evidence profile: json_contract_shape; `python` vérifie les sections du rapport. |
| AC2 | Les trois lecteurs cibles sont distingués. | Evidence profile: json_contract_shape; `rg -n "débutant|Astrologue" _condamad/reports`. |
| AC3 | Les composants hors vue principale sont listés. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "NatalLifeDomains" _condamad/reports`. |
| AC4 | Les détails experts sont routés vers le mode astrologue. | Evidence profile: json_contract_shape; `rg -n "NatalAstrologerMode" _condamad/reports`. |
| AC5 | Les cinq chapitres cibles sont définis. | Evidence profile: json_contract_shape; `rg -n "vocation" _condamad/reports`. |
| AC6 | La QA responsive est bornée. | `rg -n "QA locale rejouée|Captures authentifiées" _condamad/reports/cs-395-non-regression-lecture-natale-publique.md`. |

## Implementation Tasks

- [x] Task 1: Inventorier les blocs visibles et leurs états. (AC: AC1)
- [x] Task 2: Classer les surfaces par lecteur et décision. (AC: AC2, AC3, AC4)
- [x] Task 3: Définir les cinq chapitres et la carte CS-391 à CS-395. (AC: AC5)
- [x] Task 4: Rattacher les constats navigateur au rapport. (AC: AC6)

## Mandatory Reuse / DRY Constraints

- Réutiliser le rapport CS-390 comme source de cadrage des stories suivantes.
- Ne pas recréer un second rapport concurrent.

## No Legacy / Forbidden Paths

- Aucun wrapper legacy historique ne doit être proposé.
- Aucun chemin compatibility ne doit être ajouté.
- Aucun fallback public ne doit être conservé par inertie.

## Regression Guardrails

- Applicable invariants: `RG-071`, `RG-073`, `RG-129`, `RG-150`, `RG-151`.
- Required regression evidence: `pnpm --dir frontend test -- NatalChartPage natalInterpretation NatalAstrologerMode`.
- Allowed differences: aucun delta applicatif.

## Files to Inspect First

- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/features/natal-chart/NatalAstrologerMode.tsx`

## Expected Files to Modify

Likely files:

- `_condamad/reports/cs-390-audit-architecture-lecture-natale.md` - rapport d'audit.

Likely tests:

- `frontend/src/tests/NatalChartPage.test.tsx` - témoin applicatif lu par la QA finale.

Files not expected to change:

- `backend/app/**` - hors scope.
- `frontend/src/**` - hors scope.

## Dependency Policy

- New dependencies: none.
- Justification: aucun changement de dépendance n'est autorisé.

## Validation Plan

- VC1: `pnpm --dir frontend test -- NatalChartPage natalInterpretation NatalAstrologerMode`
- VC2: `pnpm --dir frontend lint`
- VC3: `rg -n "dominant_topics|dominant_axes|narrative_priorities" frontend/src/features/natal-chart`

## Regression Risks

- Le rapport pourrait omettre une surface publique ; AC1 et la matrice du rapport bornent ce risque.
- La capture mobile post-patch reste à rejouer ; CS-395 archive les preuves disponibles et les gardes automatisés.

## Reintroduction Guard

- Architecture guard: le scan de vocabulaire échoue si une surface technique interdite est reintroduced dans la lecture publique.

## Baseline / Before-After Rule

- Baseline artifact before implementation: `_condamad/reports/cs-390-audit-architecture-lecture-natale.md`.
- Comparison after implementation: `pnpm --dir frontend test -- NatalChartPage natalPublicDomGuard`.
- Expected invariant: la lecture publique expose le fil narratif et réserve les détails experts au mode astrologue.

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Audit public | `_condamad/reports/cs-390-audit-architecture-lecture-natale.md` | Conserver l'inventaire et la cible. |
| Validation finale | `_condamad/stories/cs-390-audit-fuites-techniques-et-architecture-lecture-natale/generated/10-final-evidence.md` | Archiver les commandes exécutées. |

## Generated Contract Check

- Non applicable: aucun contrat généré n'est modifié par cet audit.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior.

## References

- `_story_briefs/cs-390-audit-fuites-techniques-et-architecture-lecture-natale.md`
- `_condamad/reports/cs-390-audit-architecture-lecture-natale.md`
- `_condamad/stories/regression-guardrails.md`
