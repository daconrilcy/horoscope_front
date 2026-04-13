# Story 66.36: Gating de non-régression end-to-end sur golden set de prompts et outputs

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As a Platform Architect,
I want compléter la matrice d'évaluation par une campagne de non-régression end-to-end rejouable et bloquante sur un golden set stable,
so that toute publication d'artefact LLM ou activation de release soit arrêtée dès qu'une dérive structurelle, d'observabilité canonique, ou un retour de chemin legacy interdit réapparaît sur le périmètre nominal supporté.

## Contexte

Les stories 66.16, 66.29 à 66.35 ont déjà fermé une grande partie des dérives nominales du gateway LLM, mais il reste encore un trou majeur entre "métrique de qualité" et "gate de prod réellement bloquant" :

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) décrit désormais une matrice d'évaluation croisant `feature`, `plan`, `persona`, `context_quality`, `pipeline_kind`, avec contrôle des placeholders, budgets, personas et contrats. Cette matrice reste cependant surtout doctrinale tant qu'elle n'est pas reliée à un golden set stable et à un verdict machine-bloquant avant publication.
- [backend/app/llm_orchestration/services/eval_harness.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/eval_harness.py) fournit déjà un harness de fixtures YAML rejouées via `LLMGateway.execute()`, avec `EvalReport`, `EvalFixtureResult`, `failure_rate` et `blocked_publication`. Ce socle est utile, mais il reste centré sur des vérifications simples de schéma/champs attendus et ne compare ni `obs_snapshot`, ni dérive structurelle profonde, ni réapparition de chemins legacy interdits.
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py) bloque déjà un `publish` si le `failure_rate` dépasse `eval_failure_threshold`, ce qui prouve que le repo sait faire un gate de publication. En revanche, ce gate n'impose pas encore une vraie campagne de non-régression orientée release/runtime, ni une comparaison avec une baseline golden stable.
- [backend/app/llm_orchestration/services/replay_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/replay_service.py) sait rejouer une exécution à partir d'un snapshot d'entrée chiffré et renvoyer un diff non textuel de statut. Ce mécanisme constitue une brique crédible pour automatiser un replay avant publication, mais aujourd'hui il ne sert pas de gate systématique sur un set de prompts safe versionné.
- [backend/app/llm_orchestration/services/performance_qualification_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/performance_qualification_service.py) et [backend/app/llm_orchestration/performance_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/performance_registry.py) ont introduit en 66.35 une doctrine de seuils explicites, de verdict automatisé et de corrélation stricte à `active_snapshot_id`, `active_snapshot_version`, `manifest_entry_id`. 66.36 doit réutiliser cette discipline de "thresholds bloquants versionnés" au lieu d'inventer un second mode de décision.
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py) expose déjà les discriminants critiques à surveiller dans `ExecutionObservabilitySnapshot`, `ResolvedExecutionPlan`, `ReplayResult`, `EvalReport` et les enums de chemins d'exécution, y compris les valeurs legacy interdites (`fallback_resolve_model`, `legacy_execution_profile_fallback`, `non_nominal_provider_tolerated`).
- [docs/agent/story-29-N5-eval-fixtures-gate.md](/c:/dev/horoscope_front/docs/agent/story-29-N5-eval-fixtures-gate.md) et [docs/agent/story-35-3-non-regression.md](/c:/dev/horoscope_front/docs/agent/story-35-3-non-regression.md) montrent déjà deux patterns internes à réutiliser :
  - fixtures versionnées et publish gate ;
  - golden snapshots stables, synthétiques, explicitement audités.
- [backend/app/tests/golden/pro_dataset_v1.json](/c:/dev/horoscope_front/backend/app/tests/golden/pro_dataset_v1.json) prouve aussi que le repo sait maintenir un dataset golden statique et versionné quand la stabilité du runtime compte vraiment.

Le manque restant est donc précis :

- pas de golden set LLM unique, stable et versionné couvrant la matrice 66.16 ;
- pas de replay automatisé pré-publication sur ce golden set ;
- pas de seuils bloquants sur dérive structurelle autre qu'un simple `failure_rate` global ;
- pas de comparaison explicite de `obs_snapshot` contre une baseline canonique ;
- pas de vérification machine-bloquante qu'aucun chemin legacy interdit ne réapparaît sur `chat`, `guidance`, `natal`, `horoscope_daily`.

## Diagnostic exact à préserver

- La cible de cette story n'est **pas** de créer un nouveau harness parallèle isolé de l'existant. Le socle prioritaire à étendre est le duo `eval_harness.py` + gate `publish_prompt()` + outillage de replay déjà présent.
- La cible n'est **pas** non plus de comparer naïvement des blobs textuels instables ou de réintroduire une surface de fuite en contradiction avec 66.34. Les fixtures doivent rester synthétiques, safe, et compatibles avec la politique de minimisation / redaction.
- Le golden set doit couvrir le **périmètre nominal supporté** (`chat`, `guidance`, `natal`, `horoscope_daily`) et ses dimensions de variation réellement gouvernées (`plan`, `persona`, `context_quality`, `pipeline_kind`), pas seulement un use case historique isolé.
- Le gate ne doit **pas** se contenter d'un booléen "success/fail". Il doit distinguer au minimum :
  - succès nominal conforme ;
  - dérive structurelle tolérée mais visible ;
  - dérive bloquante ;
  - campagne invalide faute de contexte de release/candidat exploitable.
- La comparaison doit rester **structurelle et canonique** :
  - contrat de sortie ;
  - placeholders rendus ;
  - budgets ;
  - persona attendue ;
  - taxonomie runtime ;
  - `obs_snapshot` ;
  - absence de retour legacy interdit.
- Sur le périmètre supporté, la réapparition de `fallback_resolve_model`, `legacy_execution_profile_fallback`, `non_nominal_provider_tolerated`, `legacy_use_case_fallback` ou d'un `fallback_kind` interdit n'est pas un warning ; c'est un **échec bloquant**.
- Le replay pré-publication ne doit pas être pensé comme un outil purement admin manuel. Il doit devenir un **contrôle systématique et automatisable** dans le workflow de publication/promotion.
- Le golden set ne doit pas dépendre de prompts utilisateurs réels, de snapshots prod bruts, ni d'une vérité implicite "la dernière sortie observée". La baseline doit être volontaire, stable, versionnée et auditable.
- La story doit distinguer explicitement trois couches :
  - **golden fixture** : dataset d'entrée synthétique et stable ;
  - **golden baseline** : attendu canonique structurel et d'observabilité associé à une fixture ;
  - **golden threshold registry** : registre versionné décrivant la sévérité des drifts applicables à cette baseline.
- La story doit préserver la distinction entre les artefacts éditoriaux/structurels attendus, l'observabilité canonique attendue, et la capacité/performance évaluée par 66.35. 66.36 complète 66.35 ; elle ne la remplace pas.

## Cible d'architecture

Introduire un **LLM Golden Regression Gate** réutilisant le harness d'évaluation, le replay et l'observabilité canonique pour produire, avant publication, une campagne de non-régression end-to-end machine-bloquante.

Cette couche doit fournir :

1. un **golden set stable et versionné** de fixtures synthétiques couvrant la matrice canonique LLM ;
2. une **golden baseline** versionnée, distincte des fixtures d'entrée ;
3. un **replay automatisé** de ce golden set contre un candidat exécutable explicitement figé avant promotion ;
4. une comparaison **structurelle** des outputs et métadonnées canoniques, sans dépendre d'une lecture manuelle ;
5. une comparaison explicite de **`obs_snapshot`** sur les champs canoniques pertinents ;
6. une vérification explicite d'absence de **réapparition legacy** sur le périmètre nominal supporté ;
7. un **registre de seuils bloquants** versionné, distinct du dataset, pour dire quelle dérive est acceptable, tolérée sous contrainte, ou bloquante ;
8. une couche de **canonicalisation** versionnée avant diff pour neutraliser les variations non pertinentes ;
9. une **politique opératoire de verdict** branchée au workflow réel de publication/release ;
7. un **rapport de régression** lisible et sérialisable, exploitable en admin, en CI et en pré-déploiement.

La cible n'est donc pas "faire plus de tests". La cible est un **gate de non-régression de prod** aligné sur le runtime réel, sur la release réellement candidate, et sur la taxonomie canonique du gateway.

## Axes de contrôle à imposer

### 1. Golden fixtures stables

Chaque fixture du golden set doit définir au minimum :

- un `fixture_id` stable et versionné ;
- la taxonomie cible (`feature`, `subfeature`, `plan`, `persona`, `context_quality`, `pipeline_kind` ou équivalent stable) ;
- un input synthétique sûr, compatible 66.34 ;
- l'attendu structurel de sortie ;
- l'attendu canonique d'observabilité ;
- la politique de drift (`strict`, `thresholded`, `informational` ou équivalent stable).

La fixture ne doit pas embarquer elle-même le registre de thresholds global. Les inputs, la baseline attendue et les seuils applicables doivent rester séparés pour éviter les responsabilités concurrentes.

### 2. Replay automatisé avant publication

Le workflow de publication/promotion doit pouvoir rejouer automatiquement le golden set :

- soit contre un snapshot candidat explicite ;
- soit contre une release candidate explicite ;
- soit contre un bundle candidat explicitement figé et corrélable à un futur snapshot ;
- soit, si un override de version existe, contre un override strictement borné et documenté ;

mais jamais contre un état "best effort" reconstruit opportunistement depuis des tables live sans identité de release.

### 3. Dérive structurelle bloquante

Le gate doit comparer au minimum :

- `validation_status` ;
- structure et présence des champs attendus dans `structured_output` ;
- placeholders survivants ou budgets cassés ;
- invariants de persona et de contrat ;
- mismatch de shape, types, cardinalités, discriminants, minima de contenu et champs critiques explicitement stables ;
- diff non textuel des statuts et contrats.

La comparaison structurelle ne doit pas dériver vers un diff sémantique fin de valeurs éditoriales volatiles si ces valeurs ne font pas partie des invariants explicitement stabilisés par la baseline.

### 4. Comparaison explicite de `obs_snapshot`

La campagne doit comparer la baseline et le run courant sur les champs canoniques, au minimum :

- `pipeline_kind` ;
- `execution_path_kind` ;
- `fallback_kind` ;
- `requested_provider`, `resolved_provider`, `executed_provider` ;
- `context_quality`, `context_compensation_status` ;
- `max_output_tokens_source`, `max_output_tokens_final` ;
- `executed_provider_mode` ;
- `attempt_count` ;
- `provider_error_code` ;
- `breaker_state`, `breaker_scope` ;
- `active_snapshot_id`, `active_snapshot_version`, `manifest_entry_id` quand le contexte de comparaison les exige.

Ces champs ne doivent pas tous être comparés avec la même sévérité. La story impose une classification explicite entre :

- **strict** : invariants bloquants ;
- **thresholded** : champs comparés sous seuil ou règle de drift ;
- **informational** : champs remontés au rapport mais non bloquants à eux seuls.

### 5. Réapparition legacy interdite

Le gate doit échouer explicitement si un run supporté réintroduit :

- un `execution_path_kind` legacy interdit ;
- un `fallback_kind` interdit ;
- une source d'exécution `fallback_resolve_model` ou provider non nominal toléré ;
- une taxonomie d'observabilité ou de résultat contredisant 66.29 à 66.35.

## Latest Technical Specifics

Les éléments externes suivants doivent être intégrés pour éviter une implémentation datée ou approximative :

- La documentation officielle pytest rappelle que `@pytest.mark.parametrize` est le mécanisme standard pour exprimer une suite déterministe de cas pilotés par dataset, ce qui convient directement à un golden set versionné et exhaustif. Source : [pytest documentation](https://docs.pytest.org/en/stable/how-to/parametrize.html).
- La documentation OpenAI sur les data controls précise que les abuse monitoring logs peuvent contenir prompts, réponses et métadonnées dérivées, avec une rétention par défaut jusqu'à 30 jours ; en inférence, le golden set de non-régression ne doit pas recycler des prompts utilisateurs réels ni des sorties prod sensibles. Source : [OpenAI Data Controls](https://developers.openai.com/api/docs/guides/your-data).

Inférences à expliciter dans la story :

- un golden gate crédible doit être **piloté par dataset** et non par une poignée d'assertions ad hoc dispersées ;
- les fixtures de non-régression doivent rester **synthétiques et auditées**, même si le replay technique existe ;
- le gate doit être **machine-bloquant** et non reposer sur une lecture humaine des différences ;
- les comparaisons doivent porter sur des artefacts **stables et canoniques**, pas sur des sorties textuelles volatiles dont la variabilité masquerait une vraie régression structurelle.
- toute comparaison fiable doit passer par une **canonicalisation** explicite des éléments volatils, ordre-insensibles ou non pertinents pour le verdict ;
- un verdict intermédiaire n'a de valeur que s'il est **relié à un comportement opératoire explicite** dans le workflow de publication ou de release.

## Acceptance Criteria

1. **AC1 — Golden set versionné obligatoire** : le repo introduit un golden set stable, versionné et auditable couvrant au minimum `chat`, `guidance`, `natal` et `horoscope_daily`, avec variation explicite sur `plan`, `persona`, `context_quality` et `pipeline_kind` quand ces dimensions sont pertinentes pour la famille testée.
2. **AC2 — Fixtures sûres et synthétiques** : les fixtures utilisent uniquement des inputs synthétiques compatibles avec 66.34. Aucun prompt utilisateur réel, snapshot prod brut, contenu natal réel, PII ou sortie sensible non minimisée n'est utilisé comme baseline golden.
3. **AC3 — Séparation fixture / baseline / thresholds** : l'implémentation sépare explicitement le dataset d'entrée, la baseline canonique attendue, et le registre de drift/thresholds ; le dataset golden ne sert pas de source de vérité unique pour les seuils.
4. **AC4 — Réutilisation du socle existant** : l'implémentation étend le harness d'évaluation et/ou le replay existant au lieu de créer un troisième moteur de gate isolé. La source de vérité du verdict reste un artefact versionné du repo.
5. **AC5 — Replay automatisé pré-publication** : avant publication d'un artefact LLM ou activation d'une release candidate sur le périmètre supporté, le workflow exécute automatiquement la campagne golden correspondante sans intervention manuelle obligatoire.
6. **AC6 — Comparaison structurelle des outputs** : chaque replay compare au minimum `validation_status`, la shape de `structured_output`, la présence/absence des champs requis, les types, cardinalités, discriminants, minima de contenu explicitement stabilisés, les placeholders survivants, les budgets, et les invariants de contrat décrits par la matrice 66.16, sans dériver vers un diff textuel ou sémantique fin de valeurs éditoriales volatiles.
7. **AC7 — Seuils bloquants sur dérive structurelle** : la plateforme introduit une source de vérité versionnée décrivant, par famille ou classe de fixture, quels écarts sont `bloquants`, `tolérés sous contrainte`, ou `informatifs`. Un run échoue automatiquement dès qu'un seuil bloquant est dépassé.
8. **AC8 — Comparaison explicite de `obs_snapshot`** : la campagne compare la baseline et le run courant sur les champs canoniques de `obs_snapshot`, y compris au minimum `pipeline_kind`, `execution_path_kind`, `fallback_kind`, triplet provider, `context_compensation_status`, `max_output_tokens_source`, `max_output_tokens_final`, `executed_provider_mode`, `attempt_count`, `provider_error_code`, `breaker_state`, `breaker_scope`.
9. **AC9 — Corrélation release quand applicable** : si la campagne vise une release candidate ou un snapshot publié, le rapport inclut et valide explicitement `active_snapshot_id`, `active_snapshot_version` et `manifest_entry_id`. Une comparaison qui perd cette corrélation est invalide.
10. **AC10 — Interdiction explicite des chemins legacy** : sur `chat`, `guidance`, `natal`, `horoscope_daily`, le gate échoue si une exécution ou un snapshot publie ou réintroduit `legacy_use_case_fallback`, `legacy_execution_profile_fallback`, `non_nominal_provider_tolerated`, `fallback_resolve_model`, `fallback_provider_unsupported` ou tout équivalent legacy interdit par 66.29 à 66.35.
11. **AC11 — Alias legacy normalisés sans échappatoire** : un alias d'entrée encore toléré en compatibilité hérite des mêmes exigences de gate et ne peut pas servir de trou de contournement vers un chemin legacy. La normalisation d'alias intervient avant la sélection du dataset, l'application des thresholds et la classification des legacy states.
12. **AC12 — Rapport de régression lisible et sérialisable** : la campagne produit un artefact machine-readable et un résumé lisible indiquant au minimum : `fixture_id`, famille, candidat comparé, statut par fixture, diffs structurels, diffs `obs_snapshot`, détections legacy, seuils appliqués, verdict final, et cause de blocage si échec.
13. **AC13 — Workflow de bless/update explicite** : la façon de créer, bénir, modifier ou invalider une baseline golden est documentée. Une mise à jour de baseline ne peut pas se faire implicitement par "dernier run observé".
14. **AC14 — Gating branché au workflow réel** : l'admin publish / release workflow / script de pré-déploiement concerné appelle effectivement ce gate sur le périmètre supporté. Une publication supportée ne peut pas être considérée recevable si le gate n'a pas été exécuté ou s'il a échoué.
15. **AC15 — Couverture tests du gate** : des tests couvrent la résolution du golden set, la classification des drifts, les seuils bloquants, la comparaison `obs_snapshot`, la détection de chemins legacy interdits, l'invalidation d'un run incomplet et le format de rapport.
16. **AC16 — Documentation réalignée** : [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md) et la doc ops pertinente expliquent le golden set, les seuils de drift, la comparaison `obs_snapshot`, la règle anti-réapparition legacy, et le point exact du workflow où le gate bloque une publication.
17. **AC17 — Canonicalisation obligatoire avant comparaison** : tout champ ou sous-artefact réputé volatile, ordre-insensible ou non pertinent pour le verdict est normalisé par une couche canonique versionnée avant diff ; l'absence de canonicalisation explicite rend la campagne invalide.
18. **AC18 — Classification des champs `obs_snapshot`** : les champs comparés dans `obs_snapshot` sont classés en `strict`, `thresholded` ou `informational`, et cette classification vit dans une source de vérité versionnée distincte du dataset golden.
19. **AC19 — Corrélation stricte au candidat exécutable** : sur le périmètre nominal supporté, la campagne golden ne compare qu'un snapshot candidat, une release candidate, ou un bundle explicitement figé et corrélable à un futur snapshot ; une reconstruction opportuniste depuis des tables live sans identité de release invalide le run.
20. **AC20 — Rapport safe-by-design** : le rapport machine-readable et lisible de golden regression n'expose ni prompt brut, ni `raw_output`, ni `structured_output` complet sensible, ni contenu utilisateur, ni extrait textuel rejouable, et reste conforme à la politique de minimisation/redaction de 66.34.
21. **AC21 — Politique de verdict opératoire** : le workflow de publish/release explicite le comportement exact des verdicts `pass`, `constrained`, `fail`, `invalid`, y compris leur caractère bloquant ou non selon le type de workflow.
22. **AC22 — Stabilité du golden set** : la baseline golden ne doit contenir que des invariants à faible churn attendu. Une variation éditoriale bénigne ne doit pas forcer une re-bénédiction massive du dataset.

## Tasks / Subtasks

- [x] Task 1: Définir le format et l'emplacement du golden set LLM (AC1, AC2, AC13)
  - [x] Choisir une structure stable de fixtures/snapshots versionnés cohérente avec les patterns existants (`eval_fixtures`, `tests/golden`).
  - [x] Définir un schéma de fixture intégrant taxonomie, input synthétique, attentes structurelles, attentes `obs_snapshot` et politique de drift.
  - [x] Documenter la règle de bénédiction/mise à jour d'une baseline golden.

- [x] Task 2: Étendre le harness d'évaluation existant vers une vraie campagne golden end-to-end (AC3, AC4, AC6, AC12)
  - [x] Réutiliser [backend/app/llm_orchestration/services/eval_harness.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/eval_harness.py) comme point de départ.
  - [x] Ajouter la capacité de rejouer un candidat précis avant publication.
  - [x] Produire un rapport enrichi par fixture avec statut, diffs structurels et verdict agrégé.

- [x] Task 3: Introduire la comparaison structurelle et le registre de seuils (AC6, AC7, AC12)
  - [x] Définir une source de vérité versionnée pour les seuils de drift.
  - [x] Comparer `validation_status`, shape `structured_output`, placeholders, budgets et invariants de contrat.
  - [x] Introduire une couche de canonicalisation avant diff pour les artefacts ordre-insensibles, volatils ou tolérant `null`/absence.
  - [x] Distinguer `blocking`, `constrained`, `informational` ou équivalent stable.

- [x] Task 4: Comparer explicitement `obs_snapshot` et les discriminants runtime (AC8, AC9)
  - [x] Définir l'allowlist des champs `obs_snapshot` à comparer.
  - [x] Classer les champs en `strict`, `thresholded`, `informational`.
  - [x] Ajouter une logique de diff stable et lisible sur les champs canoniques.
  - [x] Exiger `active_snapshot_id`, `active_snapshot_version`, `manifest_entry_id` quand le contexte candidat/release le requiert.

- [x] Task 5: Verrouiller la non-réapparition des chemins legacy (AC10, AC11)
  - [x] Encoder la liste canonique des états legacy interdits sur le périmètre supporté.
  - [x] Vérifier ces états dans les outputs, snapshots, rapports et assertions de tests.
  - [x] Appliquer la normalisation des alias avant sélection de dataset et classification des legacy states.
  - [x] Ajouter au moins un cas sur alias legacy normalisé pour prouver l'absence d'échappatoire.

- [x] Task 6: Brancher le gate au workflow de publication réel (AC5, AC19, AC21)
  - [x] Identifier le point de branchement correct dans [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py) et, si nécessaire, dans le workflow release/snapshot associé.
  - [x] Verrouiller le mode d'exécution de référence : snapshot candidat, release candidate ou bundle explicitement figé, jamais tables live opportunistes.
  - [x] Définir le comportement opératoire exact de `pass`, `constrained`, `fail`, `invalid`.
  - [x] Bloquer la publication si la campagne est échouée ou invalide.
  - [x] Rendre le verdict consultable côté admin/ops sans lecture manuelle fragile.

- [x] Task 7: Ajouter la couverture de non-régression du gate (AC15, AC17, AC18, AC20)
  - [x] Étendre les tests du harness existant.
  - [x] Ajouter des tests sur les diffs `obs_snapshot`.
  - [x] Ajouter des tests sur la détection des chemins legacy interdits.
  - [x] Ajouter des tests sur la canonicalisation des diffs.
  - [x] Ajouter des tests garantissant que le rapport reste safe-by-design.
  - [x] Ajouter des tests sur l'invalidation d'un run sans contexte complet.

- [x] Task 8: Documentation et vérification locale obligatoires (AC16)
  - [x] Mettre à jour la documentation runtime/ops avec le workflow golden gate.
  - [x] Après activation du venv PowerShell, exécuter `.\.venv\Scripts\Activate.ps1`.
  - [ ] Dans `backend/`, exécuter `ruff format .` puis `ruff check .`.
  - [ ] Exécuter `pytest -q`.
  - [x] Exécuter au minimum les suites ciblées harness / replay / publish gate / golden regression.

## Dev Notes

### Ce que le dev doit retenir avant d'implémenter

- Le projet possède déjà un **publish gate** LLM via `run_eval()` et `publish_prompt()`. 66.36 doit l'élever vers une campagne golden de non-régression, pas repartir de zéro.
- La story doit rester alignée avec 66.34 : pas de réintroduction de contenu sensible dans des snapshots ou rapports de gate sous prétexte de faciliter la comparaison.
- La story doit rester alignée avec 66.35 : les verdicts doivent être **versionnés, explicites et bloquants**, à la manière des SLO/SLA, pas "observés visuellement".
- Les discriminants runtime utiles existent déjà dans `ExecutionObservabilitySnapshot`, `ResolvedExecutionPlan` et `GatewayMeta`. Il faut les comparer, pas en inventer d'autres concurrents.
- La liste des états legacy interdits est déjà documentée dans `docs/llm-prompt-generation-by-feature.md` et encodée dans les enums/modèles ; 66.36 doit s'y brancher comme garde-fou de maintenance.
- Le replay courant renvoie un diff non textuel de validation. C'est un excellent point d'appui, mais insuffisant tant que `obs_snapshot` et les chemins legacy ne sont pas comparés.
- Le golden set doit être **stable**. Toute valeur réputée volatile ou environnement-dépendante doit être normalisée, exclue, ou comparée via seuil/allowlist explicite.
- Le registre des thresholds de golden regression ne doit pas être dispersé dans les fixtures. Il doit vivre dans une source de vérité dédiée et versionnée, distincte du dataset.
- La comparaison `obs_snapshot` ne doit pas être uniformément stricte. Certains champs relèvent d'invariants durs, d'autres de seuils, d'autres du reporting informatif uniquement.
- Le rapport de gate doit rester compatible 66.34 : aucune fuite de prompt, de `raw_output`, de `structured_output` sensible ou de payload rejouable.

### Ce que le dev ne doit pas faire

- Ne pas créer un nouveau harness parallèle si `eval_harness.py` et le gate `publish_prompt()` peuvent être étendus proprement.
- Ne pas comparer des `raw_output` textuels instables ou du contenu sensible réel comme si cela constituait une baseline exploitable.
- Ne pas utiliser le "dernier run observé" comme source de vérité implicite pour bénir une nouvelle baseline.
- Ne pas laisser un alias legacy contourner le gate supporté.
- Ne pas réduire le contrôle anti-legacy à une simple vérification HTTP ou à un booléen générique `success`.
- Ne pas documenter un état "warning" pour un chemin legacy réapparu sur une famille supportée : c'est un échec bloquant.

### Fichiers à inspecter en priorité

- [backend/app/llm_orchestration/services/eval_harness.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/eval_harness.py)
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/llm_orchestration/services/replay_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/replay_service.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/llm_orchestration/services/performance_qualification_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/performance_qualification_service.py)
- [backend/app/llm_orchestration/performance_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/performance_registry.py)
- [backend/app/llm_orchestration/tests/test_eval_harness.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_eval_harness.py)
- [backend/app/llm_orchestration/tests/test_performance_qualification.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_performance_qualification.py)
- [backend/app/llm_orchestration/tests/test_replay_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/tests/test_replay_service.py)
- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)

### Previous Story Intelligence

- **66.16** a formalisé la matrice d'évaluation systématique ; 66.36 doit la rendre exécutable comme gate bloquant et non rester au niveau de la seule doctrine de test.
- **66.29 à 66.31** ont fermé les chemins fallback/use-case-first, `resolve_model`, et les dépendances legacy sur le périmètre supporté ; 66.36 doit empêcher toute réapparition silencieuse de ces états dans les snapshots, fixtures ou assertions.
- **66.32** a imposé la corrélation à la release active (`active_snapshot_id`, `active_snapshot_version`, `manifest_entry_id`) ; 66.36 doit préserver cette traçabilité quand la campagne cible une release/snapshot.
- **66.34** a durci la politique de non-fuite ; 66.36 doit garder des fixtures synthétiques et des comparaisons non textuelles ou structurelles.
- **66.35** a introduit la logique de thresholds et de verdict automatisé ; 66.36 doit réemployer ce pattern pour les drifts structurels et d'observabilité.

### Git Intelligence

Commits récents pertinents observés :

- `939bae53` : `docs(llm): clarify story 66.35 qualification contract`
- `ebc35300` : `fix(llm): harden qualification correlation and document story 66.35`
- `f1231546` : `fix(ops): cleanup repo artifacts and logs (Story 66.35)`
- `4b6d745a` : `fix(ops): remove sensitive .env and harden snapshot correlation (Story 66.35)`
- `baa31921` : `fix(ops): harden snapshot verification and performance endpoint responses (Story 66.35)`

Pattern à réutiliser :

- une seule source de vérité versionnée pour les seuils ;
- corrélation stricte à la release/snapshot réellement exécuté ;
- rejet métier structuré plutôt qu'erreur implicite ;
- durcissement de la doc en même temps que le code ;
- tests ciblés sur les chemins de rejet, pas seulement sur le nominal.

### Testing Requirements

- Ajouter un test du golden resolver garantissant qu'un dataset inexistant/incomplet invalide la campagne au lieu de la laisser passer silencieusement.
- Ajouter un test couvrant un drift structurel bloquant dans `structured_output`.
- Ajouter un test couvrant une dérive `obs_snapshot.execution_path_kind` ou `fallback_kind`.
- Ajouter un test couvrant la réapparition de `legacy_execution_profile_fallback`, `non_nominal_provider_tolerated` ou `fallback_resolve_model` sur une famille supportée.
- Ajouter un test sur alias legacy normalisé (par exemple daily) pour prouver qu'il hérite du même gate.
- Ajouter un test de rapport vérifiant la présence de `fixture_id`, verdict, diffs structurels et diffs `obs_snapshot`.
- Ajouter un test d'intégration du workflow de publication montrant qu'un gate golden échoué bloque effectivement la publication.
- Commandes backend obligatoires, toujours après activation du venv PowerShell :
  - `.\.venv\Scripts\Activate.ps1`
  - `cd backend`
  - `ruff format .`
  - `ruff check .`
  - `pytest -q`
  - `pytest app/llm_orchestration/tests/test_eval_harness.py -q`
  - `pytest app/llm_orchestration/tests/test_performance_qualification.py -q`
  - `pytest app/llm_orchestration/tests/test_replay_service.py -q`

### Project Structure Notes

- Travail essentiellement backend + documentation ops/runtime.
- Le point de branchement naturel reste `backend/app/llm_orchestration/` et `backend/app/api/v1/routers/`.
- Les fixtures golden doivent rester dans une zone de tests/versionnement cohérente avec le dépôt, pas dans un répertoire ad hoc non gouverné.
- Aucun changement frontend utilisateur n'est attendu ; au plus, une exposition admin/ops du rapport si nécessaire.

### References

- [docs/llm-prompt-generation-by-feature.md](/c:/dev/horoscope_front/docs/llm-prompt-generation-by-feature.md)
- [backend/app/llm_orchestration/services/eval_harness.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/eval_harness.py)
- [backend/app/api/v1/routers/admin_llm.py](/c:/dev/horoscope_front/backend/app/api/v1/routers/admin_llm.py)
- [backend/app/llm_orchestration/services/replay_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/replay_service.py)
- [backend/app/llm_orchestration/models.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/models.py)
- [backend/app/llm_orchestration/services/performance_qualification_service.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/services/performance_qualification_service.py)
- [backend/app/llm_orchestration/performance_registry.py](/c:/dev/horoscope_front/backend/app/llm_orchestration/performance_registry.py)
- [docs/agent/story-29-N5-eval-fixtures-gate.md](/c:/dev/horoscope_front/docs/agent/story-29-N5-eval-fixtures-gate.md)
- [docs/agent/story-35-3-non-regression.md](/c:/dev/horoscope_front/docs/agent/story-35-3-non-regression.md)
- [backend/app/tests/golden/pro_dataset_v1.json](/c:/dev/horoscope_front/backend/app/tests/golden/pro_dataset_v1.json)
- [pytest documentation](https://docs.pytest.org/en/stable/how-to/parametrize.html)
- [OpenAI Data Controls](https://developers.openai.com/api/docs/guides/your-data)

## Dev Agent Record

### Agent Model Used

GPT-5 Codex

### Debug Log References

### Completion Notes List

- 2026-04-13: implémentation du golden regression gate via `GoldenRegressionService` et `golden_regression_registry.py`, branchée au publish admin.
- La campagne corrèle désormais strictement le run au snapshot actif réellement exécutable, résout `manifest_entry_id` depuis le manifest de release et invalide tout run sans contexte de release recevable.
- La comparaison applique une canonicalisation explicite avant diff, contrôle `validation_status`, `output_shape`, placeholders survivants et `obs_snapshot` avec classification `strict` / `thresholded` / `informational`.
- La réapparition de chemins legacy interdits inclut désormais les sources `execution_profile_source` non nominales (`fallback_resolve_model`, `fallback_provider_unsupported`) en plus de `execution_path_kind` et `fallback_kind`.
- Politique opératoire implémentée au publish: `pass` autorise, `constrained` autorise avec warning explicite, `fail` et `invalid` bloquent avec réponse structurée `409`.
- Vérification locale ciblée effectuée après correction de review: `ruff check` sur les fichiers 66.36 et `pytest tests/integration/test_story_66_36_golden_regression.py tests/integration/test_story_66_36_admin_integration.py -q` -> `11 passed`.

### File List

- `_bmad-output/implementation-artifacts/66-36-gating-de-non-regression-end-to-end-sur-golden-set-de-prompts-et-outputs.md`
- `_bmad-output/implementation-artifacts/sprint-status.yaml`
- `docs/llm-prompt-generation-by-feature.md`
- `backend/app/api/v1/routers/admin_llm.py`
- `backend/app/api/v1/routers/admin_llm_release.py`
- `backend/app/infra/db/models/llm_prompt.py`
- `backend/app/llm_orchestration/admin_models.py`
- `backend/app/llm_orchestration/models.py`
- `backend/app/llm_orchestration/golden_regression_registry.py`
- `backend/app/llm_orchestration/services/golden_regression_service.py`
- `backend/migrations/versions/9a2d0fcc031f_add_golden_set_path_to_llm_use_case_.py`
- `backend/tests/fixtures/golden/natal_test.yaml`
- `backend/tests/integration/test_story_66_36_admin_integration.py`
- `backend/tests/integration/test_story_66_36_golden_regression.py`
