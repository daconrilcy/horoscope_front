# CS-305 — Stabilize Frontend Full Vitest Suite After Projection Wiring

## Résumé

Rendre la suite frontend complète `vitest run` verte après CS-303 afin de lever la limitation qui empêche le rapport CS-302 à CS-304 d'être marqué `Delivered`.

## Contexte

Le rapport `_condamad/reports/CS-302-CS-304-delivery-report.md` classe l'initiative en `Partially delivered` parce que CS-303 a une revue d'implémentation `CLEAN` et des tests ciblés verts, mais la suite frontend complète échoue encore avec 19 échecs déclarés non liés dans les domaines dashboard, daily horoscope, shortcuts et consultations/localisation.

Cette story doit traiter la dette de validation, pas modifier le comportement de projection B2C livré par CS-303.

## Objectif

Identifier, corriger ou classifier formellement tous les échecs de la suite frontend complète afin que `node .\scripts\run-vite-logged.mjs vitest vitest run` passe sans limitation pour le périmètre frontend.

## Préalable obligatoire

Relire :

- `_condamad/reports/CS-302-CS-304-delivery-report.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/10-final-evidence.md`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/generated/11-code-review.md`
- `frontend/src/tests/**`
- `frontend/scripts/run-vite-logged.mjs`

## Périmètre inclus

1. Reproduire la suite frontend complète et capturer la liste exacte des tests en échec.
2. Distinguer les échecs réellement préexistants des régressions causées par CS-303, avec preuve.
3. Corriger les tests ou le code frontend lorsque l'échec révèle une régression réelle.
4. Mettre à jour les fixtures, mocks ou traductions uniquement si elles sont la source prouvée de l'échec.
5. Préserver le comportement CS-303 : consommation via API centrale, états projection, disclaimers app-owned, aucun secret ou champ interne rendu.
6. Ajouter une preuve finale qui montre la suite complète frontend verte.
7. Mettre à jour les preuves CS-303 ou le rapport de livraison uniquement si la correction change leur statut de validation.

## Hors périmètre

- Refaire l'UI `/natal`.
- Modifier le backend projection.
- Supprimer ou ignorer des tests pour obtenir un vert artificiel.
- Marquer des échecs comme non liés sans preuve de reproduction.
- Ajouter une dépendance frontend sans justification stricte.
- Changer les contrats API publics.

## Critères d'acceptation

1. La commande frontend complète échoue initialement ou la preuve explique pourquoi elle est déjà verte.
2. Chaque échec initial est corrigé ou classifié avec une preuve concrète.
3. `pnpm lint` passe dans `frontend`.
4. Les tests ciblés CS-303 passent toujours.
5. `node .\scripts\run-vite-logged.mjs vitest vitest run` passe sans échec.
6. Aucun direct `fetch` vers `/v1/astrology/projections`, style inline ou exposition de champ interne n'est introduit.
7. La preuve finale indique si le rapport CS-302 à CS-304 peut retirer la limitation de suite frontend complète.

## Validation attendue

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation
node .\scripts\run-vite-logged.mjs vitest vitest run component-architecture-guards NatalChartPage natalChartApi
node .\scripts\run-vite-logged.mjs vitest vitest run
rg -n "fetch\\(.*/v1/astrology/projections|provider_response|raw_runtime|replay_snapshot|admin_answer_audit|expert_technical_projection_v1|astrology_full_data_v1" src
```

## Dépendances

- CS-303.
- Rapport `_condamad/reports/CS-302-CS-304-delivery-report.md`.

## Risques

Le risque principal est de masquer des régressions frontend générales sous l'étiquette "non lié". Cette story doit rendre la suite complète exploitable comme preuve, pas seulement protéger les tests ciblés de CS-303.
