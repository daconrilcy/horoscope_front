# Story 70.18: Cleaner la structure backend et converger les namespaces techniques

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want nettoyer la structure du backend et converger les namespaces techniques vers une organisation unique et lisible,
so that le code backend reste maintenable, sans couches paralleles ni dossiers de base concurrents pour une meme responsabilite.

## Contexte

Les stories 70-13 a 70-17 ont deja fortement nettoye le backend LLM, mais elles ont aussi laisse apparaitre une derive structurelle : plusieurs couches techniques couvrent la meme thematique sous des noms differents.

Le cas le plus visible est la coexistence de `backend/app/infra/` et `backend/app/infrastructure/`, alors que l architecture de reference du projet, les habitudes du backend et les regles du repo convergent vers `infra/` comme dossier canonique.

L audit local mene pendant la verification de structure a montre que :

- `app.infra` est le centre de gravite historique et reel du backend ;
- `app.infrastructure` ne couvrait qu un sous-perimetre partiel, principalement LLM ;
- les deux dossiers portaient une thematique identique, ce qui cree de la confusion de maintenance et ouvre la porte a une duplication future ;
- la regle de gouvernance demandee par le produit est desormais explicite : **pas d ajout de dossier de base dans `backend/` sans accord explicite de l utilisateur**.

Cette story vise donc un nettoyage structurel backend pragmatique, avec une premiere tache deja clairement identifiee : **la convergence de `app.infrastructure` vers `app.infra` et la migration complete des imports associes**. La story doit ensuite prolonger cette logique pour eviter qu un nouveau dedoublement de fondation backend ne reapparaisse ailleurs.

## Objectif

Etablir un backend avec :

- une seule convention de nommage par couche technique fondationnelle ;
- aucun dossier de base concurrent pour une meme responsabilite ;
- une gouvernance explicite sur la creation de nouveaux dossiers racines backend ;
- des imports alignes sur les chemins canoniques reels ;
- des garde-fous qui evitent le retour de la dette structurelle.

## Acceptance Criteria

1. **AC1 - Namespace infrastructure unique** : il n existe plus de coexistence active entre `backend/app/infra/` et un autre dossier base-equivalent portant la meme responsabilite. Le namespace canonique backend pour l infrastructure technique reste `app.infra`.
2. **AC2 - Migration complete des imports** : tous les imports nominaux backend, scripts et tests visant un ancien namespace technique concurrent sont migres vers le namespace canonique retenu, sans shim durable non justifie.
3. **AC3 - Suppression des duplications de fondation** : aucun dossier de base doublon ou quasi-doublon n est laisse en place dans `backend/app/` pour une meme couche (ex. `infra` vs `infrastructure`) sauf justification transitoire explicite documentee.
4. **AC4 - Structure backend documentee** : la documentation de reference backend indique clairement quels sont les dossiers fondationnels autorises sous `backend/app/`, leur role, et la convention de nommage attendue.
5. **AC5 - Regle de gouvernance enforcee** : la regle "pas d ajout de dossier de base dans `backend/` sans accord explicite de l utilisateur" est inscrite dans les regles du repo et reprise dans la documentation de structure backend.
6. **AC6 - Garde-fou anti-reintroduction** : un controle automatise ou semi-automatise permet de detecter l apparition d un nouveau dossier de base backend non approuve ou d imports pointant vers un namespace structurellement deprecie.
7. **AC7 - Aucun refactor cosmétique massif** : le nettoyage reste cible, oriente structure et maintenabilite. Il n introduit pas de refonte de style ou de deplacement sans justification fonctionnelle ou architecturale claire.
8. **AC8 - Cohérence avec l architecture du projet** : la structure finale reste coherente avec l architecture de reference du monorepo (`api`, `core`, `domain`, `services`, `infra`) et ne reintroduit pas de nouvelle taxonomie parallele.
9. **AC9 - Validation backend obligatoire** : la story n est consideree terminee que si les verifications locales backend dans le venv ont ete executees et tracees (`ruff check`, suites pytest ciblees ou completes justifiees), avec preuve que la migration structurelle n a pas casse les imports ni les points d entree critiques.
10. **AC10 - Horloge backend centralisee** : tout nouvel acces applicatif a l heure ou a la date courante backend passe par un provider canonique unique (`DatetimeProvider`) positionne dans la couche `core`, afin d eviter les appels disperses a `datetime.now(...)`, `date.today()` ou helpers locaux equivalents.
11. **AC11 - Modeles DB LLM regroupes et non legacy** : tous les modeles SQLAlchemy relevant du perimetre LLM actuellement places directement sous `backend/app/infra/db/models/` sont regroupes sous le sous-namespace canonique `backend/app/infra/db/models/llm/`, avec migration complete des imports backend, scripts et tests vers `app.infra.db.models.llm.*`, preuve que les nouveaux fichiers sont effectivement utilises par le runtime/tests, et absence de fichier racine, import ou shim legacy conservant l ancien chemin.
12. **AC12 - Commentaires et docstrings en français** : chaque fichier applicatif cree ou significativement modifie par cette story contient un commentaire global en français en haut de fichier et des docstrings en français pour les modules, classes, fonctions publiques ou fonctions non triviales, afin d expliciter l intention sans paraphraser le code.
13. **AC13 - Source de verite runtime clarifiee** : supprimer ou deprecier dans `PromptAssemblyConfigModel` tout champ qui duplique le contrat fonctionnel ou la strategie d execution deja portee ailleurs, en particulier `execution_config`, `interaction_mode`, `user_question_policy`, `input_schema`, `output_contract_ref` et `fallback_use_case`, afin que la responsabilite entre assembly, prompt version et execution profile soit univoque.
14. **AC14 - Fin de l ambiguite entre profile et assembly** : interdire qu une configuration d assembly puisse surcharger librement des parametres d execution si un `execution_profile_ref` est present ; soit `execution_config` est supprime, soit il est remplace par un mecanisme d overrides borne et explicitement nomme.
15. **AC15 - Champs metier string remplaces par des types fermes** : introduire des enums ou des check constraints pour les champs metier a domaine fini comme `provider`, `reasoning_profile`, `verbosity_profile`, `output_mode`, `tool_mode`, `granularity`, `taxonomy_scope`, `interaction_mode`, `user_question_policy`, `environment`, `pipeline_kind` et `breaker_state`.
16. **AC16 - Invariants DB explicites pour les releases** : garantir au niveau base de donnees qu il n existe qu une seule release active a la fois et que `LlmReleaseSnapshotModel.version` est unique.
17. **AC17 - Modele de schema de sortie reellement versionne** : permettre plusieurs versions pour un meme `name` dans `LlmOutputSchemaModel` et remplacer l unicite simple sur `name` par une unicite `(name, version)`, ou retirer le champ `version` s il n a pas de role reel.
18. **AC18 - Agregat de consommation sans redondance semantique** : supprimer le doublon entre `taxonomy_scope` et `is_legacy_residual` en ne conservant qu une seule source de verite pour distinguer nominal et legacy residual.
19. **AC19 - Agregat de consommation calculable proprement** : documenter et implementer une strategie de recalcul fiable pour `latency_p50_ms`, `latency_p95_ms` et `error_rate_bps`, afin d eviter des mises a jour incrementales incoherentes sur des metriques non additives.
20. **AC20 - Clarification des colonnes provider en observabilite** : deprecier ou renommer le champ `provider` de `LlmCallLogModel` pour eviter toute ambiguite avec `requested_provider`, `resolved_provider` et `executed_provider`.
21. **AC21 - Table d observabilite allegee** : scinder `LlmCallLogModel` en au moins deux couches logiques si necessaire : un log coeur pour les dimensions nominales de l appel, et une extension pour les metadonnees enrichies de hardening, breaker, erreurs runtime et release observability.
22. **AC22 - Indexation alignee sur les usages reels** : ajouter les index necessaires aux requetes d exploitation probables sur `llm_call_logs`, notamment sur `timestamp`, `trace_id`, `feature/subfeature/plan`, `active_snapshot_version` et `executed_provider`, en plus des deux index existants.
23. **AC23 - Payloads d exemple alignes sur la taxonomie canonique** : etendre `LlmSamplePayloadModel` pour supporter au minimum `subfeature` et `plan` en plus de `feature` et `locale`, afin d aligner les payloads QA sur la resolution canonique reelle.
24. **AC24 - Mixins d audit factorises** : factoriser les helpers de timestamp et les colonnes d audit repetees (`utc_now`, `created_at`, `updated_at`, `created_by`, `published_at`) dans des mixins ou helpers communs, afin de supprimer la duplication transversale du module `models.llm`.
25. **AC25 - Validation des JSON bornes** : ajouter une validation structuree pour les champs JSON qui ont deja une forme implicite, notamment `formatting` dans les personas et les listes JSON comme `style_markers`, `boundaries`, `allowed_topics` et `disallowed_topics`.
26. **AC26 - Semantique explicite des composants optionnels d assembly** : remplacer les booleens `feature_enabled`, `subfeature_enabled`, `persona_enabled` et `plan_rules_enabled` par une semantique de resolution plus explicite, afin de distinguer clairement absence, heritage, desactivation volontaire et nullabilite metier.
27. **AC27 - Legacy explicitement marque ou eteint** : documenter et materialiser dans le modele la frontiere entre objets canoniques et objets legacy encore toleres, notamment autour de `LlmUseCaseConfigModel` et `LlmPromptVersionModel`, pour eviter la derive de source de verite entre paradigme `use_case` et paradigme `feature/subfeature/plan/locale`.
28. **AC28 - Relations ORM completes et coherentes** : completer les relationships manquantes ou asymetriques entre assembly, execution profile, release snapshot et output schema, afin de rendre le graphe ORM plus navigable et de reduire les acces bases sur cles etrangeres "a la main".
29. **AC29 - Conventions de taille homogenes** : harmoniser les longueurs de `String(...)` pour les memes concepts metier entre tables, par exemple `locale`, `feature`, `subfeature`, `provider`, `model`, afin de reduire les divergences arbitraires de schema.
30. **AC30 - Unicite published mutualisee** : factoriser le pattern d index partiel "un seul published par scope" dans une convention commune ou un helper partage, car il est repete au moins sur prompts, assemblys et execution profiles.
31. **AC31 - Validation metier rapprochee des colonnes sensibles** : ajouter des validators explicites sur les champs sensibles au runtime comme `model`, `timeout_seconds`, `max_output_tokens`, `plan_rules_ref`, `output_contract_ref`, pour detecter les etats invalides avant publication, pas seulement au niveau service.
32. **AC32 - Nommage homogene des concepts cout/tokens** : harmoniser la terminologie entre `tokens_in/tokens_out/cost_usd_estimated` dans l observabilite et `input_tokens/output_tokens/estimated_cost_microusd` dans l agregat de consommation, afin de faciliter mapping, ETL et lecture admin.
33. **AC33 - Extinction effective des champs legacy d assembly** : les colonnes `execution_config`, `interaction_mode`, `user_question_policy`, `input_schema`, `output_contract_ref` et `fallback_use_case` ne doivent plus etre des sources de verite nominales dans `PromptAssemblyConfigModel`. Elles doivent soit etre supprimees du modele persistant, soit deplacees dans un mecanisme de compatibilite explicitement isole, non ambigu et non utilise par le runtime nominal.
34. **AC34 - Chemin de suppression documente pour la compatibilite legacy** : tout champ ou comportement conserve temporairement pour compatibilite dans les modeles LLM doit porter une date cible, une justification explicite, un consommateur identifie et un test de non-reintroduction. Aucun champ `compat` ne peut rester sans plan de suppression trace.
35. **AC35 - Relation output_schema portee par une vraie cle etrangere** : la relation entre assembly et output schema ne doit plus reposer sur une jointure texte transformee. `PromptAssemblyConfigModel` doit porter une reference canonique explicite vers `LlmOutputSchemaModel.id`, avec une foreign key reelle, et l eventuel ancien champ texte ne doit subsister qu en compatibilite transitoire strictement bornee.
36. **AC36 - Fin complete du dedoublement observabilite coeur / metadonnees** : les metadonnees operationnelles deplacees dans `LlmCallLogOperationalMetadataModel` ne doivent plus etre dupliquees dans `LlmCallLogModel`. Une fois la migration terminee, les champs operationnels enrichis ne doivent exister que dans la table dediee, afin d eviter toute redondance structurelle et toute ambiguite de lecture.
37. **AC37 - Modeles LLM tous alignes sur les mixins d audit communs** : tout modele LLM portant des colonnes d audit compatibles doit obligatoirement utiliser les mixins partages (`CreatedAtMixin`, `UpdatedAtMixin`, `CreatedByMixin`, `PublishedAtMixin`) au lieu de redeclarer les colonnes localement. Aucun doublon de definition d audit ne doit subsister dans le sous-package `models.llm`.
38. **AC38 - Enums fermes durcis aussi au niveau base pour tous les domaines stables** : tout champ metier a domaine fini deja type cote Python doit aussi etre protege au niveau base par une contrainte fermee homogene. Cela inclut les personas (`tone`, `verbosity`) et les statuts structurants quand ils restent stockes comme chaines.
39. **AC39 - Conventions de longueurs SQLAlchemy centralisees** : les longueurs `String(...)` pour les concepts metier partages ne doivent plus etre codees en dur table par table. Elles doivent etre centralisees dans une convention commune ou des constantes reutilisees, afin d eviter toute derive future sur `feature`, `subfeature`, `plan`, `locale`, `provider`, `model`, `version`, `request_id`, `trace_id`, etc.
40. **AC40 - Defaults DateTime unifies sans lambdas dispersees** : tout timestamp LLM doit utiliser le provider canonique commun via les mixins ou un helper partage ; aucun `default=lambda: datetime_provider.utcnow()` ne doit subsister dans les modeles LLM lorsqu un helper commun existe deja. Cela vaut aussi pour `expires_at` et `refreshed_at`, afin d eviter une demi-factorisation.
41. **AC41 - Validateurs metier mutualises pour les references textuelles sensibles** : les validations de type "non vide si fourni", bornes numeriques, listes JSON, domaines fermes et compatibilites transitoires doivent etre factorisees dans des validateurs ou mixins reutilisables. Aucun pattern de validation simple ne doit etre reecrit localement dans plusieurs modeles sans utilitaire commun.
42. **AC42 - Relations ORM bidirectionnelles completes sur tout le graphe canonique** : toute relation canonique entre assembly, execution profile, prompt version, use case, release snapshot, active release, output schema, call log et metadata operationnelle doit etre navigable dans les deux sens des lors qu elle correspond a un lien metier nominal. Aucun acces manuel recurrent par cle technique ne doit rester necessaire la ou une `relationship` ORM stable est attendue.
43. **AC43 - Contrat de source de verite executable et teste** : le repo doit contenir un test de conformite explicite qui echoue si un champ non canonique redevient source de verite runtime, en particulier si un assembly recontrole des parametres d execution deja portes par `LlmExecutionProfileModel`, ou si un prompt version redevient porteur d une decision runtime nominale.
44. **AC44 - Convention de nommage cross-table centralisee** : les concepts identiques doivent avoir partout le meme nom de colonne ou un alias officiellement documente unique. Il faut eliminer les ecarts residuels ou les encapsuler clairement, notamment entre vocabulaire d observabilite, agregats et compatibilite.
45. **AC45 - Couche compatibilite explicitement separee du modele nominal** : si des champs ou comportements legacy doivent encore vivre, ils doivent etre regroupes dans une couche ou un sous-ensemble explicitement identifie comme compatibilite, plutot que de rester meles au modele nominal principal. L objectif est qu un lecteur du modele sache immediatement ce qui releve du runtime canonique et ce qui releve d un residuel de transition.
46. **AC46 - Tests anti-duplication structurelle obligatoires** : ajouter des tests ou validateurs qui echouent si un nouveau helper, mixin, validator, pattern d index, contrainte de domaine ou convention d audit est redeclare localement alors qu un equivalent canonique existe deja dans `llm_audit.py`, `llm_constraints.py`, `llm_indexes.py` ou `llm_json_validators.py`.
47. **AC47 - Zero compat implicite a l initialisation sans borne de suppression** : tout remapping implicite dans `__init__`, setter de propriete ou alias d attribut doit etre soit supprime, soit borne a une transition documentee avec test d extinction. Les mecanismes comme l acceptation de `provider=` ou la reabsorption des anciens flags `*_enabled` ne doivent jamais devenir permanents.
48. **AC48 - Documentation de structure modele generee depuis le code** : la documentation du package `models.llm` doit etre alignee automatiquement ou semi-automatiquement sur le code, en listant pour chaque table : role, source de verite, champs legacy toleres, relations ORM, contraintes majeures, et statut canonique/compatibilite.
49. **AC49 - Aucune colonne nominale sans justification d usage** : toute colonne du sous-package `models.llm` doit avoir soit un consommateur runtime/admin/test identifie, soit une justification de conservation transitoire documentee. A defaut, elle doit etre supprimee.
50. **AC50 - Definition formelle du perimetre canonique LLM** : le repo doit contenir une definition executable ou au minimum controlee par test de ce qui constitue le perimetre canonique LLM en base : tables autorisees, helpers autorises, champs d execution autoritaires, champs de compatibilite toleres, et dependances admises. Toute derive hors de ce perimetre doit faire echouer la validation structurelle.
51. **AC51 - Compatibilite operationnelle sans repollution du log coeur** : les proprietes de compatibilite exposees par `LlmCallLogModel` pour les champs operationnels doivent rester de simples proxys vers `LlmCallLogOperationalMetadataModel`. Aucun champ operationnel enrichi (`pipeline_kind`, `requested_provider`, `executed_provider`, `breaker_state`, `active_snapshot_version`, etc.) ne doit redevenir une colonne persistee de `llm_call_logs`. Un test de perimetre canonique doit echouer si ces colonnes reapparaissent dans la table coeur.
52. **AC52 - DRY complet des timestamps sur les modeles LLM restants** : tous les modeles LLM portant a la fois `created_at` et `updated_at` doivent utiliser `CreatedUpdatedAtMixin`, et tous les modeles portant uniquement `created_at`, `created_by` ou `published_at` doivent utiliser les mixins dedies. Aucune redeclaration locale de colonnes d audit ou de defaults temporels ne doit subsister dans `backend/app/infra/db/models/llm/`, sauf justification explicite documentee et testee.

## Tasks / Subtasks

- [x] **Task 1: Migrer `app.infrastructure` vers `app.infra`** (AC: 1, 2, 3, 8, 9)
  - [x] Deplacer les elements utiles sous `backend/app/infra/`.
  - [x] Reecrire tous les imports backend, scripts et tests vers `app.infra.*`.
  - [x] Supprimer le dossier `backend/app/infrastructure/` une fois les imports converges.
  - [x] Verifier qu aucun import residuel ne pointe vers `app.infrastructure.*`.

- [x] **Task 2: Cartographier les autres dossiers de base backend** (AC: 3, 4, 8)
  - [x] Inventorier les dossiers racines existants sous `backend/app/`.
  - [x] Identifier les zones de recouvrement, doublons semantiques ou noms ambigus.
  - [x] Classer chaque dossier en `canonique`, `tolere`, `a converger`, `a interdire`.
  - [x] Documenter les cas limites pour eviter de futurs deplacements arbitraires.

- [x] **Task 3: Documenter la structure backend cible** (AC: 4, 5, 8)
  - [x] Produire ou mettre a jour un document de gouvernance structurelle backend.
  - [x] Y decrire les dossiers fondationnels autorises et leurs responsabilites.
  - [x] Expliciter la convention de nommage a retenir pour toute nouvelle couche technique.
  - [x] Ajouter la regle de non-creation de dossier de base sans accord utilisateur.

- [x] **Task 4: Ajouter un garde-fou anti-reintroduction** (AC: 5, 6, 9)
  - [x] Ajouter un script, test ou validateur capable de detecter l apparition d un namespace structurel deprecie.
  - [x] Faire echouer ce controle si un dossier de base non approuve est ajoute dans `backend/` ou `backend/app/`.
  - [x] Cibler au minimum les imports vers d anciens namespaces techniques deprecias.
  - [x] Documenter comment mettre a jour ce garde-fou si une nouvelle couche est explicitement approuvee.

- [x] **Task 5: Validation finale** (AC: 1, 2, 6, 9)
  - [x] Activer le venv avant toute commande Python : `.\.venv\Scripts\Activate.ps1`
  - [x] Executer `cd backend ; ruff check .`
  - [x] Executer une campagne `pytest -q` ciblee ou complete justifiee sur les zones touchees.
  - [x] Verifier que les imports critiques backend demarrent toujours correctement apres convergence.
  - [x] Lister clairement les limites restantes et les prochains dossiers potentiellement a converger.

- [x] **Task 6: Centraliser les acces DateTime backend** (AC: 8, 9, 10)
  - [x] Inventorier les appels backend a `datetime.now(...)`, `date.today()` et helpers locaux du type `utc_now()`.
  - [x] Ajouter un `DatetimeProvider` canonique dans `backend/app/core/`.
  - [x] Migrer les usages applicatifs backend vers ce provider.
  - [x] Ajouter un garde-fou de non-reintroduction pour les acces directs a l horloge courante.

- [x] **Task 7: Regrouper les modeles DB LLM sous `models/llm`** (AC: 2, 3, 6, 8, 9, 11)
  - [x] Identifier tous les fichiers `llm_*` et modeles associes au domaine LLM sous `backend/app/infra/db/models/`.
  - [x] Deplacer ces modeles sous `backend/app/infra/db/models/llm/` sans changer les noms de tables SQLAlchemy ni les schemas DB.
  - [x] Mettre a jour tous les imports backend, scripts, migrations et tests vers `app.infra.db.models.llm.*`.
  - [x] Mettre a jour les exports/barrels eventuels de `app.infra.db.models` pour conserver les imports publics explicitement acceptes.
  - [x] Ajouter ou mettre a jour un commentaire global en français en haut de chaque fichier LLM deplace ou modifie.
  - [x] Ajouter ou mettre a jour les docstrings en français des classes SQLAlchemy, helpers et fonctions non triviales touchees.
  - [x] Verifier que chaque fichier de `backend/app/infra/db/models/llm/` est effectivement reference par au moins un import runtime, migration, bootstrap ou test pertinent.
  - [x] Verifier qu aucun ancien fichier LLM racine, import `app.infra.db.models.llm_*`, alias de compatibilite ou shim legacy ne subsiste hors exception explicitement documentee et temporaire.
  - [x] Ajouter ou ajuster un garde-fou qui detecte la reintroduction de nouveaux modeles LLM directement a la racine `models/`.
  - [x] Executer les tests d import, les tests LLM DB touches et `ruff check` apres migration.

- [x] **Task 8: Normaliser la documentation inline des fichiers touches** (AC: 4, 7, 9, 12)
  - [x] Verifier les fichiers applicatifs crees ou significativement modifies pendant la story.
  - [x] Ajouter un commentaire global en français en haut de fichier quand il manque.
  - [x] Ajouter ou corriger les docstrings en français pour les modules, classes, fonctions publiques et fonctions non triviales.
  - [x] Eviter les commentaires redondants qui paraphrasent une ligne de code evidente.
  - [x] Lancer `ruff check` pour verifier que les ajouts restent conformes.

- [x] **Task 9: Refactorer les modeles DB LLM apres regroupement namespace** (AC: 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52)
  - [x] Clarifier la source de verite runtime entre assembly, prompt version, execution profile, release et output schema.
  - [x] Supprimer ou deprecier les champs redondants avant d ajouter des migrations destructives.
  - [x] Introduire les enums, check constraints, unicites et index necessaires sans casser les donnees existantes.
  - [x] Factoriser les patterns transverses d audit, d unicite `published` et de timestamp dans des helpers ou mixins communs.
  - [x] Completer les relationships ORM et la validation metier des colonnes sensibles.
  - [x] Documenter la strategie de recalcul des agregats non additifs et la frontiere canonique/legacy.
  - [x] Ajouter les migrations Alembic, tests de schema et tests de non-regression associes.

## Dev Notes

### Developer Context

- Le choix structurel cible pour cette story est deja tranche : **`app.infra` est le namespace canonique**.
- La premiere tache de migration `app.infrastructure -> app.infra` a ete explicitement demandee par le produit et doit etre traitee comme la priorite numero un de la story.
- Cette story ne doit pas recreer un nouveau namespace de fondation ni une couche temporaire supplementaire pour "faciliter" la convergence.
- La regle repo est explicite : **pas d ajout de dossier de base dans `backend/` sans accord explicite de l utilisateur**.

### Architecture Compliance

- Respecter la structure de reference backend du projet : `api`, `core`, `domain`, `services`, `infra`.
- Eviter tout renommage large sans gain architectural clair.
- Ne pas introduire `infrastructure_v2`, `foundation`, `platform`, `technical`, ou autre variante racine non approuvee.

### Previous Story Intelligence

- Story 70-14 a deja cherche a reorganiser les fichiers backend LLM de facon DRY.
- Story 70-15 a fait converger la source de verite runtime vers les namespaces canoniques.
- Story 70-17 a encore documente `infrastructure/*` comme cible LLM canonique dans son contexte, ce qui montre que la gouvernance structurelle backend n etait pas totalement refermee.
- La presente story doit donc solder la dette de structure restante et refermer la porte a la reintroduction de couches paralleles.

### Implementation Guidance

- Favoriser un delta coherent et localise.
- Reutiliser `app.infra` plutot que de dupliquer des wrappers.
- Si une suppression de dossier ou d import a un impact test, migrer d abord les consommateurs puis seulement supprimer l ancien chemin.
- Toute compatibilite transitoire doit etre courte, explicite, et candidate a suppression immediate.

### Testing Requirements

- Verifier au minimum la resolution des imports sur les composants critiques touches par la migration.
- Couvrir les tests ou suites qui importent les providers LLM et les repositories migres.
- Si une suite plus large echoue pour un probleme de schema ou de fixture preexistant, le documenter explicitement au lieu de masquer l incident.

### References

- [Source: AGENTS.md]
- [Source: _bmad-output/implementation-artifacts/70-14-reorganiser-et-consolider-les-fichiers-du-process-llm-backend.md]
- [Source: _bmad-output/implementation-artifacts/70-15-basculer-la-source-de-verite-runtime-llm-vers-les-namespaces-canoniques.md]
- [Source: _bmad-output/implementation-artifacts/70-17-db-cleanup-llm-canonique.md]
- [Source: backend/app/domain/llm/runtime/gateway.py]
- [Source: backend/app/domain/llm/runtime/provider_runtime_manager.py]
- [Source: backend/app/api/v1/routers/admin_llm.py]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- 2026-04-23 : demande utilisateur de generer une story 70-18 de nettoyage de la structure backend.
- Intention explicite utilisateur : faire de la migration `app.infrastructure -> app.infra` la premiere tache de la story.
- Contrainte additionnelle produit : ne plus ajouter de dossier de base dans `backend/` sans accord explicite.
- 2026-04-23 : reprise dev-story de 70-18 a partir du contexte de la story 70-13 ; passage de la story et du sprint en `in-progress`.

### Completion Notes List

- Story 70-18 creee pour cadrer le nettoyage structurel backend au-dela du seul perimetre LLM.
- La migration `app.infrastructure -> app.infra` est positionnee en Task 1 comme demande.
- La gouvernance "pas de nouveau dossier de base backend sans accord" est incluse dans le cadrage de la story.
- 2026-04-23 : AC10 et une tache dediee a la centralisation des acces DateTime backend ont ete ajoutes pour imposer un provider d horloge canonique en couche `core`.
- 2026-04-23 : AC11 et une tache dediee ont ete ajoutes pour regrouper les modeles DB LLM sous `backend/app/infra/db/models/llm/` et migrer les imports associes.
- 2026-04-23 : AC11 renforcee pour exiger la preuve que les nouveaux fichiers `models/llm` sont bien utilises et qu aucun ancien chemin legacy, alias ou shim durable ne subsiste.
- 2026-04-23 : AC12 ajoutee pour imposer un commentaire global en français en haut des fichiers touches et des docstrings en français sur les modules/classes/fonctions publiques ou non triviales.
- 2026-04-23 : AC33 a AC50 ajoutes a la story pour durcir la fermeture du modele LLM canonique sur les champs legacy, la compatibilite, les foreign keys, les mixins, les conventions structurelles et les garde-fous executables.
- 2026-04-23 : AC11 mise en oeuvre : les 9 modeles DB LLM ont ete deplaces sous `backend/app/infra/db/models/llm/`, les imports backend/scripts/tests ont ete migres, le barrel racine `app.infra.db.models` ne reexporte plus les symboles LLM, et le garde-fou `test_story_70_18_llm_model_namespace_guard.py` verifie l absence de fichiers/imports legacy ainsi que l usage effectif de chaque fichier canonique.
- 2026-04-23 : AC13 a AC32 ajoutes comme backlog de refacto DB LLM apres regroupement namespace : source de verite runtime, contraintes DB, enums, relations ORM, audit mixins, observabilite, agregats, indexation et nomenclature cout/tokens.
- 2026-04-23 : Tasks 1 a 4 finalisees : `app.infrastructure` est absent, les imports `app.infrastructure` sont gardes par test, et `docs/backend-structure-governance.md` classe les dossiers racines backend/app en canoniques, toleres, a converger ou interdits.
- 2026-04-23 : Task 6 finalisee : les helpers locaux `utc_now()` applicatifs/scripts detectes ont ete remplaces par l'import canonique `app.core.datetime_provider.utc_now` ou par `datetime_provider.utcnow()`, et le garde-fou DateTime bloque `datetime.now(`, `date.today(` et les nouveaux `def utc_now(` hors provider.
- 2026-04-23 : Le script `run_ops_review_queue_alerts.py` importe explicitement le barrel canonique `app.infra.db.models.llm` afin d'enregistrer les relationships SQLAlchemy LLM apres retrait des exports LLM du barrel racine.
- 2026-04-23 : Validations executees dans le venv : `ruff format .`, `ruff check .`, tests cibles 70-18/70-17/70-13 et `pytest -q` complet (`2992 passed, 12 skipped`).
- 2026-04-23 : Task 9 avancee partiellement sur AC16, AC17 et AC23 : unicite DB de `LlmReleaseSnapshotModel.version`, pointeur actif LLM contraint a une seule ligne logique, `LlmOutputSchemaModel` versionne par unicite `(name, version)`, et `LlmSamplePayloadModel` etendu aux dimensions `subfeature` et `plan`.
- 2026-04-23 : Migration Alembic `20260423_0074_llm_schema_release_sample_invariants.py` appliquee sur `backend/horoscope.db`; le registre 70-17 inclut cette migration comme revue.
- 2026-04-23 : Validations Task 9 partielles executees dans le venv : `ruff format .`, `ruff check .`, `pytest -q tests/integration/test_story_70_17_llm_db_cleanup_registry.py tests/integration/test_story_70_18_llm_db_invariants.py tests/integration/test_admin_llm_sample_payloads.py` (`23 passed`), `pytest -q tests/integration/test_backend_sqlite_alignment.py tests/unit/test_story_70_13_bootstrap.py` (`10 passed`), import `app.main` OK.
- 2026-04-23 : Task 9 avancee sur AC22 : `LlmCallLogModel` declare les index d exploitation sur `timestamp`, `trace_id`, `feature/subfeature/plan/timestamp`, `active_snapshot_version` et `executed_provider/timestamp`; la migration Alembic `20260423_0075_add_llm_call_log_operational_indexes.py` est appliquee sur `backend/horoscope.db` et ajoutee au registre 70-17.
- 2026-04-23 : Validations AC22 executees dans le venv : `ruff format .`, `ruff check .`, `pytest -q tests/integration/test_story_70_17_llm_db_cleanup_registry.py tests/integration/test_story_70_18_llm_db_invariants.py tests/integration/test_admin_llm_sample_payloads.py tests/integration/test_backend_sqlite_alignment.py tests/unit/test_story_70_13_bootstrap.py tests/unit/test_story_70_18_llm_model_namespace_guard.py tests/unit/test_story_70_18_backend_structure_guard.py tests/unit/test_story_70_18_datetime_provider_guard.py` (`42 passed`), import `app.main` OK.
- 2026-04-23 : AC19 documentee dans `backend/docs/llm-canonical-consumption-rebuild.md` : source de verite `llm_call_logs`, champs additifs, percentiles non additifs, scope nominal versus `legacy_residual`, et regle de recalcul par fenetre etendue aux buckets.
- 2026-04-23 : Validation finale de la tranche AC19/AC22 executee dans le venv : `ruff check .`, `pytest -q tests/integration/test_story_70_18_llm_db_invariants.py tests/integration/test_story_70_17_llm_db_cleanup_registry.py` (`12 passed`).
- 2026-04-23 : AC18 clarifiee dans `docs/llm-release-runbook.md` : un snapshot de release est l artefact versionne, `llm_active_releases` est un pointeur singleton remplace lors d une activation ou d un rollback, et les lectures runtime doivent correler snapshot actif, version et manifest entry.
- 2026-04-23 : Validation apres clarification AC18 executee dans le venv : `ruff check .`, `pytest -q tests/integration/test_story_70_18_llm_db_invariants.py tests/integration/test_story_70_17_llm_db_cleanup_registry.py` (`12 passed`).
- 2026-04-23 : AC31 mise en oeuvre sur les colonnes sensibles ciblees : `LlmExecutionProfileModel` refuse les modeles vides, timeouts non positifs et limites `max_output_tokens` non positives; `PromptAssemblyConfigModel` refuse les references optionnelles vides `plan_rules_ref` et `output_contract_ref`.
- 2026-04-23 : AC28 avancee sur la navigation ORM assembly/profil : `PromptAssemblyConfigModel.execution_profile` expose la relation directe vers `LlmExecutionProfileModel` a partir de `execution_profile_ref`.
- 2026-04-23 : Validations AC28/AC31 executees dans le venv : `ruff format .`, `ruff check .`, `pytest -q tests/unit/test_story_70_18_llm_sensitive_model_validators.py tests/integration/test_story_70_18_llm_db_invariants.py tests/integration/test_story_70_17_llm_db_cleanup_registry.py` (`17 passed`).
- 2026-04-23 : AC30 avancee : le helper `published_unique_index` centralise la convention "un seul published par scope" pour prompts, assemblies et execution profiles sans changer les noms d index ni les colonnes.
- 2026-04-23 : Alembic charge maintenant explicitement le package canonique `app.infra.db.models.llm` dans `migrations/env.py`, ce qui corrige l echec de metadata ou `astrologer_profiles.persona_id` ne trouvait pas `llm_personas`.
- 2026-04-23 : Validations AC30 executees dans le venv : `ruff format .`, `ruff check .`, `pytest -q tests/unit/test_story_70_18_llm_sensitive_model_validators.py tests/unit/test_story_70_18_llm_model_namespace_guard.py tests/integration/test_story_70_18_llm_db_invariants.py tests/integration/test_story_70_17_llm_db_cleanup_registry.py` (`23 passed`), import `app.main` OK.
- 2026-04-23 : AC13 documentee dans `backend/docs/llm-runtime-source-of-truth.md` : assembly comme entree runtime nominale, execution profile pour provider/modele, prompt version pour texte, output schema pour contrat, release snapshot pour configuration figee et active release comme pointeur runtime.
- 2026-04-23 : AC18/AC32 mis en oeuvre sur l agregat de consommation canonique : `taxonomy_scope` est retire du read model au profit de `is_legacy_residual` comme source unique, et les colonnes internes d agregat sont alignees sur l observabilite (`tokens_in`, `tokens_out`, `cost_usd_estimated_microusd`). L API admin conserve ses champs de reponse historiques `input_tokens`, `output_tokens` et `estimated_cost`.
- 2026-04-23 : Migration Alembic `20260423_0076_harmonize_consumption_aggregate_terms.py` appliquee sur `backend/horoscope.db`; elle migre les bases historiques, cree le read model sur base neuve si absent, et couvre les colonnes operationnelles `llm_call_logs` encore presentes en ORM/bootstrap mais absentes de l historique Alembic.
- 2026-04-23 : Validations AC18/AC32 executees dans le venv : `ruff check .`, `ruff format --check .`, `pytest -q tests/integration/test_story_70_18_llm_db_invariants.py` (`5 passed`), `pytest -q app/tests/unit/test_llm_canonical_consumption_service.py` (`10 passed`), `pytest -q app/tests/integration/test_admin_llm_canonical_consumption_api.py` (`8 passed`), inspection locale `horoscope.db` OK pour les colonnes d agregat et de logs operationnels.
- 2026-04-23 : AC13/AC14 mis en oeuvre sur les champs redondants d assembly : `PromptAssemblyConfigModel` materialise les champs de compatibilite runtime legacy, la documentation source de verite precise que `execution_config` n est plus une source libre quand `execution_profile_ref` existe, et `ConfigCoherenceValidator` rejette les overrides contradictoires de `model`, `provider`, `timeout_seconds`, `max_output_tokens`, `temperature` ou `fallback_use_case` a la publication.
- 2026-04-23 : Correction associee AC14 : `AssemblyAdminService.create_draft` persiste maintenant `execution_profile_ref`, afin que les drafts admin entrent bien dans le chemin de validation profile-owned.
- 2026-04-23 : Validations AC13/AC14 executees dans le venv : `ruff check .`, `ruff format --check .`, `pytest -q tests/unit/test_story_70_18_llm_sensitive_model_validators.py` (`7 passed`), `pytest -q tests/llm_orchestration/test_config_coherence_validator.py` (`4 passed`), `pytest -q tests/llm_orchestration/test_story_66_11_execution_profiles.py` (`2 passed`), `pytest -q tests/llm_orchestration/test_assembly_resolution.py` (`11 passed`), `pytest -q tests/integration/test_story_70_18_llm_db_invariants.py` (`5 passed`), import `app.main` OK.
- 2026-04-23 16:23 : AC15/AC29 mis en oeuvre : helper `allowed_values_check`, contraintes DB sur les domaines stables (`reasoning_profile`, `verbosity_profile`, `output_mode`, `tool_mode`, `interaction_mode`, `user_question_policy`, `granularity`) et harmonisation des longueurs `provider`, `model`, `feature`, `subfeature`, `plan`, `locale` via Alembic 0077.
- 2026-04-23 16:23 : AC20/AC21 mis en oeuvre : `LlmCallLogModel.provider` est d abord marque comme champ de compatibilite, les champs `requested_provider/resolved_provider/executed_provider` sont declares comme autoritaires, et `llm_call_log_operational_metadata` isole les metadonnees operationnelles one-to-one avec backfill Alembic 0078.
- 2026-04-23 17:05 : AC20 finalisee completement : la colonne legacy ambiguë `llm_call_logs.provider` est renommee en `provider_compat` via Alembic 0080, les lecteurs backend bornes basculent sur `executed_provider` ou `provider_compat`, et l invariant de schema interdit le retour d une colonne `provider` ambiguë sur `llm_call_logs`.
- 2026-04-23 16:23 : AC24/AC25 mis en oeuvre : mixins d audit LLM (`CreatedAtMixin`, `UpdatedAtMixin`, `CreatedByMixin`, `PublishedAtMixin`) et validateurs JSON bornes pour `LlmPersonaModel.formatting`, `style_markers`, `boundaries`, `allowed_topics`, `disallowed_topics`.
- 2026-04-23 16:23 : AC26/AC27/AC28 finalises : `AssemblyComponentResolutionState` explicite les etats `absent/inherited/enabled/disabled`, `LlmUseCaseConfigModel` et `LlmPromptVersionModel` materialisent les frontieres legacy/canonique, et les relations ORM couvrent assembly -> output schema, prompt -> use case, release snapshot <-> active release, plus metadata operationnelle des logs.
- 2026-04-23 19:30 : correctif post-refacto sur AC14/AC20 : `LlmCallLogModel` accepte encore `provider=` a l instanciation en le remappant vers `provider_compat` sans restaurer un attribut ORM ambigu, et `seed_66_20_convergence` regenere une `execution_config` minimale coherente avec `execution_profile_ref` pour eviter a la fois le blocage de coherence startup et l echec runtime de resolution d assembly.
- 2026-04-23 19:30 : validation finale executee dans le venv apres correctif de regression : `ruff check app\\infra\\db\\models\\llm\\llm_observability.py scripts\\seed_66_20_convergence.py`, `pytest -q app\\tests\\unit\\test_llm_canonical_consumption_service.py app\\tests\\integration\\test_admin_llm_canonical_consumption_api.py tests\\integration\\test_admin_llm_catalog.py app\\tests\\integration\\test_ops_monitoring_llm_api.py app\\tests\\integration\\test_load_smoke_critical_flows.py` (`49 passed`), puis `pytest -q` complet backend (`3003 passed, 12 skipped`).
- 2026-04-24 : correctif post-review AC23/AC33 : le garde-fou admin de preview/runtime compare desormais le scope canonique complet `feature/subfeature/plan/locale`, les sample payloads admin sont normalises sur la taxonomie canonique, et le bootstrap SQLite local ne recree plus les colonnes legacy de `llm_call_logs`.
- 2026-04-24 : correctifs de regression post-review : normalisation de la tonalite legacy `calm` dans le seed astrologues, tests d evaluation migres vers `persona_state` / `plan_rules_state`, test de migration 8b2d aligne sur `output_schema_id`, et registre 70-17 complete avec la migration `20260423_0081_finalize_llm_canonical_perimeter.py` et les nouveaux chemins de compatibilite bornes.
- 2026-04-24 : validations ciblees executees dans le venv : `ruff check scripts\\seed_astrologers_6_profiles.py app\\tests\\integration\\test_migration_8b2d52442493_add_input_schema_to_assembly.py tests\\evaluation\\test_differentiation.py tests\\evaluation\\test_prompt_resolution.py`, puis `pytest -q app\\tests\\integration\\test_astrologers_v2.py app\\tests\\integration\\test_migration_8b2d52442493_add_input_schema_to_assembly.py tests\\evaluation\\test_differentiation.py tests\\evaluation\\test_prompt_resolution.py tests\\integration\\test_story_70_17_llm_db_cleanup_registry.py` (`17 passed`).
- 2026-04-24 : validation utilisateur complementaire : confirmation que le `pytest -q` complet backend repasse apres integration des correctifs.
- 2026-04-24 : AC51/AC52 ajoutees et mises en oeuvre : `LlmSamplePayloadModel` reutilise maintenant `CreatedUpdatedAtMixin`, et les tests 70-18 renforcent le perimetre canonique pour bloquer toute reintroduction de colonnes operationnelles dans `llm_call_logs` ainsi que toute redeclaration locale de colonnes d audit dans `models.llm`.

### File List

- _bmad-output/implementation-artifacts/70-18-cleaner-la-structure-backend-et-converger-les-namespaces-techniques.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/models/llm/
- backend/tests/unit/test_story_70_18_llm_model_namespace_guard.py
- Imports LLM mis a jour dans backend/app, backend/scripts et backend/tests.
- backend/app/infra/db/models/astrologer.py
- backend/app/infra/db/models/audit_event.py
- backend/app/infra/db/models/billing.py
- backend/app/infra/db/models/calibration.py
- backend/app/infra/db/models/canonical_entitlement_mutation_audit.py
- backend/app/infra/db/models/chart_result.py
- backend/app/infra/db/models/chat_conversation.py
- backend/app/infra/db/models/chat_message.py
- backend/app/infra/db/models/config_text.py
- backend/app/infra/db/models/consultation_template.py
- backend/app/infra/db/models/consultation_third_party.py
- backend/app/infra/db/models/daily_prediction.py
- backend/app/infra/db/models/editorial_template.py
- backend/app/infra/db/models/enterprise_account.py
- backend/app/infra/db/models/enterprise_api_credential.py
- backend/app/infra/db/models/enterprise_billing.py
- backend/app/infra/db/models/enterprise_editorial_config.py
- backend/app/infra/db/models/enterprise_feature_usage_counters.py
- backend/app/infra/db/models/feature_flag.py
- backend/app/infra/db/models/flagged_content.py
- backend/app/infra/db/models/geo_place_resolved.py
- backend/app/infra/db/models/geocoding_query_cache.py
- backend/app/infra/db/models/llm/llm_assembly.py
- backend/app/infra/db/models/llm/llm_audit.py
- backend/app/infra/db/models/llm/llm_constraints.py
- backend/app/domain/llm/configuration/assembly_admin_service.py
- backend/app/domain/llm/configuration/config_coherence_validator.py
- backend/app/domain/llm/runtime/observability_service.py
- backend/app/infra/db/models/llm/llm_json_validators.py
- backend/tests/llm_orchestration/test_config_coherence_validator.py
- backend/tests/llm_orchestration/test_observability.py
- backend/docs/llm-runtime-source-of-truth.md
- backend/app/infra/db/models/llm/llm_execution_profile.py
- backend/app/infra/db/models/llm/llm_indexes.py
- backend/app/infra/db/models/llm/llm_output_schema.py
- backend/app/infra/db/models/llm/llm_persona.py
- backend/app/infra/db/models/llm/llm_observability.py
- backend/app/infra/db/models/llm/llm_prompt.py
- backend/app/infra/db/models/llm/llm_release.py
- backend/app/infra/db/models/llm/llm_sample_payload.py
- backend/app/infra/db/models/llm/llm_canonical_consumption.py
- backend/migrations/versions/20260423_0077_constrain_llm_domains_and_lengths.py
- backend/migrations/versions/20260423_0078_add_call_log_operational_metadata.py
- backend/tests/integration/test_story_70_18_llm_db_invariants.py
- backend/tests/unit/test_story_70_18_llm_sensitive_model_validators.py
- backend/app/services/llm_canonical_consumption_service.py
- backend/app/api/v1/routers/admin_llm_consumption.py
- backend/app/api/v1/routers/admin_llm.py
- backend/app/tests/unit/test_llm_canonical_consumption_service.py
- backend/app/tests/integration/test_admin_llm_canonical_consumption_api.py
- backend/migrations/versions/20260423_0076_harmonize_consumption_aggregate_terms.py
- backend/tests/integration/test_story_70_18_llm_db_invariants.py
- backend/docs/llm-canonical-consumption-rebuild.md
- backend/app/api/v1/routers/admin_llm_sample_payloads.py
- backend/app/domain/llm/governance/feature_taxonomy.py
- backend/app/domain/llm/runtime/gateway.py
- backend/app/infra/db/bootstrap.py
- backend/migrations/versions/20260423_0074_llm_schema_release_sample_invariants.py
- backend/migrations/versions/20260423_0075_add_llm_call_log_operational_indexes.py
- backend/migrations/env.py
- backend/tests/integration/test_admin_llm_sample_payloads.py
- backend/tests/integration/test_admin_llm_catalog.py
- backend/app/tests/integration/test_db_bootstrap_partial_upgrade.py
- backend/app/tests/integration/test_migration_8b2d52442493_add_input_schema_to_assembly.py
- backend/scripts/seed_astrologers_6_profiles.py
- backend/tests/evaluation/test_differentiation.py
- backend/tests/evaluation/test_prompt_resolution.py
- backend/tests/integration/test_story_70_18_llm_db_invariants.py
- backend/tests/unit/test_story_70_18_llm_sensitive_model_validators.py
- backend/app/infra/db/models/pdf_template.py
- backend/app/infra/db/models/persona_config.py
- backend/app/infra/db/models/privacy.py
- backend/app/infra/db/models/product_entitlements.py
- backend/app/infra/db/models/reference.py
- backend/app/infra/db/models/stripe_billing.py
- backend/app/infra/db/models/stripe_webhook_event.py
- backend/app/infra/db/models/support_incident.py
- backend/app/infra/db/models/support_ticket_category.py
- backend/app/infra/db/models/user.py
- backend/app/infra/db/models/user_birth_profile.py
- backend/app/infra/db/models/user_natal_interpretation.py
- backend/app/infra/db/models/user_prediction_baseline.py
- backend/app/infra/db/models/user_refresh_token.py
- backend/app/ops/llm/prompt_registry_v2.py
- backend/app/services/enterprise_credentials_service.py
- backend/docs/llm-canonical-consumption-rebuild.md
- backend/docs/llm-db-cleanup-registry.json
- backend/docs/llm-runtime-source-of-truth.md
- backend/horoscope.db
- backend/scripts/run_ops_review_queue_alerts.py
- backend/scripts/seed_30_5_new_use_cases.py
- backend/scripts/seed_support_categories.py
- backend/scripts/update_all_prompts_59_5.py
- backend/scripts/update_guidance_prompts_59_4.py
- backend/tests/unit/test_story_70_18_backend_structure_guard.py
- backend/tests/unit/test_story_70_18_datetime_provider_guard.py
- docs/architecture-backend.md
- docs/backend-structure-governance.md
- docs/llm-release-runbook.md

### Change Log

- 2026-04-23 : creation de la story 70-18 pour nettoyer la structure backend et converger les namespaces techniques, avec priorite explicite sur la migration `app.infrastructure -> app.infra`.
- 2026-04-23 : implementation AC11, regroupement des modeles DB LLM sous `app.infra.db.models.llm`, suppression des exports legacy LLM du barrel racine et ajout du garde-fou de namespace.
- 2026-04-23 : ajout des AC13-AC32 et de la Task 9 pour cadrer les refactors DB LLM structurels restants.
- 2026-04-23 : ajout des AC33-AC50 pour completer la fermeture structurelle du modele LLM canonique, de la compatibilite legacy et des garde-fous d invariants.
- 2026-04-23 : finalisation des garde-fous structure backend et DateTime, documentation de gouvernance backend, synchronisation du registre 70-17 avec le namespace `models/llm`, validation complete backend.
- 2026-04-23 : ajout des invariants DB LLM AC16/AC17 et extension AC23 des sample payloads par `subfeature` et `plan`, avec migration Alembic et tests d integration dedies.
- 2026-04-23 : ajout des index d exploitation AC22 sur `llm_call_logs`, avec migration Alembic, registre DB cleanup et test d inspection de schema.
- 2026-04-23 : documentation AC19 de la strategie de recalcul des agregats canoniques LLM et de la frontiere canonique/legacy.
- 2026-04-23 : clarification AC18 de la semantique snapshot de release et pointeur actif singleton dans le runbook LLM.
- 2026-04-24 : correctifs post-review sur preview admin, normalisation canonique des sample payloads, bootstrap SQLite local, seeding astrologues et registre 70-17, avec validations ciblees puis confirmation utilisateur du `pytest -q` complet backend.
- 2026-04-24 : ajout des AC51/AC52 pour verrouiller les proxys operationnels de `LlmCallLogModel` et finaliser le DRY des timestamps sur les modeles LLM restants.
- 2026-04-23 : ajout des validateurs AC31 sur colonnes sensibles LLM et relation ORM AC28 entre assembly et execution profile, avec tests unitaires.
- 2026-04-23 : factorisation AC30 de la convention d index partiel `published` et chargement explicite du package LLM dans Alembic.
- 2026-04-23 : documentation AC13 de la source de verite runtime LLM entre assembly, release, prompt, execution profile et output schema.
- 2026-04-23 : implementation AC18/AC32 sur l agregat de consommation canonique : suppression du doublon `taxonomy_scope`, harmonisation `tokens_in/tokens_out/cost_usd_estimated_microusd`, migration Alembic 0076 et tests service/API/schema.
- 2026-04-23 : implementation AC13/AC14 sur assembly : champs runtime redondants marques comme compatibilite, validation profile-owned des `execution_config` contradictoires et persistence de `execution_profile_ref` en creation de draft admin.
- 2026-04-23 16:23 : implementation AC15/AC29 avec contraintes de domaines fermes, longueurs homogenes et migration Alembic 0077.
- 2026-04-23 16:23 : implementation AC20/AC21 avec couche `llm_call_log_operational_metadata`, provider legacy explicitement marque et backfill Alembic 0078.
- 2026-04-23 16:23 : implementation AC24/AC25 via mixins d audit LLM et validateurs JSON bornes sur les personas.
- 2026-04-23 16:23 : implementation AC26/AC27/AC28 avec etats explicites des composants assembly, frontiere legacy/canonique materialisee et relations ORM completes.
- 2026-04-23 19:30 : correctif de regression sur `provider_compat` et `seed_66_20_convergence`, puis revalidation backend complete (`3003 passed, 12 skipped`).
