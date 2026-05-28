# Review adversariale finale theme_astral prompt contract - CS-377

## Verdict global

Corrections requises avant cloture finale. Le runtime, la persistence et les tests cibles passent, mais les exemples provider finaux ne respectent pas le contrat `birth_context` attendu.

## Findings par severite

1. Medium F-001 bug: les trois payloads provider officiels du dossier `1973-04-24-1100-paris-theme-astral-v1` gardent la naissance reelle dans `chart_id`, mais `birth_date`, `birth_time_local`, `birth_place.city`, `birth_place.country`, `birth_place.timezone`, `latitude` et `longitude` restent `null`.
2. Info F-002 risque accepte: le provider smoke CS-376 existe mais l'appel externe est skippe sans opt-in.
3. Info F-003 risque accepte: les exemples utilisent des textes sources non vides et sourcees, avec disclosure explicite des familles `production-like` fixture-backed.

## Preuve fichier ligne

- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/free-provider-payload.json:56-68`: `chart_id` contient `birth:1973-04-24 11:00 Europe/Paris Paris France`, mais `birth_date`, `birth_time_local`, `city`, `country`, `timezone`, `latitude`, `longitude` sont `null`.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/basic-provider-payload.json:56-68`: meme drift.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/premium-provider-payload.json:56-68`: meme drift.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/intermediate-data.json:12-16`: le scenario contient `Paris`, `France`, `Europe/Paris`, latitude `48.8566`, longitude `2.3522`.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md:3`: le dossier est annonce comme une naissance le `1973-04-24` a `11:00` a Paris, France.
- `_condamad/examples/prompt-generation-cartography/1973-04-24-1100-paris-theme-astral-v1/README.md:28`: le README affirme que le runtime expose `birth_date`, `birth_time_local`, `birth_place`, coordonnees et flags, tout en indiquant que `chart_id` reste technique.
- `backend/tests/llm_orchestration/test_theme_astral_provider_smoke.py`: provider smoke marque opt-in; `pytest -m provider_smoke` a retourne `1 skipped, 3 deselected`.

## Matrice de conformite CS-372 a CS-376

| Story | Verdict | Justification |
|---|---|---|
| CS-372 | PASS | Profils `essential`, `expanded`, `complete` prouves par tests et scans. |
| CS-373 | PARTIAL | Runtime birth context PASS; exemples officiels FAIL. |
| CS-374 | PASS | Materiau interpretatif source, non vide, disclosure fixture presente. |
| CS-375 | PARTIAL | Documentation coherente en intention, mais masque le drift des payloads exemples. |
| CS-376 | PASS avec skip externe | Smoke implemente, appel provider reel non execute sans opt-in. |

## Matrice des scans

| Scan | Resultat | Interpretation |
|---|---|---|
| `deep`, `essential`, `expanded`, `complete`, `delivery_profile`, `birth_context` | PASS | Profils et structure existent; hits larges hors domaine classes. |
| `chart_json`, `natal_data`, `llm_astrology_input_v1`, `legacy`, `free`, `basic`, `premium`, `"plan"` | PASS interprete | Pas de fuite exacte dans les valeurs JSON provider cible; hits larges tests ou autres domaines. |
| Inspection JSON `birth_context` provider | FAIL | Les trois payloads gardent le contexte connu dans `chart_id` et non dans les champs structures. |
| Inspection `interpretation_material` | PASS | Textes non vides, `source_ref` explicites, source mixte documentee. |

## Commandes executees

- `ruff check .` depuis `backend` apres activation venv: PASS.
- `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py tests/integration/test_theme_astral_prompt_contract_persistence.py tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py tests/architecture/test_theme_astral_prompt_contract_guard.py tests/llm_orchestration/test_theme_astral_provider_smoke.py --tb=short`: PASS, `16 passed, 1 skipped, 9 deselected`.
- `python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_smoke.py -m provider_smoke --tb=short`: SKIPPED, `1 skipped, 3 deselected`.
- Scans `rg` cibles sur profils, birth context, carriers historiques et plan labels: executes et interpretes.
- Scripts du skill `condamad_domain_audit_validate.py` et `condamad_domain_audit_lint.py`: PASS apres review du dossier d'audit cible.

## Risques residuels

- F-001 bloque la cloture contractuelle tant que les exemples officiels restent contradictoires.
- F-002 ne bloque pas la cloture si l'equipe accepte l'absence d'appel provider externe dans l'audit non interactif.
- F-003 ne bloque pas la cloture car la source fixture-backed est explicitement qualifiee.

## Decision

Ne pas clore le contrat final tant que F-001 n'est pas corrige. La correction attendue est bornee aux exemples/validateurs et ne necessite pas de refactor runtime si les tests actuels restent verts.
