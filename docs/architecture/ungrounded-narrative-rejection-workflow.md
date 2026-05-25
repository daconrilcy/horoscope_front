<!-- Commentaire global: ce document fixe le workflow canonique de rejet des reponses narratives non fondees sans creer de surface runtime, API, DB, frontend ou retry. -->

# Workflow `ungrounded_narrative_rejection_workflow`

`ungrounded_narrative_rejection_workflow` definit le traitement auditable d'une reponse narrative LLM qui ne peut pas etre rattachee aux preuves attendues.
Il complete `narrative_answer_audit_v1` pour le statut d'audit et reutilise `evidence_refs` pour la validite des preuves, sans devenir proprietaire du calcul astrologique, des prompts, du provider, de la persistence ou d'une projection client.

Ce workflow est declaratif.
Il ne cree pas de table, migration, repository, route API, schema OpenAPI, serializer, client frontend, ecran admin, prompt template, appel provider, file de retry ou mecanisme de retry.

## Identite du workflow

| Champ | Regle |
|---|---|
| `workflow_id` | Valeur exacte: `ungrounded_narrative_rejection_workflow`. |
| `answer_id` | Identifiant unique de la reponse narrative auditee. |
| `answer_type` | Categorie de reponse heritee de `narrative_answer_audit_v1`: `basic`, `premium`, `long`, `sensitive` ou `free_short`. |
| `grounding_status` | Etat d'audit avant rejet, generalement `ungrounded`, ou resultat equivalent issu de preuves invalides. |
| `status` | Valeur terminale exacte: `rejected`. |

Le statut `rejected` est un etat terminal auditable.
Une fois applique, il ne peut pas redevenir `grounded`, `partial`, `ungrounded` ou `not_checked` dans le meme cycle de generation.
Toute tentative future de produire une autre narration doit creer une nouvelle generation auditee, avec un nouvel audit ou une nouvelle version explicitement reliee.

## Conditions de transition

La transition vers `rejected` est autorisee uniquement lorsque l'audit prouve qu'une reponse ne doit pas etre exposee au client.
Les conditions canoniques sont:

| Condition | Transition |
|---|---|
| `grounding_status` vaut `ungrounded` dans `narrative_answer_audit_v1`. | La reponse passe a `status: rejected`. |
| Une ou plusieurs `evidence_refs` attendues sont invalides avec `missing_source`, `unsupported_source_type`, `missing_hash` ou `hash_mismatch`. | La reponse passe a `status: rejected` si la section concernee supporte une affirmation client importante. |
| Une section auditee devient `unfounded` faute de preuve valide et hashable. | La reponse passe a `status: rejected` si la prose ne peut pas etre corrigee sans nouvelle generation. |
| La provenance LLM minimale est absente: prompt, provider, model, `llm_input_hash` ou `projection_hash`. | La reponse passe a `status: rejected` parce que l'audit ne peut pas verifier la narration. |

Le workflow ne fabrique jamais une preuve nominale par fallback silencieux.
Une preuve manquante ou invalide reste visible dans l'audit admin.

## Donnees conservees pour analyse interne

La réponse rejetée est conservee pour analyse interne seulement.
Le champ `raw_answer_storage` retient le contenu brut rejete afin que l'equipe habilitee puisse diagnostiquer l'ecart entre narration, prompt, provider, model et preuves.

| Champ | Obligation |
|---|---|
| `raw_answer_storage` | Contenu brut de la reponse IA rejetee, stocke en perimetre interne protege. |
| `evidence_refs` | References de preuves controlees et leur etat de validation au moment du rejet. |
| `audit_metadata.source` | Source fonctionnelle de la generation ou du cas d'usage. |
| `audit_metadata.prompt` | Reference de prompt ou snapshot autorise par `narrative_answer_audit_v1`. |
| `audit_metadata.provider` | Identifiant interne du provider LLM. |
| `audit_metadata.model` | Identifiant interne du modele utilise. |
| `audit_metadata.projection_hash` | Hash stable de la projection factuelle auditee. |
| `audit_metadata.llm_input_hash` | Hash stable de l'entree LLM auditee. |

Ces donnees ne sont pas un payload public.
Elles servent au diagnostic, a l'analyse qualite, a la revue admin future et a la preuve d'audit.

## Reponse controlee cote client

Le champ `client_message` contient un message controle et supportable par le service client.
Il ne doit jamais inclure `raw_answer_storage`, la reponse IA brute, le prompt, les hashes, les details provider ou les lignes d'audit.

Message controle canonique:

```json
{
  "client_message": "Nous ne pouvons pas afficher cette interpretation car sa fiabilite n'a pas pu etre confirmee. Notre support peut vous aider si le probleme persiste."
}
```

Les projections client-facing futures peuvent adapter la formulation, mais doivent conserver la regle suivante:
le client recoit un message contrôlé, jamais la reponse non fondee ni la reponse IA brute rejetee.

## Raisons de rejet structurees

`rejection_reason` est obligatoire et doit prendre une valeur structuree, recherchable et stable.

| Valeur | Sens |
|---|---|
| `ungrounded_claim` | Une affirmation narrative importante ne peut pas etre rattachee aux faits ou preuves attendus. |
| `missing_evidence_ref` | Une preuve attendue est absente. |
| `unsupported_evidence_source` | Une preuve pointe vers un `source_type` non autorise par `evidence_refs`. |
| `evidence_hash_mismatch` | Le hash fourni ne correspond pas au payload canonique de la source. |
| `missing_grounding_metadata` | La provenance minimale manque: prompt, provider, model, `projection_hash` ou `llm_input_hash`. |
| `unsafe_client_exposure` | La reponse contient des donnees ou details qui ne doivent pas etre exposes au client. |

`rejection_detail` est optionnel et reserve au diagnostic interne protege.
Il peut decrire la section, l'evidence invalide, le controle ayant echoue et le contexte provider, mais il doit etre masque de toute surface client-facing.

Champs minimums pour l'analyse admin future:

- `answer_id`;
- `answer_type`;
- `rejection_reason`;
- `rejection_detail` si disponible;
- `grounding_status` avant rejet;
- `evidence_refs.validation_state`;
- `audit_metadata.source`;
- `audit_metadata.provider`;
- `audit_metadata.model`;
- `audit_metadata.projection_hash`;
- `audit_metadata.llm_input_hash`;
- date technique du rejet.

## Logs et alertes internes

Le workflow exige un log interne au moment du rejet.
Le `log_event` canonique est `narrative_answer_rejected`.

| Champ de log | Regle |
|---|---|
| `event_type` | Valeur exacte: `narrative_answer_rejected`. |
| `workflow_id` | `ungrounded_narrative_rejection_workflow`. |
| `answer_id` | Identifiant de reponse auditee. |
| `answer_type` | Categorie fonctionnelle de la reponse. |
| `rejection_reason` | Valeur structuree obligatoire. |
| `grounding_status` | Etat avant rejet, par exemple `ungrounded`. |
| `provider` | Identifiant interne du provider. |
| `model` | Identifiant interne du modele. |
| `projection_hash` | Hash de projection; masquable selon la politique de logs. |
| `llm_input_hash` | Hash d'entree LLM; masquable selon la politique de logs. |
| `raw_answer_included` | Doit valoir `false` dans les logs standards. |

`alert_event` est reserve aux canaux internes de monitoring ou d'analyse.
Il doit permettre de rechercher le volume et les causes des rejets sans exposer inutilement les donnees client-sensibles.
Les payloads d'alerte ne contiennent pas la reponse brute rejetee; ils referencent l'audit interne par identifiants et hashes masques si necessaire.

## Confidentialite minimale

`privacy_controls` est obligatoire et doit couvrir:

| Controle | Regle |
|---|---|
| `masking` | Masquer les donnees client-sensibles, prompts bruts, provider internals et hashes si le canal ne requiert pas leur lecture directe. |
| `access_scope` | Restreindre `raw_answer_storage`, `rejection_detail`, prompt et metadonnees provider aux roles internes habilites: audit, qualite, support escalade ou securite. |
| `client_exposure` | Exposer uniquement `client_message` ou une projection publique future explicitement approuvee. |
| `final_retention_decision` | Valeur exacte: `product_policy_pending`; la duree RGPD finale reste une decision produit/juridique hors de cette story. |

Le rejet protege le client sans supprimer la trace necessaire au diagnostic interne.

## Politique de retry

`retry_policy` prend la valeur exacte `future_story_decision`.
Cette story ne cree pas de retry queue, de retry automatique, de fallback provider, de re-generation silencieuse ou de bouton admin de relance.

Toute strategie de retry devra etre traitee par une story dediee, avec contrat de persistence, droits admin, limitation de tentatives, observabilite et preuve anti-boucle.

## Frontiere debug

`debug_boundary` separe ce workflow des donnees de calcul astrologique et des traces runtime de calcul.
Le workflow peut referencer des identifiants d'audit, des hashes de projection et des `evidence_refs`, mais il ne stocke pas de payload debug de calcul, ne lit pas les traces de calcul comme source de preuve narrative et ne modifie pas les logs d'astrology runtime.

Les diagnostics de calcul restent dans leurs owners existants.
Les diagnostics de rejet narratif restent dans `ungrounded_narrative_rejection_workflow`, `narrative_answer_audit_v1`, `evidence_refs` et l'observabilite LLM runtime existante.

## Exemple documentaire

```json
{
  "workflow_id": "ungrounded_narrative_rejection_workflow",
  "answer_id": "answer_123",
  "answer_type": "premium",
  "grounding_status": "ungrounded",
  "status": "rejected",
  "rejection_reason": "evidence_hash_mismatch",
  "rejection_detail": "Section dominants.overview liee a une evidence_ref dont le source_hash ne correspond pas au payload canonique.",
  "raw_answer_storage": "internal_only_retained_rejected_ai_answer",
  "evidence_refs": [
    {
      "evidence_ref_id": "dominants.overview.ref.001",
      "validation_state": "hash_mismatch"
    }
  ],
  "audit_metadata": {
    "source": "narrative_generation",
    "prompt": "prompt_ref:premium_narrative.v1",
    "provider": "provider_internal_id",
    "model": "model_internal_id",
    "projection_hash": "sha256:projection",
    "llm_input_hash": "sha256:llm-input"
  },
  "client_message": "Nous ne pouvons pas afficher cette interpretation car sa fiabilite n'a pas pu etre confirmee. Notre support peut vous aider si le probleme persiste.",
  "log_event": {
    "event_type": "narrative_answer_rejected",
    "raw_answer_included": false
  },
  "alert_event": {
    "event_type": "narrative_answer_rejection_alert",
    "raw_answer_included": false
  },
  "privacy_controls": {
    "masking": "required",
    "access_scope": "internal_authorized_roles_only",
    "final_retention_decision": "product_policy_pending"
  },
  "retry_policy": "future_story_decision",
  "debug_boundary": "separate_from_calculation_debug_and_astrology_runtime_traces"
}
```

Cet exemple illustre la forme contractuelle.
Il ne constitue ni un serializer runtime, ni une route publique, ni une migration, ni un schema OpenAPI.
