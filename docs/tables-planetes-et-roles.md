# Tables liées aux planètes et rôles

## Périmètre

Ce document recense les tables du backend liées directement ou indirectement aux planètes dans l'état courant du schéma Alembic, après les migrations `20260512_0086_deversion_astrology_structures.py`, `20260513_0087_normalize_astral_sign_profiles.py`, `20260513_0089_rename_daily_planet_profiles.py`, `20260513_0090_create_astral_systems.py`, `20260513_0091_rename_planets_to_astral_planets.py` et `20260513_0092_create_astral_planet_sign_dignities.py`.

Deux catégories sont distinguées :

- Tables directement liées aux planètes par clé étrangère ou modèle SQLAlchemy explicite.
- Tables qui consomment ou historisent des informations planétaires sous forme de JSON, sans colonne `planet_id`.

## Vue d'ensemble

| Table | Lien aux planètes | Rôle principal | Versionnée |
| --- | --- | --- | --- |
| `astral_planets` | Table canonique des planètes | Vocabulaire stable des corps planétaires | Non |
| `astral_prediction_daily_planet_profiles` | `planet_id -> astral_planets.id` | Profil de pondération prédictive quotidienne, sans rôle dans le calcul du thème astral | Oui, via `reference_version_id` |
| `planet_category_weights` | `planet_id -> astral_planets.id` | Pondération planète -> catégorie de vie | Oui, via `reference_version_id` |
| `astral_sign_rulerships` | `planet_id -> astral_planets.id` | Maîtrises planétaires principales des signes astraux | Non |
| `astral_planet_sign_dignities` | `astral_planet_id -> astral_planets.id` | Dignités planétaires par signe, type de dignité et système astrologique | Non |
| `daily_prediction_category_scores` | JSON `contributors_json` | Historique des contributeurs, dont planètes/aspects | Indirectement via le run |
| `daily_prediction_turning_points` | JSON `driver_json` | Historique des événements déclencheurs, dont planètes conductrices | Indirectement via le run |
| `chart_results` | JSON `result_payload` | Snapshot de résultat de thème astral/calcul contenant les positions | Version texte dans payload et colonnes |
| `user_prediction_baselines` | Pas de planète directe | Baselines par catégorie, calculées à partir de scores déjà agrégés | Oui, via référence/ruleset |

## Tables de référence directes

### `astral_planets`

Définie par `PlanetModel` dans `backend/app/infra/db/models/reference.py`.

Ancien nom :

- `planets` jusqu'à la migration `20260513_0091`.
- Renommée en `astral_planets` par `20260513_0091_rename_planets_to_astral_planets.py`.

Colonnes principales :

| Colonne | Type | Rôle |
| --- | --- | --- |
| `id` | `Integer` | Identifiant technique. |
| `code` | `String(32)` | Code stable utilisé dans les calculs et mappings, par exemple `sun`, `moon`, `mars`. Unique. |
| `name` | `String(64)` | Nom lisible. |

Rôle métier :

- Sert de dictionnaire canonique des planètes.
- Depuis la migration `20260512_0086`, la table n'est plus rattachée à `reference_versions`.
- Les doublons historiques par version ont été repliés vers une ligne canonique par `code`.
- Les tables paramétriques référencent ce vocabulaire stable via `planet_id` ou `astral_planet_id`.

Contraintes :

- Unicité sur `code`.
- Index sur `code`.

Planètes attendues par le seed de prédiction :

| Code | Classe fonctionnelle attendue |
| --- | --- |
| `sun` | Luminaire |
| `moon` | Luminaire |
| `mercury` | Personnelle |
| `venus` | Personnelle |
| `mars` | Personnelle |
| `jupiter` | Sociale |
| `saturn` | Sociale |
| `uranus` | Transpersonnelle |
| `neptune` | Transpersonnelle |
| `pluto` | Transpersonnelle |

## Tables de paramétrage du moteur de prédiction quotidienne

### `astral_prediction_daily_planet_profiles`

Définie par `PlanetProfileModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Qualification :

- Table de configuration du moteur de prédiction quotidienne.
- Ne participe pas au calcul astronomique du thème astral : elle ne calcule ni longitudes, ni signes, ni maisons, ni aspects natals.
- S'applique après la production des positions et événements astrologiques, pour pondérer, qualifier et router les signaux de prédiction.
- Le nom runtime Python reste `planet_profiles` dans `PredictionContext` et les DTO, mais le nom SQL canonique est `astral_prediction_daily_planet_profiles`.

Clés :

- `planet_id -> astral_planets.id`
- `reference_version_id -> reference_versions.id`
- Unicité : `(reference_version_id, planet_id)`

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `class_code` | Famille astrologique utilisée par les pondérations prédictives : `luminary`, `personal`, `social`, `transpersonal`. Sert notamment à `NatalSensitivity` pour distinguer les planètes personnelles/rapides des planètes plus structurelles. |
| `speed_rank` | Rang relatif de vitesse ou de priorité temporelle. Sert de critère secondaire dans `NatalSensitivity` pour reconnaître une planète rapide/personnelle. |
| `speed_class` | Classe de vitesse : `fast`, `medium`, `slow`. Sert à filtrer ou pondérer la sensibilité natale, pas à calculer la vitesse astronomique réelle. |
| `weight_intraday` | Poids d'une planète dans les contributions intraday. Utilisé par `ContributionCalculator._w_planet`. |
| `weight_day_climate` | Poids de climat quotidien ou natal plus structurel. Utilisé dans `NatalSensitivity` pour pondérer l'occupation des maisons liées à une catégorie. |
| `typical_polarity` | Polarité usuelle : `positive`, `negative`, `neutral`. Sert à résoudre les valences contextuelles dans `ContributionCalculator` et à polariser certains modulateurs intraday. |
| `orb_active_deg` | Orbe maximal actif propre à la planète transitante. Utilisé par `EventDetector._orb_max`, combiné au multiplicateur d'aspect. |
| `orb_peak_deg` | Orbe de pic d'influence prévu par le modèle de référence. Actuellement chargé dans `PlanetProfileData`, mais sans consommation directe identifiée dans le runtime de scoring. |
| `keywords_json` | Mots-clés interprétatifs de la planète. Parsés par le repository en `keywords`; surtout utile comme matériau éditorial ou futur template, pas comme donnée de calcul astronomique. |
| `micro_note` | Note éditoriale courte, optionnelle. Présente dans le modèle SQL, mais non exposée dans `PlanetProfileData` au moment de cette analyse. |

Rôle runtime :

- Chargée par `PredictionReferenceRepository.get_planet_profiles`.
- Injectée dans `PredictionContext.planet_profiles`.
- Validée comme obligatoire par `PredictionContextLoader._validate_context`.
- Utilisée par :
  - `EventDetector._orb_max` pour déterminer l'orbe actif d'un événement transitant.
  - `ContributionCalculator._w_planet` pour pondérer les événements selon le corps en transit.
  - `ContributionCalculator._pol` pour donner une polarité aux aspects contextuels.
  - `IntradayActivationBuilder` et `TransitSignalBuilder` pour moduler les signaux continus.
  - `NatalSensitivity` pour pondérer l'occupation natale et filtrer les planètes rapides/personnelles.

Hors périmètre :

- Le calcul du thème astral reste porté par les services d'éphémérides, de maisons et d'aspects, puis historisé dans `chart_results.result_payload`.
- Modifier cette table change le scoring ou la restitution des prédictions, mais ne change pas les positions des planètes dans un thème.

Valeurs seedées notables :

| Planète | Classe | Vitesse | Intraday | Climat jour | Polarité | Orbe actif | Orbe pic |
| --- | --- | --- | ---: | ---: | --- | ---: | ---: |
| `sun` | `luminary` | `slow` | 0.6 | 1.0 | `positive` | 5.0 | 1.5 |
| `moon` | `luminary` | `fast` | 1.0 | 0.8 | `neutral` | 4.5 | 1.2 |
| `mercury` | `personal` | `fast` | 0.9 | 0.7 | `neutral` | 3.0 | 1.0 |
| `venus` | `personal` | `medium` | 0.7 | 0.8 | `positive` | 3.0 | 1.0 |
| `mars` | `personal` | `medium` | 0.8 | 0.9 | `negative` | 3.0 | 1.0 |
| `jupiter` | `social` | `slow` | 0.4 | 1.0 | `positive` | 2.5 | 0.8 |
| `saturn` | `social` | `slow` | 0.3 | 1.0 | `negative` | 2.5 | 0.8 |
| `uranus` | `transpersonal` | `slow` | 0.1 | 0.5 | `neutral` | 2.0 | 0.6 |
| `neptune` | `transpersonal` | `slow` | 0.1 | 0.4 | `neutral` | 2.0 | 0.6 |
| `pluto` | `transpersonal` | `slow` | 0.1 | 0.3 | `neutral` | 2.0 | 0.6 |

### `planet_category_weights`

Définie par `PlanetCategoryWeightModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Clés :

- `planet_id -> astral_planets.id`
- `category_id -> prediction_categories.id`
- `reference_version_id -> reference_versions.id`
- Unicité : `(reference_version_id, planet_id, category_id)`

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `weight` | Intensité du lien entre une planète et une catégorie de prédiction. |
| `influence_role` | Rôle qualitatif : `primary`, `secondary`, parfois assimilable à un facteur de routage. |

Rôle runtime :

- Chargée par `PredictionReferenceRepository.get_planet_category_weights`.
- Injectée dans `PredictionContext.planet_category_weights`.
- Utilisée par `DomainRouter._build_planet_index` pour produire le blend planète -> catégorie.
- Utilisée par `TransitSignalBuilder._build_weighted_routing` pour router les signaux continus par thème.

Logique de routage :

- Dans `DomainRouter`, une planète inconnue conserve un plancher neutre de `0.50`.
- Une planète connue amplifie une catégorie avec la formule `0.50 + 0.50 * weight`.
- Dans `TransitSignalBuilder`, `influence_role` module le poids :
  - `primary` : multiplicateur `1.0`
  - `secondary` : multiplicateur `0.6`

Exemples de rôles par catégorie :

| Planète | Catégories principalement pilotées |
| --- | --- |
| `sun` | `energy`, `career`, `pleasure_creativity` |
| `moon` | `mood`, `health`, `love`, `family_home` |
| `mercury` | `work`, `communication` |
| `venus` | `love`, `sex_intimacy`, `pleasure_creativity` |
| `mars` | `energy`, `sex_intimacy` |
| `jupiter` | `career`, `money` |
| `saturn` | `work`, `career` |
| `uranus` | Rôle secondaire sur énergie, travail, carrière, social, communication, créativité |
| `neptune` | Rôle secondaire sur humeur, santé, amour, intimité, foyer, social, créativité |
| `pluto` | Rôle secondaire sur énergie, humeur, santé, travail, carrière, argent, amour, intimité, créativité |

Le seed attend `85` lignes de poids planète -> catégorie pour une version de référence complète.

## Table de maîtrise signe -> planète

### `astral_sign_rulerships`

Définie par `AstralSignRulershipModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Ancien nom :

- `sign_rulerships` dans la migration initiale `20260307_0032`.
- Renommée en `astral_sign_rulerships` par `20260513_0087`.

Clés :

- `astral_sign_id -> astral_signs.id`
- `planet_id -> astral_planets.id`
- Unicité : `(astral_sign_id, planet_id, rulership_type, system)`

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `astral_sign_id` | Signe concerné. |
| `planet_id` | Planète maîtresse du signe. |
| `rulership_type` | Type de maîtrise, actuellement `domicile` dans le seed. |
| `system` | Système astrologique, actuellement `traditional`. |
| `weight` | Intensité de la maîtrise, seedée à `1.0`. |
| `is_primary` | Indique la maîtrise principale utilisée par défaut. |

Rôle runtime :

- Chargée par `PredictionReferenceRepository.get_sign_rulerships(system="traditional")`.
- Filtrée sur `rulership_type = "domicile"`, `system = "traditional"` et `is_primary = true`.
- Exposée comme mapping `sign_code -> planet_code` dans `PredictionContext.sign_rulerships`.

Maîtrises traditionnelles seedées :

| Signe | Planète maîtresse |
| --- | --- |
| `aries` | `mars` |
| `taurus` | `venus` |
| `gemini` | `mercury` |
| `cancer` | `moon` |
| `leo` | `sun` |
| `virgo` | `mercury` |
| `libra` | `venus` |
| `scorpio` | `mars` |
| `sagittarius` | `jupiter` |
| `capricorn` | `saturn` |
| `aquarius` | `saturn` |
| `pisces` | `jupiter` |

## Table de dignité planète -> signe

### `astral_planet_sign_dignities`

Définie par `AstralPlanetSignDignityModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Qualification :

- Table de référence stable non versionnée.
- Décrit la condition essentielle d'une planète dans un signe pour un système astrologique donné.
- Complète `astral_sign_rulerships`, qui ne garde que les maîtrises principales traditionnelles utilisées par le contexte de prédiction actuel.
- Alimentée depuis `docs/recherches astro/planet_sign_diginities.json` par la migration `20260513_0092_create_astral_planet_sign_dignities.py` et par le seed applicatif idempotent.

Clés :

- `astral_sign_id -> astral_signs.id`
- `astral_planet_id -> astral_planets.id`
- `astral_dignity_type_id -> astral_dignity_type.id`
- `astral_system_id -> astral_systems.id`
- Unicité : `(astral_sign_id, astral_planet_id, astral_dignity_type_id, astral_system_id)`

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `astral_sign_id` | Signe dans lequel la dignité est évaluée. |
| `astral_planet_id` | Planète concernée. |
| `astral_dignity_type_id` | Type de dignité : domicile, détriment, exaltation ou chute. |
| `astral_system_id` | Système astrologique applicable : traditionnel, moderne, hellénistique ou médiéval. |
| `weight` | Pondération qualitative de la dignité, positive pour une dignité favorable et négative pour une faiblesse. |
| `is_primary` | Indique si l'association est considérée comme principale dans son système. |

Rôle des données JSON :

- Le JSON source contient des identifiants de signes et planètes, ainsi que les libellés `dignity_type` et `system`.
- À l'injection, `dignity_type` est remplacé par `astral_dignity_type.id`.
- À l'injection, `system` est remplacé par `astral_systems.id`.
- Les identifiants de signes et planètes sont résolus vers les lignes canoniques `astral_signs` et `astral_planets`.

Comptage attendu :

| Groupe | Nombre de lignes |
| --- | ---: |
| Dignités traditionnelles | 38 |
| Dignités modernes | 12 |
| Total | 50 |

Exemples seedés :

| Signe | Planète | Dignité | Système | Poids | Principale |
| --- | --- | --- | --- | ---: | --- |
| `aries` | `mars` | `domicile` | `traditional` | 1.0 | Oui |
| `taurus` | `venus` | `domicile` | `traditional` | 1.0 | Oui |
| `libra` | `mars` | `detriment` | `traditional` | -1.0 | Oui |
| `aries` | `sun` | `exaltation` | `traditional` | 0.8 | Oui |
| `libra` | `sun` | `fall` | `traditional` | -0.8 | Oui |
| `scorpio` | `uranus` | `domicile` | `modern` | 1.0 | Oui |

Rôle runtime courant :

- La table est disponible comme référentiel normalisé pour les futures lectures de dignité.
- Elle n'est pas encore chargée dans `PredictionContext` au même titre que `astral_sign_rulerships`.
- Aucun calcul de position astronomique ne dépend de cette table : elle qualifie une relation planète/signe, elle ne produit pas les positions.

## Tables adjacentes nécessaires au fonctionnement

Ces tables ne sont pas des tables de planètes, mais elles structurent leur usage.

### `reference_versions`

Rôle :

- Versionne les paramètres de prédiction, pas le vocabulaire stable `planets`.
- Verrouille les versions via `is_locked`.
- Les modèles paramétriques déclenchent `_ensure_reference_version_is_mutable` avant mise à jour.

Tables planétaires versionnées via `reference_version_id` :

- `astral_prediction_daily_planet_profiles`
- `planet_category_weights`

### `prediction_categories`

Rôle :

- Catalogue les domaines de prédiction : énergie, humeur, santé, travail, carrière, argent, amour, intimité, foyer, social, communication, créativité.
- Sert de cible aux poids `planet_category_weights`.

### `aspects` et `aspect_profiles`

Rôle :

- Ne référencent pas directement les planètes.
- Définissent les aspects utilisables pour mesurer les relations planète transitante -> cible natale.
- `ContributionCalculator` combine `w_planet`, `w_aspect`, `f_orb`, `f_phase`, `f_target` et la polarité pour produire une contribution.

### `astro_points` et `point_category_weights`

Rôle :

- Définissent les angles astrologiques (`asc`, `dsc`, `mc`, `ic`) et leur routage vers les catégories.
- Complètent les planètes comme cibles ou points de contexte.

## Tables de résultats avec données planétaires en JSON

### `chart_results`

Définie par `ChartResultModel`.

Colonnes pertinentes :

- `reference_version`
- `ruleset_version`
- `result_payload`

Rôle :

- Stocke un snapshot complet du résultat de calcul.
- Les positions planétaires sont contenues dans le JSON `result_payload`, pas dans une table normalisée dédiée.
- Le payload est construit en aval des services de thème natal et peut contenir les positions, maisons, aspects, angles et métadonnées.
- C'est la zone persistée qui reflète le calcul du thème astral, contrairement à `astral_prediction_daily_planet_profiles` qui ne contient que des paramètres de scoring.

### `daily_prediction_category_scores`

Définie par `DailyPredictionCategoryScoreModel`.

Colonne pertinente :

- `contributors_json`

Rôle :

- Stocke les contributeurs qui expliquent un score par catégorie.
- Peut contenir des références aux planètes impliquées dans les événements, mais sans contrainte SQL vers `planets`.
- Sert aux écrans de diagnostic, QA, calibration et restitution publique.

### `daily_prediction_turning_points`

Définie par `DailyPredictionTurningPointModel`.

Colonne pertinente :

- `driver_json`

Rôle :

- Stocke les événements conducteurs d'un point de bascule.
- Les planètes y apparaissent comme éléments explicatifs d'événements détectés, non comme clés relationnelles.

### `daily_prediction_runs`

Rôle :

- Porte le contexte de calcul : utilisateur, date locale, `reference_version_id`, `ruleset_id`, mode/version moteur.
- Ne contient pas de planète directement.
- Sert de racine aux scores, points de bascule et blocs horaires qui peuvent expliquer des influences planétaires.

### `user_prediction_baselines`

Rôle :

- Stocke des statistiques de baseline par utilisateur, catégorie, version et ruleset.
- Ne contient pas de planète directement.
- Les effets planétaires y sont déjà agrégés dans les scores journaliers qui alimentent les baselines.

## Flux fonctionnel simplifié

1. `astral_planets` fournit les codes stables.
2. `astral_prediction_daily_planet_profiles` ajoute les paramètres de pondération prédictive par version de référence.
3. `planet_category_weights` mappe chaque planète vers les catégories de vie.
4. `astral_sign_rulerships` fournit le mapping signe -> planète maîtresse.
5. `astral_planet_sign_dignities` fournit les dignités planète -> signe normalisées, disponibles pour enrichir les règles futures.
6. `PredictionReferenceRepository` charge les tables prédictives actives dans `PredictionContext`.
7. `EventDetector` détecte les événements planète transitante -> cible natale.
8. `DomainRouter` route les événements vers les catégories avec les poids planète/maison.
9. `ContributionCalculator` calcule la contribution numérique.
10. `TransitSignalBuilder` produit les timelines continues par thème.
11. `daily_prediction_*` persiste les scores, contributeurs et points de bascule.

## Points d'attention

- `astral_planets` est désormais stable et non versionnée. Ne pas réintroduire `reference_version_id` dans cette table sans décision d'architecture.
- Les paramètres d'interprétation ou de scoring de prédiction quotidienne doivent aller dans `astral_prediction_daily_planet_profiles` ou `planet_category_weights`, pas dans `astral_planets`.
- Les données astronomiques calculées pour un thème astral ne doivent pas être ajoutées dans `astral_prediction_daily_planet_profiles`; elles relèvent des payloads de calcul (`chart_results`) ou des objets runtime de thème.
- `astral_sign_rulerships` est non versionnée dans l'état courant. Elle représente une taxonomie canonique des maîtrises, pas un paramétrage par version.
- `astral_planet_sign_dignities` est non versionnée dans l'état courant. Elle représente une taxonomie canonique des dignités planète/signe par système, alimentée depuis le JSON documentaire.
- Les colonnes JSON (`result_payload`, `contributors_json`, `driver_json`) ne garantissent pas l'intégrité référentielle avec `astral_planets`. Elles servent à la traçabilité et à la restitution.
- Les noms de planètes peuvent exister en minuscules (`sun`) dans les tables de référence et en forme titrée (`Sun`) dans certains objets runtime. Les repositories et calculateurs normalisent partiellement ces accès.

## Fichiers sources consultés

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/models/daily_prediction.py`
- `backend/app/infra/db/models/chart_result.py`
- `backend/app/infra/db/models/user_prediction_baseline.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/services/prediction/context_loader.py`
- `backend/app/domain/prediction/domain_router.py`
- `backend/app/domain/prediction/contribution_calculator.py`
- `backend/app/domain/prediction/transit_signal_builder.py`
- `backend/migrations/versions/20260218_0001_create_reference_tables.py`
- `backend/migrations/versions/20260307_0032_migration_a_prediction_reference_tables.py`
- `backend/migrations/versions/20260307_0036_backfill_prediction_planet_profile_orbs.py`
- `backend/migrations/versions/20260512_0086_deversion_astrology_structures.py`
- `backend/migrations/versions/20260513_0087_normalize_astral_sign_profiles.py`
- `backend/migrations/versions/20260513_0089_rename_daily_planet_profiles.py`
- `backend/migrations/versions/20260513_0090_create_astral_systems.py`
- `backend/migrations/versions/20260513_0091_rename_planets_to_astral_planets.py`
- `backend/migrations/versions/20260513_0092_create_astral_planet_sign_dignities.py`
- `docs/recherches astro/planet_sign_diginities.json`
