# CS-315 — Faire Valider La Matrice Produit Des Plans Pour Les Projections /natal

## Résumé

CS-309 prouve techniquement la différenciation free/basic/premium en suivant les réponses backend, mais le ledger garde une limite produit sur la frontière commerciale exacte. Cette story obtient une validation produit explicite et l'inscrit dans la documentation attendue.

## Contexte

`_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/product-ambiguities.md` indique que la matrice UI est une preuve QA, pas une décision d'entitlement. Le rapport consolidé recommande un sign-off produit pour rendre l'implémentation parfaite côté alignement offre.

## Objectif

Transformer la matrice CS-309 en décision produit documentée, sans dupliquer la politique d'accès dans React.

## Préalable obligatoire

Relire :

- `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/plan-matrix-after.md`
- `_condamad/stories/CS-309-verifier-differenciation-free-basic-premium-projections-natal/evidence/product-ambiguities.md`
- `backend/tests/api/test_projection_authorization.py`
- `frontend/src/tests/natalInterpretation.test.tsx`

## Périmètre inclus

1. Documenter la matrice free/basic/premium officiellement acceptée pour `beginner_summary_v1` et `client_interpretation_projection_v1`.
2. Clarifier quelle équipe est owner de la décision produit.
3. Vérifier que les fixtures frontend CS-309 reflètent toujours les réponses backend.
4. Ajouter un court artefact de décision ou mettre à jour un document architecture/produit existant.
5. Si la décision diffère du comportement backend actuel, créer un brief backend séparé au lieu de corriger React localement.

## Hors périmètre

- Changer l'entitlement backend dans cette story.
- Ajouter une matrice de droits hardcodée dans React.
- Modifier Stripe, pricing, checkout ou abonnement.
- Réécrire les textes d'upsell au-delà de la décision de matrice.

## Critères d'acceptation

1. La matrice produit officielle est documentée avec owner et date.
2. Le document distingue décision produit et implémentation backend.
3. Les tests CS-309 restent backend-sourced et ne dupliquent pas la politique en React.
4. Toute divergence produit/backend devient un follow-up brief explicite.

## Validation attendue

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi
```

Pour le backend si une comparaison est nécessaire :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q tests\api\test_projection_authorization.py tests\api\test_projection_endpoint.py --tb=short
```

## Risques

Le risque principal est de transformer une décision commerciale en logique frontend. La règle reste: le frontend affiche les réponses backend, il ne décide pas des droits.
