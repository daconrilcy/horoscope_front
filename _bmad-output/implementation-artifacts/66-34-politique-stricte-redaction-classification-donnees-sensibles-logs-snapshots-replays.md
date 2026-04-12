# Story 66.34: Politique stricte de redaction et de classification des données sensibles dans logs, snapshots et replays

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want imposer une politique runtime unique de classification, de redaction et de segregation des données sensibles sur les surfaces d'observabilité LLM,
so that `obs_snapshot`, `llm_call_logs`, les dashboards, les audits et les replays n'exposent jamais par erreur du contenu utilisateur, des données natales, des secrets ou des artefacts de prompting au-delà de ce qui est strictement nécessaire à l'exploitation.

## Contexte

Les stories 65.15, 66.25, 66.32 et 66.33 ont beaucoup renforcé l'observabilité technique et la traçabilité runtime du pipeline LLM, mais sans encore fermer explicitement le sujet "données sensibles dans les surfaces ops" de bout en bout :

- [backend/app/ai_engine/services/log_sanitizer.py](/c:/dev/horoscope_front/backend/app/ai_engine/services/log_sanitizer.py) applique déjà une redaction best-effort par clés (`password`, `token`, `birth_data`, `content`, `message`, etc.), mais cette logique reste largement heuristique, orientée payloads Python, et non gouvernée par une classification centrale réutilisable dans tout le backend.
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py) persiste `llm_call_logs` à partir de métadonnées runtime utiles (`pipeline_kind`, `attempt_count`, `provider_error_code`, `active_snapshot_id`, etc.) et ne stocke pas `user_input` en clair dans `llm_call_logs`, mais le contrat exact "ce qui a le droit d'aller dans un log d'exploitation" n'est pas formalisé comme une politique stable et testable.
- La même couche persiste un [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py) `LlmReplaySnapshotModel` chiffré à courte rétention, ce qui est utile pour le replay, mais la séparation conceptuelle entre "données d'exploitation" et "contenu utilisateur rejouable" n'est pas encore imposée comme frontière d'architecture explicite.
- [backend/app/llm_orchestration/services/replay_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/replay_service.py) déchiffre le snapshot, relance le gateway, puis retourne aujourd'hui un `ReplayResult` contenant `raw_output` et `structured_output`. Cela ouvre un canal de restitution de contenu LLM complet dans une surface admin technique qui, par doctrine, devrait d'abord rester une surface ops.
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py) expose `/v1/admin/llm/call-logs`, `/dashboard`, `/replay` et écrit aussi des événements d'audit via [backend/app/services/audit_service.py](/c:/dev/horoscope_front/backend/app/services/audit_service.py), mais il n'existe pas encore de garde-fou transverse garantissant que `details`, payloads d'erreur, résultat de replay ou futures enrichissements dashboard ne puissent pas réintroduire du sensible.
- [frontend/src/pages/admin/AdminLogsPage.tsx](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminLogsPage.tsx) n'affiche aujourd'hui que des métadonnées sur les logs LLM, mais la modale audit affiche `JSON.stringify(log.details, null, 2)` sans politique de reveal/masquage centralisée ; si des détails sensibles remontent un jour côté audit, le front les affichera mécaniquement.
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) documente bien `obs_snapshot`, `llm_call_logs`, la release active et la taxonomie provider, mais ne fige pas encore une matrice explicite "sink -> données autorisées / interdites / redaction attendue".

Le système a donc déjà des briques utiles, mais il leur manque une doctrine runtime commune et contraignante :

- classification explicite des champs et artefacts sensibles ;
- serializers sûrs par sink (`logs`, `obs_snapshot`, `DB observability`, `audit`, `dashboard`, `replay`) ;
- interdiction de mélanger données d'exploitation et contenu utilisateur ;
- couverture de non-fuite prouvant qu'une évolution future du code ne réintroduit pas des fuites via `details`, `raw_output`, `structured_output`, `context`, messages ou données natales.

## Diagnostic exact à préserver

- La cible de cette story n'est **pas** de supprimer l'observabilité LLM ni le replay admin ; la cible est de les rendre strictement compatibles avec une politique de minimisation et de redaction.
- La cible n'est **pas** non plus de faire reposer la sécurité uniquement sur `sanitize_for_logging()` ; cette fonction doit devenir un maillon d'une politique transverse, pas le seul garde-fou.
- `llm_call_logs` est déjà conçu comme un journal d'exploitation sans `user_input` en clair. Cette propriété doit être conservée et rendue plus stricte, pas relâchée.
- `LlmReplaySnapshotModel` est aujourd'hui séparé de `LlmCallLogModel` et chiffré. Cette séparation est saine et doit être transformée en invariant architectural explicite.
- Le replay ne doit plus être considéré comme une permission implicite d'afficher ou de persister du contenu utilisateur brut dans les surfaces admin techniques, les audits ou les dashboards.
- `obs_snapshot` doit rester un snapshot **d'observabilité** ; il ne doit jamais devenir un transport opportuniste de texte utilisateur, de prompt résolu, de `raw_output`, de persona block, de `chart_json` ou de données natales détaillées.
- Les événements d'audit et leurs `details` ne doivent pas servir de canal parallèle pour réintroduire des contenus que `llm_call_logs` et `obs_snapshot` excluent déjà.
- La story doit couvrir le risque de fuite aussi bien sur le chemin nominal que sur le chemin d'erreur, y compris dans les exceptions, les `details`, les logs d'intégrité replay, et les futures évolutions de dashboard.
- La séparation recherchée est conceptuelle et technique :
  - **données d'exploitation** = taxonomie, IDs, métriques, statuts, timings, compteurs, discriminants ;
  - **contenu utilisateur** = messages, questions, prompts, sorties textuelles, données natales, PII, secrets, artefacts rejouables.

## Cible d'architecture

Introduire une **Sensitive Data Classification & Redaction Policy** centrale pour le pipeline LLM, appliquée de façon cohérente à tous les sinks d'observabilité.

Cette politique doit :

1. définir une taxonomie stable des données (`secret`, `direct_identifier`, `quasi_identifier`, `user_authored_content`, `derived_sensitive_domain_data`, `operational_metadata`, ou équivalent stable) ;
2. associer à chaque sink une règle explicite : `forbidden`, `redacted`, `hashed`, `encrypted_isolated`, `allowed_verbatim`, `allowed_masked` ;
3. fournir des serializers/redactors dédiés aux surfaces suivantes :
   - logs applicatifs structurés ;
   - `obs_snapshot` / `GatewayMeta` ;
   - persistance `llm_call_logs` ;
   - `llm_replay_snapshots` ;
   - payloads admin et dashboards ;
   - événements d'audit ;
4. interdire qu'un objet riche (`GatewayResult`, `ReplayResult`, exception `details`, payloads audit) soit sérialisé "tel quel" dans une surface d'exploitation sans passer par cette politique ;
5. imposer une frontière stricte entre :
   - **journalisation/pilotage ops** ;
   - **contenu rejouable** chiffré et borné ;
   - **révélation explicite et auditée** éventuelle d'un contenu sensible, si un tel besoin est retenu hors production.

La cible n'est donc pas seulement "masquer quelques clés". La cible est une **doctrine runtime de non-fuite**, gouvernée par le type de donnée **et** par la destination.

## Politique de classification à imposer

La story doit rendre explicite, documentée et testable la classification minimale suivante :

- **`secret_credential`** : API keys, tokens, secrets, credentials, authorization headers, encryption material ;
- **`direct_identifier`** : email, phone, address, user-entered contact data, government identifiers ;
- **`technical_correlation_identifier`** : `request_id`, `trace_id`, `active_snapshot_id`, `manifest_entry_id` et autres identifiants techniques dont la finalité est la corrélation d'exécution interne, autorisables seulement sur des sinks ops explicitement listés ;
- **`correlable_business_identifier`** : `user_id`, `target_id`, IDs de profil natal, IDs de compte, IDs métier ou tout identifiant permettant de rattacher une trace à une personne, à un dossier ou à un artefact métier sensible ; cette catégorie ne doit jamais être autorisée "en bloc" sur un sink ops sans décision explicite de masquage ou de réduction ;
- **`user_authored_content`** : messages utilisateur, question, situation, `raw_output`, `structured_output`, prompt résolu, persona block, historique conversationnel ;
- **`derived_sensitive_domain_data`** : `birth_data`, `natal_data`, `chart_json`, `natal_chart_summary`, interprétations, données astrologiques dérivées d'un utilisateur ;
- **`operational_metadata`** : `pipeline_kind`, `execution_path_kind`, `validation_status`, `attempt_count`, `provider_error_code`, `breaker_state`, `active_snapshot_id`, `manifest_entry_id`, coûts/tokens agrégés, latence, use case, feature, subfeature, plan, environnement.

Règle de gouvernance attendue :

- `operational_metadata` est la **seule** catégorie nominalement autorisée en clair dans `obs_snapshot`, `llm_call_logs`, dashboards et logs ops ;
- un champ n'est **pas** opérationnel simplement parce qu'il "aide au debug" ; aucun extrait de prompt, aperçu de message, preview de sortie, texte d'erreur enrichi avec du contenu, ou fragment de payload métier ne peut être requalifié en `operational_metadata` ;
- la politique doit reposer sur une **allowlist positive** de champs ops explicitement autorisés, pas seulement sur une blacklist des champs interdits ;
- `user_authored_content`, `derived_sensitive_domain_data`, `direct_identifier` et `secret_credential` sont interdits dans ces surfaces, sauf transformation explicite (`masked`, `hashed`, `redacted`) justifiée par le sink ;
- le replay snapshot chiffré peut contenir du contenu sensible **uniquement** parce qu'il est un store isolé, chiffré, TTL-court, non indexé pour l'exploitation et non exposé aux dashboards ;
- aucune surface d'audit ou de dashboard ne doit afficher un blob `details` ou un objet `ReplayResult` non passé par le serializer sûr de la politique.

## Latest Technical Specifics

Les informations externes suivantes doivent être intégrées pour éviter une implémentation datée ou trop locale :

- L'OWASP Logging Cheat Sheet rappelle que les logs ne doivent pas contenir directement mots de passe, tokens, PII sensible, secrets ou données d'une classification supérieure au système de logs, et recommande une stratégie explicite de suppression, masquage, hash ou chiffrement selon le besoin. Source : [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html).
- La documentation Python 3.13 sur `logging.Filter` précise qu'un filtre attaché aux handlers peut voir chaque `LogRecord` et, depuis Python 3.12+, remplacer le `LogRecord` avant émission. Cela donne un point d'application central plus sûr qu'une simple discipline ad hoc aux call sites. Source : [Python 3.13 logging documentation](https://docs.python.org/3.13/library/logging.html).
- La documentation OpenAI sur les data controls précise que les abuse-monitoring logs de l'API peuvent contenir certains prompts, réponses et métadonnées dérivées, avec rétention par défaut jusqu'à 30 jours ; elle précise aussi qu'en Zero Data Retention, `store` est traité comme `false` sur `/v1/responses`. Source : [OpenAI API data controls](https://platform.openai.com/docs/models/how-we-use-your-data).

Inférences à expliciter dans la story :

- le produit ne doit pas se croire "sûr" simplement parce que le provider chiffre ou retient déjà des données ; chaque copie locale supplémentaire (`logs`, `audit`, `replay`, `dashboard`) augmente la surface de fuite ;
- sur Python 3.13, un filtre/formatter central de redaction côté logging est réaliste et préférable à une confiance exclusive dans les développeurs appelants ;
- la politique locale doit être plus stricte que la simple rétention du provider : minimiser en amont, séparer les stores, et ne jamais persister le contenu utilisateur en clair dans un système d'exploitation si ce contenu n'est pas indispensable au but de ce système.

## Acceptance Criteria

1. **AC1 — Taxonomie centrale obligatoire** : le backend introduit une taxonomie centrale et versionnée des catégories de données sensibles pertinentes au pipeline LLM, au minimum équivalente à `secret_credential`, `direct_identifier`, `technical_correlation_identifier`, `correlable_business_identifier`, `user_authored_content`, `derived_sensitive_domain_data`, `operational_metadata`. Cette taxonomie est réutilisée par les loggers, l'observabilité, l'audit et le replay au lieu de multiplier des listes locales divergentes.
2. **AC2 — Matrice sink -> traitement explicite** : la politique documente et encode, pour chaque sink (`structured logs`, `obs_snapshot`, `llm_call_logs`, `llm_replay_snapshots`, API admin logs/dashboard, audit trail, payload replay), si chaque catégorie est `forbidden`, `redacted`, `masked`, `hashed`, `encrypted_isolated` ou `allowed`. L'absence de décision explicite pour un sink est un défaut d'implémentation.
3. **AC3 — Allowlist positive des champs ops** : pour `obs_snapshot`, `llm_call_logs`, dashboards et APIs admin techniques, l'implémentation maintient une allowlist explicite de champs opérationnels autorisés. Un champ ne peut pas être admis au seul motif qu'il est "utile au debug". Toute donnée textuelle issue d'un prompt, d'un message, d'une sortie LLM, d'une donnée natale ou d'un `details` libre reste interdite tant qu'elle n'est pas explicitement classifiée et autorisée pour ce sink.
4. **AC4 — `obs_snapshot` strictement opérationnel** : `ExecutionObservabilitySnapshot`, `GatewayMeta` et tout snapshot équivalent ne peuvent porter que des métadonnées d'exploitation issues de l'allowlist positive. Aucun champ de type message utilisateur, question, prompt résolu, `raw_output`, `structured_output`, `chart_json`, `natal_data`, `birth_data`, bloc persona ou payload rejouable n'y est introduit, y compris par erreur future de sérialisation.
5. **AC5 — `llm_call_logs` sans contenu utilisateur** : `LlmCallLogModel` et `log_call()` restent strictement limités aux métadonnées d'exploitation et aux empreintes irréversibles permises par la politique. Aucun contenu utilisateur brut, sortie LLM brute, contrat de sortie complet, PII directe ou identifiant métier corrélable non transformé ne peut y être persisté.
6. **AC6 — Replay snapshot isolé et borné** : `LlmReplaySnapshotModel` reste la seule zone où un input rejouable sensible peut exister côté observabilité LLM, avec chiffrement, TTL court, absence d'indexation fonctionnelle pour les dashboards, et absence de duplication en clair vers `llm_call_logs`, audit ou logs applicatifs.
7. **AC7 — Contrat de replay strictement non textuel** : `ReplayResult` et `/v1/admin/llm/replay` ne renvoient plus par défaut `raw_output`, `structured_output`, aperçu textuel, diff textuel, extrait sémantique ni aucun contenu utilisateur sensible brut ou dérivé. La réponse nominale du replay expose uniquement des métadonnées ops, un diff de statut/validation/taxonomie/provider/release, et éventuellement des empreintes irréversibles explicitement autorisées. Si une révélation de contenu est retenue hors prod, elle doit être explicitement séparée, fortement auditée, bornée par rôle/environnement et non active par défaut.
8. **AC8 — Audit trail sûr par DTO borné** : `AuditService.record_event()` et les événements d'audit liés à l'observabilité LLM, au replay ou aux erreurs ne transportent pas de contenus sensibles non redigés. Les événements LLM sensibles sont sérialisés via des DTOs safe dédiés ou une structure bornée équivalente, et non via un `details: dict[str, Any]` libre utilisé comme blob opportuniste. Les actions `llm_call_replayed`, `llm_logs_purge` et assimilées n'enregistrent que des références sûres (`request_id`, log id, prompt version id, statut, raison), jamais le contenu rejoué ou la nouvelle réponse complète.
9. **AC9 — Dashboard/admin API sûrs** : les endpoints admin exposant logs LLM, dashboard ou audits ne renvoient que des champs conformes à la matrice de classification et à l'allowlist positive de sortie. Les listes, filtres, exports et vues de détail ne peuvent pas afficher naïvement un `details: dict` complet sans passer par un serializer de sortie aligné sur la politique.
10. **AC10 — Front admin aligné** : les composants de cockpit technique, notamment [frontend/src/pages/admin/AdminLogsPage.tsx](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminLogsPage.tsx), n'affichent pas de détails libres potentiellement sensibles sans masquage/restriction explicite. La modale audit, la modale replay et les messages de résultat respectent la séparation entre métadonnées ops et contenu utilisateur.
11. **AC11 — Hiérarchie de confiance explicite** : l'implémentation applique la politique dans l'ordre suivant : serializers safe par sink, DTOs bornés pour les surfaces admin/audit/replay, puis filtre global de logging comme filet terminal. Le filtre global ne constitue pas à lui seul le contrat principal de sûreté.
12. **AC12 — Hashing et fingerprinting bornés** : lorsqu'une corrélation fonctionnelle est nécessaire (`input_hash`, identifiant technique, fingerprint), la politique précise les usages autorisés (`corrélation technique court terme`, `déduplication`, `matching d'intégrité replay`) et interdit explicitement les usages de substitution durable (`recherche produit/dashboard`, `filtrage fonctionnel exposé aux ops`, `pseudo-identifiant stable`).
13. **AC13 — Couverture chemin d'erreur incluse** : les exceptions, `details`, logs d'intégrité replay, erreurs de validation et erreurs provider respectent la même politique que le chemin nominal. Une erreur ne doit pas exposer plus de données qu'un succès.
14. **AC14 — Non-régression sur données natales et PII** : des tests prouvent que `birth_data`, `natal_data`, `chart_json`, emails, messages utilisateur, prompts, sorties LLM et identifiants métier corrélables n'apparaissent ni dans `llm_call_logs`, ni dans `obs_snapshot`, ni dans les réponses admin/dashboard, ni dans les événements d'audit liés au replay.
15. **AC15 — Contrat de reveal exceptionnel explicite** : si le produit conserve un besoin de révélation manuelle d'un contenu sensible pour diagnostic en environnement non production, ce reveal doit être un workflow séparé, explicite, role-gated, traçable et absent des surfaces de monitoring par défaut. Aucune révélation implicite via `/replay`, `/call-logs`, audit export ou modale front n'est acceptable.
16. **AC16 — Documentation de gouvernance** : [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) et la documentation d'architecture pertinente décrivent noir sur blanc la taxonomie, la matrice sink -> traitement, la frontière entre `llm_call_logs` et `llm_replay_snapshots`, l'allowlist positive des champs ops autorisés, et la politique de restitution du replay.
17. **AC17 — Couverture de non-fuite automatisée** : une suite de tests dédiée échoue dès qu'un nouveau champ sensible fuit vers un log, un snapshot, un audit ou un dashboard sans classification et redaction conformes.

## Tasks / Subtasks

- [ ] Task 1: Introduire la taxonomie centrale et la matrice de politique (AC1, AC2, AC15)
  - [ ] Créer un module dédié de classification/redaction dans `backend/app/llm_orchestration/` ou `backend/app/core/` réutilisable par observabilité, audit et admin.
  - [ ] Définir les catégories de données et les stratégies de traitement par sink.
  - [ ] Documenter la matrice "sink -> catégories autorisées / interdites / transformées".
  - [ ] Distinguer explicitement `technical_correlation_identifier` et `correlable_business_identifier`.

- [ ] Task 2: Verrouiller `obs_snapshot` et `llm_call_logs` sur les seules métadonnées ops (AC3, AC4, AC11, AC13)
  - [ ] Auditer [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py) et [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py) pour lister explicitement les champs autorisés.
  - [ ] Introduire une allowlist positive des champs opérationnels admis par sink.
  - [ ] Interdire ou redacter tout futur champ non opérationnel avant sérialisation/persistance.
  - [ ] Vérifier que `input_hash` et les IDs techniques restent conformes à la politique de corrélation minimale.

- [ ] Task 3: Séparer strictement replay rejouable et exploitation (AC5, AC6, AC14)
  - [ ] Réaligner [backend/app/llm_orchestration/services/replay_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/replay_service.py) pour que le replay consomme le snapshot chiffré sans re-exposer le contenu brut dans la réponse nominale.
  - [ ] Figer le contrat de `ReplayResult` sur des métadonnées sûres et un diff strictement non textuel.
  - [ ] Si un reveal exceptionnel est conservé hors production, le modéliser comme un chemin distinct, explicite et audité.

- [ ] Task 4: Aligner audit et admin APIs sur la politique (AC7, AC8, AC12, AC13)
  - [ ] Introduire des DTOs safe dédiés ou une structure bornée équivalente pour les événements d'audit LLM sensibles.
  - [ ] Introduire un sanitizer/sérialiseur pour `AuditService` et pour les payloads `details` liés au LLM.
  - [ ] Réaligner [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py) pour que `/call-logs`, `/dashboard` et `/replay` n'exposent que des DTOs sûrs.
  - [ ] Couvrir aussi les payloads d'erreur et messages de replay échoué.

- [ ] Task 5: Centraliser la redaction des logs applicatifs (AC10, AC12)
  - [ ] Étendre ou remplacer [backend/app/ai_engine/services/log_sanitizer.py](/c:/dev/horoscope_front/backend/app/ai_engine/services/log_sanitizer.py) par une approche centralisée compatible Python 3.13 (`logging.Filter` ou mécanisme équivalent).
  - [ ] Appliquer explicitement la hiérarchie de confiance : serializers safe par sink -> DTOs bornés -> filtre global terminal.
  - [ ] Éviter que de nouveaux `logger.info(..., extra=payload)` ou `details={...}` contournent la politique.
  - [ ] Tester le chemin nominal et le chemin d'erreur.

- [ ] Task 6: Réaligner le cockpit frontend admin (AC8, AC9, AC14)
  - [ ] Mettre à jour [frontend/src/pages/admin/AdminLogsPage.tsx](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminLogsPage.tsx) pour ne plus afficher des blobs `details` non filtrés si le backend ne garantit pas déjà leur sûreté.
  - [ ] Vérifier les libellés, modales et messages de replay pour qu'ils restent purement ops par défaut.
  - [ ] Ajouter ou adapter les tests frontend associés.

- [ ] Task 7: Couverture de non-fuite (AC13, AC16)
  - [ ] Étendre [backend/app/ai_engine/tests/test_log_sanitizer.py](/c:/dev/horoscope_front/backend/app/ai_engine/tests/test_log_sanitizer.py) avec une classification par sink, pas seulement par clé.
  - [ ] Étendre [backend/app/llm_orchestration/tests/test_observability.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_observability.py) pour vérifier l'absence de fuite dans `llm_call_logs`.
  - [ ] Ajouter des tests replay et admin API garantissant qu'aucun `raw_output`, `structured_output`, `birth_data`, email brut ou message utilisateur ne ressort dans les réponses ops.
  - [ ] Ajouter un test frontend sur l'absence d'affichage d'un `details` sensible brut.

- [ ] Task 8: Vérification locale obligatoire
  - [ ] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [ ] Dans `backend/`, exécuter `ruff format .` puis `ruff check .`.
  - [ ] Exécuter `pytest -q`.
  - [ ] Exécuter au minimum les suites ciblées observabilité/replay/admin/front liées à cette story.

## Dev Notes

### Ce que le dev doit retenir avant d'implémenter

- `log_sanitizer.py` protège déjà plusieurs clés sensibles, mais sa logique est key-based et pas encore pilotée par une taxonomie transverse ni par la destination du flux.
- `observability_service.log_call()` sépare déjà `llm_call_logs` et `llm_replay_snapshots`; cette séparation est le bon point d'appui pour imposer une frontière nette exploitation vs contenu rejouable.
- `ReplayResult` renvoie aujourd'hui `raw_output` et `structured_output`; c'est la dérive principale à corriger si l'on veut garder le replay comme outil ops sans en faire une fuite de contenu.
- `AdminLogsPage` n'affiche pas aujourd'hui le contenu complet des logs LLM, mais la modale audit affiche un JSON libre ; il faut traiter ce front comme une surface d'exposition à part entière, pas comme un simple miroir passif du backend.
- La story doit couvrir aussi le chemin d'erreur : beaucoup de fuites naissent dans `details`, exceptions, messages d'intégrité ou logs de diagnostic.
- La politique doit être spécifique au sink. Une donnée peut être :
  - interdite en log ;
  - hashée en persistance ;
  - chiffrée dans un store isolé de replay ;
  - totalement absente des dashboards.
- Le contrat ops doit être défini par **allowlist positive** des champs autorisés, pas par simple intuition "debug utile".
- Les identifiants techniques de corrélation et les identifiants métier corrélables ne doivent pas être mélangés dans une même catégorie permissive.
- Le filtre global logging est un filet terminal, pas la source principale de confiance ; la sûreté doit déjà être acquise au niveau des DTOs et serializers par sink.
- Il faut éviter une fausse solution du type "on tronque tout". La troncature seule ne remplace pas une classification et n'empêche pas forcément la fuite de PII ou de contenu sensible.

### Ce que le dev ne doit pas faire

- Ne pas ajouter de nouveaux champs sensibles à `ExecutionObservabilitySnapshot`, `GatewayMeta`, `LlmCallLogModel` ou aux DTOs admin "pour aider le debug".
- Ne pas réutiliser `AuditService.details` comme canal de dump commode d'un résultat de replay, d'un payload d'entrée ou d'une erreur enrichie.
- Ne pas conserver un `details: dict[str, Any]` libre comme contrat nominal des événements d'audit LLM sensibles si des DTOs safe dédiés peuvent borner la surface.
- Ne pas conserver `ReplayResult.raw_output` ou `ReplayResult.structured_output` dans la réponse nominale "par simplicité" sans séparation explicite du reveal.
- Ne pas remplacer cette fuite par un "aperçu", un "diff texte" ou un résumé sémantique de contenu ; cela reste du contenu.
- Ne pas supposer qu'un payload chiffré en base devient affichable ou exportable dans une surface ops.
- Ne pas s'appuyer uniquement sur une liste de clés sensibles ; certaines données sont sensibles par contexte, pas seulement par nom de champ.
- Ne pas introduire une redaction divergente entre backend logs, persistance, audits et frontend admin.
- Ne pas masquer un problème structurel par un simple "preview" de contenu en UI.

### Fichiers à inspecter en priorité

- [backend/app/ai_engine/services/log_sanitizer.py](/c:/dev/horoscope_front/backend/app/ai_engine/services/log_sanitizer.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [backend/app/llm_orchestration/services/replay_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/replay_service.py)
- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/services/audit_service.py](/c:/dev/horoscope_front/backend/app/services/audit_service.py)
- [frontend/src/pages/admin/AdminLogsPage.tsx](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminLogsPage.tsx)
- [backend/app/ai_engine/tests/test_log_sanitizer.py](/c:/dev/horoscope_front/backend/app/ai_engine/tests/test_log_sanitizer.py)
- [backend/app/llm_orchestration/tests/test_observability.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_observability.py)
- [backend/app/llm_orchestration/tests/test_replay_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_replay_service.py)
- [frontend/src/tests/AdminLogsPage.test.tsx](/c:/dev/horoscope_front/frontend/src/tests/AdminLogsPage.test.tsx)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

### Previous Story Intelligence

- **65.15** a installé le cockpit technique et le replay admin ; 66.34 doit maintenant empêcher que ce cockpit devienne un canal de fuite de contenu utilisateur via modales, audit ou réponses de replay.
- **66.25** a imposé un `obs_snapshot` canonique ; 66.34 doit protéger ce snapshot contre toute dérive de contenu non opérationnel.
- **66.32** a ajouté `active_snapshot_id/version` et `manifest_entry_id` dans l'observabilité ; 66.34 doit conserver cette richesse de corrélation sans rouvrir la porte aux prompts, personas ou contrats complets dans les surfaces ops.
- **66.33** a enrichi l'observabilité provider-centric (`attempt_count`, `provider_error_code`, `breaker_state`, `breaker_scope`) ; 66.34 doit préserver ces discriminants utiles tout en imposant que les enrichissements futurs restent strictement "operational metadata only".

### Git Intelligence

Commits récents pertinents observés :

- `83079c5c` : `docs(llm): clarify story 66.33 runtime contracts`
- `66efdf8d` : `fix(llm): harden openai provider runtime`
- `f9c6012e` : `docs(llm): tighten story 66.32 snapshot scope and freeze model`
- `182000fa` : `docs(llm): close story 66.32 artifact and release snapshot docs`
- `d92be25f` : `fix(llm): strictly decouple snapshot validation from live tables and fix async delete await`

Pattern à réutiliser :

- introduire une seule source de vérité par axe de gouvernance ;
- fermer les ambiguïtés runtime dans le code avant d'élargir la documentation ;
- préférer des discriminants stables, testables et bornés à des payloads riches implicites ;
- prouver la sûreté par tests de non-fuite, pas par hypothèse.

### Testing Requirements

- Ajouter un test unitaire de classification qui vérifie qu'un même champ peut être `forbidden` dans `llm_call_logs` mais `encrypted_isolated` dans `llm_replay_snapshots`.
- Ajouter un test unitaire garantissant que `birth_data`, `natal_data`, `chart_json`, `message`, `question`, `raw_output` et `structured_output` ne peuvent pas être sérialisés dans `obs_snapshot`.
- Ajouter un test unitaire sur `log_call()` prouvant qu'aucun payload sensible n'est persisté dans `LlmCallLogModel`, même quand `GatewayResult` contient du contenu riche.
- Ajouter un test unitaire sur `replay()` prouvant que la réponse nominale ne retourne plus le contenu brut rejoué.
- Ajouter un test unitaire sur `replay()` prouvant qu'elle ne retourne ni aperçu textuel ni diff textuel de contenu.
- Ajouter un test unitaire sur les erreurs de replay montrant qu'aucun `details` sensible n'est reflété.
- Ajouter un test d'intégration API sur `/v1/admin/llm/call-logs` et `/v1/admin/llm/replay` vérifiant l'absence de fuite de données natales, PII et contenu utilisateur.
- Ajouter un test d'intégration sur l'audit `llm_call_replayed` garantissant que `details` ne contient pas `raw_output`, `structured_output` ni input decrypté.
- Ajouter un test couvrant un identifiant métier corrélable (`user_id`, `target_id`, ID de profil`) pour vérifier qu'il ne fuit pas en clair dans un sink ops non autorisé.
- Ajouter un test frontend sur `AdminLogsPage` garantissant qu'un détail sensible brut n'est pas rendu tel quel dans la modale de détail ou de replay.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`
  - `pytest app/ai_engine/tests/test_log_sanitizer.py -q`
  - `pytest app/llm_orchestration/tests/test_observability.py -q`
  - `pytest app/llm_orchestration/tests/test_replay_service.py -q`
- Commandes frontend recommandées pour la partie admin :
  - `cd frontend`
  - `npm test -- AdminLogsPage`

### Project Structure Notes

- Travail backend + frontend admin + documentation.
- Aucun changement produit côté pages utilisateur n'est attendu.
- Les modifications doivent rester concentrées dans `backend/app/ai_engine/`, `backend/app/llm_orchestration/`, `backend/app/api/v1/routers/`, `backend/app/services/`, `frontend/src/pages/admin/`, `frontend/src/tests/` et `docs/`.

### References

- [backend/app/ai_engine/services/log_sanitizer.py](/c:/dev/horoscope_front/backend/app/ai_engine/services/log_sanitizer.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [backend/app/llm_orchestration/services/replay_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/replay_service.py)
- [backend/app/infra/db/models/llm_observability.py](/c:/dev/horoscope_front/backend/app/infra/db/models/llm_observability.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/services/audit_service.py](/c:/dev/horoscope_front/backend/app/services/audit_service.py)
- [frontend/src/pages/admin/AdminLogsPage.tsx](/c:/dev/horoscope_front/frontend/src/pages/admin/AdminLogsPage.tsx)
- [frontend/src/tests/AdminLogsPage.test.tsx](/c:/dev/horoscope_front/frontend/src/tests/AdminLogsPage.test.tsx)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- La documentation doit ajouter une section dédiée explicitant :
  - taxonomie des classes de données ;
  - matrice `sink -> traitement` ;
  - frontière `llm_call_logs` vs `llm_replay_snapshots` ;
  - doctrine admin / audit / replay.
- [65-15-observabilite-technique-incidents.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/65-15-observabilite-technique-incidents.md)
- [66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-25-renforcement-observabilite-operationnelle-pipeline-canonique-compatibilites.md)
- [66-32-versionnement-atomique-et-rollback-sur-des-artefacts-de-prompting.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-32-versionnement-atomique-et-rollback-sur-des-artefacts-de-prompting.md)
- [66-33-durcissement-operationnel-appel-provider-openai.md](/c:/dev/horoscope_front/_bmad-output/implementation-artifacts/66-33-durcissement-operationnel-appel-provider-openai.md)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [Python 3.13 logging documentation](https://docs.python.org/3.13/library/logging.html)
- [OpenAI API data controls](https://platform.openai.com/docs/models/how-we-use-your-data)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- Story 66.34 créée pour fermer explicitement le risque de fuite entre observabilité LLM, replay et surfaces admin.
- Le cadrage impose une classification centrale par type de donnée et par sink, avec séparation stricte entre métadonnées ops et contenu utilisateur.
- Le scope couvre backend, audit, replay, dashboard admin et frontend `AdminLogsPage`, avec tests de non-fuite obligatoires.

### File List

- `_bmad-output/implementation-artifacts/66-34-politique-stricte-redaction-classification-donnees-sensibles-logs-snapshots-replays.md`
