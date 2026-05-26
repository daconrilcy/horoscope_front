# CS-314 — Ajouter Un Pack De Screenshots Navigateur Pour Les Profils CS-310

## Résumé

CS-310 est livrée avec une preuve navigateur équivalente, mais sans nouvelles captures. Cette story ajoute une passe navigateur réelle et des screenshots pour les cinq profils synthétiques CS-310.

## Contexte

`_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/generated/10-final-evidence.md` indique que les captures navigateur nouvelles ont été sautées, avec une dépendance sur CS-306 et les tests ciblés. Le rapport consolidé classe ce point comme limite QA résiduelle.

## Objectif

Renforcer CS-310 par une preuve visuelle réelle, sans changer l'application sauf bug reproductible bloquant.

## Préalable obligatoire

Relire :

- `_condamad/reports/CS-307-CS-311-delivery-report.md`
- `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/profile-set.json`
- `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/manual-qa-ledger.json`
- `_condamad/stories/CS-310-tests-manuels-profils-naissance-projections-natal/evidence/browser-equivalent-notes.md`
- `frontend/src/pages/NatalChartPage.tsx`

## Périmètre inclus

1. Démarrer localement le frontend et le backend requis.
2. Se connecter avec l'utilisateur test si nécessaire.
3. Exécuter les cinq profils synthétiques existants de CS-310.
4. Capturer au moins une vue desktop et une vue mobile par catégorie critique, dont missing time et controlled incomplete.
5. Mettre à jour un ledger screenshot avec route, profil, viewport, état visible, résultat et chemin de capture.
6. Créer un follow-up brief si une anomalie reproductible apparaît.

## Hors périmètre

- Modifier les profils synthétiques sans justification.
- Valider subjectivement le contenu astrologique.
- Introduire une suite E2E permanente sans owner clair.
- Modifier backend/API sauf bug bloquant prouvé par capture et test.

## Critères d'acceptation

1. Un dossier de screenshots CS-310 existe sous le capsule de story.
2. Chaque profil a une trace navigateur réelle ou une justification explicite.
3. Les états degraded, controlled error, disclaimers et absence de surfaces sensibles sont visibles ou documentés.
4. Les anomalies sont soit absentes, soit converties en briefs `_story_briefs`.
5. Les validations ciblées frontend/backend restent passantes.

## Validation attendue

```powershell
cd frontend
pnpm lint
node .\scripts\run-vite-logged.mjs vitest vitest run natalInterpretation NatalChartPage natalChartApi
```

Pour le backend :

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -B -m pytest -q tests\api\test_projection_real_conditions.py tests\api\test_projection_endpoint.py --tb=short
```

## Risques

Le risque principal est de découvrir une divergence visuelle non couverte par les tests. Toute divergence doit être capturée, classée et transformée en correction ou follow-up explicite.
