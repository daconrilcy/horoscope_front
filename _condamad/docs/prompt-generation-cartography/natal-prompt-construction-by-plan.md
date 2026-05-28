<!-- Commentaire global: ce document cartographie la construction des prompts natals par plan sans modifier le runtime. -->

# Construction des prompts de theme astral natal par plan

## Executive summary

Le flux natal moderne construit le prompt provider depuis un use case canonique, une assembly runtime, un rendu de developer prompt, le contrat `llm_astrology_input_v1`, puis le handoff `LLMGateway`. Les blocs prompt-visible du payload natal sont limites a `facts`, `signals`, `limits` et `shaping`; `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, `provider response` et `observability` restent backend-only, validation-only ou audit-only. Sources: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`, `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`, `backend/app/domain/llm/runtime/gateway.py`.

Annexe Mermaid: `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md`.

Aucun appel provider LLM reel n'a ete effectue pour produire ce document. Les textes exacts de prompt stockes en configuration runtime ne sont pas inventes: ils sont notes `a extraire depuis la configuration runtime`.

## Scope: theme astral natal, plans free, basic, premium

Le scope couvre uniquement la construction du prompt pour le theme astral natal B2C et les plans `free`, `basic`, `premium`. CS-320 fixe la regle produit: tous les plans conservent les calculs astrologiques et les interpretations; la differenciation se fait par donnees transmises au LLM, profondeur redactionnelle, sections exposees et budget de sortie. Sources: `_story_briefs/cs-320-definir-differenciation-llm-front-par-plan-b2c.md`, `backend/app/services/llm_generation/natal/interpretation_service.py`.

Hors scope: UI frontend, schema DB, auth, migrations, prompt seeds, output schemas, provider integration, reecriture des prompts et execution LLM.

## Vocabulaire: prompt-visible, backend-only, validation-only, audit-only

| Terme | Definition CS-356 | Source |
|---|---|---|
| `prompt-visible` | Donnee incluse dans les messages provider ou le payload user rendu. | `gateway.py`, `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md` |
| `backend-only` | Donnee utile au runtime, a la selection, aux metadata ou a la persistence, sans devenir matiere de prompt. | `prompt-generation-current-implementation.md` |
| `validation-only` | Donnee utilisee pour valider ou rejeter la sortie, notamment `evidence`, `grounding_status`, `validation_owner`. | `llm_astrology_input_v1.py`, `05-output-validation-persistence-audit.md` |
| `audit-only` | Donnee de tracabilite: `provenance`, `projection_hash`, `llm_input_hash`, `provider response`, persistence et observability. | `05-output-validation-persistence-audit.md` |

## Point de depart: donnees recues par le process de prompt

Le process natal part du service `NatalInterpretationService`: il construit `structured_facts_v1`, `AINarrativeInputContract`, une projection client par plan, puis appelle `_build_llm_astrology_input_v1`. Le gateway recoit ensuite un `LLMExecutionRequest` contenant le use case, le contexte, la locale, les metadata runtime et le bloc `llm_astrology_input_v1`. Sources: `backend/app/services/llm_generation/natal/interpretation_service.py`, `backend/app/domain/llm/runtime/gateway.py`.

`chart_json` et `natal_data` ne sont pas des carriers prompt-visible du flux natal moderne quand `llm_astrology_input_v1` est present. Ils restent classes runtime-only, historiques, tests, admin samples ou surfaces non modernes selon CS-343 a CS-350.

## Construction de llm_astrology_input_v1

`LLMAstrologyInputV1Builder.build` assemble un objet complet avec `facts`, `signals`, `limits`, `evidence`, `shaping`, `provenance`, `exclusions` et `data_roles`. Le hash `llm_input_hash` est calcule depuis les seuls blocs prompt-influencing `facts`, `signals`, `limits`, `shaping`; il ne rend pas `provenance` prompt-visible. Sources: `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`, stories CS-330 a CS-342.

| Bloc | Role | Visibilite | Source owner |
|---|---|---|---|
| `facts` | Positions, maisons, aspects majeurs, dominantes et metadata factuelles issues de `structured_facts_v1`. | prompt-visible | `_facts_block` |
| `signals` | Signaux interpretatifs, readiness flags, masking policy et liens de projection publique. | prompt-visible | `_signals_block` |
| `limits` | Donnees manquantes, sections indisponibles, incertitudes et surfaces exclues. | prompt-visible | `_limits_block` |
| `shaping` | Plan, module, profondeur editoriale et selection d'input LLM. | prompt-visible | `_shaping_block` |
| `evidence` | References de grounding et statut de validation. | validation-only | `_evidence_block` |
| `provenance` | Versions, `projection_hash`, `llm_input_hash`, politique de hash et `prompt_ref`. | audit-only | `_provenance_block` |

## Matrice des donnees injectees par bloc et par plan

| Plan | `facts` | `signals` | `limits` | `shaping` | `evidence` / `provenance` |
|---|---|---|---|---|---|
| `free` | Prompt-visible, filtre par selection d'input et sortie courte. | Prompt-visible si autorise par la selection. | Prompt-visible pour borner les absences et exclusions. | Prompt-visible: plan `free`, profondeur courte, budget reduit. | validation-only / audit-only, jamais prompt-visible. |
| `basic` | Prompt-visible avec couverture plus large que `free` selon projection. | Prompt-visible avec signaux utiles au module achete. | Prompt-visible pour eviter invention et surpromesse. | Prompt-visible: plan `basic`, profondeur intermediaire, sections controlees. | validation-only / audit-only, jamais prompt-visible. |
| `premium` | Prompt-visible avec profondeur maximale autorisee par le contrat. | Prompt-visible avec signaux narratifs plus riches. | Prompt-visible pour expliciter limites et indisponibilites. | Prompt-visible: plan `premium`, profondeur haute, budget plus large. | validation-only / audit-only, jamais prompt-visible. |

Cette matrice documente une differenciation de payload, de profondeur et de budget. Elle ne documente pas une suppression de calculs backend par plan. Sources: CS-320, CS-330, `LLM_ASTROLOGY_INPUT_DATA_ROLES`.

## Resolution use case, assembly, placeholders et plan rules

`canonical_use_case_registry.py` declare `NATAL_LLM_ASTROLOGY_INPUT_SCHEMA`: les use cases natals modernes exigent `llm_astrology_input_v1`, et plusieurs use cases natals exigent aussi `persona_name`. `assembly_resolver.py` resout feature template, subfeature template, plan rules, hard policy et length budget, puis `assemble_developer_prompt` concatene feature, subfeature et plan rules. Sources: `backend/app/domain/llm/configuration/canonical_use_case_registry.py`, `backend/app/domain/llm/configuration/assembly_resolver.py`.

`PromptRenderer.render` applique la gouvernance de placeholders; les placeholders requis manquants refusent le rendu, alors que les optionnels avec fallback restent bornes. Le contenu exact de `system_core`, du developer prompt et des plan rules persiste en configuration: `a extraire depuis la configuration runtime`.

## Introduction de l'astrologue/persona

La `persona astrologue` est resolue comme bloc separe du developer prompt. `resolve_assembly` produit `persona_block` via `compose_persona_block` si la configuration l'active; `assemble_developer_prompt` indique que la persona est geree separement; `LLMGateway.compose_structured_messages` ajoute ensuite ce bloc comme message `developer` optionnel. Sources: `assembly_resolver.py`, `backend/app/domain/llm/runtime/gateway.py`, `02-configuration-assembly-placeholder-audit.md`.

Par plan, `free` peut utiliser un use case court sans persona obligatoire, tandis que les use cases natals riches `basic` et `premium` documentes dans le registre exigent `persona_name` lorsque `persona_strategy` vaut `required`. Le texte exact de persona reste `a extraire depuis la configuration runtime`.

## Construction de la securite et des limites

La securite est separee en couches: hard policy d'assembly, limites prompt-visible du bloc `limits`, non-invention portee par les guards CS-335 a CS-342, validation de sortie, repair, puis rejet controle. `get_hard_policy("astrology")` alimente l'assembly; `_limits_block` transporte les donnees manquantes et surfaces exclues; `validate_output` verifie la forme de sortie; le rejected workflow controle les claims non groundes. Sources: `assembly_resolver.py`, `llm_astrology_input_v1.py`, `gateway.py`, `05-output-validation-persistence-audit.md`.

Les regles de non-invention ne doivent pas etre confondues avec une preuve semantique complete: les audits CS-347 et CS-350 gardent le risque residuel que le grounding soit borne.

## Composition finale des messages provider

Pour le mode structure, `LLMGateway.compose_structured_messages` produit: `system_core`, developer prompt rendu, `persona_block` optionnel, puis `payload user`. Pour le mode chat, `compose_chat_messages` ajoute l'historique valide avant le message user. Source: `backend/app/domain/llm/runtime/gateway.py`.

Le `payload user` inclut `llm_astrology_input_v1` apres filtrage par `_prompt_visible_llm_astrology_input`, qui conserve uniquement `facts`, `signals`, `limits`, `shaping`, puis `_without_prompt_excluded_keys` retire recursivement les cles exclues. Les parametres modele, temperature, tokens, `response_format`, `request_id`, `trace_id` et `use_case` sont runtime/provider-only metadata, pas prompt-visible payload.

## Frontiere exacte avant handoff provider

La derniere charge utile gateway-owned avant provider est `messages`, transmise a `_call_provider(messages, plan, request)` puis au runtime manager. Avant ce handoff, les exclusions doivent deja etre effectives: `evidence`, `evidence_refs`, `provenance`, `projection_hash`, `llm_input_hash`, `provider response`, persistence et observability ne font pas partie du payload prompt-visible. Sources: `03-runtime-gateway-handoff-audit.md`, `gateway.py`.

| Element | Statut avant provider |
|---|---|
| `system_core` | prompt-visible message system, texte exact `a extraire depuis la configuration runtime` |
| Developer prompt | prompt-visible message developer rendu par assembly et placeholders |
| Persona astrologue | prompt-visible message developer optionnel |
| Payload user natal | prompt-visible, limite a `facts`, `signals`, `limits`, `shaping` |
| Provider parameters | backend-only / provider-only metadata |
| `provider response` | post-provider, audit-only ou validation-owned selon usage |
| `observability` | post-provider, audit-only |

## Differences free / basic / premium

| Plan | Construction prompt | Profondeur / budget | Exclusions inchangees |
|---|---|---|---|
| `free` | Use case court possible, `llm_astrology_input_v1` requis pour le natal moderne, selection d'input reduite. | Resume ou sortie courte, budget faible. | `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, `provider response`, `observability`. |
| `basic` | Meme pipeline, blocs prompt-visible plus fournis selon projection client et plan rules. | Profondeur intermediaire, sections controlees. | Memes exclusions; aucun carrier legacy autorise. |
| `premium` | Meme pipeline, selection et shaping plus riches pour modules natals avances. | Profondeur haute, budget plus large, persona generalement requise sur les use cases riches. | Memes exclusions; aucune promotion d'audit-only en prompt-visible. |

La frontiere plan porte sur le shaping editorial et les blocs prompt-visible selectionnes, pas sur la disparition de calculs backend.

## Chemins non nominaux, repair, fallback et rejet

Si la sortie provider ne valide pas le schema, `LLMGateway._handle_repair_or_fallback` tente un repair. Pour les features supportees, le fallback legacy de use case est explicitement refuse en cas d'echec de validation; le workflow de rejet peut produire `RejectedNarrativeAnswerOutcome` et un wording controle. Sources: `gateway.py`, `05-output-validation-persistence-audit.md`.

Les fallbacks de configuration, bootstrap, tests, admin samples et provider unsupported restent non nominaux ou bornes. Ils ne remplacent pas le contrat natal moderne, ne justifient pas `chart_json` ou `natal_data` comme prompt-visible moderne, et ne changent pas les plans `free`, `basic`, `premium`.

## Tests et commandes de verification

Commandes deterministes prevues pour cette documentation:

- `python -c "from pathlib import Path; assert Path('_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md').exists()"`
- `python -c "from pathlib import Path; p=Path('_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md'); assert 'Executive summary' in p.read_text()"`
- `rg -n "free|basic|premium|persona|astrologue|hard policy|non-invention" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `rg -n "prompt-visible|backend-only|validation-only|audit-only" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `rg -n "LLMGateway|PromptRenderer|llm_astrology_input_v1|canonical_use_case_registry.py|assembly_resolver.py|prompt_renderer.py|gateway.py|interpretation_service.py" _condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`
- `python -c "import subprocess; out=subprocess.check_output(['git','status','--short','--','backend/app','backend/tests','frontend/src'], text=True); assert out.strip()==''"`

Ces commandes ne font pas d'appel provider LLM reel.

## Exemple rejoue avec donnees utilisateur completes

Les exemples JSON de handoff provider ont ete rejoues avec les donnees utilisateur completes: naissance le `1974-04-24` a `11:00:00`, `Paris, France`, timezone `Europe/Paris`. Les artefacts sont disponibles dans `_condamad/examples/prompt-generation-cartography/1974-04-24-1100-paris/`.

Ces fichiers remplacent l'ancien scenario documentaire sans heure de naissance. Ils contiennent des valeurs calculees localement via `pyswisseph`, des prompts developer rendus avec les placeholders resolus, et `provider_call_performed=false`.

## Risques residuels et questions ouvertes

- Le texte exact de `system_core`, developer prompt, plan rules et persona doit etre `a extraire depuis la configuration runtime`; ce document n'en invente pas la formulation.
- L'output schema ownership reste une question de gouvernance notee par CS-344, CS-348 et CS-350.
- Les evidence refs, la validation et les audits reduisent le risque de non-invention, mais ne prouvent pas chaque claim semantique possible.
- Admin manual execution, guidance, chat public et horoscope daily sont provider-capable hors flux natal moderne; ils ne doivent pas etre absorbes dans `llm_astrology_input_v1`.
