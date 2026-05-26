# CS-308 — Revoir Wording beginner_summary Et client_interpretation

## Résumé

Revoir le wording affiché pour `beginner_summary_v1` et `client_interpretation_projection_v1` afin de garantir une lecture claire, non anxiogène, cohérente avec les disclaimers et adaptée au public B2C.

## Contexte

Le frontend affiche maintenant les projections publiques sur `/natal`. La preuve technique est acquise, mais le contenu présenté doit être évalué comme expérience utilisateur : clarté, ton, niveau de détail, absence de promesse excessive et cohérence avec la politique de disclaimer astrologique.

## Objectif

Auditer et ajuster le wording applicatif autour des deux projections B2C sans réécrire la logique de projection backend ni faire dépendre les disclaimers du payload LLM/projection.

## Préalable obligatoire

Relire :

- `docs/architecture/astrology-disclaimer-projection-policy.md`
- `frontend/src/i18n/natalChart.ts`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `backend/app/services/api_contracts/public/projections.py`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`

## Périmètre inclus

1. Inventorier tous les textes applicatifs visibles autour des projections sur `/natal`.
2. Vérifier que les titres distinguent clairement résumé débutant et interprétation client.
3. Vérifier que le wording ne promet pas une vérité médicale, financière, juridique ou déterministe.
4. Vérifier que le mode dégradé et les données approximatives sont expliqués simplement.
5. Ajuster les textes i18n applicatifs si nécessaire.
6. Ajouter ou ajuster les tests qui verrouillent les libellés critiques, disclaimers et états dégradés.
7. Documenter les formulations refusées ou reportées si elles nécessitent une décision produit.

## Hors périmètre

- Modifier les builders backend `beginner_summary_v1` ou `client_interpretation_projection_v1`.
- Modifier les prompts, providers ou payloads runtime.
- Faire venir les disclaimers depuis le payload de projection.
- Ajouter une personnalisation par plan non déjà prévue.
- Refonte visuelle de `/natal`.

## Critères d'acceptation

1. Les textes applicatifs des deux projections sont inventoriés.
2. Les titres et descriptions distinguent clairement les deux niveaux de lecture.
3. Les disclaimers restent dans l'app et sont testés.
4. Les états degraded/empty/error/entitlement ont un wording explicite et non technique.
5. Aucun wording ne présente l'astrologie comme conseil médical, juridique, financier ou certitude déterministe.
6. Les tests frontend ciblés passent.
7. Les changements de wording sont documentés dans la preuve finale.

## Validation attendue

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation astrology-i18n natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run
rg -n "medical|juridique|financier|garanti|certain|diagnostic|traitement" src
```

## Dépendances

- CS-303.
- CS-307 si l'audit UX révèle déjà des problèmes de hiérarchie textuelle.

## Risques

Le risque principal est de corriger le wording applicatif tout en laissant le payload backend produire un contenu ambigu. Si le payload lui-même pose problème, créer une story backend/content séparée au lieu de masquer le sujet côté UI.
