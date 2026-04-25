# Story 70-21: Analyser, factoriser et deplacer les services LLM residuels sous `backend/app/services`

Status: review

## Story

As a Platform Architect,  
I want analyser, factoriser et relocaliser les services LLM encore a plat sous `backend/app/services`,  
so that le backend conserve un namespace `services` DRY, explicite, sans legacy, sans fichiers LLM orphelins au niveau racine et sans duplication entre generation, ops et QA.

## Contexte

La story 70.18b a deja regroupe les services applicatifs de generation LLM sous `backend/app/services/llm_generation/`.

La story 70.20 a confirme une regle structurelle forte sur le perimetre LLM backend :

- pas de shim durable ;
- pas de duplication entre `services`, `domain`, `ops` et `prediction` ;
- pas de compatibilite legacy ;
- la destination doit etre justifiee par la responsabilite reelle et par les consommateurs nominaux.

Malgre cela, trois fichiers LLM restent encore a plat sous `backend/app/services/` :

- `backend/app/services/llm_canonical_consumption_service.py`
- `backend/app/services/llm_ops_monitoring_service.py`
- `backend/app/services/llm_qa_seed_service.py`

L audit local montre que ces trois fichiers n ont pas le meme role :

- `llm_canonical_consumption_service.py` construit et relit un read model canonique de consommation LLM a partir de `llm_call_logs` ;
- `llm_ops_monitoring_service.py` agrege des metriques et alertes d exploitation LLM pour les routes ops ;
- `llm_qa_seed_service.py` prepare un utilisateur canonique QA et son chart pour les routes internes de generation et le bootstrap startup.

Le meme audit montre egalement :

- les seuls fichiers `backend/app/services/*.py` contenant `llm` sont ces trois fichiers ; il n existe donc pas d autre residu LLM a plat a ce niveau ;
- `backend/app/services/llm_generation/` existe deja et contient les services metier de generation (`guidance_service.py`, `chat_guidance_service.py`, `consultation_generation_service.py`, `natal_interpretation_service*.py`, `llm_token_usage_service.py`, `anonymization_service.py`, `off_scope_policy.py`) ;
- les routes `admin_llm_consumption.py` et `admin_exports.py` appellent actuellement des helpers internes de `LlmCanonicalConsumptionService` (`_normalized_calls`, `_period_start_utc`, `_normalize_taxonomy`) ;
- la route `ops_monitoring_llm.py` depend directement de `LlmOpsMonitoringService` ;
- la route `internal/llm/qa.py` et le bootstrap `startup/llm_qa_seed.py` dependent directement de `LlmQaSeedService`.

Le probleme n est donc pas seulement un deplacement physique. Il y a aussi un probleme de frontiere :

- certains helpers prives de `llm_canonical_consumption_service.py` servent deja de pseudo API publique ;
- `llm_qa_seed_service.py` melange seed QA, conventions de donnees canoniques et helper utilitaire `build_llm_qa_seed_chart_payload` ;
- le niveau racine `backend/app/services/` devient un fourre-tout pour des services LLM qui devraient vivre dans un sous-namespace explicite.

Cette story doit terminer le travail de convergence sans rouvrir de dette :

- aucun alias inverse ;
- aucun wrapper legacy ;
- aucun fichier `llm_*_service.py` maintenu a plat par confort.

## Objectif

Obtenir une organisation cible ou :

- aucun des trois fichiers LLM residuels ne reste a plat sous `backend/app/services/` ;
- chaque fichier est deplace vers un sous-namespace `services` explicite, coherent avec sa responsabilite ;
- les helpers utilises hors du module ne restent pas exposes uniquement via des methodes privees ;
- les imports production/tests sont migrés integralement ;
- des garde-fous empechent toute reintroduction de fichiers LLM a plat.

## Regle de destination attendue

La story doit partir de cette preference, puis la confirmer par audit :

- les briques directement liees a la generation et au QA de generation vont vers `backend/app/services/llm_generation/` ;
- les briques de supervision, read model de consommation, agrégation ops et monitoring LLM vont vers un sous-namespace dedie de `backend/app/services/` plutot que de rester a la racine ;
- la story reutilise au maximum les sous-dossiers existants et ne cree un nouveau sous-dossier que si la responsabilite est stable, reelle et partagee.

Le namespace `backend/app/ops/llm/` reste la source canonique des contrats, DTO, conventions et structures ops LLM.

Le namespace `backend/app/services/llm_observability/`, s il est retenu, ne porte que des services applicatifs de lecture, agrégation, refresh de read model, drilldown et monitoring a partir de la base.

Il ne doit pas redefinir de contrats, d enums, de taxonomie, de conventions ni de regles deja portes par `app.ops.llm`.

La cible pressentie minimale est :

- `backend/app/services/llm_generation/qa_seed_service.py`
- `backend/app/services/llm_observability/consumption_service.py`
- `backend/app/services/llm_observability/monitoring_service.py`

Si l audit montre une cible strictement meilleure a l interieur de `backend/app/services/`, elle est autorisee.  
En revanche, il est interdit de conserver les trois fichiers a plat ou de creer des alias `app.services.llm_*_service`.

## Acceptance Criteria

1. **AC1 - Audit structurel explicite des trois fichiers cibles**  
   La story documente pour chacun des trois fichiers :
   - ses consommateurs reels ;
   - sa responsabilite dominante ;
   - la destination canonique retenue sous `backend/app/services/` ;
   - les raisons de cette destination.

2. **AC2 - Plus aucun fichier LLM residuel a plat sous `backend/app/services/`**  
   Apres implementation, les fichiers suivants n existent plus a la racine de `backend/app/services/` :
   - `llm_canonical_consumption_service.py`
   - `llm_ops_monitoring_service.py`
   - `llm_qa_seed_service.py`

3. **AC3 - Relocalisation vers des sous-namespaces coherents**  
   Les fichiers sont deplaces vers des sous-dossiers explicites sous `backend/app/services/`, en reutilisant l existant quand possible.  
   La solution par defaut doit privilegier :
   - `llm_generation/` pour le seed QA de generation ;
   - un sous-namespace `llm_observability/` pour consommation canonique et monitoring.

4. **AC4 - DRY strict sur les helpers exposes hors module**  
   Les routeurs et exports ne doivent plus appeler de primitives internes de normalisation, de periode ou de taxonomie.  
   Le service de consommation expose des methodes publiques orientees cas d usage : lecture d agregats, refresh du read model, drilldown admin et lignes d export.  
   Il est interdit de transformer mecaniquement un helper prive en helper public si cela laisse la logique de composition dans les routeurs.

5. **AC5 - Aucune compatibilite legacy**  
   Aucun shim, alias, wrapper transitoire ou import inverse `app.services.llm_*_service` n est ajoute.  
   Tous les imports nominaux sont migrés directement vers les nouveaux chemins.

6. **AC6 - Verification du perimetre LLM adjacent**  
   La story verifie explicitement s il existe d autres fichiers lies a la generation ou au pilotage LLM sous `backend/app/services/` qui devraient entrer dans la refactorisation.  
   La conclusion de l audit doit au minimum couvrir :
   - `backend/app/services/llm_generation/*`
   - `backend/app/services/ops_monitoring_service.py`
   - `backend/app/startup/llm_qa_seed.py`
   - `backend/app/api/v1/routers/admin_llm_consumption.py`
   - `backend/app/api/v1/routers/ops_monitoring_llm.py`
   - `backend/app/api/v1/routers/internal/llm/qa.py`

7. **AC7 - Perimetre additionnel decide explicitement sans scope creep**  
   Si l audit trouve d autres fichiers LLM residuels a plat sous `backend/app/services/` ou des duplications directement liees aux trois fichiers cibles, ils sont integres dans cette story.  
   Si l audit revele une refactorisation plus large, non strictement necessaire a la suppression des trois residus, elle est documentee comme follow-up separe.  
   Aucun fichier ne doit rester hors perimetre s il maintient une duplication active avec les trois services migres.

8. **AC8 - Factoring du seed QA**  
   `llm_qa_seed_service.py` est assaini avant ou pendant son deplacement :
   - le role du service est borne au seed canonique QA ;
   - les constantes et helpers non necessaires a la surface publique sont rendus prives, deplaces ou supprimes ;
   - `build_llm_qa_seed_chart_payload` est supprime, privatise ou deplace sauf si au moins un consommateur nominal production ou QA est identifie ; si conserve public, son consommateur est documente et couvert par test.
   - le service QA seed reste un service de preparation de donnees de test internes et ne doit pas etre appele par le runtime nominal de generation LLM hors endpoints QA, bootstrap QA ou tests explicitement identifies.

9. **AC9 - Frontiere claire pour la consommation canonique**  
   Le service de consommation canonique expose une surface publique orientee cas d usage pour :
   - rafraichir le read model ;
   - lire les agregats admin ;
   - produire les lignes de drilldown ;
   - produire les donnees necessaires aux exports admin.  
   Les routeurs ne doivent pas reconstruire eux-memes les periodes, la normalisation de taxonomie ou les lignes exportees.  
   Les primitives techniques partagees restent internes au service ou sont extraites dans un module prive du meme namespace si plusieurs services du namespace les consomment.

10. **AC10 - Frontiere claire pour le monitoring ops**  
   Le service de monitoring LLM conserve une responsabilite d aggregation et d alerting d exploitation.  
   Aucun couplage supplementaire avec API, startup ou generation metier n est introduit.

11. **AC11 - Aucune duplication avec `ops/llm`, `domain/llm` ou `llm_generation`**  
   Toute logique deja presente ailleurs est reutilisee ou factorisee.  
   Il est interdit d introduire une seconde implementation concurrente de :
   - taxonomie canonique ;
   - contrats ops ;
   - calcul d etats impossibles ;
   - seed bootstrap ;
   - logique de generation LLM.
   Le role de `services/llm_generation/llm_token_usage_service.py` est distingue explicitement du service de consommation canonique :
   - `llm_token_usage_service.py` reste lie au runtime ou a la generation ;
   - le service de consommation canonique reste lie a l agregation, au read model, a l admin et aux exports ;
   - aucune logique de calcul de consommation n est dupliquee entre les deux.

12. **AC12 - Migrations completes des imports et patch targets**  
   Tous les imports de production et de tests pointent vers les nouveaux chemins.  
   Tous les patch targets string-based dans les tests sont migrés vers les nouveaux chemins.  
   Cela inclut au minimum :
   - `admin_llm_consumption.py`
   - `admin_exports.py`
   - `ops_monitoring_llm.py`
    - `internal/llm/qa.py`
   - `startup/llm_qa_seed.py`
   - les tests unitaires et d integration du perimetre.

13. **AC13 - Garde-fous anti-regression structurels**  
   La story ajoute ou met a jour des tests qui echouent si :
   - un nouveau fichier Python racine sous `backend/app/services/` commence par `llm_` ou porte une responsabilite LLM evidente ;
   - un des anciens modules `app.services.llm_canonical_consumption_service`, `app.services.llm_ops_monitoring_service` ou `app.services.llm_qa_seed_service` est encore importe, patche ou reexporte ;
   - `backend/app/services/__init__.py` reintroduit un alias, un re-export ou une compatibilite vers les anciens chemins ;
   - un routeur admin, ops ou QA appelle une methode privee du service de consommation comme contrat nominal ;
   - un alias legacy est reintroduit.

14. **AC14 - Documentation francaise conforme AGENTS**  
    Tout fichier Python nouveau ou significativement modifie contient :
    - un commentaire global en francais en tete de fichier ;
    - des docstrings en francais pour les classes, fonctions publiques et fonctions non triviales.

15. **AC15 - Validation backend obligatoire dans le venv**  
   La story n est complete que si les verifications backend ont ete executees dans le venv :
   - `.\.venv\Scripts\Activate.ps1`
   - `cd backend ; ruff format .`
   - `cd backend ; ruff check .`
   - `cd backend ; pytest -q` ou suites ciblees explicitement justifiees si un `pytest -q` complet est techniquement impossible ou disproportionne ; la justification doit etre ecrite dans le Dev Agent Record

16. **AC16 - Aucune regression fonctionnelle des surfaces admin, ops et QA**  
   Les endpoints dependants continuent de fonctionner apres migration :
   - consommation admin ;
   - exports admin de consommation ;
   - monitoring ops LLM ;
   - seed utilisateur QA ;
   - endpoints internes QA de guidance, chat, natal et horoscope daily.
   Les endpoints concernes ne doivent plus importer les anciens modules, ne doivent plus appeler de helpers prives, et doivent conserver leurs schemas de reponse existants sauf justification explicite.

## Tasks / Subtasks

- [x] **Task 1: Cartographier le perimetre reel et decider la destination de chaque fichier**  
  AC: 1, 3, 6, 7  
  - [x] Lister tous les imports de `llm_canonical_consumption_service`, `llm_ops_monitoring_service` et `llm_qa_seed_service`.
  - [x] Lister les tests qui patchent ou importent ces modules.
  - [x] Classer chaque fichier : generation, ops/read-model, bootstrap QA, utilitaire partage.
  - [x] Confirmer ou ajuster les destinations ciblees sous `backend/app/services/`.

- [x] **Task 2: Finaliser le namespace cible sous `backend/app/services/`**  
  AC: 2, 3, 11  
  - [x] Reutiliser `backend/app/services/llm_generation/` pour le seed QA si confirme.
  - [x] Introduire un sous-namespace `backend/app/services/llm_observability/` uniquement si l audit confirme qu il porte une responsabilite stable et partagee.
  - [x] Refuser tout deplacement cosmétique qui ne clarifie pas la responsabilite.

- [x] **Task 3: Factoriser la surface publique du service de consommation**  
  AC: 4, 9, 12  
  - [x] Identifier les methodes privees actuellement utilisees comme contrat nominal.
  - [x] Introduire une API publique sobre pour les besoins de normalisation et de drilldown.
  - [x] Migrer `admin_llm_consumption.py` et `admin_exports.py` vers cette API publique.
  - [x] Supprimer la dependance aux helpers prives exposes de fait.

- [x] **Task 4: Assainir et deplacer le monitoring ops LLM**  
  AC: 3, 10, 11, 12  
  - [x] Deplacer `llm_ops_monitoring_service.py` vers le namespace cible.
  - [x] Conserver son role borne a l aggregation et a l alerting LLM.
  - [x] Migrer `ops_monitoring_llm.py` et ses tests vers le nouveau chemin.

- [x] **Task 5: Assainir et deplacer le seed QA LLM**  
  AC: 3, 8, 12, 16  
  - [x] Deplacer `llm_qa_seed_service.py` vers le namespace cible.
  - [x] Reevaluer `build_llm_qa_seed_chart_payload` : conserver, privatiser, deplacer ou supprimer selon les consommateurs reels.
  - [x] Migrer `startup/llm_qa_seed.py`, `internal/llm/qa.py` et les tests associes.

- [x] **Task 6: Verifier les autres fichiers potentiellement inclus dans le perimetre**  
  AC: 6, 7, 11  
  - [x] Verifier si d autres fichiers `services` lies a la generation LLM doivent etre regroupes dans le meme lot.
  - [x] Documenter explicitement pourquoi `services/llm_generation/*` reste tel quel ou est complete.
  - [x] Documenter explicitement pourquoi `ops_monitoring_service.py` generaliste reste hors perimetre.

- [x] **Task 7: Ajouter les garde-fous structurels**  
  AC: 5, 13  
  - [x] Ajouter un test echouant si un `backend/app/services/llm_*_service.py` reapparait a la racine.
  - [x] Ajouter un test echouant si un import nominal utilise encore les anciens chemins.
  - [x] Ajouter un test echouant si les routeurs admin/ops dependent encore de methodes privees du service de consommation.

- [x] **Task 8: Validation finale**  
  AC: 14, 15, 16  
  - [x] Activer le venv avant toute commande Python.
  - [x] Executer `cd backend ; ruff format .`
  - [x] Executer `cd backend ; ruff check .`
  - [x] Executer `cd backend ; pytest -q` ou une campagne ciblee explicitement justifiee.
  - [x] Verifier qu aucun import `app.services.llm_*_service` ne subsiste dans le code nominal et dans les tests.

## Dev Notes

### Findings deja confirmes

- Les seuls fichiers LLM encore a plat sous `backend/app/services/` sont les trois fichiers cibles.
- `backend/app/services/llm_generation/` est deja le namespace etabli pour les services metier de generation.
- `llm_canonical_consumption_service.py` porte deja des helpers techniques reutilises hors de son module, ce qui signale une API partagee mal delimitee.
- `llm_ops_monitoring_service.py` depend de `app.ops.llm.ops_contract`, mais reste un service applicatif de lecture/agrégation a partir de la base.
- `llm_qa_seed_service.py` est consomme par `startup/llm_qa_seed.py` et `api/v1/routers/internal/llm/qa.py`, donc son deplacement doit migrer startup, API et tests en meme temps.
- `app.ops.llm` porte deja les contrats, conventions et structures ops ; la refactorisation ne doit pas recreer un deuxieme espace contractuel concurrent sous `services`.

### Contraintes de conception

- Ne pas forcer les trois fichiers dans le meme sous-dossier si leurs responsabilites divergent.
- Ne pas recreer de couche `application/` parallele pour ces services.
- Ne pas dupliquer des contrats deja definis dans `app.ops.llm`, `app.domain.llm` ou `app.services.llm_generation`.
- Ne pas conserver un ancien chemin par alias pour faciliter la transition.
- Ne pas exposer de nouvelles methodes publiques si elles ne servent qu a contourner un mauvais design.

### Risques techniques a traiter

- Couplage actuel des routeurs admin a des methodes privees de `LlmCanonicalConsumptionService`.
- Patch targets de tests potentiellement nombreux apres changement de module.
- Risque de creer un sous-dossier artificiel `llm_observability` trop mince si la factorisation n est pas justifiee.
- Risque de melanger bootstrap QA et generation metier nominale dans un meme module sans frontiere claire.

### Cible de verification minimale

- `backend/app/api/v1/routers/admin_llm_consumption.py`
- `backend/app/api/v1/routers/admin_exports.py`
- `backend/app/api/v1/routers/ops_monitoring_llm.py`
- `backend/app/api/v1/routers/internal/llm/qa.py`
- `backend/app/startup/llm_qa_seed.py`
- `backend/app/tests/unit/test_llm_canonical_consumption_service.py`
- `backend/app/tests/integration/test_admin_llm_canonical_consumption_api.py`
- `backend/app/tests/integration/test_ops_monitoring_llm_api.py`
- `backend/app/tests/integration/test_llm_qa_seed.py`
- `backend/app/tests/integration/test_llm_qa_router.py`
- les garde-fous structurels type `test_story_70_18_backend_structure_guard.py`

## References

- [Source: AGENTS.md]
- [Source: _bmad-output/implementation-artifacts/70-18b-cleanup-generation-prompts-llm.md]
- [Source: _bmad-output/implementation-artifacts/70-20-auditer-et-assainir-ai-engine-adapter.md]
- [Source: _bmad-output/implementation-artifacts/70-16-documenter-valider-et-exposer-des-routes-de-test-pour-la-generation-llm.md]
- [Source: backend/app/services/llm_canonical_consumption_service.py]
- [Source: backend/app/services/llm_ops_monitoring_service.py]
- [Source: backend/app/services/llm_qa_seed_service.py]
- [Source: backend/app/services/llm_generation/__init__.py]
- [Source: backend/app/api/v1/routers/admin_llm_consumption.py]
- [Source: backend/app/api/v1/routers/admin_exports.py]
- [Source: backend/app/api/v1/routers/ops_monitoring_llm.py]
- [Source: backend/app/api/v1/routers/internal/llm/qa.py]
- [Source: backend/app/startup/llm_qa_seed.py]
- [Source: backend/app/tests/unit/test_story_70_18_backend_structure_guard.py]
- [Source: docs/2026-04-20-audit-prompts-backend.md]
- [Source: docs/2026-04-21-audit-prompts-backend-post-story-70-15-v2.md]

## Dev Agent Record

### Implementation Plan

- Auditer les consommateurs nominaux, imports et patch targets des trois services LLM residuels a plat.
- Deplacer la consommation canonique et le monitoring ops sous un namespace `services/llm_observability/` et deplacer le seed QA sous `services/llm_generation/`.
- Exposer une API publique orientee cas d usage pour la consommation canonique afin de supprimer les appels routeurs vers des helpers prives.
- Migrer les routeurs, le bootstrap startup et les tests vers les nouveaux chemins sans alias legacy.
- Ajouter des garde-fous structurels contre la reintroduction de modules `app.services.llm_*_service` et des appels a des methodes privees.
- Executer format, lint et tests backend dans le venv puis consigner les preuves et la liste des fichiers modifies.

### Completion Notes

- Audit structurel final:
  - `llm_canonical_consumption_service.py` etait consomme par `admin_llm_consumption.py`, `admin_exports.py` et les tests de consommation. Sa responsabilite dominante est le read model, le drilldown admin et les exports. Il a ete relocalise vers `backend/app/services/llm_observability/consumption_service.py` parce qu il agrege et projette la consommation a partir des logs persistants sans redefinir les contrats `app.ops.llm`.
  - `llm_ops_monitoring_service.py` etait consomme par `ops_monitoring_llm.py` et s appuyait deja sur `app.ops.llm.ops_contract`. Sa responsabilite dominante est l aggregation et l alerting d exploitation. Il a ete relocalise vers `backend/app/services/llm_observability/monitoring_service.py` car il partage le meme perimetre stable d observabilite que le read model de consommation.
  - `llm_qa_seed_service.py` etait consomme par `startup/llm_qa_seed.py`, `api/v1/routers/internal/llm/qa.py` et les tests QA. Sa responsabilite dominante est le seed de donnees QA internes de generation. Il a ete relocalise vers `backend/app/services/llm_generation/qa_seed_service.py` car il prepare l utilisateur de test et son chart pour les endpoints QA et le bootstrap QA, sans relevé ops.
- Surface publique du service de consommation factorisee:
  - ajout de `get_average_latency_index`, `get_drilldown_entries` et `get_export_rows` pour remplacer les usages nominaux de `_normalized_calls`, `_period_start_utc` et `_normalize_taxonomy` dans les routeurs.
  - `admin_llm_consumption.py` et `admin_exports.py` ne dependent plus de helpers prives du service.
- Namespace final:
  - creation de `backend/app/services/llm_observability/` pour les services de lecture, agregat et monitoring LLM.
  - reutilisation de `backend/app/services/llm_generation/` pour le seed QA.
  - suppression des trois fichiers LLM residuels a plat sous `backend/app/services/`.
- Seed QA:
  - `build_llm_qa_seed_chart_payload` n avait pas de consommateur nominal hors ancien module. Il a ete supprime au lieu d etre conserve publiquement.
- Perimetre adjacent verifie:
  - `backend/app/services/llm_generation/*` reste le namespace nominal des services metier de generation et ne duplique pas la consommation canonique ni le monitoring.
  - `backend/app/services/ops_monitoring_service.py` reste hors perimetre car il couvre le monitoring applicatif general instance-local, distinct du monitoring LLM persistant.
- Garde-fous ajoutes:
  - nouveau test `backend/app/tests/unit/test_story_70_21_services_llm_structure_guard.py` pour bloquer le retour de fichiers `llm_*_service.py` a la racine, les imports legacy et les appels routeurs a des helpers prives du service de consommation.
- Ajustements complementaires necessaires pour cloturer la validation:
  - mise a jour de `backend/docs/llm-db-cleanup-registry.json` afin d autoriser les nouveaux chemins de consommation/monitoring.
  - correction de quelques depassements `E501` preexistants dans le perimetre `canonical_entitlement` afin d obtenir `ruff check .` vert sur tout le backend.

### Validation Evidence

- Commandes executees dans le venv:
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend ; ruff format .`
  - `cd backend ; ruff check .`
  - `cd backend ; pytest -q`
  - `cd backend ; python -c "from app.main import app; print(app.title)"`
- Resultats:
  - `ruff format .` OK
  - `ruff check .` OK
  - `pytest -q` OK, `3036 passed, 12 skipped`
  - smoke import backend OK, sortie `horoscope-backend`

### File List

- backend/app/services/llm_observability/__init__.py
- backend/app/services/llm_observability/consumption_service.py
- backend/app/services/llm_observability/monitoring_service.py
- backend/app/services/llm_generation/qa_seed_service.py
- backend/app/api/v1/routers/admin_llm_consumption.py
- backend/app/api/v1/routers/admin_exports.py
- backend/app/api/v1/routers/ops_monitoring_llm.py
- backend/app/api/v1/routers/internal/llm/qa.py
- backend/app/startup/llm_qa_seed.py
- backend/app/tests/unit/test_llm_canonical_consumption_service.py
- backend/app/tests/unit/test_story_70_21_services_llm_structure_guard.py
- backend/app/tests/integration/test_llm_qa_seed.py
- backend/docs/llm-db-cleanup-registry.json
- backend/app/api/v1/routers/ops_entitlement_mutation_audits.py
- backend/app/services/canonical_entitlement/alert/query.py
- backend/app/services/canonical_entitlement/alert/retry.py
- backend/app/services/llm_canonical_consumption_service.py (supprime)
- backend/app/services/llm_ops_monitoring_service.py (supprime)
- backend/app/services/llm_qa_seed_service.py (supprime)

### Change Log

- 2026-04-25: relocalisation finale des services LLM residuels sous `llm_observability/` et `llm_generation/`, factorisation de l API publique de consommation, migration complete des imports/tests, ajout des garde-fous structurels et validation backend complete.
