# Epic 41 Extension Spec: Calibration Relative Utilisateur et Micro-tendances des Journées Plates

Status: draft-for-story-splitting

## Contexte

Le moteur daily prediction produit aujourd'hui des scores absolus lisibles et honnêtes, mais certaines journées ressortent comme "plates" pour un utilisateur donné:

- top catégories à `10/20`
- `decision_windows = null`
- `turning_points = []`
- `best_window = null`
- `main_turning_point = null`

Ce comportement est correct d'un point de vue absolu, mais il reste insuffisant d'un point de vue produit:

- l'utilisateur ne perçoit pas toujours la nuance entre "journée plate" et "journée sans aucune tendance relative"
- de petits écarts significatifs à l'échelle de son propre profil restent invisibles
- le top 3 d'une journée plate peut être arbitraire en cas d'égalité stricte

L'objectif de cette extension n'est pas de rendre artificiellement spectaculaires les journées neutres, mais d'ajouter une lecture relative et personnalisée qui permette de faire émerger des micro-tendances sans mentir sur le niveau d'actionnabilité réel.

## Problème Produit

La calibration actuelle est essentiellement globale / absolue.

Elle répond bien à la question:

"Cette journée est-elle forte ou faible en valeur absolue ?"

Elle répond mal à la question:

"Pour cet utilisateur, quelle est la ou les tendances les plus saillantes d'une journée pourtant globalement neutre ?"

Conséquences:

- journées plates perçues comme pauvres ou répétitives
- faible différenciation entre deux journées neutres mais en réalité différentes au regard du profil utilisateur
- difficulté à fournir un discours éditorial utile du type:
  - "journée globalement calme"
  - "léger avantage relatif pour communication / humeur / énergie"

## Objectif Produit

Ajouter une seconde couche de lecture, relative au profil utilisateur, pour:

1. conserver la calibration absolue comme source de vérité produit
2. identifier les micro-tendances d'une journée plate à l'échelle du profil utilisateur
3. garder un garde-fou clair sur l'actionnabilité:
   - une journée plate reste signalée comme plate
   - aucune micro-tendance ne doit créer artificiellement des `decision_windows` ou des `turning_points`

## Non-objectifs

- ne pas remplacer la calibration absolue existante
- ne pas réécrire le moteur intraday principal
- ne pas rendre "positive" une journée neutre par simple re-scaling
- ne pas créer de faux pivots ou faux créneaux décisionnels à partir de micro-signaux
- ne pas imposer un pré-calcul blocking lors de l'inscription utilisateur

## Principes Produit

### 1. Dual Scoring

Chaque catégorie quotidienne dispose de deux lectures:

- lecture absolue:
  - score global métier existant, exposé publiquement en priorité
- lecture relative utilisateur:
  - position de la journée par rapport à la distribution historique simulée de cet utilisateur

### 2. Honesty First

Si la journée est plate selon le moteur absolu:

- `flat_day = true`
- `best_window = null`
- `main_turning_point = null`
- `decision_windows = null`
- `turning_points = []`

La couche relative ne modifie pas cette vérité.

### 3. Relative Helpfulness

Sur une journée plate, on autorise une aide éditoriale complémentaire:

- top 3 relatif utilisateur
- texte de micro-tendance
- niveau de confiance faible ou modéré

Exemple:

"Journée globalement calme. Parmi les nuances du jour, la communication, l'énergie et l'humeur ressortent légèrement au-dessus de votre baseline habituelle."

## Hypothèse Métier Retenue

Le bon horizon de baseline utilisateur est de 12 mois glissants simulés à partir du thème natal déjà calculé.

Cette baseline est calculée offline / asynchrone et stockée en base.

La baseline doit permettre, par catégorie:

- moyenne
- écart-type
- percentiles
- effectif de jours simulés

## Vocabulaire

- `absolute score`: score produit existant
- `relative score`: position normalisée du jour versus baseline utilisateur
- `flat day`: journée sans actionnabilité suffisante selon les règles absolues
- `micro-trend`: tendance relative faible mais stable, visible uniquement comme aide secondaire
- `user baseline`: distribution historique simulée des scores d'un utilisateur sur 12 mois

## Proposition Fonctionnelle

### A. Détection d'une journée plate

Une journée est "plate" si:

- aucune `decision_window` publique n'est exposable
- aucun `turning_point` public n'est exposable
- les scores absolus ne dépassent pas le seuil de major aspect / actionability

La définition exacte reste celle déjà utilisée par la couche publique Epic 41.

### B. Micro-tendances sur journée plate

Si `flat_day = true`, calculer pour chaque catégorie:

- `relative_z_score`
- `relative_percentile`
- `relative_rank`

Puis sélectionner au plus 3 catégories de micro-tendance selon:

- z-score relatif positif minimal
- ou percentile personnel supérieur à un seuil
- avec garde-fou pour éviter les égalités artificielles

### C. Rendu utilisateur

La réponse publique reste pilotée par l'absolu.

On enrichit le `summary` avec un bloc secondaire du type:

- `flat_day: true`
- `micro_trends: [...]`
- `relative_top_categories: [...]`
- `relative_summary: "..."` 

Exemple de rendu:

- `overall_tone = neutral`
- `flat_day = true`
- `relative_top_categories = ["communication", "energy", "mood"]`
- `relative_summary = "Journee calme, avec un leger avantage relatif pour la communication, l'energie et l'humeur."`

## Modèle de Calcul

### 1. Baseline utilisateur sur 12 mois

Pour chaque utilisateur et chaque catégorie, simuler les scores journaliers sur 12 mois glissants.

Stocker au minimum:

- `mean_raw_score`
- `std_raw_score`
- `mean_note_20`
- `std_note_20`
- `p10_note_20`
- `p50_note_20`
- `p90_note_20`
- `sample_size_days`
- `window_start_date`
- `window_end_date`
- `reference_version`
- `ruleset_version`
- `house_system_effective`

### 2. Score relatif journalier

Pour une catégorie donnée:

- `z = (raw_score_day - mean_raw_score_user_category) / std_raw_score_user_category`

Fallback si `std_raw_score = 0` ou très faible:

- utiliser percentile simple ou distance relative aux percentiles
- éviter les divisions instables

### 3. Confidence relative

Associer une confiance relative aux micro-tendances selon:

- taille effective de l'échantillon
- stabilité de la distribution
- distance du score au centre de la distribution

Exemple:

- `low` si `|z| < 0.5`
- `medium` si `0.5 <= |z| < 1.0`
- `high` si `|z| >= 1.0`

Pour l'API publique, il est recommandé de ne pas exposer de `high` sur une journée plate si le score absolu reste neutre; garder cette donnée surtout pour debug / analytics.

## Données à Stocker

### Nouvelle table recommandée

`user_daily_prediction_baselines`

Colonnes proposées:

- `id`
- `user_id`
- `category_code`
- `window_start_date`
- `window_end_date`
- `sample_size_days`
- `mean_raw_score`
- `std_raw_score`
- `mean_note_20`
- `std_note_20`
- `p10_note_20`
- `p50_note_20`
- `p90_note_20`
- `reference_version`
- `ruleset_version`
- `house_system_effective`
- `computed_at`
- `source_job_version`

Contraintes proposées:

- unicité sur:
  - `user_id`
  - `category_code`
  - `window_start_date`
  - `window_end_date`
  - `reference_version`
  - `ruleset_version`
  - `house_system_effective`

### Option recommandée pour éviter une relecture coûteuse

Ajouter au snapshot journalier un petit bloc calculé à la volée ou persisté:

- `relative_score`
- `relative_percentile`
- `relative_rank`
- `micro_trend_confidence`

Décision recommandée:

- phase 1: calcul à la volée depuis la baseline
- phase 2: persistance si le coût runtime devient significatif

## Jobs et Pipeline

### Job 1: Initial user baseline generation

Déclenchement:

- après inscription complète, une fois le thème natal disponible
- ou après complétion du profil si le thème a déjà été calculé

Mode:

- async / batch
- non bloquant pour l'utilisateur

Responsabilités:

- simuler 12 mois glissants
- produire les distributions par catégorie
- persister la baseline

### Job 2: Baseline refresh

Déclenchement:

- périodique
- ou si changement de:
  - `reference_version`
  - `ruleset_version`
  - `house_system_effective`
  - données natales impactant le calcul

Responsabilités:

- recalcul incrémental ou full refresh
- invalidation propre des baselines obsolètes

## Règles API

### Contrat public daily

Le endpoint `/v1/predictions/daily` s'enrichit sans casser le contrat existant.

Ajouts recommandés dans `summary`:

- `flat_day: bool`
- `relative_top_categories: list[str]`
- `relative_summary: str | null`
- `micro_trends: list[MicroTrendDTO]`

`MicroTrendDTO` proposé:

- `code: str`
- `relative_rank: int`
- `relative_percentile: float | null`
- `relative_signal: str`
  - `slight`
  - `moderate`
- `summary: str | null`

Règles:

- `micro_trends` n'apparaît que si `flat_day = true`
- `micro_trends` n'alimente jamais `decision_windows`
- `micro_trends` n'alimente jamais `turning_points`
- `best_window` reste `null` sur journée plate

### Contrat debug

Le debug peut exposer davantage:

- `relative_z_score`
- `relative_percentile`
- `baseline_mean_raw_score`
- `baseline_std_raw_score`
- `baseline_window_start`
- `baseline_window_end`

## Editorial / UX

### Message principal

Le message principal doit rester cohérent avec l'absolu:

- "journée calme"
- "journée neutre"
- "peu de signaux structurants"

### Message secondaire

Le message secondaire peut introduire les micro-tendances:

- "parmi les nuances du jour..."
- "leger avantage relatif pour..."
- "ce ne sont pas des signaux forts, mais..."

### Interdictions UX

- ne pas présenter les micro-tendances comme des opportunités fortes
- ne pas afficher de badge de type "meilleur créneau"
- ne pas réintroduire de bruit intraday visuel

## Stratégie Technique Recommandée

### Phase 1

- baseline utilisateur stockée en base
- calcul relatif au runtime dans le service daily
- enrichissement du `summary`
- aucun changement du moteur intraday

### Phase 2

- optimisation de la génération baseline
- persistance optionnelle de métriques relatives sur le run
- observabilité produit

## Impacts Backend

Zones impactées probables:

- `backend/app/services/daily_prediction_service.py`
- `backend/app/services/daily_prediction_types.py`
- `backend/app/prediction/public_projection.py`
- `backend/app/prediction/persisted_snapshot.py`
- `backend/app/api/v1/routers/predictions.py`
- nouvelle couche baseline:
  - repository
  - service
  - job
  - modèles DB
  - migration Alembic

## Critères d'acceptation Produit

1. Une journée plate reste exposée comme plate:
   - pas de `decision_windows`
   - pas de `turning_points`
   - pas de faux `best_window`

2. Sur une journée plate, l'API peut néanmoins fournir un top 3 relatif personnalisé et un résumé secondaire lisible.

3. Deux journées plates distinctes pour un même utilisateur peuvent désormais produire des micro-tendances différentes.

4. Les micro-tendances ne dégradent pas le budget de bruit intraday défini en 41.5.

5. Les jours non plats continuent à être pilotés exclusivement par le scoring absolu et les fenêtres décisionnelles existantes.

6. Le recalcul baseline n'introduit pas de latence bloquante sur l'inscription ni sur la consultation du daily.

## Critères d'acceptation Techniques

1. Une baseline 12 mois peut être générée de façon déterministe pour un utilisateur donné.

2. La baseline est invalidée ou versionnée correctement si:
   - thème natal modifié
   - version de référence modifiée
   - ruleset modifié
   - house system effectif modifié

3. Le calcul relatif gère les cas dégénérés:
   - variance nulle
   - historique incomplet
   - baseline absente

4. L'API publique est backward-compatible:
   - ajout de champs optionnels uniquement

5. Les suites de tests QA distinguent:
   - journée plate sans micro-tendance
   - journée plate avec micro-tendances
   - journée active avec windows/pivots

## Risques

### Risque 1: faux relief

Des micro-écarts pourraient être sur-interprétés.

Mitigation:

- micro-tendances strictement secondaires
- wording explicite "léger"
- pas d'impact sur les fenêtres / pivots

### Risque 2: coût de calcul 12 mois

La simulation initiale peut être coûteuse.

Mitigation:

- job async
- batching
- stockage persistant

### Risque 3: drift de baseline

Une baseline trop ancienne perd de sa pertinence.

Mitigation:

- refresh périodique
- versionnage
- timestamps de fraîcheur

## QA / Testing

Ajouter des tests pour:

- génération baseline 12 mois
- calcul z-score / percentile avec variance nulle
- fallback si baseline absente
- journée plate avec micro-tendances visibles
- journée plate totalement neutre sans micro-tendance exploitable
- journée active inchangée
- non-régression budget de bruit intraday

## Recommandation de découpage en stories BMAD

### Story 41.12

Introduire la baseline utilisateur 12 mois et sa persistance.

### Story 41.13

Calculer les métriques relatives journalières à partir de la baseline.

### Story 41.14

Exposer les micro-tendances de journée plate dans l'assembleur public et le contrat API.

### Story 41.15

Déclencher et maintenir les jobs de génération / refresh de baseline utilisateur.

### Story 41.16

Ajouter la QA produit et les garde-fous anti faux-relief / anti-bruit.

## Draft de stories candidates

### 41.12 - Baseline utilisateur 12 mois

As a backend maintainer,
I want persister une baseline de scores journaliers simulés sur 12 mois par utilisateur et par catégorie,
so that le système puisse comparer une journée donnée à l'historique personnel simulé de l'utilisateur.

### 41.13 - Scoring relatif journalier

As a prediction engine designer,
I want calculer des métriques relatives utilisateur pour chaque catégorie quotidienne,
so that une journée neutre puisse quand même révéler des micro-tendances personnalisées sans altérer le score absolu.

### 41.14 - Projection publique des micro-tendances sur journée plate

As a utilisateur consultant le daily,
I want voir un signal secondaire de micro-tendance quand la journée est calme,
so that je distingue une journée neutre uniforme d'une journée neutre avec quelques dominantes relatives.

### 41.15 - Jobs de génération et refresh de baseline

As a platform engineer,
I want générer et rafraîchir les baselines utilisateur de façon asynchrone,
so that le calcul relatif soit disponible sans dégrader la latence du produit.

### 41.16 - QA et budget de bruit pour la calibration relative

As a QA engineer,
I want valider que la calibration relative enrichit les journées plates sans créer de faux signaux forts,
so that le produit reste honnête, lisible et stable.

## Décisions Recommandées

- retenir la baseline 12 mois glissants
- utiliser `raw_score` comme base de calcul relative principale
- garder `note_20` comme rendu principal
- réserver la lecture relative aux journées plates ou quasi plates
- exposer les enrichissements sous forme optionnelle et additive
- interdire toute conversion de micro-tendance en `decision_window` ou `turning_point`

## Références

- User request 2026-03-10
- `_bmad-output/planning-artifacts/epics.md#Epic-41`
- `backend/app/prediction/public_projection.py`
- `backend/app/services/daily_prediction_service.py`
- `backend/app/tests/integration/test_daily_prediction_qa.py`
