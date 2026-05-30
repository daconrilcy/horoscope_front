# CS-400 - Cloturer La QA Live Richesse Et Non-Regression De La Lecture Natale

<!-- Commentaire global: ce brief cadre la validation de cloture des corrections de lecture natale. -->

## Resume

Executer une QA de cloture backend, frontend et navigateur apres CS-396 a CS-399. Mettre a
jour le rapport live CS-390/395, verifier Free, Basic et Premium et verrouiller les nouveaux
invariants contre les chapitres dupliques, les sources vides, la consommation injustifiee de
quota et le retour du rendu legacy.

## Contexte

Le rapport live actuel indique encore que la narrative n'apparait jamais. La situation a
evolue: la narrative est visible, mais elle peut etre artificiellement paddee, vide de
sources et debitée sur le quota Basic lifetime. La cloture doit remplacer l'ancien constat
par des preuves authentifiees et reproductibles.

## Objectif

Prouver:

```text
Free = experience courte explicite
Basic = 5 chapitres distincts + sources + quota correct
Premium = profondeur superieure + mode astrologue preserve
UI = accordeons narratifs modernes, aucun fallback legacy
```

## Perimetre inclus

1. Mettre a jour `_condamad/reports/cs-390-395-qa-live-natal-ecarts-restant.md`.
2. Produire `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md`.
3. Tester Free, Basic et Premium sur API et navigateur.
4. Tester desktop et mobile, accordéons, sources, actions, historique, PDF et mode astrologue.
5. Tester une regeneration corrective Basic historiquement invalide.
6. Verifier qu'un rejet editorial ne consomme pas de quota.
7. Verifier les metriques de couverture editoriale Basic.
8. Verifier les lignes `RG-155` a `RG-158` creees par CS-396 a CS-399 et leurs guards
   deterministes.
9. Capturer les screenshots de preuve dans `output/playwright/`.

## Hors perimetre

- Ajouter de nouvelles fonctionnalites.
- Elargir les allowlists de fuite technique.
- Declencher des appels provider reels hors environnement de QA controle.
- Modifier les calculs astrologiques.

## Sources obligatoires

- `_condamad/reports/cs-390-395-qa-live-natal-ecarts-restant.md`
- `_condamad/stories/regression-guardrails.md`
- `backend/docs/narrative-natal-reading-v1-contract.md`
- `backend/tests/unit/test_narrative_natal_reading_v1.py`
- `backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
- `frontend/src/tests/natalNarrativeReading.test.tsx`
- `frontend/src/tests/natalPublicDomGuard.test.tsx`
- `frontend/src/tests/NatalChartPage.test.tsx`

## Livrable attendu

Le rapport CS-400 doit contenir:

1. Baseline du defaut du 2026-05-30.
2. Matrice Free/Basic/Premium.
3. Matrice desktop/mobile.
4. Preuves quota valide, rejet non debite et remediation Basic.
5. Preuves de richesse: chapitres distincts, familles couvertes et sources publiques.
6. Screenshots avant/apres.
7. Commandes executees et resultats.
8. Nouveaux invariants du registre.
9. Risques residuels explicites.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-047`, `RG-052`, `RG-071`, `RG-073`, `RG-129` - frontiere frontend preservee.
  - `RG-149`, `RG-150`, `RG-152` - pipeline natal moderne et rejets preserves.
  - `RG-153`, `RG-154` - composition publique et denylist DOM preservees.
  - `RG-155` a `RG-158` - integrite semantique, richesse editoriale, quota transactionnel et
    accordeons narratifs modernes preserves.
- Required regression evidence:
  - `pytest -q backend/tests -k "natal and (narrative or rejected or quota or theme_astral)"`
  - `pytest -q --long backend/app/tests/integration/test_natal_chart_long_entitlement.py backend/app/tests/integration/test_natal_interpretation_endpoint.py`
  - `pnpm --dir frontend test -- NatalChartPage natalNarrativeReading natalPublicDomGuard NatalAstrologerMode`
  - `pnpm --dir frontend lint`
  - `pnpm --dir frontend build`
  - QA navigateur authentifiee Free/Basic/Premium desktop/mobile.
- Allowed differences:
  - Les lectures historiques invalides demandent une regeneration corrective.
  - Les chapitres narratifs utilisent une divulgation progressive moderne.

## Criteres d'acceptation

1. Le rapport live ancien est actualise et ne pretend plus que la narrative est absente.
2. Basic affiche cinq chapitres distincts et des sources non vides.
3. Un rejet editorial ne consomme aucune unite de quota.
4. Une lecture historique invalide peut etre regeneree gratuitement une seule fois de facon
   idempotente.
5. Les accordéons modernes fonctionnent en desktop et mobile.
6. Free, Basic et Premium sont verifies sans fuite technique publique.
7. Le registre contient les nouveaux invariants et leurs preuves executables.
8. Aucun risque critique ou majeur n'est laisse sans story de suivi explicite.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests --tb=short -k "natal and (narrative or rejected or quota or theme_astral)"
python -B -m pytest -q --long app/tests/integration/test_natal_chart_long_entitlement.py app/tests/integration/test_natal_interpretation_endpoint.py --tb=short
```

Frontend:

```powershell
cd frontend
pnpm test -- NatalChartPage natalNarrativeReading natalPublicDomGuard NatalAstrologerMode
pnpm lint
pnpm build
```

## Dependances

- CS-396.
- CS-397.
- CS-398.
- CS-399.

## Risques

Le risque principal est une validation nominale sur fixtures sans preuve live. La story doit
inclure une QA navigateur authentifiee et distinguer clairement appel provider controle,
fixture et simple relecture persistee.
