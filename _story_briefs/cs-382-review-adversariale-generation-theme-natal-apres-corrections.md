# CS-382 - Review Adversariale Generation Theme Natal Apres Corrections

<!-- Commentaire global: ce brief cadre la revue adversariale des corrections de generation natale et de non-regression prompt. -->

## Resume

Auditer adversarialement les corrections issues de CS-379, CS-380 et CS-381 pour verifier que la generation de theme natal refonctionne, que `traditional_conditions` respecte le contrat produit, et que l'enrichissement des prompts `theme_astral_llm_input_v1` n'a pas regresse.

## Contexte

CS-379 doit corriger la source backend du payload invalide observe des le `POST /v1/users/me/natal-chart`. CS-380 doit proteger l'UI sans officialiser un contrat partiel. CS-381 doit prouver la coexistence du flux utilisateur et du payload prompt enrichi.

Cette story existe pour verifier ces corrections avec une posture hostile: chercher les trous de preuve, les faux positifs de test, les corrections qui masquent le bug, et les regressions silencieuses du contrat prompt.

## Objectif

Produire une review qui repond clairement:

- le crash initial est-il impossible a reproduire apres correction sur un nouveau theme ?
- le `POST /v1/users/me/natal-chart` retourne-t-il un `traditional_conditions` complet quand l'heure de naissance est connue ?
- `traditional_conditions` est-il absent uniquement quand le calcul fiable est impossible, par exemple `no_time` ?
- le front evite-t-il le crash sans inventer de faits astrologiques ?
- les enrichissements prompt-visible restent-ils presents et separes du payload UI public ?

## Perimetre inclus

1. Lire les diffs de CS-379, CS-380 et CS-381.
2. Rejouer ou inspecter les tests ajoutes par ces stories.
3. Examiner les assertions pour detecter les tests trop permissifs.
4. Comparer le payload `POST /v1/users/me/natal-chart` et le payload `GET /latest`.
5. Verifier explicitement les cas avec heure connue et `no_time`.
6. Verifier que les types front n'ont pas officialise un contrat partiel.
7. Verifier que les guards React n'ajoutent aucun calcul astrologique.
8. Verifier que `theme_astral_llm_input_v1` conserve ses blocs enrichis attendus.
9. Produire un rapport de findings classes par severite.

## Hors perimetre

- Corriger les findings dans cette story.
- Appeler un provider LLM reel.
- Redefinir le contrat produit de `traditional_conditions`.
- Refaire les prompts ou leur wording.
- Ajouter de nouvelles features.

## Sources obligatoires

- Fichiers modifies par CS-379, CS-380 et CS-381
- `_story_briefs/cs-379-stabiliser-contrat-public-generation-theme-natal-apres-enrichissement-prompts.md`
- `_story_briefs/cs-380-durcir-natal-expert-panel-contre-payloads-partiels-sans-masquer-contrat.md`
- `_story_briefs/cs-381-non-regression-generation-theme-natal-et-enrichissement-prompts.md`
- `backend/app/services/chart/json_builder.py`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx`
- `frontend/src/api/natal-chart/index.ts`
- Tests backend et frontend touches par les stories

## Livrable attendu

Creer:

```text
_condamad/reports/cs-382-review-adversariale-generation-theme-natal.md
```

Le rapport doit contenir:

1. Synthese du verdict.
2. Liste des fichiers et tests inspectes.
3. Findings classes `Critical`, `High`, `Medium`, `Low`.
4. Pour chaque finding: preuve, impact, correction attendue, story cible.
5. Liste des checks executes.
6. Risques residuels.
7. Decision finale: corrections requises ou cloture acceptable.

## Criteres d'acceptation

1. La review inspecte explicitement le payload `POST` de creation, pas seulement `GET /latest`.
2. La review couvre au moins un cas heure connue et un cas `no_time`.
3. La review verifie que l'absence de `traditional_conditions` n'est pas liee au plan commercial.
4. La review verifie que le front ne calcule pas `hayz`, `rejoicing` ou des scores.
5. La review verifie que les tests CS-379 a CS-381 echoueraient sur le bug initial ou sur un fixture equivalent.
6. La review verifie que les enrichissements prompt-visible ne sont pas retires ou remplaces par des carriers legacy.
7. Tous les findings sont actionnables, deduplices et rattaches a une source.
8. Si aucun finding n'est ouvert, le rapport explique les preuves de cloture.

## Commandes de validation minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff check .
python -B -m pytest -q tests --tb=short -k "natal_chart or traditional_conditions or theme_astral or llm_astrology_input"
```

Frontend:

```powershell
cd frontend
pnpm lint
pnpm test -- NatalExpertPanel BirthProfilePage natalChartApi
pnpm build
```

Scans:

```powershell
rg -n "is_hayz|is_rejoicing|traditional_conditions|chart_json|natal_data|llm_astrology_input_v1|theme_astral_llm_input_v1" backend/app backend/tests frontend/src
```

## Risques

Le risque principal est une review de surface qui valide seulement l'absence de crash. La review doit aussi prouver que la correction n'a pas degrade le contrat astrologique ni l'enrichissement prompt.
