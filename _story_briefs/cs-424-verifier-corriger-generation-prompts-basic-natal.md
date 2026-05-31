# CS-424 - Verifier Et Corriger La Generation Des Prompts Basic Natal

<!-- Commentaire global: ce brief cadre l'audit et la correction du prompt final Basic natal, au-dela du seul payload provider. -->

## Resume

Verifier que la generation effective du prompt `theme_astral_prompt_v1` consomme correctement le
payload Basic enrichi et demande explicitement un rapport humain, comprehensible et non mecanique.
Corriger le template/seed/assembly si le prompt final laisse le modele produire une liste de
donnees astrologiques ou reprendre les libelles du payload comme prose utilisateur.

CS-416 a prouve que `basic_natal_prompt_payload` est confidentiel, plan-backed et sans carriers
legacy. Cette preuve ne valide pas encore que le prompt final rendu au provider:

- explique comment utiliser `basic_natal_prompt_payload`;
- interdit les phrases templates observees;
- demande une introduction, des themes explicatifs et une conclusion;
- place les sources en annexe, pas dans le corps principal;
- preserve les contraintes de non-invention et de non-prescription.

## Constat Technique

Le seed actuel `seed_theme_astral_prompt_contract.py` contient un template generique:

```text
Respecte runtime_contract, safety_contract, astrologer_voice, feature_context,
delivery_profile, input_data et output_contract.
```

Ce texte est suffisant pour une validation de contrat, mais trop faible pour une lecture Basic
lisible. Il ne dit pas au provider quoi faire de `input_data.basic_natal_prompt_payload.sections`,
`editorial_evidence`, `style_constraints`, `limitations` et `disclaimers`. Le modele peut donc
prendre le chemin le plus simple: enumerer les labels et generer une prose de justification.

## Objectif

Prouver et, si necessaire, corriger le prompt final rendu pour Basic:

```text
Prompt final
=> contient les consignes redactionnelles Basic.
=> consomme le payload Basic enrichi sans exposer de champs interdits.
=> demande un rapport continu, pas une liste de sources.
=> refuse les templates mecaniques et les labels anglais bruts.
```

## Perimetre Inclus

1. Auditer le chemin complet:
   - seed/template `THEME_ASTRAL_PROMPT_TEMPLATE`;
   - use case `theme_astral`;
   - assembly `feature=theme_astral`, `subfeature=prompt_contract`, `plan=expanded` pour Basic;
   - rendu `assemble_developer_prompt`;
   - rendu `LLMGateway.build_user_payload`.
2. Ajouter un snapshot du prompt final rendu pour un payload Basic representatif, sans appel
   provider live.
3. Ajouter ou etendre un test qui prouve que le prompt final Basic contient:
   - consigne de rapport humain;
   - ordre attendu introduction/themes/conclusion;
   - politique d'utilisation des sources en annexe;
   - interdiction de copier les labels comme contenu principal;
   - interdiction des phrases templates observees.
4. Corriger `THEME_ASTRAL_PROMPT_TEMPLATE` ou l'assembly canonique si ces consignes manquent.
   Les consignes specifiques Basic doivent etre injectees via le payload Basic, le
   `delivery_profile` Basic ou une section conditionnelle clairement ciblee; le template global ne
   doit pas devenir proprietaire des regles metier Basic.
5. Mettre a jour les tests de seed/bootstrap pour prouver que les assemblies publiees prennent le
   nouveau prompt.
6. Verifier que le prompt final ne reintroduit pas `chart_json`, `natal_data`, PII, scores,
   chemins internes, IDs bruts ou libelles commerciaux.
7. Verifier que les changements ne cassent pas les profils free/premium du meme contrat
   `theme_astral_prompt_v1`.
8. Ajouter un test de routage actif prouvant que le flux Basic reel utilise bien l'assembly publiee
   `theme_astral_prompt_v1` et ne repasse pas par `natal_interpretation` ou
   `natal_interpretation_short`.

## Hors Perimetre

- Changer le payload provider Basic lui-meme, sauf adaptation minimale necessaire a CS-421.
- Modifier la validation du draft Basic, sauf ajout de tests miroir pour le prompt.
- Faire un appel provider live.
- Changer les contrats API publics ou le rendu frontend.
- Modifier les anciens prompts `natal_interpretation_short` ou `natal_interpretation` hors
  preuve qu'ils sont encore dans le chemin Basic actif.
- Creer une seconde famille de prompt Basic concurrente.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/basic-payload-after.json`
- `_condamad/stories/CS-416-contraindre-payload-llm-basic-par-reading-plan/evidence/validation.txt`
- `_story_briefs/cs-421-renforcer-contrat-redactionnel-basic-natal.md`
- `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py`
- `backend/tests/integration/llm/test_theme_astral_provider_payload_handoff.py`
- `backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py`
- `backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`
- `backend/tests/llm_orchestration/test_assembly_resolution.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-018` - les familles supportees ne doivent pas redevenir proprietaires de prompt via fallback legacy.
  - `RG-021` - aucun fallback prompt canonique non audite ne doit etre ajoute.
  - `RG-149` - la cartographie prompt-generation doit distinguer les processus provider-capable.
  - `RG-152` - le prompt/public contract ne doit pas exposer `chart_json`, audit ou signaux internes.
  - `RG-155` - pas de padding semantique ni chapitres dupliques.
  - `RG-164` - Basic reste plan-backed.
  - `RG-165` - le payload/prompt Basic exclut PII, scores, chemins et IDs bruts.
  - `RG-166` - les drafts acceptes matchent `BasicNatalReadingPlan`.
  - `RG-167` - Basic complete utilise `basic-natal-reading-v1`.
  - `RG-168` - `BasicNatalInterpretationV2` reste le contrat public canonique.
  - `RG-169` - qualite redactionnelle Basic, seulement si cree par CS-421.
- Required regression evidence:
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short`
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/integration/llm/test_theme_astral_provider_payload_handoff.py --tb=short`
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short`
  - Depuis `backend/` avec venv active: `python -B -m pytest -q tests/llm_orchestration/test_assembly_resolution.py -k "theme_astral or basic or prompt_contract" --tb=short`
  - Scan: `rg -n "PROMPT_FALLBACK_CONFIGS|fallback_target_use_case" backend/app/domain/llm backend/app/ops/llm backend/tests/llm_orchestration`
  - Scan: `rg -n "chart_json|natal_data|audit_input|ranking_score|weighted_score|condition_axis|prompt_hint|user_id|email|latitude|longitude" backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py backend/tests/integration/llm backend/tests/llm_orchestration`
  - Snapshot: prompt final rendu Basic avant/apres dans le dossier evidence de la story.
- Registry enrichment expected:
  - Ajouter un nouvel invariant `RG-171` si la story cree une garde durable du prompt final Basic
    redactionnel.
- Allowed differences:
  - `THEME_ASTRAL_PROMPT_TEMPLATE` devient plus prescriptif sur la forme redactionnelle.
  - Les tests et snapshots du prompt final sont mis a jour.
  - Les prompts free/premium peuvent recevoir des clarifications generiques si elles ne changent pas
    leur contrat de sortie.

## Criteres D'acceptation

1. Un test rend le prompt final Basic complet depuis l'assembly publiee et un payload Basic
   representatif.
2. Le prompt final Basic contient une consigne explicite de rapport humain, lisible sans recherche
   supplementaire.
3. Le prompt final Basic impose l'ordre introduction, themes explicatifs, conclusion, sources en
   annexe.
4. Le prompt final Basic interdit de presenter les sources comme contenu principal.
5. Le prompt final Basic interdit les phrases templates du baseline:
   `cette lecture s'appuie uniquement`, `Ce repere retient`,
   `avec une confiance editoriale controlee`.
6. Le prompt final Basic demande de vulgariser les libelles astrologiques et de ne pas copier les
   labels anglais bruts.
7. Le prompt final Basic conserve les contraintes de non-invention, non-fatalisme, non-prediction
   ferme et non-prescription.
8. Le prompt final et le user payload ne contiennent pas les carriers/champs interdits.
9. Les assemblies `theme_astral/prompt_contract` publiees restent uniques par depth et continuent
   de pointer vers `theme_astral_prompt_v1`.
10. Le chemin Basic actif utilise l'assembly publiee attendue et aucun ancien prompt
    `natal_interpretation` ou `natal_interpretation_short`.
11. Les consignes Basic sont ciblees par payload/profil/condition explicite; le template global ne
    devient pas proprietaire des regles metier Basic.
12. Les profils free/premium gardent leur handoff contractuel existant.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration/llm/test_theme_astral_prompt_contract_bigbang.py --tb=short
python -B -m pytest -q tests/integration/llm/test_theme_astral_provider_payload_handoff.py --tb=short
python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py tests/llm_orchestration/test_theme_astral_provider_payload_builder.py --tb=short
python -B -m pytest -q tests/llm_orchestration/test_assembly_resolution.py -k "theme_astral or basic or prompt_contract" --tb=short
```

Scans:

```powershell
rg -n "PROMPT_FALLBACK_CONFIGS|fallback_target_use_case" backend/app/domain/llm backend/app/ops/llm backend/tests/llm_orchestration
rg -n "chart_json|natal_data|audit_input|ranking_score|weighted_score|condition_axis|prompt_hint|user_id|email|latitude|longitude" backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py backend/tests/integration/llm backend/tests/llm_orchestration
```

Evidence attendue:

```text
_condamad/stories/CS-424-verifier-corriger-generation-prompts-basic-natal/evidence/basic-final-prompt-before.txt
_condamad/stories/CS-424-verifier-corriger-generation-prompts-basic-natal/evidence/basic-final-prompt-after.txt
_condamad/stories/CS-424-verifier-corriger-generation-prompts-basic-natal/evidence/basic-user-payload-after.json
_condamad/stories/CS-424-verifier-corriger-generation-prompts-basic-natal/evidence/validation.txt
```

## Dependances

- CS-416 pour la contrainte du payload Basic.
- CS-421 pour le contrat redactionnel attendu par le payload Basic.
- CS-423 doit verifier le resultat live apres CS-424.

## Risques

Le risque principal est de corriger seulement le payload et de laisser un prompt generique qui ne
guide pas assez le modele. Cette story ferme cette faille en testant le prompt final rendu.

Risque secondaire: durcir le prompt en introduisant des instructions qui contredisent le schema de
sortie ou la privacy. Les scans et tests de handoff doivent prouver que le prompt reste compatible
avec `theme_astral_response_contract_v1` et sans carriers legacy.
