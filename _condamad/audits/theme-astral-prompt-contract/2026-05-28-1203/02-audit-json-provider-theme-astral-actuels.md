# CS-362 - Audit JSON provider theme astral actuels

## Executive summary

Les payloads `free`, `basic` et `premium` sont valides en JSON et partagent un squelette top-level stable. Le constat "les structures top-level et imbriquees ne sont pas stables" est donc invalide pour les cles top-level, `llm_astrology_input_v1`, `facts/signals/limits/shaping`, `response_format` et `provider_parameters`. Il reste valide pour l'enveloppe `messages`, car `free` a trois messages alors que `basic` et `premium` en ont quatre.

Les divergences de quantite sont fortes et intentionnellement plan-specifiques: `free` envoie 2 positions, 0 maisons et 3 aspects; `basic` envoie 7 positions, 4 maisons et 8 aspects; `premium` envoie 11 positions, 12 maisons et 14 aspects. Cette variabilite doit etre preservee comme choix de delivery, pas confondue avec une derive structurelle.

Le plan commercial est visible dans les payloads: top-level `plan` et `shaping.plan` dans le message utilisateur. Les champs audit/runtime/hashes/provenance sont listes dans `audit_excluded_from_prompt`; ils ne sont pas presents comme valeurs prompt-visible, mais la liste d'exclusion elle-meme appartient au provider payload actuel. Le `basic` confirme aussi une incoherence: le developer prompt contient des consignes orientees premium.

## Tableau comparatif free/basic/premium

| Plan | Surface | Structure status | Value status | LLM visibility | Evidence | CS-363 recommendation |
|---|---|---|---|---|---|---|
| free | top-level | stable | plan-variable | top-level provider artifact | E-004 | keep skeleton; move commercial plan backend-only |
| basic | top-level | stable | plan-variable | top-level provider artifact | E-004 | keep skeleton; move commercial plan backend-only |
| premium | top-level | stable | plan-variable | top-level provider artifact | E-004 | keep skeleton; move commercial plan backend-only |
| free | messages | divergent | 3 roles: system/developer/user | prompt-visible | E-004, E-005 | define explicit message-role policy |
| basic | messages | divergent | 4 roles: system/developer/developer/user | prompt-visible | E-004, E-005 | keep persona if product-owned; remove premium wording |
| premium | messages | divergent | 4 roles: system/developer/developer/user | prompt-visible | E-004, E-005 | keep persona if product-owned |
| all | response_format | stable | same schema property keys | provider parameter | E-004 | keep and version as output_contract |
| all | provider_parameters | stable keys | values vary by plan | provider-only | E-004, E-005 | move backend-only |

## Divergences structurelles

- Top-level keys are stable across all three files: `use_case`, `plan`, `mode`, `provider_call_performed`, `generation_kind`, `model`, `messages`, `response_format`, `provider_parameters`, `audit_excluded_from_prompt`.
- `llm_astrology_input_v1` root is stable across all three user messages: `facts`, `limits`, `shaping`, `signals`.
- Nested key families are stable for audited blocks: `facts`, `signals`, `limits`, `shaping`, `response_format` schema properties and `provider_parameters`.
- `messages` is structurally divergent: `free` has no second developer/persona message; `basic` and `premium` do.
- Conclusion: structural instability exists at message-envelope level, not at the main JSON key contract level.

## Divergences de quantite de donnees

| Axis | free | basic | premium | Reading |
|---|---:|---:|---:|---|
| messages | 3 | 4 | 4 | persona/developer message varies |
| developer chars | 6068 | 12070 | 29881 | prompt volume grows by plan |
| user chars | 3599 | 7192 | 11183 | selected facts grow by plan |
| positions | 2 | 7 | 11 | plan-specific variability |
| houses | 0 | 4 | 12 | plan-specific variability |
| major_aspects | 3 | 8 | 14 | plan-specific variability |
| dominants | 1 | 2 | 3 | plan-specific variability |
| interpretation_hints | 2 | 3 | 4 | plan-specific variability |
| allowed_fact_groups | 3 | 7 | 8 | delivery selection grows |
| section_codes | 4 | 5 | 9 | output depth grows |
| max_output_tokens | 4000 | 16000 | 32000 | provider-only delivery policy |

## Donnees inutiles ou backend-only

| Data family | Current evidence | Decision |
|---|---|---|
| plan commercial | top-level `plan` and prompt-visible `shaping.plan` | move backend-only / replace |
| metadata runtime | `use_case`, `mode`, `generation_kind`, `model`, `provider_parameters`, `provider_call_performed` | move backend-only |
| audit data | `audit_excluded_from_prompt` top-level list | move backend-only |
| hashes | `projection_hash`, `llm_input_hash` listed as excluded | keep excluded; drop list from provider payload |
| traces | no direct trace field observed | keep absent |
| debug | no direct debug field observed | keep absent |
| provenance/provider_response/observability/replay_snapshot | listed as excluded | keep backend-only |
| chart_json/natal_data | listed as excluded | drop-from-provider-payload |
| source_metadata | prompt-visible inside `facts` | replace by split birth_context vs backend-only calculation metadata |

## Donnees manquantes pour la redaction

| Needed contract family | Current substitute | Gap | Recommendation |
|---|---|---|---|
| delivery_profile | `editorial_depth_profile`, `precision_level`, `output_expectations`, `llm_input_selection` | mixed with commercial plan | replace |
| feature_context | `module`, `use_case`, prompt prose | runtime names leak into contract | replace |
| astrologer_voice | second developer message in `basic/premium`; absent in `free` | not a stable named block | keep/replace with explicit voice contract |
| interpretation_material | facts and short hints | no rich material block | replace via CS-365 material builder |
| output_contract | `response_format` plus prompt text | split owner | keep schema; version durable output contract |

## Incoherences de prompt

- `basic` contains premium-oriented instructions in the developer prompt evidence path; this confirms the brief risk.
- Developer and user messages duplicate `llm_astrology_input_v1` content: rendered developer prompt includes the data and the user message sends the same carrier again.
- `plan` is visible to the model as a commercial label. The future contract should expose delivery requirements without commercial vocabulary.
- `source_metadata` mixes LLM-useful context and backend-only calculation details.

## Matrice keep / move backend-only / replace / drop-from-provider-payload

| Surface | keep | move backend-only | replace | drop-from-provider-payload |
|---|---|---|---|---|
| Stable top-level skeleton | yes | no | no | no |
| `messages` carrier | yes | no | role policy to define | no |
| Commercial `plan` | no | yes | yes, by delivery profile | no |
| `provider_parameters` | no | yes | no | no |
| `response_format` | yes | no | version as output_contract | no |
| `audit_excluded_from_prompt` | no | yes | no | yes from provider payload artifact |
| `projection_hash`, `llm_input_hash` | no | yes | no | yes |
| `provider_response`, `observability`, `replay_snapshot`, `provenance` | no | yes | no | yes |
| `chart_json`, `natal_data` | no | yes | no | yes |
| `source_metadata` | partial | yes for calculation metadata | yes as birth_context | no |
| `llm_input_selection` | yes | no | maybe under delivery_profile | no |
| `interpretation_hints` | partial | no | yes as interpretation_material | no |
| premium wording in basic | no | no | yes as basic delivery contract | yes |

## Recommandations pour CS-363

1. Define a target provider contract with stable key shape and explicit plan-variable value families.
2. Remove commercial `plan` from prompt-visible content and replace it with `delivery_profile`.
3. Split `source_metadata` into LLM-needed `birth_context` and backend-only calculation/runtime metadata.
4. Choose a single prompt-visible data carrier; avoid developer/user duplication of `llm_astrology_input_v1`.
5. Preserve `response_format` but bind it to a versioned `output_contract`.
6. Add a guard proving `basic` does not contain premium-only prompt instructions.
7. Keep trace/debug absent and keep audit/provenance/hash/provider-response data backend-only.
