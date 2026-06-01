# Rapport date - Analyse live test interpretations LLM natal

Date du rapport: 2026-06-01

Utilisateur teste: `daconrilcy@hotmail.com` (`users.id=14`)

Chart observe: `f8e6468c-5c5f-4fd2-aa3a-93084fbeedfa`

## Synthese executive

Le bug fonctionnel profond est confirme. Le parcours live a produit trois interpretations publiques persistantes pour le meme theme natal:

| id | level DB | use_case DB | variant_code | persona_id | plan audit | role reel |
| --- | --- | --- | --- | --- | --- | --- |
| 6 | `COMPLETE` | `natal_long_free` | `free_short` | null | `free` | lecture Free, exposee publiquement comme `natal_interpretation_short` |
| 7 | `SHORT` | `natal_interpretation_short` | null | null | `free` | nouvelle lecture courte generee pendant/apres passage Basic |
| 8 | `COMPLETE` | `natal_interpretation` | `single_astrologer` | `c0a80101-...` | `basic` | lecture complete Basic, mais issue d'un prompt/contrat premium puis fallback Basic V2 |

Le contenu vu "en Basic tout de suite" n'est pas une lecture Basic canonique: la ligne `id=7` est un `natal_interpretation_short` genere avec `plan=free` dans les logs LLM, meme apres creation du profil Stripe Basic. Le front declenche explicitement ce comportement via `shouldRefreshShortAfterBasicUpgrade`.

La lecture complete Basic (`id=8`) est elle aussi instable: elle passe par `use_case=natal_interpretation`, un prompt publie qui contient encore les exigences "PREMIUM", "complete enrichi" et `AstroResponse_v3`. Le service ajoute un payload Basic, puis valide a posteriori. Dans le cas observe, le validateur a active un fallback deterministe (`was_fallback=1`), ce qui explique le texte Basic generique et pauvre.

## Chronologie observee

Donnees lues en read-only dans `backend/horoscope.db`.

| Horodatage UTC | Evenement |
| --- | --- |
| `2026-06-01 04:20:41` | Creation utilisateur `daconrilcy@hotmail.com`. |
| `2026-06-01 04:21:06` | Creation du chart `f8e6468c-...`. |
| `2026-06-01 04:21:32` | Generation `natal_long_free`, `plan=free`, persistee en `id=6`. |
| `2026-06-01 04:21:50` | Creation locale du profil Stripe, encore avant snapshot complet. |
| `2026-06-01 04:22:19` | Profil Stripe mis a jour: `entitlement_plan=basic`, `subscription_status=active`. |
| `2026-06-01 04:22:58` | Generation `natal_interpretation_short`, encore loggee `plan=free`, request `18a43bd...`; elle met a jour la ligne `id=7`. |
| `2026-06-01 04:28:58` | Generation `natal_interpretation`, `plan=basic`, persona standard; persistee en `id=8`, `was_fallback=1`. |

Point important: `created_at` de `id=7` reste `04:21:47`, mais son payload correspond au refresh ulterieur. Le service met a jour la ligne existante sans mettre a jour `created_at`, ce qui rend `persisted_at` trompeur.

## Cartographie des flux

### Flux Free

Le front, quand `isLockedFree=true`, autorise une requete `use_case_level=complete` sans persona. Le backend gate alors `natal_chart_long`, recoit `variant_code=free_short`, puis redirige dans `_generate_free_short`.

Resultat:

- DB: `level=COMPLETE`, `use_case=natal_long_free`, `variant_code=free_short`;
- API publique GET: remappe en `meta.level=short`, `use_case=natal_interpretation_short`;
- rendu: `FreePublicReading`.

Ce double langage `COMPLETE` en DB mais `short` en public rend le reste du parcours fragile.

### Flux Basic "immediat"

Dans `frontend/src/features/natal-chart/NatalInterpretation.tsx`, le cas:

- plan `single_astrologer`;
- utilisateur non free lock;
- presence d'une ancienne `free_short`;
- absence de vraie ligne `SHORT`;

active `shouldRefreshShortAfterBasicUpgrade`. L'effet associe force:

- `useCaseLevel="short"`;
- `forceRefresh=true`;
- nouvel appel `POST /v1/natal/interpretation`.

Ce chemin court ne passe pas par `NatalChartLongEntitlementGate`, car le gate n'est execute que si `body.use_case_level == "complete"`. Il depend ensuite de `EffectiveEntitlementResolverService.resolve_b2c_user_snapshot` dans le service LLM.

Dans le live test, le log LLM de la requete `18a43bd4cddb4719a521a99768f988c3` est:

- `use_case=natal_interpretation_short`;
- `plan=free`;
- `model=gpt-4o-mini`;
- `latency_ms=28981`;
- `fallback_triggered=0`.

Donc l'interpretation presentee comme Basic a ete generee avec le prompt court Free.

### Flux Basic complete

Le clic sur "Obtenir le theme natal complet" ouvre le selecteur de persona et lance:

- `use_case_level=complete`;
- `persona_id=c0a80101-...`;
- `variant_code=single_astrologer` via le gate backend;
- `use_case_key=natal_interpretation`.

Le service detecte `user_plan == "basic"` et construit `basic_natal_prompt_payload`. Le gateway remplace ensuite la variable `llm_astrology_input_v1` par ce payload Basic quand le contexte contient `BASIC_NATAL_PROMPT_PAYLOAD_KEY`.

Probleme: le prompt actif pour `natal_interpretation` reste un prompt premium:

- il contient `EXIGENCE PREMIUM`;
- il declare le mode `"complete enrichi"`;
- il demande un JSON strict `AstroResponse_v3`;
- il demande 9 a 10 sections longues.

Le provider produit donc une reponse de forme premium, pas un draft Basic. Le validateur Basic rejette cette forme et bascule vers `build_basic_natal_deterministic_fallback`. La ligne `id=8` contient alors a la fois:

- un payload top-level premium brut (`title`, `summary`, `sections`, `highlights`, `advice`);
- un `basic_natal_interpretation_v2` fallback, generique;
- `was_fallback=1`;
- `answer_type=premium` malgre `plan=basic`.

## Causes racines

### 1. Le front cree une interpretation courte supplementaire apres upgrade Basic

Le comportement `shouldRefreshShortAfterBasicUpgrade` est incompatible avec la regle produit exprimee pendant le test: "une interpretation Free, une autre Basic". Il cree une troisieme famille fonctionnelle:

- Free short public depuis `natal_long_free/free_short`;
- Short regeneree depuis `natal_interpretation_short`;
- Complete Basic depuis `natal_interpretation/single_astrologer`.

Les tests front actuels codifient en partie ce comportement: ils verifient que le CTA complet reste disponible en Basic tant que le quota n'est pas epuise, mais ne verifient pas l'invariant "maximum deux interpretations visibles Free puis Basic".

### 2. Le cache/pipeline entitlement peut rester sur `free` apres checkout Stripe

Le statut d'abonnement est mis en cache process-local (`subscription_cache.py`). Le webhook Stripe invalide bien le cache dans `StripeBillingProfileService`, mais l'invalidation est locale au process. Dans le live test, apres le snapshot Stripe Basic (`04:22:19`), un appel LLM `natal_interpretation_short` a encore ete resolu `plan=free` (`04:22:58`).

Hypotheses compatibles avec les preuves:

- cache `free` encore present dans le process qui traite l'API LLM;
- webhook et API servis par des processus differents;
- requetes front lancees avant convergence du snapshot entitlement;
- absence de bypass cache pour les actions immediatement post-checkout.

### 3. Le Basic complete utilise le mauvais contrat de generation

Le Basic complete devrait avoir un contrat provider dedie. Aujourd'hui il utilise `natal_interpretation` et tente de contraindre le prompt premium en remplaçant la donnee d'entree par `basic_natal_prompt_payload`.

Ce n'est pas suffisant. Le texte du prompt, le schema de sortie et les exigences editoriales restent premium. Le fallback Basic devient alors la voie normale des sorties non conformes.

### 4. L'audit classe Basic complete comme `premium`

`_answer_type_for_audit` retourne `premium` pour tout `level=complete` qui n'est pas `variant_code=free_short`. La ligne Basic complete observee a donc:

- `plan=basic`;
- `variant_code=single_astrologer`;
- `answer_type=premium`.

Cette incoherence rend les audits et diagnostics moins fiables.

### 5. La cle de cache/persistence service n'inclut pas toujours le `chart_id`

Dans `NatalInterpretationService.interpret`, la recherche de cache initiale filtre par:

- `user_id`;
- `level`;
- `persona_id`;
- `variant_code` pour complete.

Elle ne filtre pas `chart_id`. La persistence utilise aussi une requete `unique_stmt` sans `chart_id`. Pourtant l'index DB unique inclut bien `chart_id`.

Risque: une interpretation d'un ancien theme peut etre servie ou ecrasee pour un nouveau theme du meme utilisateur. Ce n'est pas le declencheur principal du live test, mais c'est un defaut structurel severe.

## Pourquoi le contenu Basic "dit n'importe quoi"

Deux mecanismes se cumulent:

1. La reponse immediate Basic (`id=7`) est en realite une sortie courte Free, donc elle peut parler d'une "forte influence de Venus et du Soleil", "Ascendant en Cancer", etc. avec peu de garanties Basic.
2. La reponse complete Basic (`id=8`) passe par un prompt premium puis fallback Basic. Le `basic_natal_interpretation_v2` fallback contient des textes generiques du type "s'eclaire a partir des annexes publiques disponibles", signe que le draft provider n'a pas respecte le contrat Basic.

Le fallback evite d'exposer un payload techniquement invalide, mais il ne produit pas une vraie lecture Basic qualitative. Il masque le rejet au lieu de bloquer ou de regenerer avec un prompt Basic correct.

## Corrections recommandees

1. Supprimer ou neutraliser `shouldRefreshShortAfterBasicUpgrade`.
   - Apres upgrade Basic, ne pas generer un nouveau `natal_interpretation_short`.
   - Afficher la Free existante jusqu'a generation Basic complete, ou lancer directement le flux Basic attendu selon la decision produit.

2. Rendre le parcours Basic atomique cote backend.
   - Pour `single_astrologer`, le bouton doit produire une seule interpretation Basic canonique.
   - Le backend devrait refuser une generation `short` post-upgrade si elle sert uniquement de substitut Basic.

3. Creer un vrai contrat LLM Basic.
   - Use case ou assembly dedie Basic, avec prompt sans exigences premium.
   - Schema de sortie draft Basic compatible avec `validate_basic_natal_draft_against_plan`.
   - Interdire `template_source=fallback_default` pour `plan=basic` + `natal_interpretation`.

4. Ne plus persister le payload premium brut comme interpretation publique Basic.
   - Si le draft provider est rejete, stocker le brut en audit-only.
   - La ligne publique doit porter uniquement le contrat Basic accepte, ou etre rejetee.

5. Corriger l'audit.
   - `answer_type` doit devenir `basic` quand `plan=basic` ou `variant_code=single_astrologer`.
   - `was_fallback=1` doit etre observable dans l'UI/admin ou declencher une alerte.

6. Aligner cache et unicite sur `chart_id`.
   - Ajouter `chart_id == chart_id` dans la recherche de cache et dans `unique_stmt`.
   - Garder `variant_code` dans les requetes de dedupe/persistence pour rester coherent avec les index DB.

7. Durcir l'entitlement post-checkout.
   - Bypass ou invalidation partagee du cache d'abonnement pour les appels sensibles juste apres checkout.
   - Test d'integration: profil Stripe passe `free -> basic`, puis `POST /v1/natal/interpretation` doit resoudre `plan=basic` immediatement.

## Tests de non-regression a ajouter

- Front: apres upgrade Free -> Basic avec une `free_short` existante, aucun appel `useCaseLevel="short"` force ne doit etre arme si l'objectif est de produire la lecture Basic.
- Backend service: `interpret(... chart_id=B ...)` ne doit jamais retourner une ligne cachee du `chart_id=A`.
- Backend service: Basic complete doit produire `answer_type=basic`, `plan=basic`, `variant_code=single_astrologer`.
- LLM gateway: `plan=basic` + `natal_interpretation` ne doit pas utiliser un prompt contenant `EXIGENCE PREMIUM` ou `AstroResponse_v3`.
- E2E/API: pour un utilisateur Free qui upgrade Basic, la liste `/v1/natal/interpretations?chart_id=...` doit contenir au maximum:
  - une lecture Free publique;
  - une lecture Basic publique;
  - zero lecture short supplementaire generee par transition de plan.

## Partie 2 - Cartographie des fichiers du processus LLM apres calcul

Cette partie liste les fichiers qui participent, directement ou indirectement, aux interpretations LLM une fois le theme natal calcule. La distinction est importante:

- `runtime public`: appele dans le parcours utilisateur observe;
- `runtime support`: appele par le runtime ou par ses contrats;
- `configuration/seed`: configure les prompts, assemblies, schemas ou plans;
- `admin/tests/scripts`: utile au diagnostic mais pas appele dans le flux public;
- `suspect/obsolescence`: fichier ou responsabilite qui semble entretenir un double pipeline.

### Entree API publique et recuperation du theme calcule

| Fichier | Role | Statut |
| --- | --- | --- |
| `backend/app/api/v1/routers/public/natal_interpretation.py` | Endpoint public `POST /v1/natal/interpretation`, GET par id, liste, suppression, PDF. Applique le gate uniquement pour `complete`. | runtime public |
| `backend/app/api/v1/routers/public/users.py` | Route historique qui appelle encore `interpret_chart` et remappe vers le flux Free/short. | suspect/legacy |
| `backend/app/services/user_profile/natal_chart_service.py` | Charge le dernier theme natal utilisateur et expose les donnees de calcul au service LLM. | runtime support |
| `backend/app/services/user_profile/birth_profile_service.py` | Fournit le profil de naissance et certains modes de degradation. | runtime support |
| `backend/app/services/chart/json_builder.py` | Construit un JSON de theme plus ancien encore passe au service. Le prompt moderne utilise surtout `llm_astrology_input_v1` ou le payload Basic. | suspect/legacy |

### Autorisations, plan, quota et bascule Free/Basic/Premium

| Fichier | Role | Statut |
| --- | --- | --- |
| `backend/app/services/entitlement/natal_chart_long_entitlement_gate.py` | Decide si une demande complete devient `free_short`, `single_astrologer` ou autre variante. | runtime public |
| `backend/app/services/entitlement/b2c_runtime_gate.py` | Gate generique B2C utilise par les entitlements. | runtime support |
| `backend/app/services/entitlement/effective_entitlement_resolver_service.py` | Resolves le snapshot d'entitlement effectif. | runtime support |
| `backend/app/services/entitlement/effective_entitlement_gate_helpers.py` | Helpers communs de gate et d'erreurs. | runtime support |
| `backend/app/services/entitlement/entitlement_types.py` | Types de decision, variantes et metadata entitlement. | runtime support |
| `backend/app/services/entitlement/feature_scope_registry.py` | Registre feature/subfeature/variant. | runtime support |
| `backend/app/services/entitlement/public_entitlements.py` | Representation publique des entitlements. | runtime support |
| `backend/app/services/billing/subscription_status.py` | Determine le plan utilisateur. Dans le live test, une generation post-checkout est encore loggee `plan=free`. | runtime support, suspect |
| `backend/app/services/billing/subscription_cache.py` | Cache process-local du statut d'abonnement; risque fort apres checkout si plusieurs process. | runtime support, suspect |
| `backend/app/services/billing/stripe_billing_profile_service.py` | Met a jour le profil Stripe et invalide le cache local. | runtime support |
| `backend/app/services/quota/usage_service.py` | Consommation et suivi des quotas, notamment `natal_chart_long`. | runtime support |
| `backend/app/services/quota/window_resolver.py` | Resolution des fenetres de quota. | runtime support |

### Orchestrateur principal de generation natale

| Fichier | Role | Statut |
| --- | --- | --- |
| `backend/app/services/llm_generation/natal/interpretation_service.py` | Fichier central: cache, choix use case, Free short, Basic, Premium, payloads, validation, fallback, persistence, audit, liste. | runtime public, suspect majeur |
| `backend/app/services/llm_generation/natal/prompt_context.py` | Contexte de prompt natal et donnees de degradation. | runtime support |
| `backend/app/services/llm_generation/natal/public_interpretation.py` | Helpers d'erreurs publiques et entitlement info. | runtime support |
| `backend/app/services/llm_generation/natal/stored_interpretation_payload.py` | Charge/separe payload public accepte, payload rejete, `narrative_natal_reading_v1`, `basic_natal_interpretation_v2`. | runtime support |
| `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py` | Construit la lecture narrative publique a partir d'une reponse complete. | runtime support |
| `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py` | Valide la lecture publique et le draft Basic; construit aussi le fallback Basic deterministe. | runtime support, suspect |
| `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py` | Controle semantique entre payload LLM et faits astrologiques. | runtime support |
| `backend/app/services/llm_generation/natal/rejected_answer_workflow.py` | Workflow de rejet et stockage audit-only des reponses non conformes. | runtime support |
| `backend/app/services/llm_generation/llm_token_usage_service.py` | Enregistrement usage tokens. | runtime support |

Le probleme algorithmique principal est concentre dans `interpretation_service.py`: il decide trop de choses dans un meme flux. Il melange le produit Free, le produit Basic, le produit Premium, les modules thematiques, la compatibilite legacy et la persistence. Ce melange permet qu'un plan Basic utilise `natal_interpretation` premium, puis soit converti a posteriori en Basic par validation/fallback.

### Donnees astrologiques apres calcul et projection vers LLM

| Fichier | Role | Statut |
| --- | --- | --- |
| `backend/app/domain/astrology/natal_calculation.py` | Contrat principal du resultat de calcul natal. | runtime support |
| `backend/app/domain/astrology/runtime/natal_result_assembler.py` | Assemble le resultat natal runtime. | runtime support |
| `backend/app/domain/astrology/runtime/chart_object_runtime_data.py` | Donnees runtime des objets astrologiques. | runtime support |
| `backend/app/domain/astrology/runtime/chart_object_capability_taxonomy.py` | Taxonomie des capacites par objet. | runtime support |
| `backend/app/domain/astrology/runtime/chart_signature_runtime_data.py` | Donnees runtime de signature du theme. | runtime support |
| `backend/app/domain/astrology/runtime/natal_calculation_nodes.py` | Noeuds de calcul natal. | runtime support |
| `backend/app/domain/astrology/runtime/natal_calculation_graph.py` | Graphe de calcul natal. | runtime support |
| `backend/app/domain/astrology/runtime/natal_calculation_registry.py` | Registre de calcul natal. | runtime support |
| `backend/app/domain/astrology/builders/aspect_runtime_builder.py` | Prepare/repare les donnees d'aspects exposees au runtime. | runtime support |
| `backend/app/domain/astrology/interpretation/chart_interpretation_input_contracts.py` | Contrats d'entree pour interpretation. | runtime support |
| `backend/app/domain/astrology/interpretation/chart_object_interpretation_selector.py` | Selectionne les interpretations d'objets astrologiques. | runtime support |
| `backend/app/domain/astrology/interpretation/chart_object_interpretation_projector.py` | Projette les interpretations d'objets dans le payload. | runtime support |
| `backend/app/domain/astrology/interpretation/chart_interpretation_input_builder.py` | Construit l'entree d'interpretation a partir du calcul. | runtime support |
| `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py` | Produit les faits structures utilises pour contraindre le LLM. | runtime support |
| `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py` | Contrats d'entree narrative IA. | runtime support |
| `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py` | Construit l'entree narrative IA. | runtime support |
| `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py` | Projection publique/client des faits d'interpretation. | runtime support |
| `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py` | Contrat moderne envoye au LLM pour les use cases natals. | runtime support |
| `backend/app/domain/astrology/interpretation/basic_natal_eligibility.py` | Eligibilite des faits pour la lecture Basic. | runtime support |
| `backend/app/domain/astrology/interpretation/natal_fact_graph.py` | Graphe de faits natals. | runtime support |
| `backend/app/domain/astrology/interpretation/natal_fact_graph_builder.py` | Construction du graphe de faits. | runtime support |
| `backend/app/domain/astrology/interpretation/natal_salience_model.py` | Score d'importance des faits. | runtime support |
| `backend/app/domain/astrology/interpretation/natal_theme_taxonomy.py` | Taxonomie des themes Basic/nataux. | runtime support |
| `backend/app/domain/astrology/interpretation/natal_synthesis_resolver.py` | Resolution de synthese entre faits saillants. | runtime support |
| `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py` | Plan deterministe de lecture Basic, ensuite transforme en payload prompt. | runtime support |
| `backend/app/domain/astrology/interpretation/astral_point_interpretation.py` | Contrats d'interpretation des points astraux. | runtime support |
| `backend/app/infra/db/repositories/astral_point_interpretation_repository.py` | Acces DB aux interpretations de points astraux. | runtime support |

Ces fichiers representent la bonne direction algorithmique: contraindre le LLM par des faits structures. Le bug live indique que cette couche est ensuite affaiblie par le mauvais choix de use case/prompt et par la conversion fallback.

### Runtime LLM, prompts, schemas, providers

| Fichier | Role | Statut |
| --- | --- | --- |
| `backend/app/domain/llm/runtime/adapter.py` | Facade appelee par le service natal pour generer. | runtime public |
| `backend/app/domain/llm/runtime/gateway.py` | Resolution prompt, rendu, payload provider, validation et fallback gateway. Remplace `llm_astrology_input_v1` par le payload Basic si present. | runtime public, suspect |
| `backend/app/domain/llm/runtime/contracts.py` | Contrats runtime LLM. | runtime support |
| `backend/app/domain/llm/runtime/providers.py` | Abstraction provider. | runtime support |
| `backend/app/domain/llm/runtime/provider_runtime_manager.py` | Selection et execution provider. | runtime support |
| `backend/app/domain/llm/runtime/provider_parameter_mapper.py` | Mapping des parametres model/provider. | runtime support |
| `backend/app/domain/llm/runtime/output_validator.py` | Validation des sorties LLM. | runtime support |
| `backend/app/domain/llm/runtime/input_validator.py` | Validation des entrees LLM. | runtime support |
| `backend/app/domain/llm/runtime/length_budget_injector.py` | Contraintes de longueur. | runtime support |
| `backend/app/domain/llm/runtime/context_quality_injector.py` | Qualite du contexte injecte. | runtime support |
| `backend/app/domain/llm/runtime/fallback.py` | Fallback runtime. | runtime support |
| `backend/app/domain/llm/runtime/fallback_governance.py` | Gouvernance des fallbacks. | runtime support |
| `backend/app/domain/llm/runtime/repair.py` | Tentative de reparation LLM. | runtime support |
| `backend/app/domain/llm/runtime/repair_prompter.py` | Prompt de reparation. | runtime support |
| `backend/app/domain/llm/runtime/observability.py` | Donnees d'observabilite runtime. | runtime support |
| `backend/app/domain/llm/runtime/observability_service.py` | Persistence/logging observabilite. | runtime support |
| `backend/app/infra/providers/llm/openai_responses_client.py` | Client OpenAI Responses. | runtime support |
| `backend/app/infra/providers/llm/circuit_breaker.py` | Protection provider. | runtime support |
| `backend/app/infra/llm/rate_limiter.py` | Rate limiting LLM. | runtime support |
| `backend/app/infra/llm/cache.py` | Cache LLM infra. | runtime support |
| `backend/app/domain/llm/prompting/catalog.py` | Catalogue hardcode de prompts fallback, dont `natal_long_free`, `natal_interpretation`, `natal_interpretation_short`. | suspect/legacy |
| `backend/app/domain/llm/prompting/prompt_renderer.py` | Rendu des templates de prompt. | runtime support |
| `backend/app/domain/llm/prompting/schemas.py` | Schemas de sortie prompt/LLM. | runtime support |
| `backend/app/domain/llm/prompting/validators.py` | Validateurs prompt. | runtime support |
| `backend/app/domain/llm/prompting/validation.py` | Validation generale de prompting. | runtime support |
| `backend/app/domain/llm/prompting/placeholder_policy.py` | Politique de placeholders. | runtime support |
| `backend/app/domain/llm/prompting/narrative_natal_reading_v1.py` | Contrat public narratif. | runtime support |
| `backend/app/domain/llm/prompting/context.py` | Ancien contexte prompt generique. | suspect/legacy |
| `backend/app/domain/llm/prompting/personas.py` | Definition/persona LLM. | runtime support |
| `backend/app/domain/llm/prompting/persona_composer.py` | Composition persona dans les prompts. | runtime support |
| `backend/app/domain/llm/prompting/persona_boundary.py` | Garde-fous persona. | runtime support |

### Configuration canonique LLM et assemblies

| Fichier | Role | Statut |
| --- | --- | --- |
| `backend/app/domain/llm/configuration/canonical_use_case_registry.py` | Registre canonique des use cases, dont `natal_interpretation`. | configuration |
| `backend/app/domain/llm/configuration/assembly_resolver.py` | Resolution assembly par feature/plan/use case. | configuration |
| `backend/app/domain/llm/configuration/assembly_registry.py` | Registre d'assemblies. | configuration |
| `backend/app/domain/llm/configuration/assemblies.py` | Definition des assemblies. | configuration |
| `backend/app/domain/llm/configuration/prompt_version_lookup.py` | Lookup versions prompt. | configuration |
| `backend/app/domain/llm/configuration/prompt_versions.py` | Versions de prompt cote code. | configuration |
| `backend/app/domain/llm/configuration/execution_profile_registry.py` | Registre profils execution. | configuration |
| `backend/app/domain/llm/configuration/execution_profiles.py` | Profils execution model/tokens. | configuration |
| `backend/app/domain/llm/configuration/theme_astral_contracts.py` | Contrats plus recents `theme_astral`/Basic. | configuration, suspect parallel |
| `backend/app/domain/llm/configuration/config_coherence_validator.py` | Verification coherence config LLM. | configuration |
| `backend/app/domain/llm/configuration/coherence.py` | Helpers coherence. | configuration |
| `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py` | Builder provider pour les contrats `theme_astral`. | configuration/runtime support, suspect parallel |

Constat important: le Basic semble avoir ete commence dans une direction plus contractuelle (`basic_natal_prompt_payload`, `theme_astral_contracts`, taxonomy Basic), mais le parcours public continue d'utiliser le use case historique `natal_interpretation`. Cela cree deux modeles mentaux concurrents.

### Persistence, audit et modeles DB

| Fichier | Role | Statut |
| --- | --- | --- |
| `backend/app/infra/db/models/user_natal_interpretation.py` | Table publique des interpretations; index uniques avec `chart_id` et `variant_code`. | runtime public |
| `backend/app/infra/db/models/llm/llm_prompt.py` | Prompts, use cases, versions, logs LLM. | runtime support |
| `backend/app/infra/db/models/llm/llm_output_schema.py` | Schemas de sortie LLM. | runtime support |
| `backend/app/infra/db/models/llm/llm_persona.py` | Personas LLM. | runtime support |
| `backend/app/infra/db/models/llm/llm_observability.py` | Logs d'appels et observabilite. | runtime support |
| `backend/app/infra/db/models/llm/llm_release.py` | Releases LLM. | admin/support |
| `backend/app/infra/db/models/llm/llm_sample_payload.py` | Payloads de sample/eval. | admin/support |
| `backend/app/infra/db/repositories/llm/narrative_answer_audit_repository.py` | Audit des reponses narratives. | runtime support |
| `backend/app/infra/db/repositories/llm/prompting_repository.py` | Acces DB aux prompts/config LLM. | runtime support |

Derive observee: le modele DB encode une unicite par `chart_id`, mais le service de cache/persistence principal ne filtre pas toujours par `chart_id`. Le modele est plus sain que l'algorithme qui l'utilise.

### Contrats API et rendu frontend

| Fichier | Role | Statut |
| --- | --- | --- |
| `backend/app/services/api_contracts/public/natal_interpretation.py` | Contrat public de reponse interpretation natale. | runtime public |
| `frontend/src/api/natal-chart/index.ts` | Types TS, hooks React Query, POST/GET/list/delete/PDF. | runtime public |
| `frontend/src/api/natalChart.ts` | Client/API natal plus ancien ou complementaire. | suspect/legacy |
| `frontend/src/pages/NatalChartPage.tsx` | Page qui contient le bloc interpretation. | runtime public |
| `frontend/src/features/natal-chart/NatalInterpretation.tsx` | Orchestration UI: historique, selection persona, CTA, generation, refresh. Porte `shouldRefreshShortAfterBasicUpgrade`. | runtime public, suspect majeur |
| `frontend/src/features/natal-chart/NatalInterpretation.css` | Styles du bloc interpretation. | runtime public |
| `frontend/src/features/natal-chart/NatalInterpretationPersonaSelector.tsx` | Selecteur persona pour lecture complete. | runtime public |
| `frontend/src/features/natal-chart/NatalNarrativeReading.tsx` | Rendu lecture narrative complete. | runtime public |
| `frontend/src/features/natal-chart/NatalReadingSources.tsx` | Sources/faits affichables. | runtime public |
| `frontend/src/features/natal-chart/NatalAstrologerMode.tsx` | UI mode astrologue/persona. | runtime public |
| `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx` | Choisit le rendu Free, Basic V2 ou narrative. | runtime public |
| `frontend/src/components/natal-interpretation/NatalInterpretationTypes.ts` | Types UI internes. | runtime public |
| `frontend/src/components/natal-interpretation/NatalInterpretationMenus.tsx` | Menus UI interpretation. | runtime public |
| `frontend/src/i18n/natalChart.ts` | Libelles frontend. | runtime public |

Le frontend participe directement au bug: il ne se contente pas d'afficher l'etat backend. Il decide de creer une interpretation courte supplementaire apres upgrade Basic, puis permet un deuxieme flux complet. C'est ce qui produit trois interpretations fonctionnelles.

### Seeds, bootstrap, scripts et fichiers probablement obsoletes

| Fichier | Role | Risque |
| --- | --- | --- |
| `backend/scripts/seed_natal_short.py` | Ajoute `natal_interpretation_short` et son prompt. | Peut maintenir une voie courte separee du produit Free actuel `natal_long_free/free_short`. |
| `backend/scripts/seed_29_prompts.py` | Ancien seed prompts `natal_interpretation_short` et `natal_interpretation`. | Chevauche les seeds ops/bootstrap. |
| `backend/scripts/seed_30_2_astroresponse_v2.py` | Seed schema/prompt V2. | Historique potentiellement remplace par V3/Basic. |
| `backend/scripts/seed_30_3_gpt5_prompts.py` | Seed prompts GPT-5. | Peut diverger du catalogue/fallback DB courant. |
| `backend/scripts/seed_30_8_v3_prompts.py` | Seed prompt V3 pour `natal_interpretation`. | Peut imposer un contrat premium a un flux Basic. |
| `backend/scripts/seed_66_15_assembly_convergence.py` | Convergence assemblies. | A verifier contre DB actuelle. |
| `backend/scripts/seed_66_20_convergence.py` | Convergence taxonomy/assembly. | A verifier contre DB actuelle. |
| `backend/app/ops/llm/bootstrap/seed_29_prompts.py` | Seed ops des prompts initiaux. | Double avec `backend/scripts/seed_29_prompts.py`. |
| `backend/app/ops/llm/bootstrap/seed_30_8_v3_prompts.py` | Seed ops du prompt V3. | Source probable du prompt premium observe. |
| `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py` | Mappe `free -> natal_interpretation_short`, `basic -> natal_interpretation`, `premium -> natal_interpretation`. | Codifie le mauvais partage Basic/Premium. |
| `backend/app/ops/llm/bootstrap/seed_theme_astral_prompt_contract.py` | Seed d'un contrat Basic plus dedie. | Semble parallelise mais non utilise comme use case public principal. |
| `backend/scripts/update_all_prompts_59_5.py` | Reecriture globale de prompts. | Peut reintroduire du contexte legacy `natal_interpretation`. |
| `backend/scripts/diagnose_natal_interpretation_duplicates.py` | Diagnostic doublons. | Risque: logique de doublon a verifier avec `chart_id` et `variant_code`. |

Ces fichiers ne sont pas tous a supprimer. Mais ils montrent un historique de migrations qui a laisse cohabiter au moins quatre notions:

- `natal_long_free` pour Free public;
- `natal_interpretation_short` pour court historique;
- `natal_interpretation` pour complet/premium;
- `basic_natal_interpretation_v2` comme contrat public derive/fallback.

Cette coexistence est probablement la source du probleme d'algorithme.

### Tests existants lies au pipeline

| Fichier | Role | Limite actuelle |
| --- | --- | --- |
| `backend/tests/integration/test_basic_natal_v2_pipeline.py` | Verifie une partie du pipeline Basic V2. | Peut masquer le probleme si le gateway est fake ou si le draft est deja conforme. |
| `backend/tests/integration/test_natal_interpretation_public_free_basic_contract.py` | Verifie le contrat public Free/Basic. | Ne verrouille pas l'invariant "pas de short supplementaire apres upgrade". |
| `backend/tests/unit/test_basic_natal_narrative_validator.py` | Verifie validateur/fallback Basic. | Valide le fallback, mais pas que le bon prompt Basic est utilise. |
| `backend/tests/unit/test_basic_natal_reading_contracts.py` | Verifie contrat `basic_natal_interpretation_v2`. | Contrat utile, mais insuffisant pour le routage use case. |
| `backend/tests/unit/test_natal_llm_use_case_input_contract.py` | Verifie `llm_astrology_input_v1` sur les use cases modernes. | Ne detecte pas le remplacement par payload Basic dans un prompt premium. |
| `backend/tests/unit/test_natal_interpretation_stored_payload.py` | Verifie stockage/lecture payload. | Ne couvre pas la cle de cache/persistence sans `chart_id`. |
| `backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py` | Garde-fou schema V3. | Peut renforcer le contrat premium sur le Basic si mal route. |
| `frontend/src/tests/natalInterpretation.test.tsx` | Tests du composant interpretation. | A completer pour interdire `shouldRefreshShortAfterBasicUpgrade`. |
| `frontend/e2e/cs-423-natal-basic-readable.spec.ts` | E2E Basic lisible. | Ne couvre pas la chronologie Free -> checkout Basic -> complete. |

### Fichiers candidats a refactor ou retrait fonctionnel

Priorite 1:

- `frontend/src/features/natal-chart/NatalInterpretation.tsx`: retirer la generation short automatique post-upgrade; separer affichage historique et commande de generation.
- `backend/app/services/llm_generation/natal/interpretation_service.py`: extraire des strategies explicites `FreeShort`, `BasicSingleAstrologer`, `PremiumComplete`; chaque strategie doit avoir son use case, son schema, sa persistence et son audit.
- `backend/app/domain/llm/runtime/gateway.py`: interdire qu'un payload Basic soit injecte dans un prompt dont le contrat reste premium.
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`: ne plus mapper Basic sur `natal_interpretation` si ce use case reste premium.

Priorite 2:

- `backend/app/domain/llm/prompting/catalog.py`: supprimer ou reduire les prompts fallback natals hardcodes une fois les prompts DB/assemblies fiables. A minima, echouer fort en Basic si le prompt actif vient de `fallback_default`.
- `backend/scripts/seed_natal_short.py` et seeds historiques `seed_29*`, `seed_30*`: documenter lesquels sont encore canoniques et archiver le reste hors runtime.
- `backend/app/services/chart/json_builder.py`: verifier si le JSON legacy est encore requis. Si non, retirer du chemin LLM public.
- `frontend/src/api/natalChart.ts`: confirmer s'il reste consomme; sinon le remplacer par le client central `frontend/src/api/natal-chart/index.ts`.

Priorite 3:

- `backend/scripts/diagnose_natal_interpretation_duplicates.py`: aligner le diagnostic sur `(user_id, chart_id, level, persona_id, variant_code)`.
- `backend/app/services/llm_generation/shared/natal_context.py` et `backend/app/domain/llm/prompting/context.py`: verifier qu'ils ne reinjectent pas une interpretation precedente dans les prompts publics natals.

### Conclusion algorithmique de la cartographie

Le pipeline devrait etre une decision en trois branches exclusives apres calcul:

| Produit | Use case attendu | Schema public attendu | Variante DB attendue |
| --- | --- | --- | --- |
| Free | `natal_long_free` ou nouveau nom canonique unique | Free public short | `free_short` |
| Basic | use case Basic dedie, pas `natal_interpretation` premium | `basic_natal_interpretation_v2` | `single_astrologer` |
| Premium | `natal_interpretation` premium | `narrative_natal_reading_v1` ou complete premium | `multi_astrologer`/premium |

Aujourd'hui, l'algorithme reel fait plutot:

1. Free complete gate -> `natal_long_free/free_short`;
2. apres upgrade Basic, frontend force `natal_interpretation_short`;
3. Basic complete -> `natal_interpretation` premium + payload Basic + fallback Basic.

Ce n'est pas un simple bug d'affichage. C'est une collision de routage produit, prompt, schema et cache.

## Preuves principales

Fichiers inspectes:

- `frontend/src/features/natal-chart/NatalInterpretation.tsx`
- `frontend/src/components/natal-interpretation/NatalInterpretationContent.tsx`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/app/domain/llm/runtime/gateway.py`
- `backend/app/services/billing/subscription_status.py`
- `backend/app/services/billing/subscription_cache.py`
- `backend/app/services/billing/stripe_billing_profile_service.py`
- `backend/app/infra/db/models/user_natal_interpretation.py`

Commandes read-only utilisees:

```powershell
sqlite3 -readonly -header -column backend\horoscope.db "SELECT id,email,role,created_at FROM users WHERE lower(email)=lower('daconrilcy@hotmail.com');"
sqlite3 -readonly -header -column backend\horoscope.db "SELECT id,chart_id,level,use_case,variant_code,persona_id,persona_name,prompt_version_id,answer_type,plan,grounding_status,was_fallback,created_at,json_extract(interpretation_payload,'$.title') AS title,json_extract(interpretation_payload,'$.summary') AS summary,json_type(interpretation_payload,'$.basic_natal_interpretation_v2') AS has_basic_v2 FROM user_natal_interpretations WHERE user_id=14 ORDER BY created_at,id;"
sqlite3 -readonly -header -column backend\horoscope.db "SELECT id,use_case,feature,subfeature,plan,template_source,prompt_version_id,persona_id,model,latency_ms,tokens_in,tokens_out,validation_status,repair_attempted,fallback_triggered,request_id,trace_id,substr(input_hash,1,12) AS input_hash,timestamp FROM llm_call_logs WHERE timestamp >= '2026-06-01 04:20:00' ORDER BY timestamp,id;"
sqlite3 -readonly -header -column backend\horoscope.db "SELECT * FROM stripe_billing_profiles WHERE user_id=14;"
```

Limite: aucun test automatisé n'a ete execute, car cette intervention produit uniquement un rapport d'analyse et ne modifie pas le code applicatif.
