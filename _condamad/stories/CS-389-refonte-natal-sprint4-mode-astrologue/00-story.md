# Story CS-389 refonte-natal-sprint4-mode-astrologue: Refonte /natal Sprint 4 — Mode astrologue premium

Status: ready-to-dev

## Trigger / Source

- Source type: brief
- Source reference: demande utilisateur du 2026-05-29 — plan refonte `/natal` (couche expert)
- Selected mode: Repo-informed story
- Reason for change: les données professionnelles (secte, dignités, hayz, rejoicing,
  conditions avancées) ont de la valeur pour astrologues mais détruisent la lisibilité
  grand public; Sprint 4 les regroupe derrière « Afficher les détails techniques ».
- Source-alignment evidence: brief section 8 + Sprint 4 backlog; paradoxe 80 % calcul /
  20 % valeur visuelle résolu par mode astrologue sans perdre le moteur pro.

## Objective

Introduire le « mode astrologue » sur `/natal` : bouton « Afficher les détails techniques »
revelant panneau expert, listes planètes/maisons/aspects bruts et métadonnées avancées
(secte, dignités, hayz, rejoicing, conditions) — avec gate entitlement premium si requis,
sans recalcul frontend et sans réintroduire le bruit en vue principale par défaut.

## Domain Boundary

- Domain: frontend-natal-page
- In scope:
  - Toggle/bouton mode astrologue et container `NatalAstrologerMode`.
  - Réintégration conditionnelle `NatalExpertPanel` et blocs techniques retirés CS-386.
  - Gate UI entitlement (`multi_astrologer` ou règle produit documentée).
  - Persistance préférence session/local optionnelle si pattern existant.
  - i18n, CSS, tests Vitest toggle et rendu expert.
- Out of scope:
  - Nouvelles sections narratives Sprint 1-3 (CS-386 à CS-388).
  - Extension moteurs backend dignités/conditions/hayz.
  - Changements contrat API public JSON natal.
  - Refonte contenu interne `NatalExpertPanel` au-delà intégration mode.
- Explicit non-goals:
  - Pas de recalcul secte, hayz, scores (RG-129).
  - Pas de suppression des blocs expert du payload API.
  - Pas de dump prompt/provider LLM.

## Operation Contract

- Operation type: update
- Primary archetype: custom
- Archetype reason: feature toggle UX regroupant surfaces expert existantes.
- Behavior change allowed: constrained
- Behavior change constraints:
  - Vue principale post CS-386 reste sans bruit technique quand toggle off.
  - Toggle on réaffiche `NatalExpertPanel` et données brutes déplacées Sprint 1.
  - Gate premium documenté; free voit CTA upgrade, pas contenu expert tronqué trompeur.
- Deletion allowed: no
- Replacement allowed: yes
- User decision required if: entitlement exact du mode astrologue diffère de `multi_astrologer`.
- Additional validation rules:
  - Vitest prouve toggle off par défaut, gate premium et non-régression CS-380.
  - Scan `rg` interdit recalcul secte/hayz et styles inline statiques.

## Required Contracts

| Contract | Required | Reason |
|---|---|---|
| Runtime Source of Truth | yes | Vitest prouve toggle off/on et gate entitlement. |
| Baseline Snapshot | yes | Evidence before/after visibilité expert. |
| Ownership Routing | yes | Toggle owner feature; panel expert inchangé owner. |
| Allowlist Exception | no | Pas d'allowlist recalcul astrologique. |
| Contract Shape | no | Pas de changement shape API. |
| Batch Migration | no | Pas de migration. |
| Reintroduction Guard | yes | Interdire réapparition bruit technique sans toggle on. |
| Persistent Evidence | yes | Artefacts validation Sprint 4. |

## Runtime Source of Truth

- Primary source of truth:
  - Vitest/Testing Library sur `NatalAstrologerMode`, `NatalExpertPanel`, `NatalChartPage`.
  - `AST guard` via tests d'architecture natal-chart si présents.
- Secondary evidence:
  - scans `rg` interdisant recalcul secte/hayz côté React.
- Static scans alone are not sufficient for this story because:
  - Le toggle off/on et le gate premium doivent être prouvés au rendu.

## Baseline / Before-After Rule

- Baseline artifact before implementation:
  - `_condamad/stories/CS-389-refonte-natal-sprint4-mode-astrologue/evidence/before-astrologer-mode.txt`
- Comparison after implementation:
  - `_condamad/stories/CS-389-refonte-natal-sprint4-mode-astrologue/evidence/after-astrologer-mode.txt`
- Expected invariant:
  - Vue principale sans bruit technique quand toggle off; contrat JSON public inchangé.
  - CS-386 est deja implemente dans la branche; CS-387 et CS-388 restent preserves si presents.

## Ownership Routing Rule

| Responsibility type | Canonical owner | Forbidden destination |
|---|---|---|
| Toggle mode astrologue | `frontend/src/features/natal-chart/NatalAstrologerMode.tsx` | état toggle global unrelated |
| Panel expert | `NatalExpertPanel.tsx` | duplicate under pages |
| Gate premium | hooks entitlement existants | hardcode plan name |

## Persistent Evidence Artifacts

| Artifact | Path | Purpose |
|---|---|---|
| Validation output | `_condamad/stories/CS-389-refonte-natal-sprint4-mode-astrologue/evidence/validation.txt` | Preuve commandes frontend passées. |
| Before mode | `_condamad/stories/CS-389-refonte-natal-sprint4-mode-astrologue/evidence/before-astrologer-mode.txt` | Baseline visibilité expert. |
| After mode | `_condamad/stories/CS-389-refonte-natal-sprint4-mode-astrologue/evidence/after-astrologer-mode.txt` | Comparaison toggle on/off. |
| Review output | `_condamad/stories/CS-389-refonte-natal-sprint4-mode-astrologue/generated/11-code-review.md` | Revue automatique séparée. |

## Current State Evidence

- Evidence 1: `frontend/src/features/natal-chart/NatalExpertPanel.tsx` - panel expert complet.
- Evidence 2: `_condamad/stories/CS-386-refonte-natal-sprint1-comprehension-immediate/00-story.md` - masquage vue principale.
- Evidence 3: `frontend/src/hooks/useEntitlementSnapshot.ts` - variants billing existants.
- Evidence 4: `_condamad/stories/regression-guardrails.md` - registre consulté pour RG-129.
- Evidence 5: `_condamad/stories/story-status.md` - tracker consulté pour numéro CS-389.

## Target State

- Bouton visible « Afficher les détails techniques » / « Masquer les détails techniques ».
- Toggle off : aucune longitude brute, orbe effective, hayz, rejoicing, raw score,
  JSON dump, ni `NatalExpertPanel` visible (aligné CS-386).
- Toggle on + droit premium : panneau expert + listes planètes/maisons/aspects techniques
  + métadonnées calcul (reference_version, house system) regroupées.
- Toggle on sans droit : CTA upgrade cohérent billing; pas de fuite partielle scores.
- Accessibilité : `aria-expanded`, focus clavier, annonce screen reader.
- Tests : toggle, gate free/premium, non-régression CS-380 partial payloads.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-129` — panel expert et listes techniques consomment payload public uniquement.
  - `RG-124` — secte affichée depuis `dignities.sect`; pas recalcul React.
  - `RG-122` — hayz/rejoicing depuis `traditional_conditions` API.
  - `RG-047`, `RG-052` — CSS toggle sans inline statique.
  - `RG-071`, `RG-073` — ownership feature natal-chart.
  - CS-380 tolerance payloads partiels panel expert préservée.
- Needs-investigation invariants:
  - Entitlement exact mode astrologue — confirmer avec `useFeatureAccess` existant.
- Non-applicable examples:
  - `RG-150` — mode expert factuel; pas désérialisation rejected narratives.
  - `RG-018` — prompts LLM non touchés.
- Required regression evidence:
  - `pnpm --dir frontend test -- NatalAstrologerMode NatalExpertPanel NatalChartPage`
  - `pnpm --dir frontend lint`
  - `rg -n "DIURNAL_PLANETS|HAYZ_RULES|SECT_PLANETS" frontend/src/features/natal-chart`
- Allowed differences: copy bouton i18n; variante entitlement si validée produit.

## Acceptance Criteria

| AC | Requirement | Validation evidence required |
|---|---|---|
| AC1 | Le bouton « Afficher les détails techniques » est visible sur /natal. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalAstrologerMode`. |
| AC2 | Toggle off masque le panneau expert. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalChartPage`. |
| AC3 | Toggle on avec droit premium affiche `NatalExpertPanel`. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalAstrologerMode`. |
| AC4 | Toggle on sans droit premium affiche CTA upgrade. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalAstrologerMode`. |
| AC5 | Hayz provient du payload public. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalExpertPanel`. |
| AC6 | Payload partiel expert ne crash pas la page (CS-380). | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalExpertPanel`. |
| AC7 | Aucun style inline statique sur le toggle. | Evidence profile: targeted_forbidden_symbol_scan; `rg -n "style=" frontend/src/features/natal-chart/NatalAstrologerMode.tsx`. |
| AC8 | `aria-expanded` reflète l'état du panneau. | Evidence profile: json_contract_shape; `pnpm --dir frontend test -- NatalAstrologerMode`. |
| AC9 | Dossier evidence present. | Evidence profile: baseline_before_after_diff; `rg --files _condamad/stories/CS-389*/evidence`. |

## Implementation Tasks

- [ ] Task 1: Créer `NatalAstrologerMode` avec état toggle et gate entitlement. (AC: AC1, AC4, AC8)
- [ ] Task 2: Réintégrer `NatalExpertPanel` et blocs techniques sous toggle. (AC: AC2, AC3, AC5)
  - [ ] Subtask 2.1: Extraire listes planètes/maisons/aspects bruts depuis archive Sprint 1 ou composant dédié.
- [ ] Task 3: i18n, CSS, accessibilité bouton. (AC: AC7, AC8)
- [ ] Task 4: Tests non-régression CS-380 et evidence. (AC: AC6, AC9)

## Mandatory Reuse / DRY Constraints

- Reuse:
  - `NatalExpertPanel` intact (CS-380); `useFeatureAccess`, patterns CTA billing page.
  - Listes techniques déplacées CS-386 — réutiliser composants extraits si créés.
- Do not recreate:
  - Second panel expert parallel; logique hayz/secte duplicate.
- Shared abstraction allowed only if:
  - `NatalTechnicalDetails` wrapper purement presentational autour contenu existant.

## No Legacy / Forbidden Paths

- Forbidden unless explicitly approved:
  - legacy réaffichage du bruit technique sans toggle on
  - compatibility route parallèle `/natal/expert`
  - duplicate expert panel under `components/**`
  - silent fallback calcul secte/hayz si payload partiel
- Specific forbidden symbols / paths:
  - `DIURNAL_PLANETS`, `HAYZ_RULES`, `SECT_PLANETS` en frontend
  - `style=` inline statique

## Removal Classification Rules

- Removal classification: not applicable

## Removal Audit Format

- Removal audit: not applicable

## Delete-Only Rule

- Delete-only rule: not applicable

## External Usage Blocker

- External usage blocker:
  - CS-386 non implemente dans la branche cible.
  - Entitlement mode astrologue non confirme par produit ou hook existant.

## Generated Contract Check

- Generated contract check: not applicable
- Reason: pas de changement OpenAPI ou contrat public.

## Batch Migration Plan

- Batch migration plan: not applicable
- Reason: pas de migration multi-fichiers backend.

## Files to Inspect First

- `frontend/src/features/natal-chart/NatalExpertPanel.tsx`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/hooks/useEntitlementSnapshot.ts`
- `frontend/src/tests/NatalExpertPanel.test.tsx`
- `_condamad/stories/CS-386-refonte-natal-sprint1-comprehension-immediate/00-story.md`
- `_condamad/stories/CS-380-durcir-natal-expert-panel-contre-payloads-partiels/00-story.md`

## Expected Files to Modify

Likely files:

- `frontend/src/features/natal-chart/NatalAstrologerMode.tsx` — implementation-created path.
- `frontend/src/pages/NatalChartPage.tsx` — intégration toggle et sections techniques.
- `frontend/src/i18n/natalChart.ts` — libellés mode astrologue.
- `frontend/src/pages/NatalChartPage.css` — styles panneau replié/déplié.

Likely tests:

- `frontend/src/tests/NatalAstrologerMode.test.tsx` — implementation-created path.
- `frontend/src/tests/NatalChartPage.test.tsx` — toggle off par défaut.
- `frontend/src/tests/NatalExpertPanel.test.tsx` — non-régression CS-380.

Files not expected to change:

- `backend/app/**`
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx` — sauf props wrapper minimal.

## Dependency Policy

- New dependencies: none.
- Justification: no dependency changes are authorized.

## Validation Plan

```powershell
pnpm --dir frontend test -- NatalAstrologerMode NatalExpertPanel NatalChartPage
pnpm --dir frontend lint
pnpm --dir frontend build
rg -n "DIURNAL_PLANETS|HAYZ_RULES|SECT_PLANETS|DOMINANCE_WEIGHTS" frontend/src/features/natal-chart
Manual check: /natal par défaut sans bruit technique; toggle on révèle expert panel pour premium.
```

## Regression Risks

- Risk: bruit technique visible par défaut après régression toggle.
  - Guardrail: AC2 + test default off; reintroduction guard.
- Risk: crash panel expert sur payload partiel post CS-379/CS-380.
  - Guardrail: AC6 reprend tests CS-380.
- Risk: gate entitlement incorrect expose données premium.
  - Guardrail: AC4 tests free vs premium mockés.

## Dev Agent Instructions

- Implement only this story.
- Do not broaden the domain.
- Do not introduce new dependencies.
- Do not mark a task complete without validation evidence.
- If an AC cannot be satisfied, stop and record the blocker.
- Do not preserve legacy behavior for convenience.
- Do not bypass deletion through repointing, soft-disable, wrapper, alias, fallback, or re-export.

## References

- Brief utilisateur 2026-05-29 — section 8 mode astrologue et Sprint 4 backlog.
- CS-386 — masquage vue principale prérequis.
- CS-380 — robustesse panel expert.
- CS-387, CS-388 — sections narratives à préserver au-dessus du mode expert.
