# Refonte Big Bang - Generation prompt et reponse JSON LLM

Date du document: 2026-06-01

Statut: cadrage de refonte, sans implementation

Contexte: analyse live test `daconrilcy@hotmail.com`, rapport associe `_condamad/reports/2026-06-01-analyse-live-test-interpretations-llm-natal.md`

## Synthese executive

La proposition de depart est correcte dans l'intuition: le probleme ne se reglera pas par un patch local du prompt natal. Le systeme actuel melange plusieurs generations historiques (`natal_long_free`, `natal_interpretation_short`, `natal_interpretation`, `basic_natal_interpretation_v2`) et laisse le routage produit, le prompt, le schema de sortie, le cache et le fallback se contredire.

La refonte doit donc etre un Big Bang controle. Mais le contrat LLM ne doit pas etre le premier etage de decision: le bug nait avant l'appel provider, dans l'action produit autorisee, le slot public qui peut exister, l'entitlement, le frontend et la persistence. Il faut donc introduire un contrat produit de lecture natale au-dessus du contrat LLM.

La cible devient:

```text
Action produit backend
  -> contrat produit de lecture natale
  -> contrat de generation LLM versionne
  -> payload gouverne
  -> JSON brut strict
  -> validation forte
  -> projection publique
  -> persistence acceptee uniquement
```

La notion floue de `use_case` doit etre remplacee par un contrat de generation LLM complet, versionne et exclusif, qui decrit en un seul objet:

- la feature produit;
- le plan commercial;
- le profil moteur LLM;
- les donnees autorisees;
- les prompts systeme et utilisateur;
- le profil de style/persona;
- le schema JSON strict attendu;
- les validateurs;
- les regles de cache, persistence, audit, quotas et fallback.

Le theme natal doit devenir le premier cas d'application, mais le modele doit etre reutilisable pour les autres features.

Decision structurante: aucun ancien `use_case` natal ne doit rester capable de generer une lecture publique apres cutover.

## Requalification de la proposition

La proposition initiale:

```text
Feature : theme_natal/autre_feature_1/autre_feature_2/...
Plan : free/basic/premium
Caracterisitique moteur: {json complet permettant de definir toutes les caracteristiques du moteur LLM : gpt-4o, reasonning, etc}
Data utilisees : {calculs, donnees d'interpretation}
Prompt System : {contraintes, securite, etc.}
Prompt utilisateur : {tu es astrologue, blabla, tu dois fournir un theme natal ...}
Style, domaine, jargon : profil astrologue
Structure de la reponse : {json structure, sections,etc}
```

doit etre durcie ainsi, avec deux niveaux de contrat:

```text
ThemeNatalReadingProductContract
  feature = theme_natal
  reading_kind = natal_reading
  product_action = preview | generate_full | regenerate | download
  product_plan = resolved_backend_only
  public_slot_policy
  entitlement_policy
  allowed_output_variants
  generation_contract_selector
  public_lifecycle_policy
```

Puis:

```text
LLMGenerationContract
  identity
    feature
    reading_kind
    product_plan
    output_variant
    contract_version
    locale

  entitlement
    required_feature
    quota_policy
    allowed_plans
    forbidden_transitions

  engine_profile
    provider
    model
    response_api
    reasoning
    verbosity
    temperature
    max_output_tokens
    timeout_ms
    retry_policy
    repair_policy

  data_contract
    prompt_visible_payload_schema
    validation_only_payload_schema
    audit_only_payload_schema
    provider_only_metadata_schema
    privacy_policy
    grounding_policy

  prompt_contract
    system_policy_ref
    task_prompt_ref
    style_profile_ref
    safety_profile_ref
    forbidden_content_profile_ref

  output_contract
    response_schema_ref
    public_projection_schema_ref
    additional_properties_policy
    semantic_validators
    rejection_policy

  persistence_contract
    cache_key_policy
    uniqueness_policy
    audit_policy
    public_visibility_policy
```

Le mot important est `contract`. Le prompt n'est qu'un bloc du contrat. Le JSON de reponse n'est pas une consequence implicite du prompt: c'est un contrat versionne, teste, valide et audite.

Le contrat produit empeche qu'un bouton, un effet React, un ancien endpoint ou une cle `use_case` cree une lecture publique hors parcours autorise. Le contrat LLM ne fait qu'executer une generation deja autorisee.

## Objectifs de la refonte

1. Avoir une branche de generation unique et explicite par couple `feature + reading_kind + plan + output_variant`.
2. Supprimer les chemins legacy qui peuvent produire une lecture publique avec un prompt ou un schema d'un autre plan.
3. Garantir qu'une generation Basic ne peut jamais utiliser un prompt Premium.
4. Garantir qu'une generation Free ne peut jamais etre regeneree comme substitut Basic apres upgrade.
5. Garantir que le schema JSON recu du LLM est strict, versionne et valide avant toute exposition publique.
6. Separrer clairement:
   - ce qui est visible par le LLM;
   - ce qui sert a valider la reponse;
   - ce qui sert a auditer;
   - ce qui est expose au public.
7. Rendre les prompts modifiables sans redeployer du code, mais uniquement dans un cadre gouverne et testable.
8. Eteindre physiquement les anciens chemins au lieu d'ajouter des adaptateurs permanents.

## Non-objectifs

- Ne pas corriger seulement `shouldRefreshShortAfterBasicUpgrade`.
- Ne pas ajouter un nouveau prompt Basic a cote de l'ancien pipeline.
- Ne pas conserver `natal_interpretation` comme use case commun Basic/Premium si son contrat reste premium.
- Ne pas accepter de fallback public silencieux pour masquer une reponse LLM invalide.
- Ne pas laisser le frontend choisir le type de generation LLM a declencher selon des heuristiques d'historique.
- Ne pas reintroduire `chart_json` ou `natal_data` comme dump prompt-visible non gouverne.

## Vocabulaire cible

| Terme | Definition cible |
| --- | --- |
| `feature` | Produit fonctionnel stable: `theme_natal`, `horoscope_daily`, `guidance_contextual`, etc. |
| `product_plan` | Plan commercial resolu cote backend: `free`, `basic`, `premium`. |
| `reading_kind` | Nature stable de lecture: `natal_reading`. |
| `output_variant` | Variante produit de sortie: `free_preview`, `basic_full_reading`, `premium_full_reading`. |
| `generation_contract` | Contrat complet qui assemble moteur, donnees, prompts, schema, validation, cache et audit. |
| `engine_profile` | Configuration provider/model/parametres/runtime, versionnee independamment du prompt. |
| `data_contract` | Schema des donnees disponibles et leur classification de visibilite. |
| `prompt_contract` | References aux blocs systeme, tache utilisateur, style, securite et contraintes. |
| `output_contract` | Schema strict de reponse brute et schema public projete. |
| `public_projection` | Transformation controlee entre reponse acceptee et JSON API public. |
| `legacy path` | Toute generation hors `generation_contract` cible. Doit etre classee, migree ou supprimee. |

## Architecture cible

Le flux cible doit etre:

```text
Requete API
  -> Auth + entitlement + plan resolu
  -> ThemeNatalReadingCommandService
  -> Resolution action produit
  -> Resolution slot public autorise
  -> Selection contractuelle unique
       feature
       reading_kind
       product_plan
       output_variant
       locale
       persona/style optionnel
  -> Construction donnees
       prompt_visible
       validation_only
       audit_only
       provider_only
  -> Resolution engine_profile
  -> Resolution prompt_contract
  -> Resolution output_contract
  -> Assemblage prompt
  -> Appel provider
  -> Parsing JSON strict
  -> Validation schema
  -> Validation semantique
  -> Projection publique
  -> Persistence atomique
  -> Audit complet
  -> Reponse API
```

Le flux interdit:

```text
Plan Basic
  -> use_case premium historique
  -> payload Basic injecte dans prompt premium
  -> reponse premium invalide
  -> fallback Basic silencieux
  -> persistence publique
```

L'API publique cible devrait recevoir une action produit:

```json
{
  "chart_id": "...",
  "action": "generate_full",
  "persona_profile_id": "...",
  "locale": "fr-FR",
  "client_request_id": "..."
}
```

Elle ne devrait plus recevoir:

```json
{
  "use_case": "...",
  "use_case_level": "...",
  "variant_code": "...",
  "plan": "...",
  "forceRefresh": true
}
```

## Contrat de generation cible

### Identite

Chaque contrat doit avoir une identite stable:

| Champ | Exemple theme natal Basic | Regle |
| --- | --- | --- |
| `feature` | `theme_natal` | Ne doit pas etre un ancien nom technique comme `natal_interpretation`. |
| `reading_kind` | `natal_reading` | Distingue la nature de lecture du nom de feature. |
| `product_plan` | `basic` | Resolu uniquement cote backend. |
| `output_variant` | `basic_full_reading` | Decrit le produit rendu, pas le mode persona. |
| `contract_version` | `theme_natal.reading.basic_full_reading.v1` | Versionnee et immuable apres publication. |
| `locale` | `fr-FR` | Influe sur prompt et schema texte, pas sur les faits. |
| `persona_profile_id` | optionnel | Profil style/persona, jamais proprietaire du schema. |
| `persona_mode` | `none`, `single`, `multi` | Dimension separee de `output_variant`. |

Regle de nommage: `output_variant` decrit ce que le client recoit. Le fait qu'un astrologue/persona soit selectionne est une dimension de style et de cache, pas une variante de sortie. Cela evite de recréer une confusion entre plan, persona, variant et contrat.

### Profil moteur

Le profil moteur doit etre un objet complet et auditable:

| Champ | Regle |
| --- | --- |
| `provider` | `openai` ou autre provider supporte. |
| `api` | Exemple: `responses`. Interdit de mixer plusieurs clients dans le meme contrat. |
| `model` | Exemple: `gpt-4o`, `gpt-4o-mini`, futur modele. |
| `reasoning` | Niveau ou absence de reasoning, explicite. |
| `verbosity` | Niveau de detail attendu cote provider, distinct du style editorial. |
| `temperature` | Valeur bornee par contrat. |
| `max_output_tokens` | Budget compatible avec le schema attendu. |
| `timeout_ms` | Timeout contractuel. |
| `retry_policy` | Nombre de retries et conditions. |
| `repair_policy` | Autorisee ou interdite; si autorisee, une seule tentative et audit obligatoire. |
| `fallback_policy` | Par defaut `fail_closed`. Aucun fallback public silencieux. |

Principe: le choix du modele ne doit jamais etre cache dans le prompt, ni deduit d'un nom de use case.

### Contrat de donnees

Les donnees doivent etre classees en quatre espaces.

| Espace | Visible LLM | Persistable public | Usage |
| --- | --- | --- | --- |
| `prompt_visible` | oui | non brut | Matiere strictement necessaire pour rediger. |
| `validation_only` | non | non | Verifier que la reponse respecte les faits. |
| `audit_only` | non | audit uniquement | Rejouer, tracer, diagnostiquer. |
| `provider_only` | non narratif | non public | IDs, request metadata, trace, model params. |

Regles obligatoires:

- Aucun PII inutile dans `prompt_visible`.
- Aucun score interne brut dans les champs publics narratifs.
- Aucun chemin technique, identifiant d'evidence brut ou `audit_input` dans la projection publique.
- Les donnees de calcul et les donnees d'interpretation doivent etre fusionnees dans un payload editorial, pas dumppees.
- Les anciennes surfaces `chart_json` et `natal_data` ne doivent pas redevenir prompt-visible pour le natal moderne.

Le payload prompt-visible devrait etre constitue de cartes editoriales, pas d'un dump technique. Exemple conceptuel:

```json
{
  "fact_id": "sun_sign_aries",
  "category": "identity_core",
  "public_label": "Soleil en Belier",
  "interpretive_hint": "energie d'initiative, affirmation, besoin d'agir",
  "allowed_claims": [
    "La personne peut avoir besoin d'agir pour se sentir vivante.",
    "L'elan personnel se construit souvent dans l'initiative."
  ],
  "forbidden_claims": [
    "La personne est impulsive.",
    "La personne reussira forcement en leadership."
  ]
}
```

Le `fact_id` peut aider le LLM a suivre ses sources internes, mais il ne doit jamais sortir brut dans la projection publique. Le public recoit des sources lisibles: "Soleil en Belier", "Ascendant Cancer", "Lune en maison X", etc.

### Prompt systeme

Le prompt systeme doit contenir uniquement les regles stables et transverses:

- securite;
- non-medical, non-juridique, non-financier;
- non-predictif absolu;
- refus des diagnostics;
- respect du schema JSON;
- interdiction de mentionner le fonctionnement interne;
- interdiction de creer des faits astrologiques absents du payload;
- langue et ton general.

Il ne doit pas contenir:

- la structure produit detaillee;
- les sections specifiques du theme natal;
- les instructions de plan Free/Basic/Premium;
- les details d'un astrologue/persona.

### Prompt utilisateur

Le prompt utilisateur doit decrire la tache concrete:

- "Produire une lecture de theme natal";
- public cible;
- niveau attendu selon le contrat;
- sections attendues;
- maniere d'utiliser les donnees;
- contraintes editorialement specifiques.

Il doit etre derive du contrat, pas compose par concat opportuniste.

### Contrat redactionnel par plan

Le contrat ne doit pas seulement garantir un JSON valide. Il doit verrouiller une promesse editoriale.

| Plan | Promesse cible |
| --- | --- |
| Free preview | Apercu court, utile, non frustrant, avec 3 a 5 elements majeurs maximum. |
| Basic full reading | Lecture complete accessible, synthetique, structuree comme un recit; pas une liste technique. |
| Premium full reading | Lecture approfondie, multi-couches, plus technique, avec nuances et arbitrages. |

Structure Basic cible:

```text
opening_synthesis
dominant_patterns
inner_dynamics
relationship_style
work_and_life_direction
growth_keys
astrological_sources
```

Regles redactionnelles testables:

- Interdire "selon les annexes publiques".
- Interdire "les donnees indiquent" comme phrase mecanique repetee.
- Interdire "en tant qu'IA".
- Interdire les placements recopies sans interpretation humaine.
- Interdire les paragraphes qui commencent tous par un placement astrologique.
- Interdire le jargon non explique.
- Obliger une phrase d'interpretation humaine avant le detail technique.
- Obliger au moins une nuance ou un arbitrage par section importante.
- Obliger des sources astrologiques lisibles et non vides.

### Style, domaine, jargon

Le style doit devenir un profil separe:

| Dimension | Exemple |
| --- | --- |
| `tone` | chaleureux, clair, adulte, non sensationnaliste |
| `domain_depth` | vulgarise, intermediaire, expert |
| `jargon_policy` | termes astrologiques autorises avec explication |
| `persona_voice` | astrologue selectionne, si disponible |
| `forbidden_phrases` | phrases mecaniques, disclaimers dans le corps, libelles anglais bruts |
| `reading_posture` | reflexive, non deterministe, non predictive |

Le persona ne doit jamais pouvoir modifier:

- le schema de sortie;
- les donnees autorisees;
- les politiques de securite;
- les quotas;
- la visibilite publique.

### Structure de reponse JSON

Le schema JSON doit etre:

- strict;
- versionne;
- sans champs inconnus;
- parse avant validation metier;
- projete vers un contrat public distinct;
- testable avec fixtures.

Regles:

- Le LLM retourne un JSON brut conforme au `raw_response_schema`.
- Le backend valide ce JSON.
- Le backend construit ensuite un `public_response_schema`.
- Le public ne recoit jamais le JSON brut provider si celui-ci contient des donnees techniques.

## Contrats cibles pour le theme natal

### Free

| Dimension | Decision cible |
| --- | --- |
| `feature` | `theme_natal` |
| `reading_kind` | `natal_reading` |
| `product_plan` | `free` |
| `output_variant` | `free_preview` |
| Objectif | Resume court utile, non trompeur, avec CTA vers Basic/Premium. |
| Donnees | Donnees majeures uniquement, selectionnees. |
| Schema | `theme_natal_free_preview_v1` |
| Persistence | Une seule lecture Free par `user_id + chart_id + contract_version`. |
| Fallback | Aucun fallback LLM public silencieux; erreur recuperable ou message non genere. |

### Basic

| Dimension | Decision cible |
| --- | --- |
| `feature` | `theme_natal` |
| `reading_kind` | `natal_reading` |
| `product_plan` | `basic` |
| `output_variant` | `basic_full_reading` |
| Objectif | Lecture complete mais cadree, issue d'un plan editorial Basic deterministe. |
| Donnees | `BasicNatalReadingPlan` + support editorial + faits structures autorises. |
| Schema | `theme_natal_basic_reading_v1`. `basic_natal_interpretation_v2` peut rester compat legacy, pas contrat cible. |
| Persistence | Une seule lecture Basic par `user_id + chart_id + persona_profile_id + contract_version`. |
| Fallback | Reparation une fois; sinon rejet audite, pas de publication silencieuse. |

### Premium

| Dimension | Decision cible |
| --- | --- |
| `feature` | `theme_natal` |
| `reading_kind` | `natal_reading` |
| `product_plan` | `premium` |
| `output_variant` | `premium_full_reading` |
| Objectif | Lecture approfondie multi-axes, plus longue, plus nuancee. |
| Donnees | Payload premium distinct, plus riche que Basic. |
| Schema | `theme_natal_premium_reading_v1` |
| Persistence | Une lecture par chart/persona/contract, selon politique produit. |
| Fallback | Fail closed avec audit si schema ou grounding invalide. |

Point non negociable: Basic et Premium ne partagent pas le meme `output_contract`. Ils peuvent partager certains composants de donnees ou de securite, mais pas le meme contrat de generation final.

## Exemple conceptuel de manifeste

Ce bloc est une forme documentaire, pas une implementation.

```json
{
  "identity": {
    "feature": "theme_natal",
    "reading_kind": "natal_reading",
    "product_plan": "basic",
    "output_variant": "basic_full_reading",
    "contract_version": "theme_natal.reading.basic_full_reading.v1",
    "locale": "fr-FR"
  },
  "engine_profile": {
    "provider": "openai",
    "api": "responses",
    "model": "gpt-4o",
    "reasoning": "low",
    "verbosity": "medium",
    "temperature": 0.4,
    "max_output_tokens": 2400,
    "timeout_ms": 60000,
    "retry_policy": {
      "max_attempts": 1,
      "retry_on": ["transport_error", "rate_limit"]
    },
    "repair_policy": {
      "enabled": true,
      "max_attempts": 1,
      "repair_only_schema_errors": true
    },
    "fallback_policy": {
      "public_fallback": false,
      "on_failure": "reject_and_audit"
    }
  },
  "data_contract": {
    "prompt_visible_schema": "theme_natal_basic_prompt_payload_v1",
    "validation_only_schema": "theme_natal_basic_validation_payload_v1",
    "audit_only_schema": "theme_natal_generation_audit_v1",
    "privacy_policy": "no_pii_no_raw_scores_no_internal_ids"
  },
  "prompt_contract": {
    "system_policy_ref": "astrology_safety_policy.v1",
    "task_prompt_ref": "theme_natal.basic.task.v1",
    "style_profile_ref": "astrologer_profile.default.v1",
    "forbidden_content_profile_ref": "theme_natal.public_forbidden_content.v1"
  },
  "output_contract": {
    "raw_response_schema": "theme_natal_basic_llm_response_v1",
    "public_response_schema": "theme_natal_basic_public_response_v1",
    "additional_properties": "forbid",
    "semantic_validators": [
      "schema_strict",
      "grounding_against_plan",
      "no_technical_leak",
      "no_mechanical_fallback_phrases",
      "no_empty_sources"
    ]
  },
  "persistence_contract": {
    "cache_key": [
      "user_id",
      "chart_id",
      "feature",
      "product_plan",
      "output_variant",
      "persona_profile_id",
      "contract_version",
      "data_hash",
      "style_profile_version",
      "engine_profile_version"
    ],
    "public_visibility": "accepted_only",
    "quota_consumption": "on_accepted_persistence"
  }
}
```

## Regles de selection du contrat

Le backend doit etre l'unique proprietaire de la selection du contrat.

Entrees autorisees:

- utilisateur authentifie;
- `chart_id`;
- feature demandee;
- intention utilisateur normalisee: `preview`, `generate_full`, `regenerate`, `download`;
- persona/style selectionne, si autorise;
- locale.

Entrees interdites depuis le frontend:

- `use_case` brut;
- `plan` brut;
- `variant_code` brut;
- nom de prompt;
- schema de sortie;
- model/provider;
- force-refresh sur un niveau arbitraire.

Decision cible:

```text
resolve_entitlement(user)
  -> product_plan
resolve_product_intent(request)
  -> output_variant
resolve_generation_contract(feature, reading_kind, product_plan, output_variant, locale)
  -> contract
```

Le frontend demande une action produit. Il ne choisit plus un use case LLM.

## Regles de cache et persistence

La cle de cache doit contenir au minimum:

- `user_id`;
- `chart_id`;
- `feature`;
- `product_plan`;
- `output_variant`;
- `persona_profile_id` si applicable;
- `contract_version`;
- `prompt_contract_version`;
- `output_schema_version`;
- `data_hash`;
- `style_profile_version`;
- `engine_profile_version`.

Regles:

- Le cache ne doit jamais ignorer `chart_id`.
- Le cache ne doit jamais reutiliser une lecture d'un autre plan.
- Le cache ne doit jamais reutiliser une lecture d'une autre version de contrat.
- Le cache ne doit jamais servir une lecture `rejected`.
- La consommation de quota a lieu apres persistence acceptee, pas avant.
- Une relecture cachee ne consomme pas de quota.
- Une regeneration corrective doit etre explicite, atomique et auditee.

## Slots publics et cycle de vie

La persistence publique doit etre modelee autour d'un slot de lecture, pas autour d'une ligne LLM generique.

```text
ThemeNatalReadingSlot
  user_id
  chart_id
  feature
  reading_kind
  product_plan
  output_variant
  persona_profile_id nullable
  contract_version
  status
```

Statuts autorises:

```text
empty
generating
accepted
rejected
failed_retriable
superseded
```

Regles:

- Les routes publiques `GET/list` ne retournent que les slots `accepted`.
- Une generation en cours ne remplace jamais une lecture acceptee.
- Une regeneration cree un run separe, valide, puis remplace atomiquement la lecture publique si elle est acceptee.
- Deux clics simultanes `generate_full` ne doivent produire qu'un seul slot `generating` et une seule lecture publique acceptee.
- Le quota ne doit pas etre debite deux fois en cas de concurrence.
- Le frontend ne doit jamais deduire l'etat public depuis des lignes LLM brutes.

## Separation run LLM et lecture publique

Deux concepts doivent etre separes en DB et dans le code:

```text
llm_generation_runs
  trace complete de chaque tentative provider

theme_natal_readings / user_natal_interpretations_v2
  uniquement les lectures publiques acceptees
```

`llm_generation_runs` peut contenir:

- `raw_provider_response`;
- `parsed_raw_response`;
- `validation_errors`;
- `rejection_reason`;
- `repair_attempt_count`;
- `prompt_hash`;
- `data_hash`;
- `contract_snapshot_id`;
- `engine_profile_version`;
- `output_schema_version`.

La lecture publique ne contient que:

- `public_payload`;
- `public_schema_version`;
- `accepted_at`;
- `source_generation_run_id`;
- `generation_contract_snapshot_id`;
- `public_payload_hash`.

Cette separation rend structurel le principe suivant: le public ne recoit jamais le JSON brut provider.

## Regles de fallback, repair et rejet

Le fallback deterministe public doit disparaitre du flux nominal.

Politique cible:

| Situation | Comportement |
| --- | --- |
| Erreur transport provider | Retry selon `retry_policy`, puis erreur recuperable. |
| JSON invalide | Repair unique si autorise, sinon rejet audite. |
| Schema invalide | Repair unique si autorise, sinon rejet audite. |
| Faits inventes | Pas de repair; rejet audite direct ou regeneration controlee selon politique explicite. |
| Contradiction astrologique | Pas de repair; rejet audite direct. |
| Fuite technique | Pas de repair; rejet audite direct. |
| Texte mecanique ou vide | Rejet audite. |
| Prompt introuvable | Fail closed. |
| Contrat incoherent | Fail closed au demarrage ou a la publication. |

Un fallback peut exister pour l'UX, mais il doit etre une reponse applicative claire du type "lecture non disponible, regeneration possible", pas une fausse lecture astrologique publiee.

Principe: le repair corrige la forme, pas le fond. Si le LLM invente un ascendant, une maison, un aspect ou une dominante absente du payload, la reponse est rejetee.

## Securite et confidentialite

Garde-fous obligatoires:

- Classification explicite des donnees par visibilite.
- PII minimale dans les prompts.
- Pas de donnees de paiement ou abonnement dans le prompt.
- Pas de `email`, `user_id`, `stripe_customer_id` prompt-visible.
- Pas d'identifiants techniques bruts dans le public.
- Pas de diagnostics medicaux, psychologiques, juridiques, financiers.
- Pas de prediction deterministe.
- Pas d'incitation a decision critique.
- Disclaimers geres par le backend et deduplicables, pas par le LLM.
- Journalisation audit sans exposer de secrets ni payloads sensibles dans les logs applicatifs ordinaires.

## Gouvernance des prompts

La gouvernance cible doit distinguer:

| Element | Owner cible |
| --- | --- |
| Contrats de generation | Backend domaine LLM, versionnes. |
| Texte systeme securite | Policy centrale, partagee. |
| Texte de tache produit | Feature owner, versionne. |
| Style/persona | Domaine astrologue/persona, borne par policy. |
| Schema JSON | Contrat backend, teste. |
| Seeds/bootstrap | Provisioning uniquement, jamais source runtime directe. |
| Admin prompt editor | Edite des drafts ou versions candidates, pas le runtime sans publication validee. |

Regles de publication:

1. Un prompt ne peut etre publie que s'il reference un `generation_contract`.
2. Un prompt ne peut pas changer le schema de sortie.
3. Un prompt ne peut pas changer le plan commercial.
4. Un prompt ne peut pas elargir les donnees prompt-visible.
5. Toute publication doit generer un snapshot immutable.
6. Toute publication doit passer une suite de tests de rendu, schema et validation.

## Extinction legacy obligatoire

Le Big Bang doit inclure une liste d'interdictions explicites.

Pour le theme natal, les elements suivants doivent etre migres ou supprimes du flux public:

- `natal_interpretation` comme contrat commun Basic/Premium;
- `natal_interpretation_short` comme generation post-upgrade Basic;
- `natal_long_free` si son nom reste contradictoire avec une sortie Free preview;
- injection de `basic_natal_prompt_payload` dans un prompt premium;
- `PROMPT_FALLBACK_CONFIGS` comme source de prompt pour une famille supportee;
- fallback public deterministe qui produit une fausse lecture;
- cache/persistence sans `chart_id`;
- `answer_type=premium` pour une lecture Basic;
- CTA frontend qui declenche un niveau LLM au lieu d'une action produit.

Les anciens noms peuvent survivre temporairement en migration DB ou compatibilite de lecture, mais pas comme chemins de generation actifs.

Suppressions a rendre bloquantes par scans:

```text
natal_interpretation_short dans un chemin runtime public
shouldRefreshShortAfterBasicUpgrade
use_case_level cote frontend
variant_code cote frontend
forceRefresh pour generation LLM publique
basic_natal_prompt_payload injecte dans natal_interpretation
template_source=fallback_default pour theme_natal
AstroResponse_v3 dans un contrat Basic
EXIGENCE PREMIUM dans un contrat Basic
chart_json prompt-visible moderne
natal_data prompt-visible non gouverne
```

## Migration Big Bang proposee

### Phase 0 - Freeze et inventaire

- Geler les changements de prompts natals hors hotfix.
- Interdire toute nouvelle generation publique issue de chemins non classes.
- Capturer un inventaire DB des prompts, schemas, assemblies, use cases et interpretations existantes.

### Phase 1 - Creation du modele contractuel

- Definir le `ThemeNatalReadingProductContract`.
- Definir les contrats `theme_natal.reading.free_preview.v1`, `theme_natal.reading.basic_full_reading.v1`, `theme_natal.reading.premium_full_reading.v1`.
- Definir les schemas JSON stricts raw et public.
- Definir les payloads prompt-visible par plan.
- Definir les politiques de rejet.

### Phase 2 - Implementation en branche Big Bang avec fake provider

- Implementer le resolver contractuel sans brancher le frontend public.
- Construire les prompts via contrat.
- Verrouiller les slots publics et les runs LLM.
- Prouver le flux avec un fake provider deterministe.

### Phase 3 - Provider reel et replay fixtures

- Appeler le provider avec `response_format` strict si disponible.
- Valider et auditer sans exposer.
- Rejouer des charts anonymises.
- Comparer coherence astrologique, conformite schema, absence de fuites techniques.
- Verifier Free -> Basic -> Premium sans generation parasite.
- Verifier que les invalides sont rejetes, pas fallback publics.

### Phase 4 - Suppression physique des chemins legacy actifs

- Supprimer ou neutraliser les chemins de generation legacy avant merge.
- Supprimer `shouldRefreshShortAfterBasicUpgrade`.
- Supprimer les generations publiques par `use_case_level`.
- Supprimer l'injection Basic dans prompt Premium.
- Supprimer les fallbacks publics deterministes.
- Garder au maximum une compatibilite de lecture legacy debug/dev, non generatrice.

### Phase 5 - Cutover endpoint et frontend actions produit

- Basculer l'endpoint public vers le resolver contractuel.
- Le frontend envoie des actions produit, pas des use cases.
- Aucun endpoint public ne peut choisir entre ancien et nouveau runtime.
- Les anciennes interpretations ne peuvent pas regenerer via legacy.

### Phase 6 - Scans anti-regression et purge dev data

- Mettre a jour docs, admin, tests et guardrails.
- Purger ou marquer `legacy_readonly` les donnees de dev incompatibles.
- Publier les scans anti-retour.

## Acceptation cible

Une refonte est acceptable seulement si les invariants suivants sont vrais:

1. Un utilisateur Free obtient au maximum une lecture Free publique par chart et version de contrat.
2. Un utilisateur Basic obtient une lecture Basic issue d'un contrat Basic, jamais d'un prompt Premium.
3. Un utilisateur Premium obtient une lecture Premium issue d'un contrat Premium.
4. Le frontend ne peut pas provoquer une generation `short` arbitraire apres upgrade.
5. Le backend refuse toute combinaison contrat/prompt/schema incoherente.
6. Les schemas JSON refusent les champs inconnus.
7. Les lectures rejetees ne sont jamais exposees via GET/list public.
8. Les quotas sont consommes uniquement apres persistence acceptee.
9. Le cache est partitionne par `chart_id`, plan, variante et versions de contrat.
10. Les prompts legacy ne sont plus sources runtime pour `theme_natal`.
11. Un endpoint public ne peut pas choisir entre runtime legacy et runtime contractuel.
12. Une tentative LLM rejetee ne peut pas modifier une lecture publique acceptee.
13. Deux generations concurrentes du meme slot ne creent ni double lecture publique ni double debit quota.

## Tests et preuves a prevoir

### Backend

- Test resolver: `theme_natal + free` selectionne uniquement `free_preview`.
- Test resolver: `theme_natal + basic` selectionne uniquement `basic_full_reading`.
- Test resolver: `theme_natal + premium` selectionne uniquement `premium_full_reading`.
- Test matrice: `free + generate_full` retourne paywall/locked.
- Test matrice: `basic + preview` ne genere pas de short.
- Test anti-collision: Basic ne peut pas resoudre un prompt contenant une exigence Premium.
- Test schema: JSON LLM invalide rejete.
- Test schema: champ inconnu rejete.
- Test grounding: fait invente rejete.
- Test privacy: PII et IDs internes absents du prompt-visible.
- Test persistence: cache key inclut `chart_id`.
- Test quota: consommation apres acceptation uniquement.
- Test rejection: rejet audit-only absent des routes publiques.
- Test concurrence: deux clics simultanes produisent un seul slot `generating`, une seule lecture `accepted`, aucun double quota.
- Test entitlement frais: apres checkout Basic, `generate_full` ne peut pas etre resolu `plan=free`.

### Frontend

- Test: le frontend n'envoie plus de `use_case_level`.
- Test: le frontend n'envoie plus de `variant_code`.
- Test: apres upgrade Basic, aucune generation short automatique.
- Test: CTA "theme natal complet" envoie une action produit normalisee.
- Test: rendu Basic consomme uniquement le schema public Basic.
- Test: mentions legales dedupliquees.
- Test: aucun effet React ne declenche une generation post-upgrade sans action utilisateur explicite.

### Qualite redactionnelle

- Test: rejet des phrases mecaniques.
- Test: rejet des sources vides.
- Test: rejet du jargon brut non explique.
- Test: rejet des sections trop courtes.
- Test: rejet d'une section sans source/fact lisible valide.

### Observabilite

- Log d'appel contient `generation_contract_key`.
- Log d'appel contient `generation_contract_version`.
- Log d'appel contient `generation_contract_snapshot_id`.
- Log d'appel contient `generation_contract_hash`.
- Log d'appel contient `engine_profile_version`.
- Log d'appel contient `prompt_contract_version`.
- Log d'appel contient `output_schema_version`.
- Log d'appel contient `data_hash`.
- Log d'appel contient `validation_status`.
- Log d'appel contient `rejection_reason` si rejet.
- Log public ne contient pas de payload sensible.

## Guardrails CONDAMAD applicables

Invariants deja pertinents:

- `RG-018`: les familles supportees ne doivent pas redevenir proprietaires de prompt via `PROMPT_FALLBACK_CONFIGS`.
- `RG-021`: toute cle fallback restante doit avoir une decision persistante.
- `RG-022`: les validations prompt-generation doivent pointer vers des tests collectes.
- `RG-149`: la cartographie prompt-generation doit rester explicite et ne pas promouvoir `chart_json`/`natal_data` comme prompt-visible moderne.
- `RG-150`: les rejets LLM ne doivent jamais etre deserialises comme interpretations publiques.
- `RG-152`: `narrative_natal_reading_v1` ne doit pas exposer donnees techniques.
- `RG-155`: pas de padding semantique ou sources vides pour masquer une lecture invalide.
- `RG-156`: le Basic doit etre alimente par des supports editoriaux varies et structures.
- `RG-164`: Basic selectionne via `BasicNatalReadingPlan`, sans owner legacy/fallback.
- `RG-165`: le payload Basic exclut PII, raw carriers, scores, paths et raw IDs.
- `RG-166`: les drafts Basic invalides sont repares une fois, puis rejetes ou traites selon politique explicite.
- `RG-167`: Basic complete persiste et reutilise uniquement le moteur Basic attendu.
- `RG-168`: `basic_natal_interpretation_v2` reste strict et sans champs techniques.
- `RG-169`: qualite redactionnelle Basic et rejet des phrases mecaniques.
- `RG-171`: le prompt Basic final ne doit pas router par les anciennes cles natal.
- `RG-172`: le cache Basic doit tenir compte de la version editoriale.

La refonte devra probablement ajouter un nouveau guardrail durable: "toute generation LLM publique doit passer par un `LLMGenerationContract` versionne; aucun endpoint public ne peut appeler un prompt par use case legacy brut".

## Decisions ouvertes

1. Nom final de la feature: `theme_natal` ou `natal_chart_reading`.
2. Nom final des schemas publics: conserver `basic_natal_interpretation_v2` ou migrer vers `theme_natal_basic_reading_v1`.
3. Politique pour les anciennes interpretations deja stockees: lecture legacy seulement, regeneration forcee, ou migration.
4. Choix du provider/model par plan.
5. Niveau de support persona en Basic: style uniquement ou selection astrologue pleine.
6. Politique commerciale: une lecture Basic par chart, par astrologue, ou par version editoriale.
7. Admin UI: edition directe de prompts publies ou workflow draft/review/publish obligatoire.

## Decisions recommandees maintenant

| Decision | Recommandation |
| --- | --- |
| Nom feature | `theme_natal`, car c'est le langage produit utilisateur. |
| Nom interne lecture | `natal_reading`, pour distinguer la feature du type de lecture. |
| Variantes | `free_preview`, `basic_full_reading`, `premium_full_reading`. |
| Schema Basic cible | Migrer vers `theme_natal_basic_reading_v1`; garder `basic_natal_interpretation_v2` uniquement comme compat legacy si necessaire. |
| Anciennes interpretations | Comme l'application n'est pas encore en production, purger ou marquer `legacy_readonly` en dev; eviter une migration complexe. |
| Provider/model par plan | Ne pas en faire le sujet principal; le contrat doit le permettre, mais la priorite est coherence produit/schema/persistence. |
| Persona Basic | Persona autorisee comme style; jamais proprietaire du schema. Si elle change le texte, elle entre dans la cle de cache et le quota. |
| Admin prompt editor | Workflow draft -> test -> snapshot -> publish obligatoire; pas d'edition directe publiee. |

## Recommandation de decision

La refonte doit etre acceptee comme une rupture d'architecture du runtime public de lecture natale, pas comme une story de correction de prompt. La cible la plus saine est:

- `feature` devient le centre du routage produit;
- `reading_kind` stabilise la nature de la lecture;
- `plan` devient une entree de selection contractuelle, jamais une instruction prompt;
- `product_action` remplace les niveaux LLM envoyes par le frontend;
- `ThemeNatalReadingProductContract` decide quel slot public peut exister;
- `engine_profile` devient une configuration versionnee;
- `data_contract` devient la frontiere de securite;
- `prompt_contract` devient une composition gouvernee;
- `output_contract` devient la verite du JSON LLM;
- `public_projection` devient la seule sortie exposee;
- les chemins legacy deviennent impossibles a utiliser pour generer du public.

La premiere implementation devrait viser `theme_natal.reading.basic_full_reading.v1`, car c'est le flux qui a revele la collision la plus grave. Ensuite seulement, Free et Premium doivent etre branches sur le meme modele contractuel.

Critere de merge recommande: aucun endpoint public ne doit pouvoir appeler un prompt natal par ancien `use_case` brut. Le legacy peut etre lisible temporairement en debug/dev, mais il ne doit plus etre generatif.
