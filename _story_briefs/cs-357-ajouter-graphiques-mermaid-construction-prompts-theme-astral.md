# CS-357 - Ajouter Des Graphiques Mermaid Construction Prompts Theme Astral

<!-- Commentaire global: ce brief cadre les schemas Mermaid necessaires pour comprendre visuellement la construction des prompts de theme astral. -->

## Resume

Ajouter des graphiques Mermaid permettant de comprendre parfaitement comment les prompts finaux de theme astral sont construits avant envoi au moteur LLM, avec un focus explicite sur les plans `free`, `basic` et `premium`.

Cette story complete CS-356. Elle peut enrichir le meme document ou produire un document annexe dedie aux schemas.

## Contexte

Le flux de prompt natal combine plusieurs couches:

- donnees de naissance et calculs astrologiques;
- builders de projections et de signaux;
- `llm_astrology_input_v1`;
- resolution de use case et assembly;
- rendu de placeholders;
- persona astrologue;
- hard policy et limites;
- composition `system`, `developer`, persona, `user`;
- handoff provider sans appel reel dans la documentation.

Un lecteur doit pouvoir suivre ce flux avec des schemas qui distinguent les chemins nominaux, les exclusions et les differences par plan.

## Objectif

Produire des schemas Mermaid maintenables qui montrent:

- le pipeline complet entree -> prompt compile;
- la construction de `llm_astrology_input_v1`;
- la matrice prompt-visible vs backend-only;
- la resolution assembly/persona/plan rules;
- la composition finale des messages provider;
- les differences de profondeur entre `free`, `basic` et `premium`;
- le role des garde-fous de securite;
- la frontiere stricte "pret a envoyer" sans appel provider.

## Perimetre inclus

1. Lire CS-356 si disponible.
2. Lire la cartographie CS-350.
3. Ajouter ou completer les schemas Mermaid du document cible.
4. Verifier que les schemas utilisent des labels courts et source-alignes.
5. Ajouter une courte legende sous chaque schema.
6. Ajouter une section "Comment lire les diagrammes".

## Hors perimetre

- Modifier le runtime.
- Modifier les prompts.
- Faire un appel provider.
- Generer les exemples JSON finaux: cela appartient a CS-358.
- Ajouter une dependance de rendu Mermaid.

## Sources obligatoires

- `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`
- `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md` si CS-356 est deja realisee
- `_condamad/audits/prompt-generation-cartography/**/03-runtime-gateway-handoff-audit.md`
- `_condamad/audits/prompt-generation-cartography/**/04-natal-astrology-input-audit.md`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/domain/llm/configuration/assembly_resolver.py`
- `backend/app/domain/llm/prompting/prompt_renderer.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`

## Livrables attendus

Option preferee: enrichir le document de CS-356:

```text
_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md
```

Si le document devient trop long, creer:

```text
_condamad/docs/prompt-generation-cartography/natal-prompt-construction-mermaid.md
```

## Schemas Mermaid obligatoires

### 1. Pipeline global theme astral

Doit montrer:

`Birth data` -> calculs natals -> projections/builders -> `llm_astrology_input_v1` -> projection prompt-visible -> assembly -> renderer -> messages provider -> frontiere "no provider call".

### 2. Construction des donnees injectees

Doit montrer les sources de:

- `facts`;
- `signals`;
- `limits`;
- `shaping`;
- `evidence`;
- `provenance`;
- exclusions legacy.

### 3. Differenciation par plan

Doit montrer que les trois plans passent par les memes calculs, puis divergent sur:

- selection des donnees prompt-visibles;
- profondeur editoriale;
- budget longueur/tokens;
- schema de sortie;
- sections attendues.

### 4. Introduction astrologue/persona

Doit montrer:

`PromptAssemblyConfig` -> persona config -> `compose_persona_block` -> message `developer` optionnel -> messages provider.

### 5. Securite et non-invention

Doit montrer:

hard policy, required placeholders, limites, exclusions audit-only, output validation, repair/rejection.

### 6. Messages finaux provider

Doit etre un `sequenceDiagram` ou `flowchart` indiquant l'ordre exact:

1. `system_core`;
2. `developer prompt`;
3. persona astrologue optionnelle;
4. payload user JSON prompt-visible;
5. provider parameters hors prompt.

### 7. Frontiere prompt-visible vs backend-only

Doit montrer explicitement les exclusions:

- `evidence`;
- `provenance`;
- `projection_hash`;
- `llm_input_hash`;
- `provider_response`;
- observability;
- replay snapshots;
- `chart_json`;
- `natal_data`.

## Contraintes Mermaid

- Utiliser des labels ASCII courts.
- Eviter les blocs trop larges.
- Preferer plusieurs schemas simples a un schema illisible.
- Les diagrammes doivent rester compatibles avec Mermaid standard.
- Ne pas representer un appel provider si la story documente seulement le payload pret a envoyer.
- Ajouter une phrase de contexte sous chaque diagramme.

## Criteres d'acceptation

1. Au moins sept schemas Mermaid sont presents.
2. Les schemas couvrent les trois plans `free`, `basic`, `premium`.
3. La persona astrologue est representee comme bloc distinct du developer prompt principal.
4. La securite est representee avant et apres provider, sans confondre validation et prompt.
5. La frontiere "prompt compile pret a envoyer" est visible.
6. Les donnees exclues du prompt sont visibles.
7. Les schemas sont cites depuis ou integres au document de CS-356.

## Validation attendue

```powershell
rg -n "```mermaid|flowchart|sequenceDiagram|free|basic|premium|persona|hard policy|prompt-visible|backend-only|no provider call" _condamad/docs/prompt-generation-cartography
```

## Risques

Le risque principal est de produire des schemas decoratifs mais incomplets. Chaque diagramme doit expliquer une decision ou une frontiere du runtime.
