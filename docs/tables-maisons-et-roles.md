# Tables liées aux maisons astrologiques et rôles

## Périmètre

Ce document recense les tables du backend liées directement ou indirectement aux maisons astrologiques dans l'état courant du schéma Alembic, après les migrations `20260218_0001_create_reference_tables.py`, `20260307_0032_migration_a_prediction_reference_tables.py`, `20260308_0038_add_house_system_effective_to_daily_prediction_runs.py` et `20260512_0086_deversion_astrology_structures.py`.

Deux catégories sont distinguées :

- Tables SQL qui décrivent le vocabulaire stable des maisons ou leur paramétrage prédictif.
- Tables et payloads qui consomment, calculent ou historisent les maisons sous forme de JSON ou de colonnes de trace.

Point important : les cuspides réelles d'un thème ne sont pas stockées dans une table relationnelle dédiée. Elles sont calculées à l'exécution par SwissEph ou par le moteur simplifié, puis transportées dans les objets runtime et les payloads `chart_results.result_payload`.

## Vue d'ensemble

| Table | Lien aux maisons | Rôle principal | Versionnée |
| --- | --- | --- | --- |
| `astral_houses` | Table canonique des maisons 1 à 12 | Vocabulaire stable : numéro et nom métier | Non |
| `astral_prediction_daily_house_profiles` | `house_id -> astral_houses.id` | Profil prédictif d'une maison : angularité, visibilité, priorité | Oui, via `reference_version_id` |
| `astral_house_category_weights` | `house_id -> astral_houses.id` | Routage maison -> catégorie de vie pour le scoring | Oui, via `reference_version_id` |
| `daily_prediction_runs` | Colonne `house_system_effective` | Trace du système de maisons réellement appliqué pendant un run daily | Indirectement via le run |
| `chart_results` | JSON `result_payload.houses`, `result_payload.angles`, `result_payload.planets[*].house` | Snapshot du calcul natal : cuspides, signes des cuspides, angles et maison des planètes | Version texte dans payload et colonnes |
| `daily_prediction_category_scores` | JSON `contributors_json` | Historique des contributeurs, qui peuvent inclure maisons cible/transitée | Indirectement via le run |
| `daily_prediction_turning_points` | JSON `driver_json` | Historique des événements conducteurs, avec métadonnées de maison si présentes | Indirectement via le run |

## Tables de référence directes

### `astral_houses`

Définie par `HouseModel` dans `backend/app/infra/db/models/reference.py`.

Historique :

- Créée initialement sous l'ancien nom `houses` par `20260218_0001_create_reference_tables.py`.
- Déversionnée par `20260512_0086_deversion_astrology_structures.py`.
- Renommée en `astral_houses` par `20260513_0094_rename_house_tables.py`.
- Depuis cette migration, `astral_houses` est un vocabulaire stable, indépendant des versions de paramétrage.

Colonnes principales :

| Colonne | Type | Rôle |
| --- | --- | --- |
| `id` | `Integer` | Identifiant technique utilisé par les clés étrangères. |
| `number` | `Integer` | Numéro canonique de maison, de `1` à `12`. Sert de clé métier. |
| `name` | `String(64)` | Nom court exposé par le référentiel public, par exemple `Self`, `Resources`, `Career`. |

Contraintes :

- Unicité sur `number`.
- Plus de `reference_version_id` depuis `20260512_0086`.

Rôle métier :

- Sert de dictionnaire canonique des douze maisons.
- Fournit les numéros attendus par `build_natal_result` pour demander et valider douze cuspides.
- Sert de cible relationnelle à `astral_prediction_daily_house_profiles` et `astral_house_category_weights`.
- Ne contient pas de longitude, cuspide, signe de cuspide, système de maisons ou donnée utilisateur.

Maisons seedées par `ReferenceRepository.ensure_seed_data` :

| Numéro | Nom SQL | Domaine public utilisé en restitution |
| ---: | --- | --- |
| 1 | `Self` | Identité et présence |
| 2 | `Resources` | Ressources et valeurs |
| 3 | `Communication` | Communication et mobilité |
| 4 | `Home` | Foyer et ancrage |
| 5 | `Creativity` | Créativité et plaisirs |
| 6 | `Health` | Travail quotidien et santé |
| 7 | `Partnership` | Relations et associations |
| 8 | `Transformation` | Transformations et profondeur |
| 9 | `Beliefs` | Philosophie et horizons |
| 10 | `Career` | Ambition et rôle public |
| 11 | `Community` | Collectif et réseaux |
| 12 | `Subconscious` | Intériorité et ressources cachées |

## Tables de paramétrage du moteur de prédiction quotidienne

### `astral_prediction_daily_house_profiles`

Définie par `HouseProfileModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Qualification :

- Table de configuration du moteur de prédiction quotidienne.
- Ne calcule pas les cuspides ni l'occupation des maisons.
- Qualifie une maison déjà identifiée par le calcul astrologique pour moduler la sensibilité natale.

Clés :

- `house_id -> astral_houses.id`
- `reference_version_id -> reference_versions.id`
- Unicité : `(reference_version_id, house_id)`

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `reference_version_id` | Version de référence qui porte ce paramétrage prédictif. |
| `house_id` | Maison canonique concernée. |
| `house_kind` | Type structurel : `angular`, `succedent` ou `cadent`. Utilisé pour scorer la force de placement. |
| `visibility_weight` | Poids de visibilité de la maison. Seedé mais pas consommé directement dans les calculateurs identifiés. |
| `base_priority` | Priorité éditoriale ou prédictive de base. Seedée mais pas consommée directement dans les calculateurs identifiés. |
| `keywords_json` | Mots-clés interprétatifs optionnels, parsés dans `HouseProfileData.keywords`. |
| `micro_note` | Note éditoriale courte, présente en SQL mais non exposée dans `HouseProfileData` au moment de cette analyse. |

Rôle runtime :

- Chargée par `PredictionReferenceRepository.get_house_profiles`.
- Injectée dans `PredictionContext.house_profiles` sous forme de mapping `house_number -> HouseProfileData`.
- Validée comme obligatoire par `PredictionContextLoader._validate_context`.
- Utilisée par `NatalSensitivityCalculator._house_placement_score` pour donner une force de placement :
  - `angular` : `1.0`
  - `succedent` : `0.2`
  - `cadent` : `-0.5`

Valeurs seedées notables :

| Maison | Type | Visibilité | Priorité |
| ---: | --- | ---: | ---: |
| 1 | `angular` | 1.0 | 10 |
| 2 | `succedent` | 0.7 | 6 |
| 3 | `cadent` | 0.5 | 4 |
| 4 | `angular` | 0.9 | 9 |
| 5 | `succedent` | 0.7 | 6 |
| 6 | `cadent` | 0.6 | 5 |
| 7 | `angular` | 0.9 | 9 |
| 8 | `succedent` | 0.7 | 7 |
| 9 | `cadent` | 0.5 | 4 |
| 10 | `angular` | 1.0 | 10 |
| 11 | `succedent` | 0.6 | 5 |
| 12 | `cadent` | 0.4 | 3 |

### `astral_house_category_weights`

Définie par `HouseCategoryWeightModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Qualification :

- Table de routage thématique.
- Transforme une maison activée ou occupée en catégories de prédiction : amour, travail, santé, carrière, etc.
- Ne remplace pas le calcul astronomique : elle interprète une maison déjà calculée.

Clés :

- `house_id -> astral_houses.id`
- `category_id -> prediction_categories.id`
- `reference_version_id -> reference_versions.id`
- Unicité : `(reference_version_id, house_id, category_id)`

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `reference_version_id` | Version de référence active pour les poids de routage. |
| `house_id` | Maison canonique source. |
| `category_id` | Catégorie de prédiction cible. |
| `weight` | Intensité du lien maison -> catégorie. |
| `routing_role` | Rôle qualitatif : `primary` ou `secondary`. Sert de multiplicateur dans certains calculateurs V3. |

Rôle runtime :

- Chargée par `PredictionReferenceRepository.get_house_category_weights`.
- Injectée dans `PredictionContext.house_category_weights`.
- Utilisée par `DomainRouter._project_houses_to_categories` pour transformer le vecteur maison d'un événement en poids par catégorie.
- Utilisée par `TransitSignalBuilder._build_weighted_routing` et `IntradayActivationBuilder._build_weighted_routing` pour construire les index de routage continus.
- Utilisée par `NatalSensitivityCalculator` pour identifier les maisons pertinentes d'une catégorie et calculer :
  - l'occupation natale `Occ(c)`,
  - les maîtrises de maisons `Rul(c)`,
  - l'angularité des significateurs `Ang(c)`.

Logique de routage :

- Pour un événement avec cible natale, `DomainRouter` construit un vecteur maison :
  - `1.0` sur la maison cible si la maison transitée est absente ou identique ;
  - `0.70` sur la maison natale cible et `0.30` sur la maison natale transitée si elles diffèrent.
- Chaque maison du vecteur est projetée vers les catégories via `astral_house_category_weights`.
- Le résultat maison est combiné avec le blend planète -> catégorie.
- Dans les builders V3, `routing_role` module le poids :
  - `primary` : multiplicateur `1.0`
  - `secondary` : multiplicateur `0.6`

Poids seedés :

| Maison | Catégorie principale | Poids | Catégorie secondaire | Poids |
| ---: | --- | ---: | --- | ---: |
| 1 | `energy` | 0.8 | `mood` | 0.6 |
| 2 | `money` | 0.9 | `work` | 0.5 |
| 3 | `communication` | 0.9 | `social_network` | 0.5 |
| 4 | `family_home` | 0.9 | `mood` | 0.5 |
| 5 | `pleasure_creativity` | 0.9 | `love` | 0.6 |
| 6 | `health` | 0.9 | `work` | 0.7 |
| 7 | `love` | 0.8 | `social_network` | 0.6 |
| 8 | `sex_intimacy` | 0.8 | `money` | 0.6 |
| 9 | Aucun rôle `primary` seedé | - | `pleasure_creativity`, `career` | 0.5 / 0.4 |
| 10 | `career` | 0.9 | `work` | 0.6 |
| 11 | `social_network` | 0.9 | `pleasure_creativity` | 0.5 |
| 12 | Aucun rôle `primary` seedé | - | `mood`, `health` | 0.5 / 0.4 |

Le seed attend `24` lignes de poids maison -> catégorie pour une version de référence complète.

## Tables adjacentes nécessaires au fonctionnement

### `reference_versions`

Rôle :

- Versionne les paramètres de prédiction, pas le vocabulaire stable `astral_houses`.
- Verrouille les versions via `is_locked`.
- Les mises à jour de `astral_prediction_daily_house_profiles` et `astral_house_category_weights` passent par `_ensure_reference_version_is_mutable`.

Tables liées aux maisons versionnées via `reference_version_id` :

- `astral_prediction_daily_house_profiles`
- `astral_house_category_weights`

### `prediction_categories`

Rôle :

- Catalogue les domaines de prédiction.
- Sert de cible aux poids `astral_house_category_weights`.
- Une maison n'est jamais projetée directement vers l'utilisateur final sans passer par ces catégories dans le moteur daily.

### `astro_points` et `point_category_weights`

Rôle :

- Complètent les maisons pour les angles astrologiques (`asc`, `dsc`, `mc`, `ic`).
- Les angles sont liés aux cuspides 1, 7, 10 et 4 dans `chart_json_builder`.
- Dans `IntradayActivationBuilder`, les événements `asc` et `mc` peuvent utiliser le routage point -> catégorie en plus du routage maison.

### `prediction_rulesets`

Rôle :

- Porte le système de maisons demandé dans `RulesetData.house_system`.
- Ce système est transmis au moteur de prédiction quotidienne comme `house_system_requested`.
- Le système effectivement utilisé peut différer en cas de repli runtime.

## Données de calcul et de résultat

### Cuspides calculées

Les cuspides ne sont pas des lignes SQL. Elles sont produites à l'exécution :

- Côté thème natal, `build_natal_result` appelle `houses_provider.calculate_houses` en mode `swisseph`.
- `houses_provider.calculate_houses` appelle `swe.houses_ex` et retourne `HouseData`.
- `HouseData.cusps` contient les 12 cuspides normalisées dans `[0, 360)`.
- `HouseData.ascendant_longitude` et `HouseData.mc_longitude` exposent ASC et MC.
- Les systèmes publiquement supportés par `houses_provider` sont `placidus`, `equal` et `whole_sign`.

En moteur daily V1/V3 :

- `AstroCalculator` reçoit les `natal_cusps` calculées pour le thème natal.
- À chaque pas temporel, il calcule les cuspides courantes via `swe.houses`.
- Il tente `placidus` puis replie sur `porphyre` si Placidus échoue.
- Il calcule `natal_house_transited` pour chaque planète transitante en comparant sa longitude aux cuspides natales.

### `chart_results`

Définie par `ChartResultModel`.

Colonnes pertinentes :

| Colonne | Rôle |
| --- | --- |
| `reference_version` | Version du référentiel utilisée pour construire le thème. |
| `ruleset_version` | Version de règles utilisée. |
| `result_payload` | Snapshot JSON complet du résultat de thème. |

Rôle des données de maison dans `result_payload` :

- `houses[]` contient les cuspides calculées : `number`, `cusp_longitude`, `sign`.
- `planets[]` contient la maison occupée par chaque planète dans `house`, sauf en mode dégradé sans heure.
- `angles` dérive ASC, MC, DSC et IC des cuspides 1, 10, 7 et 4.
- Le catalogue d'évidence peut produire des identifiants `HOUSE_{num}_IN_{SIGN}` et `{PLANET}_H{house}`.

### `daily_prediction_runs`

Définie par `DailyPredictionRunModel`.

Colonne pertinente :

| Colonne | Rôle |
| --- | --- |
| `house_system_effective` | Système de maisons réellement retenu pour le run daily. Peut refléter un repli runtime. |

Rôle :

- Trace l'écart éventuel entre le système demandé et le système réellement appliqué.
- Utile pour diagnostiquer les cas où Placidus ne converge pas et où le moteur retient Porphyre.

### `daily_prediction_category_scores`

Colonne pertinente :

- `contributors_json`

Rôle :

- Stocke les contributeurs qui expliquent un score par catégorie.
- Peut contenir des événements où les métadonnées incluent `natal_house_target` et `natal_house_transited`.
- Ne garantit pas d'intégrité référentielle SQL avec `astral_houses`.

### `daily_prediction_turning_points`

Colonne pertinente :

- `driver_json`

Rôle :

- Stocke les événements conducteurs d'un point de bascule.
- Les maisons y apparaissent comme contexte d'interprétation d'un événement, pas comme clés relationnelles.

### Restitution publique des maisons activées

`PublicAstroFoundationProjector` expose des `activated_houses`, mais la logique actuelle est une projection publique simplifiée :

- Les meilleurs domaines publics sont mappés vers des maisons représentatives.
- Le mapping est fixe dans le code : ambition -> 10, relations -> 7, énergie -> 1, argent -> 2, vie personnelle -> 5.
- Les libellés viennent de `HOUSE_SIGNIFICATIONS`, pas directement de la table `astral_houses`.

## Étapes où les maisons interviennent dans les calculs astrologiques

1. `ReferenceRepository.ensure_seed_data` garantit les 12 lignes `astral_houses`.
2. `PredictionReferenceRepository` charge `astral_prediction_daily_house_profiles` et `astral_house_category_weights` pour la version de référence active.
3. `PredictionContextLoader` valide que les profils de maisons existent puis fige le contexte.
4. Pour un thème natal, `build_natal_result` lit `reference_data["houses"]` pour connaître les numéros attendus.
5. `houses_provider.calculate_houses` calcule les cuspides, l'Ascendant et le Milieu du Ciel via SwissEph.
6. `build_natal_result` valide qu'il y a exactement 12 cuspides normalisées et non dupliquées.
7. `assign_house_number` assigne chaque planète natale à une maison à partir de sa longitude et des intervalles de cuspides.
8. `chart_json_builder` sérialise les maisons, les maisons des planètes et les angles dans le payload public.
9. Pour la prédiction quotidienne, `EngineOrchestrator` extrait les cuspides natales depuis `house_cusps` ou `houses`.
10. `AstroCalculator` calcule les états astrologiques par pas temporel et la maison natale transitée par chaque planète.
11. `EventDetector` produit des événements avec une maison cible natale et une maison transitée quand l'information est disponible.
12. `DomainRouter` construit le vecteur maison puis le projette vers les catégories via `astral_house_category_weights`.
13. `ContributionCalculator`, `TransitSignalBuilder` et `IntradayActivationBuilder` consomment le routage pour produire scores et timelines.
14. `NatalSensitivityCalculator` utilise `astral_prediction_daily_house_profiles` et `astral_house_category_weights` pour moduler la sensibilité structurelle par catégorie.
15. `daily_prediction_*` persiste les scores, contributeurs, points de bascule et la trace `house_system_effective`.

## Points d'attention

- `astral_houses` est stable et non versionnée. Ne pas réintroduire `reference_version_id` dans cette table sans décision d'architecture.
- `astral_prediction_daily_house_profiles` et `astral_house_category_weights` sont des paramètres de scoring, pas des données astronomiques.
- Les cuspides réelles doivent rester dans les résultats de calcul ou les objets runtime, pas dans `astral_prediction_daily_house_profiles`.
- `visibility_weight` et `base_priority` sont seedés mais leur consommation directe n'a pas été identifiée dans les calculateurs de scoring actuels.
- `micro_note` existe en SQL pour `astral_prediction_daily_house_profiles`, mais n'est pas exposé dans `HouseProfileData`.
- Les colonnes JSON (`result_payload`, `contributors_json`, `driver_json`) ne garantissent pas l'intégrité référentielle avec `astral_houses`.
- Le calcul natal public supporte `placidus`, `equal` et `whole_sign` via `houses_provider`; le calcul daily `AstroCalculator` utilise actuellement Placidus avec repli Porphyre.
- Les modes dégradés sans heure ou sans localisation peuvent produire des maisons vides, des angles `null` et des planètes sans maison dans le payload public.
- `PublicAstroFoundationProjector.activated_houses` utilise un mapping public simplifié par domaine, pas une lecture directe de `astral_house_category_weights`.

## Fichiers sources consultés

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/models/daily_prediction.py`
- `backend/app/infra/db/models/chart_result.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/services/prediction/context_loader.py`
- `backend/app/services/prediction/engine_orchestrator.py`
- `backend/app/domain/astrology/houses_provider.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/calculators/houses.py`
- `backend/app/domain/prediction/astro_calculator.py`
- `backend/app/domain/prediction/domain_router.py`
- `backend/app/domain/prediction/natal_sensitivity.py`
- `backend/app/domain/prediction/transit_signal_builder.py`
- `backend/app/domain/prediction/intraday_activation_builder.py`
- `backend/app/domain/prediction/public_projection.py`
- `backend/app/domain/prediction/public_astro_vocabulary.py`
- `backend/app/services/chart/json_builder.py`
- `backend/migrations/versions/20260218_0001_create_reference_tables.py`
- `backend/migrations/versions/20260307_0032_migration_a_prediction_reference_tables.py`
- `backend/migrations/versions/20260308_0038_add_house_system_effective_to_daily_prediction_runs.py`
- `backend/migrations/versions/20260512_0086_deversion_astrology_structures.py`
