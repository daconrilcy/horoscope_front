# Story 70.17: Assainir la base de donnees LLM apres la convergence backend canonique

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want nettoyer, figer, archiver puis supprimer les objets DB LLM superflus, ambigus ou legacy,
so that la base reflete strictement la verite runtime canonique post-70-15 et ne conserve plus de source de verite implicite ou contradictoire.

## Contexte

La story 70-15 a converge le runtime LLM vers les namespaces canoniques `application/llm`, `domain/llm`, `infrastructure/*` et `ops/llm`. L audit post-story confirme que la source de verite nominale visee est desormais :

- `PromptAssemblyConfigModel` pour la taxonomie `feature / subfeature / plan / locale` et la composition publiee ;
- `LlmExecutionProfileModel` pour les decisions provider / model / timeout / fallback profile ;
- `LlmPersonaModel` et `LlmOutputSchemaModel` pour les artefacts versionnes ;
- `LlmReleaseSnapshotModel` + `LlmActiveReleaseModel` pour la release active ;
- `LlmCallLogModel` et `LlmCanonicalConsumptionAggregateModel` pour l observabilite et la consommation canoniques.

En revanche, la base et certains consommateurs applicatifs conservent encore des objets hybrides ou des colonnes de compatibilite qui peuvent continuer a jouer implicitement un role de source de verite legacy :

- `llm_use_case_configs` et plusieurs usages `use_case` restent vivants dans `backend/app/main.py`, `backend/app/api/v1/routers/admin_ai.py`, `backend/app/ai_engine/*` et certains tests ;
- `llm_prompt_versions` porte encore des colonnes runtime historiques (`model`, `temperature`, `max_output_tokens`, `fallback_use_case_key`, `reasoning_effort`, `verbosity`) alors que les decisions nominales doivent venir des execution profiles ;
- `llm_call_logs.use_case` et `admin_exports.py` exposent encore des champs de compatibilite (`use_case_compat`) utiles a la transition mais dangereux si on les laisse redevenir normatifs ;
- `PromptAssemblyConfigModel.fallback_use_case` et les seeds startup autour de `seed_use_cases()` indiquent que la convergence logique n est pas encore entierement traduite en convergence de schema et de donnees.

Le cleanup attendu n est donc pas un simple menage Alembic. Il doit prouver, objet par objet, ce qui reste canonique, ce qui doit etre gele, ce qui doit etre archive, et ce qui peut etre supprime sans casser runtime, admin, ops, replay, exports ou analytics.

La story 70-16 devient ici un prerequis operable important : elle a deja introduit une documentation pipeline post-70-15, un utilisateur de test canonique, des routes QA internes et une recette backend pour rejouer guidance/chat/natal/horoscope daily. Ces actifs doivent etre reutilises dans 70-17 comme surface de validation executee pour etablir la preuve de non-usage, et non ignores au profit d un simple scan statique.

## Objectif

Produire et executer un plan de cleanup DB LLM qui :

- inventorie exhaustivement le perimetre DB LLM ;
- classe chaque objet `keep / migrate / freeze / archive / drop` ;
- neutralise les ecritures legacy avant tout drop ;
- archive les donnees a valeur d audit ou d historique ;
- supprime seulement les objets prouves inutilises ;
- introduit des garde-fous anti-reintroduction.

## Acceptance Criteria

1. **AC1 - Registre de cleanup exhaustif versionne** : un registre de cleanup DB LLM est ajoute au depot. Pour chaque table, colonne structurante, index, contrainte, vue ou objet annexe du perimetre LLM, il documente le role historique, le role cible, les lecteurs connus, les writers connus, le statut d usage (`nominal`, `legacy`, `unused`, `unknown`), la decision cible (`keep`, `migrate`, `freeze`, `archive`, `drop`) et la justification.
2. **AC2 - Inventaire aligne sur le perimetre reel** : le registre couvre au minimum `llm_use_case_configs`, `llm_prompt_versions`, `llm_output_schemas`, `llm_personas`, `llm_assembly_configs`, `llm_execution_profiles`, `llm_release_snapshots`, `llm_active_releases`, `llm_call_logs`, `llm_replay_snapshots`, `llm_canonical_consumption_aggregates`, `llm_sample_payloads`, ainsi que leurs index et colonnes de compatibilite sensibles.
3. **AC3 - Aucune suppression sans preuve de non-usage** : aucun objet DB n est supprime tant que son absence d usage n est pas demontree par un faisceau de preuves documente dans le registre, couvrant au minimum : analyse statique des lecteurs/writers dans le code et les scripts, revue des surfaces admin/ops/replay/export/analytics, et validation executee des flux runtime/admin impactes.
4. **AC4 - Gel des ecritures legacy avant drop** : les chemins d ecriture vers les objets ou colonnes legacy non cibles sont neutralises avant toute suppression physique. Pour les familles canoniques, il n existe plus de nouvelle ecriture contradictoire dans les structures legacy.
5. **AC5 - Distinction explicite freeze / archive / drop** : le plan d assainissement separe clairement le gel logique, l archivage des donnees a conserver et la suppression physique. Aucune migration ne melange redirection metier, copie archive et drop final sans tracabilite claire.
6. **AC6 - Preservation des historiques utiles** : toute table ou colonne legacy portant une valeur d audit, de replay, de troubleshooting, de release history ou de reporting est archivee ou preservee avec justification avant suppression. Le lien entre l objet source et l archive est documente.
7. **AC7 - Realignement de la verite DB sur le runtime canonique** : a l issue du chantier, les decisions runtime nominales ne reposent plus sur des objets `use_case` legacy ou sur des colonnes provider/model/fallback redondantes hors `execution_profile`, `assembly`, `release snapshot` et gouvernance canonique.
8. **AC8 - Lectures critiques admin / ops realignees** : les surfaces critiques `admin_llm.py`, `admin_ai.py`, `admin_exports.py`, `admin_llm_release.py`, `admin_llm_assembly.py`, `admin_llm_consumption.py`, `llm_canonical_consumption_service.py` et `llm_ops_monitoring_service.py` lisent les objets canoniques ou des compatibilites explicitement bornees ; aucune lecture critique ne depend d un objet classe `drop`.
9. **AC9 - Migrations de cleanup ciblees, ordonnees et reversibles** : chaque migration Alembic de drop est petite, lisible et reversible autant que possible. Elle liste explicitement les objets supprimes, la raison metier/technique, la preuve de non-usage, le lien vers l archive eventuelle et la strategie de rollback. Aucun drop ne peut etre introduit avant la convergence logique et le gel des ecritures correspondants.
10. **AC10 - Aucun objet `unknown` supprime** : tout objet encore classe `unknown` dans le registre bloque toute suppression physique le concernant.
11. **AC11 - Garde-fou anti-reintroduction des lectures legacy** : un controle automatise detecte toute nouvelle lecture nominale d un objet ou champ classe `drop` ou `freeze`, en particulier autour de `use_case`, `fallback_use_case_key`, `fallback_use_case`, `use_case_compat` et des dependances DB legacy LLM.
12. **AC12 - Garde-fou anti-reintroduction des ecritures legacy** : un controle automatise detecte toute nouvelle ecriture nominale dans un objet legacy interdit.
13. **AC13 - Garde-fou anti-derive schema/migrations** : un controle automatise detecte toute nouvelle migration LLM introduisant un objet, champ ou compatibilite non classes dans le registre de cleanup.
14. **AC14 - Documentation de gouvernance post-cleanup** : la documentation backend LLM de reference explique quelles tables/colonnes restent sources de verite, quelles compatibilites sont encore tolerees, comment un futur changement DB LLM doit etre classe dans le registre, et pourquoi `DROP` ne doit jamais preceder la convergence logique.
15. **AC15 - Validation locale obligatoire** : la story est terminee seulement si les validations backend passees dans le venv sont executees et tracees (`ruff format .`, `ruff check .`, `pytest -q` ou suites ciblees justifiees), avec couverture des garde-fous, des migrations de cleanup et des flux runtime/admin touches.

## Tasks / Subtasks

- [ ] **Task 1: Produire le registre de cleanup DB LLM** (AC: 1, 2, 10, 13)
  - [ ] Inventorier les tables, colonnes structurantes, index, contraintes et vues du perimetre LLM.
  - [ ] Ajouter pour chaque objet son role historique, son role cible et sa classification `nominal / legacy / unused / unknown`.
  - [ ] Distinguer explicitement `keep / migrate / freeze / archive / drop`.
  - [ ] Versionner ce registre dans le depot a un emplacement stable cote backend/docs ou ops.

- [ ] **Task 2: Cartographier les dependances code -> DB** (AC: 1, 3, 8, 10)
  - [ ] Scanner backend/app, backend/scripts et backend/tests pour les lecteurs et writers des objets LLM.
  - [ ] Documenter explicitement les dependances autour de `llm_use_case_configs`, `llm_prompt_versions`, `llm_call_logs.use_case`, `admin_exports.use_case_compat`, `PromptAssemblyConfigModel.fallback_use_case` et des seeds `seed_use_cases()`.
  - [ ] Revoir les routeurs admin/ops, les scripts release/replay/eval et les exports CSV.
  - [ ] Marquer `unknown` tout objet ou colonne dont l usage n est pas prouve.

- [ ] **Task 3: Classifier et prioriser les convergences logiques** (AC: 4, 5, 7, 8)
  - [ ] Identifier les colonnes runtime redondantes a migrer hors `llm_prompt_versions`.
  - [ ] Identifier les objets `use_case` strictement legacy a geler, conserver temporairement ou supprimer.
  - [ ] Definir les cas ou une compatibilite reste autorisee, avec borne explicite et critere de suppression.
  - [ ] Produire un plan par lots ordonnes : convergence logique -> archive -> drop.

- [ ] **Task 4: Geler les ecritures legacy** (AC: 4, 7, 12)
  - [ ] Neutraliser les ecritures applicatives nominales vers les objets / colonnes legacy non cibles.
  - [ ] Ajouter si necessaire des garde-fous applicatifs ou validateurs startup/CI.
  - [ ] Verifier que les familles canoniques n alimentent plus les structures `use_case` legacy sauf compatibilite explicitement bornee.
  - [ ] Documenter les exceptions transitoires restantes.

- [ ] **Task 5: Realigner les lectures critiques** (AC: 3, 7, 8)
  - [ ] Migrer `admin_ai.py` hors dependance structurante a `llm_call_logs.use_case` des qu un equivalent canonique existe.
  - [ ] Realigner `admin_exports.py` et les exports de consommation pour que `use_case_compat` reste compat-only et jamais source primaire.
  - [ ] Realigner les lectures runtime/startup (`main.py`, auto-heal, seeds) vers assemblies / execution profiles / release snapshots quand le comportement nominal le permet.
  - [ ] Supprimer les lectures nominatives d objets classes `drop`.

- [ ] **Task 6: Archiver les donnees a conserver** (AC: 5, 6, 9)
  - [ ] Definir les objets contenant de la valeur d audit, de replay, de release history ou de reporting.
  - [ ] Choisir le format d archive adapte (`*_archive`, export SQL/JSON/CSV, snapshot versionne).
  - [ ] Executer et documenter l archivage avant les suppressions irreversibles.
  - [ ] Lier chaque objet supprime a son emplacement d archive ou a sa justification de non-archive.

- [ ] **Task 7: Supprimer physiquement les objets morts** (AC: 3, 9, 10)
  - [ ] Ecrire des migrations ciblees pour les colonnes legacy mortes.
  - [ ] Ecrire des migrations ciblees pour les tables legacy prouvees inutilisees.
  - [ ] Supprimer les index/contraintes/vues devenus inutiles.
  - [ ] Verifier qu aucun objet `unknown` n est supprime.

- [ ] **Task 8: Ajouter les garde-fous post-cleanup** (AC: 11, 12, 13, 14, 15)
  - [ ] Ajouter un test ou validateur liant les objets DB LLM au registre de cleanup.
  - [ ] Ajouter un garde qui detecte une nouvelle lecture nominale de champs / tables legacy interdits.
  - [ ] Ajouter un garde qui detecte une nouvelle ecriture nominale dans un objet legacy gele.
  - [ ] Ajouter un garde distinct qui detecte une derive schema/migration hors registre de cleanup.
  - [ ] Mettre a jour la documentation de gouvernance DB LLM post-cleanup.

- [ ] **Task 9: Validation finale** (AC: 15)
  - [ ] Activer le venv avant toute commande Python : `.\.venv\Scripts\Activate.ps1`
  - [ ] Executer `cd backend ; ruff format .`
  - [ ] Executer `cd backend ; ruff check .`
  - [ ] Executer `cd backend ; pytest -q` ou une campagne ciblee justifiee
  - [ ] Verifier les migrations de cleanup sur une base de test / preprod et confirmer le rollback documente.

## Dev Notes

### Developer Context

- Le runtime canonique post-70-15 vit dans `backend/app/application/llm/ai_engine_adapter.py`, `backend/app/domain/llm/runtime/gateway.py`, `backend/app/domain/llm/prompting/*`, `backend/app/domain/llm/configuration/*`, `backend/app/domain/llm/runtime/contracts.py` et `backend/app/ops/llm/*`.
- Le schema DB actuel montre deja les objets canoniques vises : `llm_assembly_configs`, `llm_execution_profiles`, `llm_release_snapshots`, `llm_active_releases`, `llm_call_logs`, `llm_canonical_consumption_aggregates`, avec migrations dediees entre `1a16484f6ae0`, `cc211a38294d`, `b91ce4044d7c`, `20260417_0069` et `20260420_0071`.
- La story 70-16 a deja livre les surfaces QA et la recette backend necessaires pour verifier les flux runtime/admin sur un utilisateur canonique. 70-17 doit reutiliser ces actifs comme preuve executee de non-usage des objets classes `drop` ou `freeze`.
- Les points de friction legacy encore visibles ne doivent pas etre supprimes aveuglement. Ils doivent d abord etre classes, puis converges :
  - `backend/app/infra/db/models/llm_prompt.py` : `LlmUseCaseConfigModel`, `LlmPromptVersionModel.use_case_key`, `model`, `temperature`, `max_output_tokens`, `fallback_use_case_key`, `reasoning_effort`, `verbosity`
  - `backend/app/infra/db/models/llm_assembly.py` : `fallback_use_case`
  - `backend/app/infra/db/models/llm_observability.py` : `use_case`
  - `backend/app/api/v1/routers/admin_ai.py` : regroupements et details encore pilotes par `use_case`
  - `backend/app/api/v1/routers/admin_exports.py` : `use_case_compat` explicitement deprecie mais encore expose
  - `backend/app/main.py` : auto-heal et seeds qui comptent encore `llm_use_case_configs` / `llm_prompt_versions`
  - `backend/app/ai_engine/*` : surfaces historiques `use_case` a auditer avant tout drop DB

### Migration Order Requirements

- Ne jamais commencer par des `DROP`.
- Toujours converger d abord la logique runtime/admin/ops.
- Ensuite geler les ecritures legacy.
- Ensuite archiver les donnees utiles.
- Enfin seulement supprimer physiquement.

### File Structure Requirements

- Registre de cleanup : preferer un document dedie sous `backend/docs/` ou `docs/` avec un nom stable et referencable par les validateurs.
- Garde-fous : privilegier `backend/tests/` et/ou `backend/app/ops/llm/semantic_*` si le controle doit tourner en CI/startup.
- Migrations : `backend/migrations/versions/` uniquement, petites et ordonnees.
- Ne pas recreer de couche parallele "cleanup tooling" hors des patterns existants `services`, `ops`, `startup`, `tests`.

### Testing Requirements

- Ajouter au minimum :
  - un test / validateur du registre de cleanup ;
  - un test detectant une lecture nominale d un objet classe `drop` ou `freeze` ;
  - un test detectant une ecriture nominale legacy interdite ;
  - des tests de non-regression pour les surfaces admin/ops touchees ;
  - des validations de migration / rollback sur base de test.
- Si la suite complete est trop lourde, justifier explicitement les suites ciblees retenues, mais conserver `ruff format`, `ruff check` et une preuve pytest exploitable.

### Previous Story Intelligence

- Story 70-15 a deja supprime le namespace runtime historique et aligne la source de verite code sur `app.domain.llm.*`. Cette story doit maintenant realigner la base sur cette verite, pas recreer une nouvelle phase de wrappers.
- Story 70-16 a deja formalise la validation runtime/admin via seed QA, routes internes et runbook de recette. 70-17 doit s appuyer sur ces chemins pour prouver qu un objet legacy n est plus requis en execution, au lieu d inventer une nouvelle surface de verification.
- L audit post-70-15 montre qu il ne reste plus de reliquat actif `app.llm_orchestration.*` dans le code nominal, mais que des compatibilites DB / observabilite subsistent encore.
- Les correctifs 2026-04-22 sur le bootstrap canonique (`main.py`, seeds guidance, gouvernance placeholders) prouvent que le runtime local depend encore de certaines structures historiques ; toute suppression DB doit donc prouver que ces points ont ete converges.

### Anti-Patterns to Avoid

- Supprimer `llm_use_case_configs` ou des colonnes `use_case*` sans avoir traite `admin_ai.py`, `admin_exports.py`, `main.py` et `ai_engine/*`.
- Deplacer simplement la dette vers un nouveau champ ou une nouvelle table "temporaire".
- Confondre colonne de compatibilite de lecture et source nominale de decision runtime.
- Archiver apres coup : l archive doit preceder le drop.
- Valider uniquement par grep sans preuve runtime/admin/ops.

### References

- [Source: _bmad-output/implementation-artifacts/70-15-basculer-la-source-de-verite-runtime-llm-vers-les-namespaces-canoniques.md]
- [Source: _bmad-output/implementation-artifacts/70-16-documenter-valider-et-exposer-des-routes-de-test-pour-la-generation-llm.md]
- [Source: docs/2026-04-21-audit-prompts-backend-post-story-70-15-v2.md]
- [Source: docs/llm-qa-runbook.md]
- [Source: backend/app/api/v1/routers/internal/llm/qa.py]
- [Source: backend/app/services/llm_qa_seed_service.py]
- [Source: _bmad-output/planning-artifacts/epics-admin-llm-preview-execution.md]
- [Source: _bmad-output/planning-artifacts/architecture.md]
- [Source: backend/app/infra/db/models/llm_prompt.py]
- [Source: backend/app/infra/db/models/llm_assembly.py]
- [Source: backend/app/infra/db/models/llm_execution_profile.py]
- [Source: backend/app/infra/db/models/llm_release.py]
- [Source: backend/app/infra/db/models/llm_observability.py]
- [Source: backend/app/infra/db/models/llm_canonical_consumption.py]
- [Source: backend/app/services/llm_canonical_consumption_service.py]
- [Source: backend/app/services/llm_ops_monitoring_service.py]
- [Source: backend/app/api/v1/routers/admin_ai.py]
- [Source: backend/app/api/v1/routers/admin_exports.py]
- [Source: backend/app/api/v1/routers/admin_llm_assembly.py]
- [Source: backend/app/api/v1/routers/admin_llm_release.py]
- [Source: backend/app/api/v1/routers/admin_llm_consumption.py]
- [Source: backend/app/main.py]
- [Source: backend/migrations/versions/1a16484f6ae0_add_llm_assembly_configs.py]
- [Source: backend/migrations/versions/b91ce4044d7c_add_llm_release_tables_and_obs.py]

## Dev Agent Record

### Agent Model Used

gpt-5

### Debug Log References

- Demande utilisateur : re-rediger la story 70-16 a partir d un draft de cleanup DB LLM post-convergence canonique.
- Sources inspectees : workflow `bmad-create-story`, config BMAD, sprint status, story 70-15, audit backend post-70-15, architecture, backlog admin LLM preview/execution, modeles DB LLM, services de consommation/ops et routeurs admin.
- Decision de cadrage : repositionner cette story en 70-17 pour conserver la vraie 70-16 et garder le cleanup DB en `ready-for-dev`.

### Completion Notes List

- Story cleanup DB LLM repositionnee en 70-17.
- La vraie 70-16 a ete restauree a l identique.
- Le cadrage 70-17 reste base sur l etat reel du schema, des routeurs admin, de l observabilite et des services runtime/ops.
- Gouvernance backlog clarifiee : la story cleanup DB a ete renumerotee en 70-17 pour preserver l historique reel de la story 70-16 deja livree ; aucun remplacement implicite de story done n est desormais tolere sans trace explicite.
- Les hotspots legacy DB les plus dangereux (`use_case`, colonnes runtime redondantes, exports compat, auto-heal startup) sont explicitement nommes pour eviter un cleanup superficiel.

### File List

- _bmad-output/implementation-artifacts/70-17-db-cleanup-llm-canonique.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
