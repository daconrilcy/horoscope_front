# CS-322 — Réconcilier Rapports Et Evidence Après Décisions Plan/Plausible

## Résumé

Mettre à jour les rapports et artefacts de clôture qui parlent encore d'une divergence backend/produit premium-only ou d'une cible Plausible/Matomo, alors que les décisions récentes sont désormais : tous les plans calculent/interprètent, la différenciation se fait LLM/front, et Plausible est la cible analytics de préparation.

## Contexte

Depuis CS-320 et CS-321 :

- `client_interpretation_projection_v1` reste disponible pour `free`, `basic`, `premium`.
- La différenciation commerciale porte sur les entrées LLM, la profondeur rédactionnelle et les sections front.
- Matomo n'est pas utilisé pour l'instant.
- Plausible est la cible de préparation analytics.

Certains artefacts antérieurs peuvent encore contenir :

- `Delivered with routed backend follow-up`
- `product/backend divergence`
- `premium-only`
- `Plausible/Matomo`
- `provider dashboard blocked`

## Objectif

Rendre les rapports et preuves de clôture cohérents avec les décisions courantes, sans modifier le runtime applicatif.

## Préalable obligatoire

Relire :

- `_condamad/reports/CS-312-CS-316-delivery-report.md`
- `docs/architecture/natal-projection-plan-matrix-product-decision.md`
- `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`
- `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md`
- `_story_briefs/cs-321-preparer-integration-plausible-analytics.md`
- `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/generated/10-final-evidence.md`
- `_condamad/stories/CS-318-valider-ingestion-analytics-provider-cs316/generated/10-final-evidence.md`

## Périmètre inclus

1. Mettre à jour le rapport CS-312-CS-316 pour retirer l'ancienne notion de divergence backend/produit premium-only.
2. Remplacer les mentions Plausible/Matomo par Plausible-first lorsque le contexte parle de suite produit.
3. Distinguer clairement :
   - clôture repo déjà obtenue ;
   - préparation Plausible à venir ;
   - différenciation LLM/front à spécifier.
4. Mettre à jour les evidence ou notes de clôture seulement si elles décrivent une décision désormais obsolète.
5. Ajouter un mini-journal de réconciliation sous le capsule de la story.

## Hors périmètre

- Modifier le backend ou le frontend runtime.
- Modifier les tests métier.
- Activer Plausible.
- Supprimer Matomo du code actif, qui est couvert par CS-323.
- Implémenter la différenciation LLM/front, couverte par CS-320.

## Critères d'acceptation

1. Le rapport CS-312-CS-316 ne présente plus la disponibilité de `client_interpretation_projection_v1` sur tous les plans comme une divergence.
2. Le rapport indique que le backend est aligné avec la décision produit d'exécuter calculs/interprétations pour tous les plans.
3. Les prochaines actions pointent vers CS-320 et CS-321/CS-323, pas vers un changement backend d'entitlement.
4. Les mentions Plausible/Matomo sont clarifiées : Plausible est la cible, Matomo n'est pas utilisé.
5. Aucun fichier applicatif runtime n'est modifié.
6. Les scans de cohérence ne trouvent plus d'ancienne formulation contradictoire dans les artefacts ciblés.

## Validation attendue

Scans de cohérence :

```powershell
rg -n "premium-only|refus.*free|refus.*basic|routed backend follow-up|product/backend divergence|Plausible/Matomo" _condamad/reports docs/architecture _story_briefs
rg -n "Plausible|Matomo|noop|client_interpretation_projection_v1|free|basic|premium" _condamad/reports/CS-312-CS-316-delivery-report.md docs/architecture/natal-projection-plan-matrix-product-decision.md _story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md
```

Diff :

```powershell
git diff --check
git diff --name-only -- _condamad/reports docs/architecture _story_briefs backend frontend
```

## Risques

Le risque principal est de réécrire l'histoire au lieu de clarifier la décision courante. Les anciennes preuves doivent rester compréhensibles, mais les rapports de clôture doivent refléter la décision produit actuelle.
