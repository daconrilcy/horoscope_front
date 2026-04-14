# Story 66.44: Gate de production continue par snapshot actif et release health

Status: ready-for-dev

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform SRE / Release Architect,
I want transformer les garanties de qualification, de golden regression et d’observabilité en gate continue avant et après activation d’un snapshot,
so that chaque release active dispose d’une preuve continue de santé, d’une surveillance post-activation gouvernée et d’un rollback déclenchable sur des seuils objectifs.

## Contexte

Le pipeline dispose déjà de briques solides mais encore partiellement séparées :

- snapshots de release ;
- service d’activation/promotion ;
- qualification de charge corrélée au snapshot ;
- golden regression corrélée au snapshot ;
- observabilité enrichie avec `active_snapshot_id`, `active_snapshot_version`, `manifest_entry_id` ;
- surfaces ops et monitoring.

La documentation runtime décrit désormais un système gouverné et rollbackable. Le dernier gap n’est plus la présence des briques, mais leur **orchestration continue autour du snapshot actif**.

Les risques résiduels sont :

- activation d’un snapshot sans preuve suffisamment fraîche et corrélée ;
- golden regression exécutée mais pas réellement bloquante ;
- absence de smoke post-activation ciblé sur le nominal supporté ;
- surveillance post-release insuffisamment reliée au snapshot actif ;
- décision de rollback encore trop manuelle, implicite ou peu traçable.

66.44 doit donc faire passer le système d’un ensemble de garanties séparées à un **gate de production continue centré sur le snapshot actif et son release health**.

## Portée exacte

Cette story couvre cinq axes et rien de plus :

1. **conditions d’activation bloquantes** liées à qualification + golden ;
2. **smoke post-activation corrélé** au snapshot actif ;
3. **fenêtre de surveillance post-activation** gouvernée ;
4. **décision de rollback** automatique ou semi-automatique sur seuils explicites ;
5. **statut synthétique de release health** exploitable par les équipes ops et release.

Elle ne doit pas :

- créer un second système de release concurrent à `ReleaseService` ;
- dupliquer qualification ou golden dans de nouveaux services sans réutilisation ;
- fonder un rollback automatique sur des heuristiques opaques ou non versionnées ;
- transformer cette story en projet généraliste de monitoring non centré snapshot.

## Diagnostic précis à traiter

Les points de faiblesse à fermer sont :

1. absence éventuelle de blocage dur avant activation si qualification ou golden sont absentes, obsolètes ou mal corrélées ;
2. manque de preuve post-activation immédiate sur le nominal supporté ;
3. absence d’un statut synthétique unifié de santé de release ;
4. corrélation incomplète entre signaux ops et snapshot actif ;
5. décision de rollback encore trop dispersée ou trop dépendante d’une lecture humaine.

La priorité d’implémentation est :

- d’abord rendre l’activation conditionnelle et traçable ;
- ensuite prouver le post-activation ;
- enfin mécaniser la décision de dégradation/rollback sur des seuils gouvernés.

## Cible d'architecture

Conserver les briques existantes :

1. **ReleaseService** = cycle de vie snapshot et activation ;
2. **Performance qualification** = preuve pré-activation ;
3. **Golden regression** = preuve fonctionnelle / non-régression ;
4. **Observabilité / ops** = preuve post-activation et monitoring.

La cible 66.44 est d’ajouter une couche d’orchestration continue :

- préconditions explicites d’activation ;
- smoke post-activation corrélé ;
- agrégation des signaux par snapshot actif ;
- statut synthétique de release health ;
- décision de rollback gouvernée.

Le système final doit rester mono-source sur le snapshot actif comme unité de pilotage release.

## Acceptance Criteria

1. **AC1 — Activation bloquée sans qualification valide** : un snapshot candidat ne peut pas être activé sans qualification de charge réussie, suffisamment récente et corrélée sans ambiguïté au snapshot candidat.
2. **AC2 — Activation bloquée sans golden regression valide** : la golden regression est obligatoire avant activation ; une exécution absente, invalide, obsolète ou non corrélée bloque l’activation.
3. **AC3 — Corrélation snapshot stricte** : les vérifications préalables utilisent les discriminants de corrélation disponibles (`active_snapshot_id`, `active_snapshot_version`, `manifest_entry_id`, ou équivalents candidats) et refusent les corrélations ambiguës.
4. **AC4 — Smoke post-activation nominal** : après activation, un smoke corrélé au snapshot actif est exécuté sur le périmètre nominal supporté et vérifie l’absence de fallback interdit ainsi que la présence des discriminants d’observabilité attendus.
5. **AC5 — Fenêtre de surveillance post-activation** : une fenêtre de monitoring post-release agrège les signaux clés du snapshot actif sur des seuils gouvernés et versionnés.
6. **AC6 — Statut synthétique de release health** : chaque snapshot exposé en release possède un statut synthétique explicite (taxonomie bornée équivalente à `candidate`, `qualified`, `activated`, `monitoring`, `degraded`, `rollback_recommended`, `rolled_back` ou similaire).
7. **AC7 — Décision de rollback gouvernée** : un mécanisme automatique ou semi-automatique peut recommander ou déclencher un rollback selon des seuils objectifs, versionnés et traçables.
8. **AC8 — Traçabilité bout en bout** : toute décision de promotion, maintien, dégradation ou rollback est historisée avec la raison, le snapshot concerné et les signaux observés.
9. **AC9 — Tableau de bord ou vue release health** : une vue exploitable permet de suivre la santé du snapshot actif ou des snapshots récents à partir des signaux corrélés.
10. **AC10 — Réutilisation des services existants** : `ReleaseService`, qualification, golden regression et observabilité sont réutilisés autant que possible ; aucun second système concurrent n’est introduit.
11. **AC11 — Documentation et exploitation réalignées** : la doc runtime ou un runbook explicitement référencé décrit le gate de production continue, le smoke post-activation, la lecture du `release health` et la politique de rollback.
12. **AC12 — Windows + PowerShell supportés** : les validations locales requises restent compatibles avec le workflow du dépôt.

## Tasks / Subtasks

- [ ] Task 1: Formaliser le modèle de release health et ses transitions (AC5, AC6, AC8)
  - [ ] Définir les statuts synthétiques de release et leurs transitions.
  - [ ] Relier ces statuts aux artefacts snapshot/activation déjà existants.
  - [ ] Garantir l’historisation des décisions et des raisons associées.

- [ ] Task 2: Bloquer l’activation sans preuves préalables corrélées (AC1, AC2, AC3, AC10)
  - [ ] Brancher qualification et golden au flux de promotion existant.
  - [ ] Refuser l’activation si la corrélation snapshot est absente, ambiguë ou obsolète.
  - [ ] Produire des erreurs lisibles et stables.

- [ ] Task 3: Ajouter le smoke post-activation corrélé (AC4, AC8)
  - [ ] Définir un smoke minimal sur les familles nominales supportées.
  - [ ] Vérifier les discriminants d’observabilité remontés.
  - [ ] Vérifier l’absence de fallback interdit pendant ce smoke.

- [ ] Task 4: Définir la surveillance post-release et la vue release health (AC5, AC6, AC9)
  - [ ] Agréger les signaux clés par snapshot actif.
  - [ ] Définir des seuils gouvernés et versionnés.
  - [ ] Exposer ces signaux dans une vue ou un tableau de bord lisible.

- [ ] Task 5: Implémenter la décision de dégradation / rollback (AC7, AC8, AC10)
  - [ ] Définir les conditions de recommandation ou déclenchement.
  - [ ] Réutiliser `ReleaseService` pour éviter tout système concurrent.
  - [ ] Garantir la traçabilité complète des transitions.

- [ ] Task 6: Réaligner la documentation et l’exploitation (AC11)
  - [ ] Mettre à jour `docs/llm-prompt-generation-by-feature.md`.
  - [ ] Documenter le flux release health / smoke / rollback.
  - [ ] Clarifier la lecture ops du snapshot actif.

- [ ] Task 7: Validation locale obligatoire
  - [ ] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [ ] Dans `backend/`, exécuter `ruff format .`.
  - [ ] Dans `backend/`, exécuter `ruff check .`.
  - [ ] Exécuter `pytest -q`.
  - [ ] Exécuter au minimum les suites ciblant release snapshots, qualification, golden regression et monitoring ops.

## Dev Notes

### Ce que le dev doit retenir avant d’implémenter

- 66.44 est une story d’orchestration continue des garanties déjà construites.
- L’unité de pilotage doit rester le snapshot actif ou candidat, pas une agrégation floue de signaux.
- Le smoke post-activation est critique : il fait le lien entre activation logique et preuve réelle en production.
- Un rollback gouverné vaut mieux qu’une réaction manuelle peu traçable.

### Ce que le dev ne doit pas faire

- Ne pas créer un second moteur de release à côté de `ReleaseService`.
- Ne pas dupliquer qualification ou golden dans un nouveau service “façade” inutile.
- Ne pas baser un rollback automatique sur des heuristiques non gouvernées.
- Ne pas produire une vue release health sans corrélation snapshot exploitable.

### Fichiers à inspecter en priorité

- [backend/app/llm_orchestration/services/release_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/release_service.py)
- [backend/app/llm_orchestration/services/performance_qualification_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/performance_qualification_service.py)
- [backend/app/llm_orchestration/services/golden_regression_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/golden_regression_service.py)
- [backend/app/api/v1/routers/ops_monitoring.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/ops_monitoring.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

### Previous Story Intelligence

- Les stories récentes ont déjà rendu le snapshot actif central dans la gouvernance runtime.
- Qualification de charge, golden regression et observabilité corrélée existent déjà comme briques.
- La doc runtime décrit un système rollbackable ; 66.44 doit rendre cette promesse opérationnellement vraie de bout en bout.

### Git Intelligence

Le chantier montre une trajectoire cohérente :

- d’abord rendre le runtime déterministe ;
- ensuite le rendre observable ;
- ensuite le rendre gouverné ;
- enfin le rendre pilotable en exploitation continue.

Signal utile :

- 66.44 doit être l’étape de fermeture release/ops de cette trajectoire ;
- le risque principal n’est plus une faiblesse de conception locale, mais l’absence d’orchestration complète entre briques déjà présentes.

### Testing Requirements

- Couvrir le blocage d’activation sans qualification corrélée.
- Couvrir le blocage d’activation sans golden regression corrélée.
- Couvrir le smoke post-activation sur le nominal supporté.
- Couvrir les transitions de statut release health.
- Couvrir la recommandation ou le déclenchement de rollback selon seuils gouvernés.
- Vérifier la traçabilité complète des décisions release.

### Project Structure Notes

- Zone principale : `backend/app/llm_orchestration/services/`
- Zones adjacentes : `backend/app/api/v1/routers/ops_monitoring.py`, `backend/tests/`, `docs/`
- Les surfaces de `release health` doivent rester cohérentes avec les modèles de snapshot et d’observabilité déjà présents.

### References

- [backend/app/llm_orchestration/services/release_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/release_service.py)
- [backend/app/llm_orchestration/services/performance_qualification_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/performance_qualification_service.py)
- [backend/app/llm_orchestration/services/golden_regression_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/golden_regression_service.py)
- [backend/app/api/v1/routers/ops_monitoring.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/ops_monitoring.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/llm_orchestration/services/observability_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/observability_service.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

### File List
