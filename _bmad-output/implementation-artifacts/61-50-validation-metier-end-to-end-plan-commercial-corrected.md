# Story 61.50 corrigée après code review

## Portée de la correction

Revue corrective appliquée après l'implémentation initiale de la story
`61-50-validation-metier-end-to-end-plan-commercial`.

## Findings corrigés

1. Le test e2e partageait un état DB entre scénarios alors que l'AC2 exigeait
   une isolation SQLite in-memory par test.
2. Le contrat frontend aplati n'était pas verrouillé complètement:
   `quota_limit` et `quota_remaining` au top-level n'étaient pas assertés pour
   toute la matrice.
3. `docs/entitlements-validation-matrix.md` ne documentait pas tous les champs
   exigés par l'AC1 ni le comportement attendu de `GET /v1/entitlements/me`.
4. `docs/entitlements-operations.md` utilisait des commandes Python hors
   activation explicite du venv, en contradiction avec `AGENTS.md`.
5. `docs/entitlements-legacy-remnants.md` n'employait pas les statuts
   normalisés attendus et manquait de traçabilité par fichier.

## Correctifs appliqués

- Réécriture de `backend/app/tests/integration/test_entitlements_e2e_matrix.py`
  avec:
  - fixture DB fonctionnelle isolée,
  - classes de tests par plan,
  - assertions sur `plan_code`, `billing_status`, `granted`, `reason_code`,
    `access_mode`, `quota_limit`, `quota_remaining`, `variant_code`,
    `usage_states`,
  - scénario explicite `billing_inactive`,
  - scénario explicite `quota_exhausted` pour le vocabulaire frontend.
- Mise à jour de `docs/entitlements-validation-matrix.md` avec la matrice
  complète et le comportement API attendu.
- Mise à jour de `docs/entitlements-operations.md` avec commandes PowerShell
  conformes au venv et procédure de validation.
- Mise à jour de `docs/entitlements-legacy-remnants.md` avec inventaire
  catégorisé: `à supprimer`, `conservé intentionnellement`, `dette documentée`.
- Mise à jour du Dev Agent Record dans l'artefact principal.

## Statut

- Story: `done`
- Sprint tracking: reste `done`
