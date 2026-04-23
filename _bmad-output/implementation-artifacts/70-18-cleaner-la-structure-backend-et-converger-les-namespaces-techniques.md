# Story 70.18: Cleaner la structure backend et converger les namespaces techniques

Status: ready-for-dev

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

## Tasks / Subtasks

- [ ] **Task 1: Migrer `app.infrastructure` vers `app.infra`** (AC: 1, 2, 3, 8, 9)
  - [ ] Deplacer les elements utiles sous `backend/app/infra/`.
  - [ ] Reecrire tous les imports backend, scripts et tests vers `app.infra.*`.
  - [ ] Supprimer le dossier `backend/app/infrastructure/` une fois les imports converges.
  - [ ] Verifier qu aucun import residuel ne pointe vers `app.infrastructure.*`.

- [ ] **Task 2: Cartographier les autres dossiers de base backend** (AC: 3, 4, 8)
  - [ ] Inventorier les dossiers racines existants sous `backend/app/`.
  - [ ] Identifier les zones de recouvrement, doublons semantiques ou noms ambigus.
  - [ ] Classer chaque dossier en `canonique`, `tolere`, `a converger`, `a interdire`.
  - [ ] Documenter les cas limites pour eviter de futurs deplacements arbitraires.

- [ ] **Task 3: Documenter la structure backend cible** (AC: 4, 5, 8)
  - [ ] Produire ou mettre a jour un document de gouvernance structurelle backend.
  - [ ] Y decrire les dossiers fondationnels autorises et leurs responsabilites.
  - [ ] Expliciter la convention de nommage a retenir pour toute nouvelle couche technique.
  - [ ] Ajouter la regle de non-creation de dossier de base sans accord utilisateur.

- [ ] **Task 4: Ajouter un garde-fou anti-reintroduction** (AC: 5, 6, 9)
  - [ ] Ajouter un script, test ou validateur capable de detecter l apparition d un namespace structurel deprecie.
  - [ ] Faire echouer ce controle si un dossier de base non approuve est ajoute dans `backend/` ou `backend/app/`.
  - [ ] Cibler au minimum les imports vers d anciens namespaces techniques deprecias.
  - [ ] Documenter comment mettre a jour ce garde-fou si une nouvelle couche est explicitement approuvee.

- [ ] **Task 5: Validation finale** (AC: 1, 2, 6, 9)
  - [ ] Activer le venv avant toute commande Python : `.\.venv\Scripts\Activate.ps1`
  - [ ] Executer `cd backend ; ruff check .`
  - [ ] Executer une campagne `pytest -q` ciblee ou complete justifiee sur les zones touchees.
  - [ ] Verifier que les imports critiques backend demarrent toujours correctement apres convergence.
  - [ ] Lister clairement les limites restantes et les prochains dossiers potentiellement a converger.

- [ ] **Task 6: Centraliser les acces DateTime backend** (AC: 8, 9, 10)
  - [ ] Inventorier les appels backend a `datetime.now(...)`, `date.today()` et helpers locaux du type `utc_now()`.
  - [ ] Ajouter un `DatetimeProvider` canonique dans `backend/app/core/`.
  - [ ] Migrer les usages applicatifs backend vers ce provider.
  - [ ] Ajouter un garde-fou de non-reintroduction pour les acces directs a l horloge courante.

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

- [ ] **Task 8: Normaliser la documentation inline des fichiers touches** (AC: 4, 7, 9, 12)
  - [ ] Verifier les fichiers applicatifs crees ou significativement modifies pendant la story.
  - [ ] Ajouter un commentaire global en français en haut de fichier quand il manque.
  - [ ] Ajouter ou corriger les docstrings en français pour les modules, classes, fonctions publiques et fonctions non triviales.
  - [ ] Eviter les commentaires redondants qui paraphrasent une ligne de code evidente.
  - [ ] Lancer `ruff check` pour verifier que les ajouts restent conformes.

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

### Completion Notes List

- Story 70-18 creee pour cadrer le nettoyage structurel backend au-dela du seul perimetre LLM.
- La migration `app.infrastructure -> app.infra` est positionnee en Task 1 comme demande.
- La gouvernance "pas de nouveau dossier de base backend sans accord" est incluse dans le cadrage de la story.
- 2026-04-23 : AC10 et une tache dediee a la centralisation des acces DateTime backend ont ete ajoutes pour imposer un provider d horloge canonique en couche `core`.
- 2026-04-23 : AC11 et une tache dediee ont ete ajoutes pour regrouper les modeles DB LLM sous `backend/app/infra/db/models/llm/` et migrer les imports associes.
- 2026-04-23 : AC11 renforcee pour exiger la preuve que les nouveaux fichiers `models/llm` sont bien utilises et qu aucun ancien chemin legacy, alias ou shim durable ne subsiste.
- 2026-04-23 : AC12 ajoutee pour imposer un commentaire global en français en haut des fichiers touches et des docstrings en français sur les modules/classes/fonctions publiques ou non triviales.
- 2026-04-23 : AC11 mise en oeuvre : les 9 modeles DB LLM ont ete deplaces sous `backend/app/infra/db/models/llm/`, les imports backend/scripts/tests ont ete migres, le barrel racine `app.infra.db.models` ne reexporte plus les symboles LLM, et le garde-fou `test_story_70_18_llm_model_namespace_guard.py` verifie l absence de fichiers/imports legacy ainsi que l usage effectif de chaque fichier canonique.

### File List

- _bmad-output/implementation-artifacts/70-18-cleaner-la-structure-backend-et-converger-les-namespaces-techniques.md
- _bmad-output/implementation-artifacts/sprint-status.yaml
- backend/app/infra/db/models/__init__.py
- backend/app/infra/db/models/llm/
- backend/tests/unit/test_story_70_18_llm_model_namespace_guard.py
- Imports LLM mis a jour dans backend/app, backend/scripts et backend/tests.

### Change Log

- 2026-04-23 : creation de la story 70-18 pour nettoyer la structure backend et converger les namespaces techniques, avec priorite explicite sur la migration `app.infrastructure -> app.infra`.
- 2026-04-23 : implementation AC11, regroupement des modeles DB LLM sous `app.infra.db.models.llm`, suppression des exports legacy LLM du barrel racine et ajout du garde-fou de namespace.
