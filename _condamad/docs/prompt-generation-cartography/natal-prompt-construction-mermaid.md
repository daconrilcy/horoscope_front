<!-- Commentaire global: ce document ajoute les diagrammes Mermaid du flux de construction des prompts natals sans changer le runtime. -->

# Graphiques Mermaid de construction des prompts de theme astral natal

Ce document est une annexe graphique de `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`. Il couvre les plans `free`, `basic` et `premium` pour le flux natal moderne fonde sur `llm_astrology_input_v1`.

Aucun appel provider LLM reel n'est represente ou effectue par ces diagrammes. La frontiere s'arrete au payload gateway-owned `messages` et aux provider parameters documentes comme `provider-parameter`.

Sources principales: `_condamad/docs/prompt-generation-cartography/prompt-generation-current-implementation.md`, `_condamad/docs/prompt-generation-cartography/natal-prompt-construction-by-plan.md`, `_condamad/audits/prompt-generation-cartography/2026-05-27-1822/03-runtime-gateway-handoff-audit.md`, `_condamad/audits/prompt-generation-cartography/2026-05-27-1835/04-natal-astrology-input-audit.md`, `backend/app/domain/llm/runtime/gateway.py`, `backend/app/domain/llm/configuration/assembly_resolver.py`, `backend/app/domain/llm/prompting/prompt_renderer.py`, `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`.

## Comment lire les diagrammes

- Les labels Mermaid restent ASCII pour faciliter le rendu.
- `prompt-visible` signifie inclus dans `system_core`, `developer prompt`, `persona astrologue` ou `payload user`.
- `backend-only`, `validation-only`, `audit-only` et `provider-parameter` indiquent une donnee hors payload prompt-visible.
- Les plans partagent les calculs backend; ils different par selection prompt-visible, profondeur editoriale, sections et budget.
- Les blocs `evidence`, `provenance`, `projection_hash`, `llm_input_hash`, `provider_response`, `chart_json`, `natal_data` et `observability` ne sont pas des inputs prompt-visible du flux natal moderne.

## Pipeline global theme astral

```mermaid
flowchart TD
  BirthData["birth data"] --> NatalCalc["natal calculations"]
  NatalCalc --> StructuredFacts["structured_facts_v1"]
  StructuredFacts --> NarrativeInput["AINarrativeInputContract"]
  StructuredFacts --> ClientProjection["client_interpretation_projection_v1"]
  NarrativeInput --> LLMInput["llm_astrology_input_v1"]
  ClientProjection --> LLMInput
  LLMInput --> Assembly["assembly resolver"]
  Assembly --> Renderer["PromptRenderer"]
  Renderer --> Messages["provider-ready messages"]
  Messages --> Boundary["no provider call in this document"]
```

Legende: le pipeline relie `birth data`, input natal, assembly et `messages`; le diagramme s'arrete avant tout appel provider.

## Construction des donnees injectees

```mermaid
flowchart LR
  FactsSource["structured_facts_v1"] --> Facts["facts prompt-visible"]
  SignalsSource["AINarrativeInputContract"] --> Signals["signals prompt-visible"]
  LimitsSource["missing data and readiness"] --> Limits["limits prompt-visible"]
  ShapingSource["client projection by plan"] --> Shaping["shaping prompt-visible"]
  Facts --> HashMaterial["llm_input_hash material"]
  Signals --> HashMaterial
  Limits --> HashMaterial
  Shaping --> HashMaterial
  Evidence["evidence validation-only"] -. excluded .-> HashMaterial
  Provenance["provenance audit-only"] -. excluded .-> HashMaterial
```

Legende: seuls `facts`, `signals`, `limits` et `shaping` forment le materiau prompt-visible; `evidence` et `provenance` restent hors prompt.

## Differenciation par plan

```mermaid
flowchart TD
  SharedCalc["shared backend calculations"] --> Free["free"]
  SharedCalc --> Basic["basic"]
  SharedCalc --> Premium["premium"]
  Free --> FreePrompt["prompt-visible selection reduced"]
  Basic --> BasicPrompt["prompt-visible selection intermediate"]
  Premium --> PremiumPrompt["prompt-visible selection rich"]
  FreePrompt --> FreeDepth["short editorial depth and low budget"]
  BasicPrompt --> BasicDepth["controlled sections and medium budget"]
  PremiumPrompt --> PremiumDepth["advanced sections and higher budget"]
```

Legende: `free`, `basic` et `premium` reutilisent les calculs; la difference porte sur le shaping, la profondeur editoriale et le budget.

## Introduction astrologue/persona

```mermaid
flowchart TD
  Config["PromptAssemblyConfigModel"] --> Resolver["resolve_assembly"]
  Resolver --> DevPrompt["developer prompt"]
  Resolver --> PersonaConfig{"persona enabled"}
  PersonaConfig -->|yes| Persona["persona astrologue developer message"]
  PersonaConfig -->|no| NoPersona["no persona message"]
  DevPrompt --> Gateway["LLMGateway.compose_structured_messages"]
  Persona --> Gateway
  NoPersona --> Gateway
```

Legende: la persona est dessinee separement du `developer prompt`; les owners cites sont `assembly_resolver.py` et `gateway.py`.

## Securite et non-invention

```mermaid
flowchart TD
  HardPolicy["hard policy"] --> AssemblySafety["assembly safety layer"]
  Limits["limits prompt-visible"] --> NonInvention["non-invention boundary"]
  InputValidation["input validation"] --> Messages["messages"]
  Messages --> OutputValidation["output validation"]
  OutputValidation -->|invalid| Repair["repair request"]
  Repair -->|still invalid| Rejection["controlled rejection"]
  OutputValidation -->|valid| Result["validated result"]
```

Legende: hard policy, non-invention, validation, repair et rejection sont des couches distinctes; elles ne fusionnent pas en un prompt unique.

## Messages finaux provider

```mermaid
sequenceDiagram
  participant G as LLMGateway
  participant R as PromptRenderer
  participant M as messages
  G->>R: render developer prompt
  R-->>G: developer prompt
  G->>M: 1 system_core
  G->>M: 2 developer prompt
  G->>M: 3 persona astrologue optional
  G->>M: 4 payload user
  G->>M: provider-parameter metadata kept outside payload user
```

Legende: l'ordre structure est `system_core`, `developer prompt`, persona optionnelle, puis `payload user`; les provider parameters restent hors payload user.

## Frontiere prompt-visible vs backend-only

```mermaid
flowchart LR
  LLMInput["llm_astrology_input_v1 full object"] --> Filter["gateway prompt filter"]
  Filter --> Visible["prompt-visible: facts signals limits shaping"]
  LLMInput -. excluded .-> ValidationOnly["validation-only: evidence grounding_status validation_owner"]
  LLMInput -. excluded .-> AuditOnly["audit-only: provenance projection_hash llm_input_hash provider_response observability"]
  LLMInput -. excluded .-> BackendOnly["backend-only: chart_json natal_data request_id trace_id"]
  Visible --> PayloadUser["payload user"]
  ValidationOnly -. not prompt-visible .-> PayloadUser
  AuditOnly -. not prompt-visible .-> PayloadUser
  BackendOnly -. not prompt-visible .-> PayloadUser
```

Legende: `chart_json`, `natal_data`, `projection_hash`, `llm_input_hash`, `provider_response` et `observability` restent hors `payload user`.

## Exclusions et no-call boundary

```mermaid
flowchart TD
  Messages["compiled messages"] --> Params["provider parameters"]
  Params --> Stop["STOP no provider call"]
  Stop --> Review["documentation review only"]
  ProviderResponse["provider_response"] -. post-provider only .-> Review
  Observability["observability"] -. audit-only post-provider .-> Review
```

Legende: le document montre la limite avant provider; `provider_response` et `observability` sont post-provider ou audit-only, pas des entrees du prompt.

## Verification notes

- `diagram`: les sections ci-dessus couvrent `Pipeline global theme astral`, `Construction des donnees injectees`, `Differenciation par plan`, `Introduction astrologue/persona`, `Securite et non-invention`, `Messages finaux provider`, `Frontiere prompt-visible vs backend-only` et `Exclusions et no-call boundary`.
- `plan`: les plans `free`, `basic` et `premium` sont explicites dans le diagramme de differenciation.
- `visibility`: les termes `prompt-visible`, `backend-only`, `validation-only`, `audit-only` et `provider-parameter` sont declares et utilises.
- `source`: les chemins sources sont cites en tete de document; les textes exacts de prompt restent a extraire depuis la configuration runtime.
- `legend`: chaque bloc Mermaid a une legende courte sous le diagramme.
