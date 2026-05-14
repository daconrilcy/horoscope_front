# Analyse de l'injection des donnees de theme astral dans le prompt LLM

Date : 2026-05-14  
Perimetre analyse : interpretation de theme natal via l'API publique `/v1/natal/interpretation` et runtime LLM canonique.

## Synthese executive

Les donnees de theme astral sont injectees dans la creation du prompt par une chaine en quatre temps :

1. La route publique charge le dernier theme natal persiste de l'utilisateur et son profil de naissance.
2. `NatalInterpretationService` transforme le `NatalResult` metier en `chart_json` public canonique, puis construit un catalogue d'evidences.
3. `AIEngineAdapter.generate_natal_interpretation` place ces donnees dans un `LLMExecutionRequest` canonique : `ExecutionContext.natal_data`, `ExecutionContext.chart_json` et `ExecutionFlags.evidence_catalog`.
4. `LLMGateway` resout le plan LLM, rend le developer prompt via les placeholders `{{chart_json}}`, `{{locale}}`, `{{use_case}}`, puis compose les messages envoyes au provider.

Point important : le `chart_json` peut etre injecte dans le developer prompt si le template contient `{{chart_json}}`. Sinon, le gateway le place dans le message utilisateur sous `Technical Data: ...`. Dans les prompts nataux semes aujourd'hui, `{{chart_json}}` est explicitement present, donc le JSON du theme est actuellement rendu dans le developer prompt.

## Fichiers principaux

- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/governance/data/prompt_governance_registry.json`
- `backend/app/ops/llm/bootstrap/seed_29_prompts.py`
- `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py`

## Flux complet

### 1. Entree API et chargement du theme

La route `POST /v1/natal/interpretation` est portee par `interpret_natal_chart`.

Elle fait d'abord :

- authentification utilisateur ;
- controle d'entitlement pour `use_case_level="complete"` ;
- chargement du dernier theme avec `UserNatalChartService.get_latest_for_user(db, current_user.id)` ;
- chargement du profil de naissance avec `UserBirthProfileService.get_for_user(db, current_user.id)` ;
- delegation a `NatalInterpretationService.interpret(...)`.

Les donnees transmises au service sont notamment :

- `chart_id=chart.chart_id` ;
- `natal_result=chart.result` ;
- `birth_profile=profile` ;
- `level=body.use_case_level` ;
- `persona_id=body.persona_id` ;
- `locale=body.locale` ;
- `question=body.question` ;
- `module=body.module` ;
- `variant_code`, issu de l'entitlement pour le complete.

Conclusion : la route n'injecte pas directement de donnees astrologiques dans le prompt. Elle selectionne la source de verite utilisateur : dernier theme natal persiste + profil natal.

### 2. Normalisation applicative dans `NatalInterpretationService`

Dans `NatalInterpretationService.interpret`, apres le cache d'interpretation, le service calcule :

```python
degraded_mode_str = _detect_degraded_mode(birth_profile)
chart_json_dict = build_chart_json(natal_result, birth_profile, degraded_mode_str)
evidence_catalog = build_enriched_evidence_catalog(chart_json_dict)
```

Ce bloc est le point ou le theme astral devient un payload consommable par le LLM.

Le service choisit ensuite le use-case :

- `natal_interpretation_short` pour `level="short"` ;
- `natal_interpretation` pour `level="complete"` sans module ;
- un use-case thematique pour `level="complete"` avec module, via `MODULE_TO_USE_CASE_KEY` ;
- `natal_long_free` pour la variante `free_short`.

Le service cree ensuite `NatalExecutionInput` :

```python
NatalExecutionInput(
    use_case_key=use_case_key,
    locale=locale,
    level=level,
    chart_json=json.dumps(chart_json_dict, ensure_ascii=False),
    natal_data=chart_json_dict,
    evidence_catalog=evidence_catalog,
    persona_id=persona_id,
    plan=user_plan,
    validation_strict=level == "complete",
    question=effective_question,
    astro_context=None,
    module=module,
    variant_code=variant_code,
    user_id=user_id,
    request_id=request_id,
    trace_id=trace_id,
)
```

Il y a donc deux representations paralleles du meme theme :

- `chart_json` : chaine JSON serialisee, destinee au rendu textuel dans le prompt ;
- `natal_data` : dictionnaire Python, destine notamment a la validation d'entree et au contexte qualifie.

### 3. Contenu de `chart_json`

`build_chart_json` construit un payload public canonique compose de cinq blocs :

- `meta`
- `planets`
- `houses`
- `house_rulers`
- `aspects`
- `angles`

Le bloc `meta` contient notamment :

- `birth_date`
- `birth_time`, nullifie en mode degrade sans heure ;
- `birth_place`, nullifie en mode degrade sans lieu ;
- `birth_timezone`
- `degraded_mode`
- `engine`
- `zodiac`
- `house_system`
- `reference_version`
- `ruleset_version`
- `chart_json_version`
- `aspects_applying_available`

Les planetes contiennent :

- `code`
- `sign`
- `longitude`
- `longitude_in_sign`
- `house`, nullifie si l'heure manque ;
- `is_retrograde`
- `speed`

Les maisons ne sont incluses que si l'heure est disponible. Elles portent :

- numero ;
- cuspide ;
- signe de cuspide ;
- signes contenus/interceptes ;
- maitre de maison ;
- occupants ;
- axe ;
- score de force.

Les aspects sont filtres sur les aspects majeurs uniquement : conjonction, opposition, trigone, carre, sextile.

Les angles `ASC`, `MC`, `DSC`, `IC` sont renseignes uniquement si l'heure et le lieu sont disponibles.

Conclusion : le prompt ne recoit pas le `NatalResult` brut. Il recoit une projection volontairement publique, lisible, reduite et adaptee a la restitution.

### 4. Catalogue d'evidences

`build_enriched_evidence_catalog(chart_json_dict)` construit un dictionnaire :

```text
ID_EVIDENCE -> libelles naturels autorises
```

Exemples d'identifiants produits :

- `SUN_ARIES`
- `MOON_H4`
- `SUN_ARIES_H10`
- `ASPECT_MARS_VENUS_TRINE`
- `ASC_CANCER`
- `HOUSE_10_IN_TAURUS`
- `HOUSE_7_RULER_VENUS_H5`

Ce catalogue n'est pas rendu dans le prompt principal par `NatalInterpretationService`. Il est passe dans `ExecutionFlags.evidence_catalog`, puis utilise cote validation de sortie par `output_validator` pour normaliser et sanitiser le champ `evidence`.

Role exact :

- le prompt demande au modele de produire un champ `evidence` ;
- le validateur compare ces evidences au catalogue autorise ;
- en strict, les evidences invalides peuvent faire echouer ou declencher recovery ;
- en non strict, elles peuvent etre filtrees/nettoyees.

Conclusion : `evidence_catalog` securise la tracabilite apres generation. Il ne sert pas de source narrative directe dans la composition du prompt.

### 5. Adaptation vers le contrat runtime LLM

`AIEngineAdapter.generate_natal_interpretation` transforme `NatalExecutionInput` en `LLMExecutionRequest`.

Mapping cle :

```python
ExecutionUserInput(
    use_case=natal_input.use_case_key,
    feature="natal",
    subfeature=subfeature,
    plan=natal_input.plan,
    locale=natal_input.locale,
    question=natal_input.question,
    persona_id_override=natal_input.persona_id,
)
```

Le `subfeature` est normalise :

- `natal_interpretation`
- `natal_interpretation_short`
- `natal_long_free`

sont mappes vers `subfeature="interpretation"`.

Les use-cases thematiques gardent leur subfeature derivee du use-case, puis la normalisation de taxonomie intervient dans le gateway.

Le contexte porte :

```python
ExecutionContext(
    natal_data=natal_input.natal_data,
    chart_json=natal_input.chart_json,
    astro_context=natal_input.astro_context,
    extra_context={
        "module": natal_input.module,
        "variant_code": natal_input.variant_code,
        "level": natal_input.level,
    },
)
```

Les flags portent :

```python
ExecutionFlags(
    validation_strict=natal_input.validation_strict,
    evidence_catalog=natal_input.evidence_catalog,
)
```

Conclusion : le gateway recoit a la fois la version JSON-string pour rendu prompt et la version objet pour validation.

### 6. Resolution du plan LLM

`LLMGateway.execute_request` suit une pipeline en six etapes :

1. validation taxonomie / legacy mapping ;
2. resolution du plan ;
3. construction des messages ;
4. appel provider ;
5. validation / normalisation de sortie ;
6. repair/fallback ;
7. construction du resultat final et observabilite.

Dans `_resolve_plan`, le gateway :

- fusionne `ExecutionContext.extra_context` avec le contexte ;
- construit un contexte commun via `CommonContextBuilder.build(...)` quand une DB et un user existent ;
- resout une assembly canonique si disponible ;
- resout le persona ;
- applique les profils d'execution ;
- rend le developer prompt.

Le contexte commun peut ajouter :

- `natal_data` depuis le dernier theme DB ;
- `natal_interpretation` depuis une interpretation precedente pour les autres use-cases ;
- `precision_level` ;
- `astrologer_profile` ;
- `period_covered` ;
- `today_date` ;
- `use_case_name`.

Attention : pour le use-case exact `natal_interpretation`, `CommonContextBuilder` ne va pas chercher une interpretation natale precedente, mais il peut recharger `natal_data` depuis le dernier theme. Ensuite `_resolve_plan` fusionne :

```python
context_dict = {**qualified_ctx.payload.model_dump(), **context_dict}
```

Le `context_dict` initial issu de la requete gagne donc en priorite sur le contexte commun si une meme cle existe. Cela preserve le `chart_json` et `natal_data` prepares par `NatalInterpretationService`.

### 7. Rendu des placeholders

Le rendu est effectue par `PromptRenderer.render`.

Les templates utilisent le format :

```text
{{chart_json}}
{{locale}}
{{use_case}}
{{persona_name}}
```

Le renderer :

- resout d'abord les blocs conditionnels `{{#context_quality:...}}...{{/context_quality}}` ;
- verifie les variables requises historiques ;
- applique la gouvernance des placeholders par famille ;
- remplace les placeholders stricts `{{snake_case}}` par leur valeur.

Pour la famille `natal`, le registre de gouvernance declare :

- `chart_json` requis ;
- `natal_data` requis ;
- `locale` optionnel avec fallback `fr-FR` ;
- `use_case` optionnel ;
- `birth_date`, `birth_time`, `birth_timezone` optionnels.

Le contrat canonique declare aussi :

- `natal_interpretation` : `required_prompt_placeholders=["chart_json", "persona_name"]` ;
- `natal_interpretation_short` : `required_prompt_placeholders=["chart_json"]` ;
- modules thematiques : `required_prompt_placeholders=["chart_json", "persona_name"]`.

### 8. Composition finale des messages

`LLMGateway._build_messages` determine si le `chart_json` doit etre remis dans le message utilisateur :

```python
chart_json_in_prompt="{{chart_json}}" in plan.rendered_developer_prompt
```

Puis :

```python
if "chart_json" in context and context["chart_json"] and not chart_json_in_prompt:
    parts.append(f"Technical Data: {context['chart_json']}")
```

Cas nominal actuel :

- les prompts nataux contiennent `{{chart_json}}` ;
- le renderer remplace `{{chart_json}}` par le JSON serialise ;
- `chart_json_in_prompt` vaut true ;
- le message utilisateur ne duplique pas `Technical Data`.

Cas fallback si un prompt ne contient pas `{{chart_json}}` :

- le developer prompt ne contient pas le theme ;
- `_build_messages` ajoute le JSON dans le message utilisateur ;
- cela evite une perte silencieuse de donnees.

Les messages finaux sont :

Mode `structured` :

```text
system: hard/system core
developer: developer prompt rendu avec chart_json si placeholder present
developer: persona_block si applicable
user: question ou fallback ou Technical Data si chart_json absent du developer prompt
```

Mode `chat` :

```text
system
developer
developer persona optionnel
historique
user
```

Les interpretations natales sont configurees en `interaction_mode="structured"` dans les contrats canoniques.

## Prompts nataux actuels

### Seed historique v1

`seed_29_prompts.py` definit :

- `NATAL_SHORT_PROMPT`
- `NATAL_COMPLETE_PROMPT`

Les deux contiennent explicitement :

```text
Données techniques (JSON du thème natal) :
{{chart_json}}
```

Ils imposent :

- source unique : donnees du theme fournies ;
- interdiction d'inventer placements/aspects/maisons ;
- JSON strict `AstroResponse_v1` ;
- champ `evidence`.

### Seed GPT-5 v3

`seed_30_8_v3_prompts.py` definit :

- `NATAL_COMPLETE_PROMPT_V3`
- les prompts thematiques via `_build_thematic_prompt_v3`.

Ils contiennent aussi :

```text
Données techniques (JSON du thème natal) :
{{chart_json}}
```

Le prompt v3 renforce :

- source unique et exclusive ;
- analyse premium hierarchisee ;
- evidence obligatoire et controlee ;
- absence de disclaimers dans la reponse, car geres cote application ;
- sortie `AstroResponse_v3`.

## Variantes fonctionnelles

### Short

Input :

- `level="short"`
- `use_case_key="natal_interpretation_short"`
- `question` optionnelle ; si absente, remplacee par `Interprète mon thème natal.`
- `validation_strict=False`

Le theme est injecte via `chart_json`.

### Complete premium

Input :

- `level="complete"`
- `use_case_key="natal_interpretation"`
- `question=None`
- persona potentiellement requise selon le contrat/assembly ;
- `validation_strict=True`

Le theme est injecte via `chart_json`, et la persona via `persona_name`/`persona_block`.

### Complete free short

Input :

- `variant_code="free_short"`
- `use_case_key="natal_long_free"`
- `level="complete"` pour la persistance ;
- `validation_strict=False`

Le meme `chart_json` est injecte, mais la sortie attendue est reduite : `title`, `summary`, `accordion_titles`, puis projection applicative vers `AstroFreeResponseV1`.

### Modules thematiques

Mapping :

- `NATAL_PSY_PROFILE` -> `natal_psy_profile`
- `NATAL_SHADOW_INTEGRATION` -> `natal_shadow_integration`
- `NATAL_LEADERSHIP_WORKSTYLE` -> `natal_leadership_workstyle`
- `NATAL_CREATIVITY_JOY` -> `natal_creativity_joy`
- `NATAL_RELATIONSHIP_STYLE` -> `natal_relationship_style`
- `NATAL_COMMUNITY_NETWORKS` -> `natal_community_networks`
- `NATAL_VALUES_SECURITY` -> `natal_values_security`
- `NATAL_EVOLUTION_PATH` -> `natal_evolution_path`

Ces modules bypassent cache et persistance pour eviter de melanger une reponse generique/premium avec une reponse module. L'injection du theme reste identique : `chart_json` + `natal_data` + `evidence_catalog`.

## Validation et securisation

### Validation d'entree

`LLMGateway._build_validation_payload` reconstruit le payload valide contre l'`input_schema`.

Regle importante :

```python
if prop == "chart_json":
    if context_dict.get("natal_data") is not None:
        payload[prop] = context_dict["natal_data"]
```

Donc pour la validation JSON schema, `natal_data` dictionnaire est prioritaire sur `chart_json` string. Si `natal_data` est absent, le gateway tente de parser `chart_json`.

Effet : le prompt peut recevoir la chaine JSON, mais la validation d'entree travaille sur l'objet JSON.

### Validation de sortie

La sortie est validee par schema :

- `AstroResponse_v1` pour short / legacy ;
- `AstroResponse_v3` pour complete v3 ;
- schema free pour `natal_long_free`.

Le champ `evidence` est nettoye via `evidence_catalog`. Ce mecanisme limite les references astrologiques non presentes dans le theme.

### Gestion des donnees manquantes

Les donnees manquantes sont traitees en amont :

- sans heure : maisons, angles et maisons des planetes sont nullifies ou omis ;
- sans lieu : lieu et angles sont nullifies ;
- le prompt demande explicitement de ne pas combler les absences ;
- `degraded_mode` informe le modele de la qualite du theme.

## Points de vigilance

### 1. `chart_json` dans le developer prompt

Les prompts actuels injectent le JSON complet dans le developer prompt. C'est coherent avec les seeds et les tests existants, mais cela melange instructions et donnees.

Le gateway contient deja une strategie alternative : si `{{chart_json}}` n'est pas dans le developer prompt, le JSON est ajoute au message utilisateur.

Arbitrage possible :

- garder l'etat actuel pour compatibilite prompt/evals ;
- ou migrer progressivement vers un developer prompt contenant uniquement les consignes et un user message contenant les donnees techniques.

### 2. Double representation `chart_json` / `natal_data`

Le systeme transporte deux versions du theme :

- string JSON pour rendu ;
- dict pour validation.

C'est utile, mais cela cree un risque de divergence si une future modification renseigne l'un sans l'autre. Aujourd'hui `NatalInterpretationService` les derive du meme `chart_json_dict`, ce qui est sain.

### 3. `evidence_catalog` non visible dans le prompt

Le modele doit deviner les identifiants `evidence` depuis le contenu de `chart_json` et les consignes du prompt. Le catalogue enrichi n'est pas fourni au modele comme liste autorisee.

Avantage : prompt plus court.

Risque : le modele peut produire des IDs proches mais invalides, ensuite filtres ou rejetes par validation.

### 4. Contexte commun recharge `natal_data`

`CommonContextBuilder` peut recharger le theme depuis la DB pendant `_resolve_plan`. La fusion donne priorite au contexte transmis par `NatalInterpretationService`, donc le comportement nominal reste coherent.

Point a surveiller : toute inversion de l'ordre de merge pourrait remplacer le payload prepare par le service par une autre version issue de la DB.

### 5. Use-case `natal_long_free`

`natal_long_free` suit le meme adapter, mais n'apparait pas dans les contrats canoniques vus comme `natal_interpretation` / `natal_interpretation_short`. Il depend donc davantage des configs/seeds runtime. A surveiller dans les evolutions de gouvernance.

## Schema de flux

```text
Utilisateur authentifie
  |
  v
POST /v1/natal/interpretation
  |
  |-- UserNatalChartService.get_latest_for_user()
  |-- UserBirthProfileService.get_for_user()
  v
NatalInterpretationService.interpret()
  |
  |-- _detect_degraded_mode()
  |-- build_chart_json(NatalResult, BirthProfile)
  |-- build_enriched_evidence_catalog(chart_json)
  |-- selection use_case_key
  v
NatalExecutionInput
  |
  |-- chart_json: string JSON
  |-- natal_data: dict
  |-- evidence_catalog: dict/list
  v
AIEngineAdapter.generate_natal_interpretation()
  |
  v
LLMExecutionRequest
  |
  |-- user_input: feature=natal, subfeature=..., plan=..., locale=...
  |-- context: natal_data, chart_json, astro_context, extra_context
  |-- flags: validation_strict, evidence_catalog
  v
LLMGateway.execute_request()
  |
  |-- _resolve_plan()
  |-- PromptRenderer.render(developer_prompt, vars)
  |-- _build_messages()
  |-- provider call
  |-- validate_output(..., evidence_catalog)
  v
GatewayResult.structured_output
  |
  v
NatalInterpretationService
  |
  |-- mapping AstroResponse v1/v2/v3/free
  |-- persistence UserNatalInterpretationModel
  v
NatalInterpretationResponse
```

## Conclusion

L'injection des donnees de theme astral est centralisee et relativement robuste :

- la route ne fabrique pas de prompt ;
- le service metier construit un `chart_json` canonique ;
- l'adapter traduit ce payload en contrat runtime ;
- le gateway rend les placeholders et evite la perte de donnees si `chart_json` n'est pas dans le developer prompt ;
- la validation d'entree privilegie l'objet `natal_data` ;
- la validation de sortie s'appuie sur `evidence_catalog`.

Le point architectural principal a clarifier pour la suite est la localisation nominale des donnees techniques : developer prompt via `{{chart_json}}` comme aujourd'hui, ou message utilisateur via le fallback deja code. Le systeme supporte les deux, mais les prompts semes et les tests actuels documentent plutot le premier choix.
