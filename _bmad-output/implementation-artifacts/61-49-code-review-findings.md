# Code Review Findings - Story 61.49

Date: 2026-03-29
Story: `61-49-contrat-frontend-unique-plan-commercial-droits-effectifs`
Reviewer: Codex

## Findings

### Medium

1. `backend/app/api/v1/routers/entitlements.py`
Le routeur omettait silencieusement une feature prioritaire si `snapshot.entitlements`
ne la contenait pas. Le contrat frontend exige pourtant la présence stable des 4
features prioritaires. Correction appliquée: fallback défensif qui retourne une entrée
refusée (`granted=false`, `reason_code="feature_not_in_plan"`) au lieu de casser la
forme de réponse.

2. `backend/app/api/v1/schemas/entitlements.py`
La docstring AC4 était placée sur `EntitlementsMeData` alors que la tâche demandait de
documenter `EntitlementsMeResponse`. Correction appliquée: docstring ajoutée au schéma
de réponse, avec conservation du détail fonctionnel sur `EntitlementsMeData`.

3. Artefacts/story file list
La `File List` de la story ne reflétait pas l'ensemble réel du delta livré
(`test_entitlements_me_endpoint.py`, `sprint-status.yaml`, story elle-même). Correction
appliquée dans l'artefact de story.

### Low

1. Ruff
Quelques lignes et imports n'étaient pas conformes à Ruff dans les nouveaux tests.
Correction appliquée.

## Outcome

- Toutes les issues ci-dessus ont été corrigées.
- Le statut story reste `done`.
