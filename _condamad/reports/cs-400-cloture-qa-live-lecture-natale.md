# CS-400 / CS-405 - Cloture QA live lecture natale

Date : 2026-05-31
Story d'execution : `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/00-story.md`
Brief source : `_story_briefs/cs-400-cloturer-qa-live-richesse-et-non-regression-lecture-natale.md`
Reference baseline : `_condamad/reports/cs-390-395-qa-live-natal-ecarts-restant.md`
Compte QA : `daconrilcy@hotmail.com`
Environnement : backend local `127.0.0.1:8001`, frontend local `127.0.0.1:5173`

## Verdict

`BLOCKED` : la cloture live Free / Basic / Premium ne peut pas etre validee dans cette execution.

Les corrections automatisees CS-396 a CS-399 restent prouvees par tests backend et frontend. Le rejeu live authentifie initial a expose un ecart produit majeur : une generation Basic `complete` forcee retournait `meta.schema_version = "v2"` sans `narrative_natal_reading_v1`, sans cinq chapitres et sans `used_astrological_elements`. La review/fix a corrige la configuration locale manquante `natal/interpretation/basic -> AstroResponse_v3`, mais un rejeu API Basic post-correction retourne encore `schema_version = "v2"`, `validation_status = "rejected"` et aucune narrative. La QA live Free / Basic / Premium reste donc non cloturee.

## Baseline du defaut

| Point controle | Baseline 2026-05-30 | Rejeu CS-405 2026-05-31 |
|---|---|---|
| Lecture Basic complete | Narrative absente ou non prouvee live | Preuve live post-correction non rejouee |
| Schema public | V1/V2 historique | Config Basic corrigee vers `AstroResponse_v3`, runtime live a rejouer |
| Cinq chapitres narratifs | Non verifies live | A rejouer apres correction assembly Basic |
| Sources publiques | Non verifiees live | A rejouer apres correction assembly Basic |
| Accordions modernes | Prouves par Vitest | Captures existantes pre-correction invalides pour cloture |
| Fuites techniques DOM | Aucune fuite observee | Aucune fuite denylist observee dans les captures Basic |

## Matrice Free / Basic / Premium

| Profil | Source de preuve | Resultat | Statut |
|---|---|---|---|
| Free | Non rejoue completement : le compte local est actuellement `basic` | La preuve Free authentifiee n'est pas disponible dans cette session | `BLOCKED` |
| Basic | API + navigateur desktop/mobile + review/fix config | L'assembly Basic manquant a ete corrige vers `natal_interpretation` + `AstroResponse_v3`; le rejeu API post-correction reste `v2` rejete | `BLOCKED` |
| Premium | Non rejoue : aucun passage controle `premium` n'a ete execute apres l'echec Basic bloquant | Le mode astrologue reste prouve par Vitest cible, pas par QA live Premium | `BLOCKED` |

## Matrice desktop / mobile

| Viewport | Capture | Constat | Statut |
|---|---|---|---|
| Desktop | `output/playwright/cs-400-basic-desktop.png` | Capture pre-correction, a remplacer avant cloture | `BLOCKED` |
| Mobile | `output/playwright/cs-400-basic-mobile.png` | Capture pre-correction, a remplacer avant cloture | `BLOCKED` |

## Provider, fixtures et relecture persistee

| Source | Evidence | Interpretation |
|---|---|---|
| Relecture persistee | `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/evidence/api-snapshot.json` | Le compte contient des interpretations historiques `short` et `natal_long_free`. |
| Provider controle local | `_condamad/stories/CS-405-cloture-qa-live-lecture-natale/evidence/api-complete-generation-response.json` | Preuve pre-correction : `POST /v1/natal/interpretation` retourne HTTP OK mais downgrade en V2, sans narrative V1. |
| Fixtures/tests | `backend-targeted-tests.txt`, `backend-long-*.txt`, `frontend-targeted-tests.txt` | Les garanties de non-regression CS-396 a CS-399 passent hors live browser. |

## Quota, rejet et regeneration corrective

| Controle | Evidence | Resultat |
|---|---|---|
| Quota Basic avant generation | `api-snapshot.json` | `natal_chart_long` accorde, `remaining = 1`. |
| Generation Basic forcee | `api-complete-generation-response.json` | Preuve pre-correction invalide ; a rejouer apres correction assembly Basic V3. |
| Rejet editorial et quota | `backend-targeted-tests.txt`, `backend-long-entitlement.txt` | PASS automatise : rejet/quota transactionnel couverts par tests. |

## Richesse editoriale Basic

| Controle | Evidence | Resultat |
|---|---|---|
| Cinq chapitres distincts | `api-complete-generation-response.json` | BLOCKED : preuve pre-correction a remplacer. |
| Sources non vides | `api-complete-generation-response.json` | BLOCKED : preuve pre-correction a remplacer. |
| Couverture familles Basic | `backend-targeted-tests.txt` | PASS automatise, non confirme en live. |

## Commandes executees

```text
.\.venv\Scripts\Activate.ps1; Push-Location backend; ruff check .; Pop-Location
# PASS

.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -m pytest -q tests --tb=short -k "natal and (narrative or rejected or quota or theme_astral)"; Pop-Location
# PASS: 30 passed, 1496 deselected

.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -m pytest -q --long app/tests/integration/test_natal_chart_long_entitlement.py --tb=short; Pop-Location
# PASS: 16 passed

.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -m pytest -q --long app/tests/integration/test_natal_interpretation_endpoint.py --tb=short; Pop-Location
# PASS: 8 passed

pnpm --dir frontend test -- NatalChartPage natalNarrativeReading natalPublicDomGuard NatalAstrologerMode
# PASS: 90 passed

pnpm --dir frontend lint
# PASS

pnpm --dir frontend build
# PASS

.\.venv\Scripts\Activate.ps1; Push-Location backend; python -B -m pytest -q tests\llm_orchestration\test_runtime_convergence.py; Pop-Location
# PASS: 5 passed, couvre l'assembly Basic AstroResponse_v3

node _condamad\stories\CS-405-cloture-qa-live-lecture-natale\evidence\capture-browser-qa.cjs
# PASS command pre-correction, FAIL product assertion: Basic accordions = 0
```

## Guardrails

| Guardrail | Evidence | Resultat |
|---|---|---|
| RG-155 | `backend-targeted-tests.txt` + generation live | Tests PASS ; preuve live pre-correction a remplacer. |
| RG-156 | `backend-targeted-tests.txt` | PASS automatise, non confirme live. |
| RG-157 | `backend-long-entitlement.txt`, `backend-targeted-tests.txt` | PASS automatise. |
| RG-158 | `frontend-targeted-tests.txt` + captures live | Tests PASS ; captures live pre-correction a remplacer. |

## Screenshots

| Fichier | Contexte |
|---|---|
| `output/playwright/cs-400-basic-desktop.png` | Capture Basic pre-correction a remplacer |
| `output/playwright/cs-400-basic-mobile.png` | Capture Basic pre-correction a remplacer |

## Risques residuels

| Risque | Severite | Suivi |
|---|---|---|
| Basic `complete` reste rejete en live apres correction assembly V3 | Critique | CS-405 reste non done tant qu'une preuve API/navigateur V3 avec narrative n'existe pas |
| Free et Premium non rejoues completement apres l'echec Basic bloquant | Majeur | A rejouer apres preuve Basic V3 post-correction |
| La cloture live positive serait trompeuse si elle s'appuyait seulement sur Vitest/Pytest | Majeur | Ce rapport garde le verdict `BLOCKED` |

## Feedback loop

No-propagation : l'echec correspond a une story runtime deja presente dans le registre (`CS-406`, `CS-407`, `CS-408`). Aucune nouvelle regle durable n'est ajoutee a `_condamad/stories/regression-guardrails.md`.
