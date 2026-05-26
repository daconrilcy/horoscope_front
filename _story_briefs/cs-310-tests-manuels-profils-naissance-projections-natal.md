# CS-310 — Tests Manuels Sur Plusieurs Profils De Naissance Pour /natal

## Résumé

Tester manuellement `/natal` avec plusieurs profils de naissance représentatifs afin de vérifier la robustesse utilisateur des projections B2C.

## Contexte

Les tests automatisés prouvent le contrat technique, mais les projections astrologiques doivent être vérifiées sur plusieurs combinaisons réelles de données de naissance : avec heure précise, sans heure, lieux différents, profils incomplets et cas limites. Cette story produit une preuve QA orientée expérience réelle.

## Objectif

Constituer un petit jeu de profils de naissance non sensibles, exécuter `/natal` pour chacun, puis documenter les résultats visibles, erreurs, modes dégradés et anomalies.

## Préalable obligatoire

Relire :

- `_condamad/stories/CS-302-test-astrology-projections-endpoint-real-conditions/evidence/response-samples.json`
- `_condamad/stories/CS-303-connect-b2c-frontend-to-astrology-projections/evidence/frontend-after.md`
- `_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence/browser-qa-ledger.json`
- `frontend/src/pages/NatalChartPage.tsx`
- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `backend/app/services/api_contracts/public/projections.py`

## Périmètre inclus

1. Définir au moins cinq profils de naissance de test non sensibles et non réels si possible.
2. Inclure un profil avec heure précise, un sans heure, un avec lieu étranger, un avec donnée incomplète contrôlée et un profil standard.
3. Exécuter `/natal` ou une simulation navigateur équivalente pour chaque profil.
4. Vérifier les projections, disclaimers, erreurs, degraded mode et absence d'exposition de données sensibles.
5. Capturer un ledger manuel avec résultat, captures optionnelles et anomalies.
6. Transformer les anomalies reproductibles en tests automatisés ou en stories séparées.
7. Documenter les limites liées aux données de test et à l'absence éventuelle de compte utilisateur réel.

## Hors périmètre

- Utiliser des données personnelles réelles sans nécessité.
- Ajouter une base de données de fixtures permanente contenant des données sensibles.
- Modifier le calcul astrologique métier sauf bug bloquant prouvé.
- Refaire l'UI `/natal`.
- Ajouter des tests E2E fragiles sans owner clair.

## Critères d'acceptation

1. Le jeu de profils de naissance est documenté avec justification de couverture.
2. Chaque profil a un résultat manuel ou navigateur traçable.
3. Le profil sans heure déclenche un affichage degraded ou approximatif compréhensible.
4. Les erreurs ou données incomplètes sont gérées sans crash UI.
5. Aucun prompt, provider payload, replay payload ou donnée admin n'est visible.
6. Les anomalies reproductibles sont soit corrigées, soit transformées en follow-up explicite.
7. Les validations frontend ciblées et backend projection pertinentes passent.

## Validation attendue

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi
```

Pour les contrôles backend :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q tests\api\test_projection_real_conditions.py tests\api\test_projection_endpoint.py --tb=short
```

## Dépendances

- CS-302.
- CS-303.
- CS-306.

## Risques

Le risque principal est de confondre QA produit et validation astrologique subjective. Cette story vérifie la robustesse, la clarté et la sécurité d'affichage, pas la vérité interprétative des contenus.
