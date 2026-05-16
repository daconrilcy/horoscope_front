# Tables liées aux planètes et rôles

## Périmètre

Ce document recense les tables du backend liées directement ou indirectement aux planètes dans l'état courant du schéma Alembic, après les migrations `20260512_0086_deversion_astrology_structures.py`, `20260513_0087_normalize_astral_sign_profiles.py`, `20260513_0089_rename_daily_planet_profiles.py`, `20260513_0090_create_astral_systems.py`, `20260513_0091_rename_planets_to_astral_planets.py`, `20260513_0092_create_astral_planet_sign_dignities.py`, `20260513_0093_drop_astral_sign_rulerships.py`, `20260513_0094_rename_house_tables.py`, `20260513_0095_create_astral_house_systems.py`, `20260514_0096_create_house_interpretation_profiles.py`, `20260514_0097_rename_astral_house_interpretation_profiles.py`, `20260514_0098_reference_house_interpretation_system.py`, `20260514_0099_rename_astral_reference_tables.py`, `20260514_0102_normalize_astral_aspects.py`, `20260515_0112_create_astral_object_reference_tables.py`, `20260515_0114_create_astral_planet_reference_tables.py` et `20260515_0115_simplify_daily_planet_profiles.py`.

Deux catégories sont distinguées :

- Tables directement liées aux planètes par clé étrangère ou modèle SQLAlchemy explicite.
- Tables qui consomment ou historisent des informations planétaires sous forme de JSON, sans colonne `planet_id`.

Depuis le refactor, les sources JSON canoniques de seed sont sous `docs/db_seeder/astrology/`. `docs/recherches astro/` reste un espace documentaire et ne doit plus être cité comme source active des seeds applicatifs.

## Héritage des systèmes astrologiques

`astral_systems` sert de taxonomie commune aux dignités planétaires et aux règles d'aspects. Son héritage est explicite : `modern` et `traditional` sont racines, `hellenistic` hérite de `traditional`, et `medieval` hérite de `traditional`.

Les dignités planétaires restent des lignes propres à leur système quand elles divergent. L'héritage d'orbes ne doit donc pas être confondu avec une recopie des maîtrises ou dignités : il évite seulement de dupliquer les règles `traditional` dans `hellenistic` et `medieval`.

## Vue d'ensemble

| Table | Lien aux planètes | Rôle principal | Versionnée |
| --- | --- | --- | --- |
| `astral_planets` | Table canonique des planètes | Vocabulaire stable des corps planétaires | Non |
| `astral_planet_definitions` | `planet_id -> astral_planets.id` | Définition structurelle : type d'objet, rôle astrologique, vitesse, polarité typique, flags physiques | Non |
| `astral_astrological_roles` | Référencé par `astral_planet_definitions.astrological_role_id` | Taxonomie des rôles `luminary`, `personal_planet`, `social_planet`, `transpersonal_planet`, `angle`, `lunar_node` | Non |
| `astral_object_types` | Référencé par `astral_planet_definitions.object_type_id` | Nature `celestial_body`, `chart_angle` ou `mathematical_point` | Non |
| `astral_calculation_types` | Référencé par `astral_planet_definitions.calculation_type_id` | Mode d'obtention : éphéméride ou calcul géométrique | Non |
| `astral_speed` | Référencé par `astral_planet_definitions.speed_class_id` | Classes de vitesse structurelles `fast`, `medium`, `slow` | Non |
| `astral_typical_polarities` | Référencé par `astral_planet_definitions.typical_polarity_id` | Polarités typiques `positive`, `neutral`, `negative` | Non |
| `astral_prediction_daily_planet_profiles` | `planet_id -> astral_planets.id` | Profil produit de pondération prédictive quotidienne, sans rôle dans le calcul du thème astral | Oui, via `reference_version_id` |
| `astral_planet_category_weights` | `planet_id -> astral_planets.id` | Pondération planète -> catégorie de vie | Oui, via `reference_version_id` |
| `astral_systems` | Référencé par `astral_planet_sign_dignities.astral_system_id` | Taxonomie stable des traditions/systèmes astrologiques utilisés pour qualifier les dignités planète -> signe | Non |
| `astral_planet_sign_dignities` | `astral_planet_id -> astral_planets.id` | Dignités planétaires par signe, type de dignité et système astrologique ; source canonique des maîtrises signe -> planète | Non |
| `astral_planet_interpretation_profiles` | `planet_id -> astral_planets.id`, `astral_system_id -> astral_systems.id`, `language_id -> languages.id` | Vocabulaire éditorial versionné des planètes pour interprétation et prompts | Oui, via `reference_version_id` |
| `astral_house_interpretation_profiles` | Pas de planète directe ; `astral_system_id -> astral_systems.id` | Vocabulaire éditorial maison, rattaché au même référentiel de systèmes que les dignités planétaires | Oui, via `reference_version_id` |
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
| `swe_id` | `Integer` | Identifiant SwissEph canonique utilisé par le domaine et le mapper runtime. |

Rôle métier :

- Sert de dictionnaire canonique des planètes.
- Depuis la migration `20260512_0086`, la table n'est plus rattachée à `astral_reference_versions`.
- Les doublons historiques par version ont été repliés vers une ligne canonique par `code`.
- Les tables paramétriques référencent ce vocabulaire stable via `planet_id` ou `astral_planet_id`.

Contraintes :

- Unicité sur `code`.
- Index sur `code`.

Planètes attendues par le seed de prédiction :

| Code | Nom | `swe_id` | Rôle structurel |
| --- | --- | ---: | --- |
| `sun` | `Sun` | 0 | `luminary` |
| `moon` | `Moon` | 1 | `luminary` |
| `mercury` | `Mercury` | 2 | `personal_planet` |
| `venus` | `Venus` | 3 | `personal_planet` |
| `mars` | `Mars` | 4 | `personal_planet` |
| `jupiter` | `Jupiter` | 5 | `social_planet` |
| `saturn` | `Saturn` | 6 | `social_planet` |
| `uranus` | `Uranus` | 7 | `transpersonal_planet` |
| `neptune` | `Neptune` | 8 | `transpersonal_planet` |
| `pluto` | `Pluto` | 9 | `transpersonal_planet` |

Les lignes sont seedées depuis `docs/db_seeder/astrology/astral_planets.json`. `backend/app/domain/astrology/planet_catalog.py` charge ce fichier pour exposer les codes SQL, les codes runtime historiques et les identifiants SwissEph.

### `astral_planet_definitions`

Définie par `AstralPlanetDefinitionModel` dans `backend/app/infra/db/models/reference.py`.

Qualification :

- Table stable et non versionnée.
- Une ligne par planète canonique (`planet_id` unique).
- Source d'autorité structurelle pour les rôles planétaires, les flags physiques, la classe de vitesse et la polarité typique.
- Seedée depuis `docs/db_seeder/astrology/astral_planet_definitions.json`.

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `planet_id` | Planète canonique ciblée. |
| `object_type_id` | Nature de l'objet, actuellement `celestial_body` pour les dix planètes seedées. |
| `astrological_role_id` | Rôle astrologique : luminaire, personnelle, sociale ou transpersonnelle. |
| `calculation_type_id` | Mode d'obtention du point, actuellement éphéméride pour les planètes. |
| `speed_rank` | Rang structurel de vitesse : Lune `0`, Soleil `1`, Mercure `2`, jusqu'à Pluton `9`. |
| `speed_class_id` | Classe `fast`, `medium` ou `slow`. |
| `typical_polarity_id` | Polarité typique : positive, neutral ou negative. |
| `is_physical_body`, `is_luminary`, `is_planet`, `is_visible_to_naked_eye` | Flags structurels utilisés pour les garde-fous et les mappings runtime. |
| `micro_note` | Note documentaire optionnelle. |

Rôle runtime :

- `PredictionReferenceRepository.get_planet_profiles` joint cette table aux profils daily. Si une définition, un rôle, une vitesse ou une polarité manque, le chargement lève une erreur.
- `AstrologyRuntimeReferenceRepository._load_planet_definitions` expose `body_class` et `is_luminary` à `AstrologyRuntimeReferenceMapper`.
- `AstrologyRuntimeReferenceMapper` ajoute `body_class`, `is_luminary` et `swe_id` à chaque `PlanetReferenceData`.

### Taxonomies planétaires structurelles

| Table | Valeurs seedées | Rôle |
| --- | --- | --- |
| `astral_astrological_roles` | `luminary`, `personal_planet`, `social_planet`, `transpersonal_planet`, `angle`, `lunar_node` | Rôle interprétatif stable d'un objet astrologique. |
| `astral_object_types` | `celestial_body`, `chart_angle`, `mathematical_point` | Nature physique ou géométrique de l'objet. |
| `astral_calculation_types` | `ephemeris`, `derived_geometry` | Mode d'obtention technique. |
| `astral_speed` | `fast`, `medium`, `slow` | Classe de vitesse relative. |
| `astral_typical_polarities` | `positive`, `neutral`, `negative` | Polarité usuelle utilisée par le moteur daily. |

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
- `reference_version_id -> astral_reference_versions.id`
- Unicité : `(reference_version_id, planet_id)`

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `weight_intraday` | Poids d'une planète dans les contributions intraday. Utilisé par `ContributionCalculator._w_planet`. |
| `weight_day_climate` | Poids de climat quotidien ou natal plus structurel. Utilisé dans `NatalSensitivity` pour pondérer l'occupation des maisons liées à une catégorie. |
| `daily_visibility_score` | Score produit de visibilité consciente ou narrative dans la journée. |
| `daily_emotional_impact_score` | Score produit d'impact émotionnel quotidien. |
| `daily_conscious_activation_score` | Score produit d'activation consciente quotidienne. |
| `is_enabled` | Permet de désactiver une planète pour le contexte daily sans la supprimer du vocabulaire stable. |
| `micro_note` | Note éditoriale courte, exposée dans `PlanetProfileData.micro_note`. |

Les champs `class_code`, `speed_rank`, `speed_class` et `typical_polarity` restent exposés dans `PlanetProfileData`, mais ils ne viennent plus de `astral_prediction_daily_planet_profiles`. Ils sont dérivés par jointure avec `astral_planet_definitions` et ses taxonomies.

Les anciens champs `orb_active_deg`, `orb_peak_deg` et `keywords_json` ne sont plus stockés dans la table SQL daily simplifiée. Le DTO conserve des champs optionnels à `None` ou vides pour compatibilité, mais ils ne sont plus alimentés par une colonne de cette table.

Rôle runtime :

- Chargée par `PredictionReferenceRepository.get_planet_profiles`.
- Injectée dans `PredictionContext.planet_profiles`.
- Validée comme obligatoire par `PredictionContextLoader._validate_context`.
- Utilisée par :
  - `EventDetector._orb_max` seulement en fallback historique si aucune règle `astral_aspect_orb_rules` ne résout l'orbe. Dans l'état courant, les champs `orb_active_deg` des DTO issus de cette table valent `None`, donc le chemin actif passe par les règles d'aspects ou par le fallback technique.
  - `ContributionCalculator._w_planet` pour pondérer les événements selon le corps en transit.
  - `ContributionCalculator._pol` pour donner une polarité aux aspects contextuels.
  - `IntradayActivationBuilder` et `TransitSignalBuilder` pour moduler les signaux continus.
  - `NatalSensitivity` pour pondérer l'occupation natale et filtrer les planètes rapides/personnelles.

Hors périmètre :

- Le calcul du thème astral reste porté par les services d'éphémérides, de maisons et d'aspects, puis historisé dans `chart_results.result_payload`.
- Modifier cette table change le scoring ou la restitution des prédictions, mais ne change pas les positions des planètes dans un thème.

Valeurs seedées notables :

| Planète | Classe | Vitesse | Intraday | Climat jour | Visibilité | Impact émotionnel | Activation consciente |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| `sun` | `luminary` | `slow` | 0.6 | 1.0 | 1.0 | 0.5 | 1.0 |
| `moon` | `luminary` | `fast` | 1.0 | 0.8 | 0.7 | 1.0 | 0.6 |
| `mercury` | `personal` | `fast` | 0.9 | 0.7 | 0.7 | 0.4 | 0.8 |
| `venus` | `personal` | `medium` | 0.7 | 0.8 | 0.8 | 0.8 | 0.5 |
| `mars` | `personal` | `medium` | 0.8 | 0.9 | 0.9 | 0.7 | 0.9 |
| `jupiter` | `social` | `slow` | 0.4 | 1.0 | 0.9 | 0.5 | 0.8 |
| `saturn` | `social` | `slow` | 0.3 | 1.0 | 0.9 | 0.6 | 0.9 |
| `uranus` | `transpersonal` | `slow` | 0.1 | 0.5 | 0.5 | 0.3 | 0.7 |
| `neptune` | `transpersonal` | `slow` | 0.1 | 0.4 | 0.4 | 0.7 | 0.3 |
| `pluto` | `transpersonal` | `slow` | 0.1 | 0.3 | 0.5 | 0.6 | 0.8 |

### `astral_planet_interpretation_profiles`

Définie par `AstralPlanetInterpretationProfileModel` dans `backend/app/infra/db/models/interpretation_reference.py`.

Qualification :

- Table éditoriale versionnée, distincte de `astral_prediction_daily_planet_profiles`.
- Une ligne par planète, système astrologique et langue pour chaque version publiée.
- Seed courant : 20 lignes, soit 10 planètes pour deux versions de référence, en système `modern` et langue `en`.
- Source JSON : `docs/db_seeder/astrology/astral_planet_interpretation_profiles.json`.

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `reference_version_id` | Version éditoriale ou référentielle active. |
| `planet_id` | Planète canonique ciblée. |
| `astral_system_id` | Système astrologique de l'interprétation. |
| `language_id` | Langue localisée issue de `languages`. |
| `title`, `summary`, `micro_note` | Texte éditorial court. |
| `*_json` | Listes structurées pour mots-clés, expressions psychologiques, relationnelles, vocationnelles, spirituelles, dynamiques, patterns, archétypes et consignes de prompt. |

Cette table ne doit pas porter de poids produit, de vitesse, de polarité de scoring, d'orbe ou de calcul astronomique. Elle alimente les interprétations et prompts, pas les positions ni les événements.

### `astral_planet_category_weights`

Définie par `PlanetCategoryWeightModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Clés :

- `planet_id -> astral_planets.id`
- `category_id -> prediction_categories.id`
- `reference_version_id -> astral_reference_versions.id`
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

## Maîtrise signe -> planète

La table SQL `astral_sign_rulerships` n'est plus présente au head Alembic. Elle a été remplacée par une vue runtime dérivée de `astral_planet_sign_dignities`.

Historique :

- `sign_rulerships` existait dans la migration initiale `20260307_0032`.
- La table a été renommée en `astral_sign_rulerships` par `20260513_0087`.
- La table a été supprimée par `20260513_0093_drop_astral_sign_rulerships.py`, après validation que `astral_planet_sign_dignities` contient les 12 domiciles traditionnels primaires.

Source canonique actuelle :

- Table : `astral_planet_sign_dignities`.
- Filtre métier : `dignity_type = "domicile"`, `system = "traditional"` et `is_primary = true`.
- Méthode spécialisée : `PredictionReferenceRepository.get_sign_rulerships_from_dignities(system="traditional")`.
- Méthode runtime conservée : `PredictionReferenceRepository.get_sign_rulerships(system="traditional")`.
- DTO runtime conservé : `PredictionContext.sign_rulerships`, exposé comme mapping `sign_code -> planet_code`.

Le nom métier `sign_rulerships` reste donc pertinent dans le moteur, mais il ne correspond plus à une table SQL dédiée.

Maîtrises traditionnelles attendues :

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

### `astral_systems`

Définie par `AstralSystemModel` dans `backend/app/infra/db/models/reference.py`.

Qualification :

- Table stable et non versionnée.
- Créée par `20260513_0090_create_astral_systems.py`.
- Sert de référentiel commun aux dignités planétaires et, depuis `20260514_0098_reference_house_interpretation_system.py`, aux profils éditoriaux d'interprétation de maisons.

Colonnes principales :

| Colonne | Type | Rôle |
| --- | --- | --- |
| `id` | `Integer` | Identifiant technique utilisé par les clés étrangères. |
| `name` | `String(32)` | Nom canonique du système ou de la tradition astrologique. Unique. |
| `inherits_from_system_id` | `Integer`, nullable | Parent d'héritage dans `astral_systems.id`; `hellenistic` et `medieval` héritent de `traditional`, tandis que `modern` et `traditional` restent racines. |

Systèmes seedés :

| Nom | Usage courant |
| --- | --- |
| `traditional` | Maîtrises traditionnelles, notamment `scorpio -> mars`, `aquarius -> saturn`, `pisces -> jupiter`. |
| `modern` | Dignités modernes et vocabulaire éditorial maison issu de `astral_house_interpretation_profiles.json`. |
| `hellenistic` | Référence disponible pour extensions historiques. |
| `medieval` | Référence disponible pour extensions historiques. |

Point d'architecture :

- Les données sources JSON peuvent encore contenir des libellés comme `"system": "traditional"` ou `"tradition": "modern"`.
- Le seed applicatif résout ces libellés vers `astral_systems.id` avant insertion.
- Les tables relationnelles ne doivent pas stocker ces valeurs en dur quand une FK vers `astral_systems` existe.

### `astral_planet_sign_dignities`

Définie par `AstralPlanetSignDignityModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Qualification :

- Table de référence stable non versionnée.
- Décrit la condition essentielle d'une planète dans un signe pour un système astrologique donné.
- Remplace `astral_sign_rulerships` comme source canonique des maîtrises principales traditionnelles utilisées par le contexte de prédiction actuel.
- Alimentée depuis `docs/db_seeder/astrology/astral_planet_sign_dignities.json` par la migration `20260513_0092_create_astral_planet_sign_dignities.py` et par le seed applicatif idempotent.

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

- La table est chargée par `PredictionReferenceRepository.get_planet_sign_dignities(system="traditional")`.
- Les maîtrises de signes sont dérivées par `get_sign_rulerships_from_dignities`, en filtrant les domiciles traditionnels primaires.
- Le résultat reste injecté dans `PredictionContext.sign_rulerships` pour préserver le contrat métier consommé par `NatalSensitivity`.
- Aucun calcul de position astronomique ne dépend de cette table : elle qualifie une relation planète/signe, elle ne produit pas les positions.

## Tables adjacentes nécessaires au fonctionnement

Ces tables ne sont pas des tables de planètes, mais elles structurent leur usage.

### `astral_reference_versions`

Rôle :

- Versionne les paramètres de prédiction, pas le vocabulaire stable `planets`.
- Verrouille les versions via `is_locked`.
- Les modèles paramétriques déclenchent `_ensure_reference_version_is_mutable` avant mise à jour.

Tables planétaires versionnées via `reference_version_id` :

- `astral_prediction_daily_planet_profiles`
- `astral_planet_category_weights`

### `prediction_categories`

Rôle :

- Catalogue les domaines de prédiction : énergie, humeur, santé, travail, carrière, argent, amour, intimité, foyer, social, communication, créativité.
- Sert de cible aux poids `astral_planet_category_weights`.

### `astral_aspects`, `astral_aspect_profiles` et `astral_aspect_definitions`

Rôle :

- Ne référencent pas directement les planètes.
- `astral_aspects` définit les 20 aspects canoniques seedés depuis `docs/db_seeder/astrology/astral_aspects.json`, avec `family -> astral_aspect_families.id`.
- `astral_aspect_profiles` porte le scoring prédictif par aspect : intensité, valence, polarité, énergie, multiplicateur d'orbe et comportement de phase.
- `astral_aspect_definitions` porte l'activation par système astrologique et l'orbe par défaut ; l'ancien `astral_aspects.default_orb_deg` n'existe plus.
- Les calculs runtime V1 restent centrés sur les cinq aspects majeurs, même si le référentiel relationnel contient aussi les aspects mineurs et avancés.
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

1. `astral_planets` fournit les codes stables et `swe_id`.
2. `astral_planet_definitions` ajoute rôle, type d'objet, vitesse structurelle, polarité typique et flags physiques.
3. `astral_prediction_daily_planet_profiles` ajoute les paramètres produit de pondération prédictive par version de référence.
4. `astral_planet_category_weights` mappe chaque planète vers les catégories de vie.
5. `astral_planet_sign_dignities` fournit les dignités planète -> signe normalisées.
6. `PredictionReferenceRepository.get_sign_rulerships_from_dignities` dérive le mapping signe -> planète maîtresse depuis les domiciles traditionnels primaires.
7. `PredictionReferenceRepository.get_planet_profiles` fusionne profil daily et définition structurelle dans `PlanetProfileData`.
8. `AstrologyRuntimeReferenceRepository` expose les planètes, dignités et classes de corps dans `AstrologyRuntimeReference`.
9. `EventDetector` détecte les événements planète transitante -> cible natale.
10. `DomainRouter` route les événements vers les catégories avec les poids planète/maison.
11. `ContributionCalculator` calcule la contribution numérique.
12. `TransitSignalBuilder` produit les timelines continues par thème.
13. `daily_prediction_*` persiste les scores, contributeurs et points de bascule.

## Points d'attention

- `astral_planets` est désormais stable et non versionnée. Ne pas réintroduire `reference_version_id` dans cette table sans décision d'architecture.
- Les paramètres d'interprétation ou de scoring de prédiction quotidienne doivent aller dans `astral_prediction_daily_planet_profiles` ou `astral_planet_category_weights`, pas dans `astral_planets`.
- Les attributs structurels de corps (`is_luminary`, rôle astrologique, vitesse, polarité typique, visibilité à l'oeil nu) doivent rester dans `astral_planet_definitions` et ses taxonomies, pas dans la table daily.
- `astral_prediction_daily_planet_profiles` a été simplifiée : ne pas y réintroduire `class_code`, `speed_rank`, `speed_class`, `typical_polarity`, `orb_active_deg`, `orb_peak_deg` ou `keywords_json`.
- `astral_planet_interpretation_profiles` est éditoriale : ne pas l'utiliser comme source de scoring, d'orbes ou de calcul astronomique.
- Les données astronomiques calculées pour un thème astral ne doivent pas être ajoutées dans `astral_prediction_daily_planet_profiles`; elles relèvent des payloads de calcul (`chart_results`) ou des objets runtime de thème.
- `astral_planet_sign_dignities` est non versionnée dans l'état courant. Elle représente une taxonomie canonique des dignités planète/signe par système, alimentée depuis le JSON documentaire.
- `astral_systems` est désormais le référentiel partagé pour les systèmes/traditions astrologiques : les dignités planétaires et les profils d'interprétation de maisons doivent y référencer un identifiant, pas du texte libre.
- `astral_sign_rulerships` ne doit pas être réintroduite : les maîtrises sont une vue filtrée de `astral_planet_sign_dignities`.
- Le moteur actuel utilise le système `traditional` pour éviter de remplacer `scorpio -> mars`, `aquarius -> saturn` et `pisces -> jupiter` par des maîtrises modernes.
- Les colonnes JSON (`result_payload`, `contributors_json`, `driver_json`) ne garantissent pas l'intégrité référentielle avec `astral_planets`. Elles servent à la traçabilité et à la restitution.
- Les noms de planètes peuvent exister en minuscules (`sun`) dans les tables de référence et en forme titrée (`Sun`) dans certains objets runtime. Les repositories et calculateurs normalisent partiellement ces accès.

## Fichiers sources consultés

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/models/interpretation_reference.py`
- `backend/app/infra/db/models/daily_prediction.py`
- `backend/app/infra/db/models/chart_result.py`
- `backend/app/infra/db/models/user_prediction_baseline.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/astrology_reference_sources.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/planet_catalog.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/services/house_interpretation_seed_service.py`
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
- `backend/migrations/versions/20260513_0093_drop_astral_sign_rulerships.py`
- `backend/migrations/versions/20260513_0094_rename_house_tables.py`
- `backend/migrations/versions/20260513_0095_create_astral_house_systems.py`
- `backend/migrations/versions/20260514_0096_create_house_interpretation_profiles.py`
- `backend/migrations/versions/20260514_0097_rename_astral_house_interpretation_profiles.py`
- `backend/migrations/versions/20260514_0098_reference_house_interpretation_system.py`
- `backend/migrations/versions/20260514_0099_rename_astral_reference_tables.py`
- `backend/migrations/versions/20260514_0102_normalize_astral_aspects.py`
- `backend/migrations/versions/20260515_0112_create_astral_object_reference_tables.py`
- `backend/migrations/versions/20260515_0114_create_astral_planet_reference_tables.py`
- `backend/migrations/versions/20260515_0115_simplify_daily_planet_profiles.py`
- `docs/db_seeder/astrology/astral_planets.json`
- `docs/db_seeder/astrology/astral_planet_definitions.json`
- `docs/db_seeder/astrology/astral_prediction_daily_planet_profiles.json`
- `docs/db_seeder/astrology/astral_planet_interpretation_profiles.json`
- `docs/db_seeder/astrology/astral_planet_sign_dignities.json`
- `docs/db_seeder/astrology/astral_house_interpretation_profiles.json`
