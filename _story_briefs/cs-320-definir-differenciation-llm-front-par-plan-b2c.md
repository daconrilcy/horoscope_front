# CS-320 — Définir La Différenciation LLM Et Front Par Plan B2C

## Résumé

Définir le contrat produit/technique qui différencie `free`, `basic` et `premium` sans bloquer les calculs astrologiques ni l'existence des interprétations. Tous les plans exécutent les calculs et produisent les interprétations; la valeur commerciale varie par les données transmises au LLM, la profondeur rédactionnelle et les sections affichées en frontend.

## Contexte

La décision produit CS-315 a été réalignée :

- `beginner_summary_v1` est disponible pour `free`, `basic` et `premium`.
- `client_interpretation_projection_v1` est disponible pour `free`, `basic` et `premium`.
- Le backend reste source d'exécution et d'autorisation.
- React ne possède pas de matrice d'entitlement locale.
- La différenciation porte sur la richesse LLM/rédactionnelle et sur l'affichage front.

Source :

- `docs/architecture/natal-projection-plan-matrix-product-decision.md`
- `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`
- `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/generated/10-final-evidence.md`

## Objectif

Créer un contrat explicite de différenciation par plan pour les projections B2C `/natal`, couvrant :

- les entrées LLM autorisées par plan ;
- la profondeur rédactionnelle attendue ;
- la précision et le niveau de détail ;
- les sections frontend visibles ou masquées ;
- les tests empêchant une régression vers un blocage de calcul ou une matrice React locale.

## Préalable obligatoire

Relire :

- `docs/architecture/natal-projection-plan-matrix-product-decision.md`
- `_story_briefs/cs-315-follow-up-backend-projection-plan-divergence.md`
- `_condamad/stories/CS-315-product-plan-matrix-signoff-natal-projections/generated/10-final-evidence.md`
- `_condamad/stories/CS-317-cloturer-cs315-final-evidence-validation-runtime/generated/10-final-evidence.md`
- `_condamad/stories/CS-319-natal-react-entitlement-matrix-guard/generated/10-final-evidence.md`
- `backend/app/services/api_contracts/public/projections.py`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`

## Périmètre inclus

1. Documenter un contrat `EditorialDepthProfile` ou équivalent pour `free`, `basic`, `premium`.
2. Définir quelles familles de faits structurés et `evidence_refs` peuvent alimenter le LLM selon le plan.
3. Définir les sections frontend visibles, résumées ou masquées par plan.
4. Préserver l'invariant : les calculs et interprétations existent pour tous les plans.
5. Définir les validations backend/frontend à ajouter dans les stories d'implémentation suivantes.
6. Identifier les fichiers owners et les non-goals pour éviter une implémentation ad hoc.

## Hors périmètre

- Bloquer `client_interpretation_projection_v1` pour `free` ou `basic`.
- Ajouter une matrice d'entitlement locale dans React.
- Modifier Stripe, pricing, checkout ou subscription.
- Implémenter immédiatement le prompt LLM ou le rendu front si le contrat n'est pas encore validé.
- Changer les calculs astrologiques.

## Critères d'acceptation

1. Le contrat nomme explicitement `free`, `basic`, `premium`.
2. Le contrat précise que tous les plans exécutent les calculs et interprétations.
3. Le contrat décrit les différences d'entrées LLM par plan.
4. Le contrat décrit les différences de profondeur rédactionnelle par plan.
5. Le contrat décrit les différences d'affichage frontend par plan.
6. Le contrat nomme les owners backend/LLM/frontend pour les futures stories d'implémentation.
7. Les validations futures empêchent un retour à une restriction d'accès par plan ou à une matrice React locale.

## Validation attendue

Documentation :

```powershell
rg -n "free|basic|premium|EditorialDepthProfile|LLM|frontend|calculs|interpretations" docs _story_briefs
```

Frontend guard existant :

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards natalInterpretation NatalChartPage natalChartApi
```

Backend accès complet :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q tests\api\test_projection_real_conditions.py tests\api\test_projection_endpoint.py --tb=short
```

## Risques

Le risque principal est de confondre différenciation commerciale et restriction d'exécution. La story doit verrouiller l'invariant : tout est calculé et interprété pour tous les plans; seuls la sélection, la rédaction et l'affichage varient.
