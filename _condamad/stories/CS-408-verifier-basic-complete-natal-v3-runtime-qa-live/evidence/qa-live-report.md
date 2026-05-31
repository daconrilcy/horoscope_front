# QA live report - CS-408

<!-- Commentaire global: ce rapport consigne la preuve QA controlee pour Basic complete natal V3. -->

## Verdict

PASS_WITH_LIMITATIONS.

La preuve CS-408 est une QA runtime controlee sans appel provider reel. Elle prouve le chemin Basic complete avec fake gateway,
persistance locale et DOM public teste par Vitest. Le smoke provider externe reste hors perimetre car la story interdit les appels
provider reels non controles.

## Avant / apres

| Controle | Avant | Apres CS-408 |
|---|---|---|
| Use case Basic complete | Baseline CS-400/CS-405 non prouvee V3 | `natal_interpretation` capture par test runtime. |
| Assembly | Basic V3 a rejouer | `natal/interpretation/basic/fr-FR` prouve par `AIEngineAdapter`. |
| Schema | `v2` rejete dans la baseline | `schema_version = "v3"` et `validation_status = "valid"`. |
| Narrative | Absente dans la baseline bloquante | `narrative_natal_reading_v1` persiste avec sources non vides. |
| DOM public | Captures pre-correction non cloturantes | Vitest confirme les accordions modernes et la denylist publique. |

## Compte QA

- Compte autorise: `daconrilcy@hotmail.com`.
- Usage: contexte documentaire uniquement; aucun appel provider reel ou navigateur live externe n'a ete lance pendant cette review.

## Preuves

- `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/basic-complete-before.json`
- `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/basic-complete-after.json`
- `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/backend-validation.txt`
- `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/frontend-validation.txt`
- `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md`

## Fichiers touches par la story

- `backend/tests/integration/test_natal_basic_complete_v3_runtime.py`
- `_condamad/reports/cs-400-cloture-qa-live-lecture-natale.md`
- `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/evidence/**`
- `_condamad/stories/CS-408-verifier-basic-complete-natal-v3-runtime-qa-live/generated/**`
- `_condamad/stories/story-status.md`

## Risque residuel

La preuve reste controlee localement. Une cloture live provider externe devra etre autorisee explicitement dans une story separee.
