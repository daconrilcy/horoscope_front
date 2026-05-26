# CS-317 — Clôturer CS-315 Avec Final Evidence Et Validation Runtime

## Résumé

Clôturer proprement CS-315, qui possède déjà un document de décision produit, mais reste `ready-to-dev` sans `generated/10-final-evidence.md` ni preuves runtime backend/frontend complètes.

## Contexte

Le rapport `_condamad/reports/CS-312-CS-316-delivery-report.md` classe CS-315 en `Implemented but not validated`.
Les artefacts suivants existent déjà :

- `docs/architecture/natal-projection-plan-matrix-product-decision.md`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/source-alignment.md`

Mais il manque :

- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md`
- une revue d'implémentation CS-315 réelle ;
- le passage effectif des validations runtime backend/frontend ;
- l'alignement final des statuts story et registre.

## Objectif

Transformer CS-315 d'un artefact produit partiellement validé en story CONDAMAD clôturée, avec preuves runtime et final evidence.

## Préalable obligatoire

Relire :

- `_condamad/reports/CS-312-CS-316-delivery-report.md`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/00-story.md`
- `docs/architecture/natal-projection-plan-matrix-product-decision.md`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/validation.txt`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/evidence/source-alignment.md`
- `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md`
- `backend/tests/api/test_projection_authorization.py`
- `frontend/src/tests/natalInterpretation.test.tsx`

## Périmètre inclus

1. Générer ou compléter les fichiers capsule CS-315 manquants si nécessaire.
2. Exécuter les validations backend/frontend explicitement listées par CS-315.
3. Créer `generated/10-final-evidence.md` avec AC-by-AC evidence.
4. Remplacer ou compléter `generated/11-code-review.md` par une vraie revue d'implémentation, pas seulement une revue éditoriale.
5. Mettre `00-story.md` et `_condamad/stories/story-status.md` à `done` uniquement si les validations passent.
6. Documenter tout écart produit/backend par un brief séparé au lieu de modifier React.

## Hors périmètre

- Modifier la politique backend d'entitlement.
- Ajouter une matrice de droits dans React.
- Modifier Stripe, pricing, checkout, subscription, DB ou migrations.
- Réécrire la décision produit CS-315 sans preuve de divergence.

## Critères d'acceptation

1. CS-315 possède `generated/10-final-evidence.md`.
2. `generated/11-code-review.md` contient une revue d'implémentation CLEAN ou les findings restants.
3. Les tests backend d'autorisation projection passent avec le venv actif.
4. Les tests frontend natal projection passent.
5. Les scans prouvent que React ne contient pas de matrice locale free/basic/premium.
6. Les statuts CS-315 story et registre sont cohérents avec le résultat réel.
7. Le rapport CS-312-CS-316 peut être reclassé sans gap CS-315.

## Validation attendue

Depuis la racine, avant toute commande Python :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q tests\api\test_projection_authorization.py tests\api\test_projection_endpoint.py --tb=short
```

Frontend :

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi
```

Scans :

```powershell
rg -n "free.*basic.*premium|accepted_matrix|entitlement matrix" frontend/src
rg -n "decision_id|decision_date|owner|accepted_matrix|implementation_source|frontend_policy|divergence_policy" docs/architecture/natal-projection-plan-matrix-product-decision.md
```

Capsule :

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents\skills\condamad-dev-story\scripts\condamad_validate.py _condamad\stories\CS-315-product-plan-matrix-signoff-natal-projections
```

## Risques

Le risque principal est de traiter le document produit comme une clôture complète alors que les validations runtime restent absentes. La story doit fermer l'évidence, pas réimplémenter la matrice.
