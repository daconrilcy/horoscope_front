# Tables liées aux maisons astrologiques et rôles

## Périmètre

Ce document recense les tables du backend liées directement ou indirectement aux maisons astrologiques dans l'état courant du schéma Alembic, après les migrations `20260218_0001_create_reference_tables.py`, `20260307_0032_migration_a_prediction_reference_tables.py`, `20260308_0038_add_house_system_effective_to_daily_prediction_runs.py`, `20260512_0086_deversion_astrology_structures.py`, `20260513_0094_rename_house_tables.py`, `20260513_0095_create_astral_house_systems.py`, `20260514_0096_create_house_interpretation_profiles.py`, `20260514_0097_rename_astral_house_interpretation_profiles.py`, `20260514_0098_reference_house_interpretation_system.py`, `20260514_0099_rename_astral_reference_tables.py`, `20260514_0102_normalize_astral_aspects.py`, `20260515_0109_create_astral_house_axis_definitions.py`, `20260515_0110_create_astral_house_axis_members.py`, `20260515_0111_deversion_astral_house_axis_definitions.py` et `20260515_0112_create_astral_object_reference_tables.py`.

Deux catégories sont distinguées :

- Tables SQL qui décrivent le vocabulaire stable des maisons, les systèmes de maisons ou leur paramétrage prédictif.
- Tables et payloads qui consomment, calculent ou historisent les maisons sous forme de JSON ou de colonnes de trace.

Point important : les cuspides réelles d'un thème ne sont pas stockées dans une table relationnelle dédiée. Elles sont calculées à l'exécution par SwissEph ou par le moteur simplifié, enrichies dans le runtime astrologique, puis transportées dans les objets `NatalResult`, les projections IA et les payloads `chart_results.result_payload`.

Depuis le refactor runtime, les sources JSON canoniques de seed sont sous `docs/db_seeder/astrology/`. Les tables stables sont chargées par `ReferenceRepository.seed_version_defaults`, puis `AstrologyRuntimeReferenceRepository` expose une photographie immutable au domaine via `AstrologyRuntimeReferenceMapper`.

## Héritage des systèmes astrologiques

Le référentiel `astral_systems` est commun aux doctrines de maisons, d'aspects et de dignités planétaires. Son héritage explicite est stocké dans `astral_systems.inherits_from_system_id` : `modern` et `traditional` sont racines, `hellenistic` hérite de `traditional`, et `medieval` hérite de `traditional`.

Pour les maisons, cet héritage ne change pas les cuspides ni les systèmes de maisons physiques. Il documente seulement la tradition astrologique commune utilisée par les profils éditoriaux et évite que les doctrines liées aux orbes soient recopiées dans des systèmes enfants.

## Vue d'ensemble

| Table | Lien aux maisons | Rôle principal | Versionnée |
| --- | --- | --- | --- |
| `astral_houses` | Table canonique des maisons 1 à 12 | Vocabulaire stable : numéro et nom métier | Non |
| `astral_house_systems` | Table canonique des systèmes de maisons | Référence stable pour l'UI, les fallbacks, les analytics et les limites astronomiques | Non |
| `astral_house_modalities` | Taxonomie `angular`, `succedent`, `cadent` | Référence structurelle des modalités de maisons ; le profil daily conserve encore `house_kind` en texte | Non |
| `astral_angle_points` | Angles liés aux cuspides 1/7/10/4 | Référence stable des points `asc`, `dsc`, `mc`, `ic` et de leur maison associée | Non |
| `astral_house_axis_definitions` | Définition éditoriale des axes maison opposée | Axe localisé par système astrologique et langue | Non |
| `astral_house_axis_members` | `house_id -> astral_houses.id`, `opposite_house_id -> astral_houses.id` | Association canonique maison -> axe -> maison opposée | Non |
| `astral_house_interpretation_profiles` | `house_id -> astral_houses.id`, `astral_system_id -> astral_systems.id` | Vocabulaire éditorial pour interprétation, prompts IA et variantes langue/système astrologique | Oui, via `reference_version_id` |
| `astral_prediction_daily_house_profiles` | `house_id -> astral_houses.id` | Source SQL scindée en profil astrologique stable et profil produit prédictif | Oui, via `reference_version_id` |
| `astral_house_category_weights` | `house_id -> astral_houses.id` | Routage maison -> catégorie de vie pour le scoring | Oui, via `reference_version_id` |
| `prediction_rulesets` | `house_system_id -> astral_house_systems.id` | Système de maisons demandé par un ruleset | Non pour le système, versionné par le ruleset |
| `daily_prediction_runs` | `house_system_effective_id -> astral_house_systems.id` | Trace du système de maisons réellement appliqué pendant un run daily | Indirectement via le run |
| `user_prediction_baselines` | `house_system_effective_id -> astral_house_systems.id` | Sépare les baselines selon le système de maisons effectif | Indirectement via fenêtre/version |
| `chart_results` | JSON `result_payload.houses`, `result_payload.house_rulers`, `result_payload.angles`, `result_payload.planets[*].house` | Snapshot du calcul natal : cuspides, signes des cuspides, maîtres de maisons, force typée, angles et maison des planètes | Version texte dans payload et colonnes |
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
- Sert de cible relationnelle à `astral_house_interpretation_profiles`, `astral_prediction_daily_house_profiles` et `astral_house_category_weights`.
- Ne contient pas de longitude, cuspide, signe de cuspide, système de maisons ou donnée utilisateur.

Maisons seedées par `ReferenceRepository.seed_version_defaults` :

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

Source actuelle : section `houses` de `docs/db_seeder/astrology/astral_structural_reference_catalog.json`.

### `astral_house_systems`

Définie par `AstralHouseSystemModel` dans `backend/app/infra/db/models/reference.py`.

Créée et seedée par `20260513_0095_create_astral_house_systems.py`.

Qualification :

- Table de référence canonique des systèmes de maisons.
- Stable et non versionnée.
- Ne calcule aucune cuspide et ne remplace pas SwissEph ni le moteur simplifié.
- Sert à éviter les typos, alimenter l'UI, piloter les fallbacks, tracer les analytics et documenter les limites astronomiques.

Colonnes principales :

| Colonne | Type | Rôle |
| --- | --- | --- |
| `id` | `BigInteger` | Identifiant technique utilisé par les tables runtime. |
| `code` | `String(50)` | Code stable applicatif, par exemple `placidus` ou `whole_sign`. Unique. |
| `name` | `String(100)` | Libellé lisible pour l'UI et l'administration. |
| `description` | `Text` | Description métier du mode de découpage. |
| `astronomical_family` | `String(50)` | Famille astronomique : `quadrant`, `sign_based` ou `ascendant_based`. |
| `supports_polar_regions` | `Boolean` | Indique si le système reste exploitable dans les régions polaires. |
| `is_quadrant_based` | `Boolean` | Distingue les systèmes basés sur les quadrants ASC/MC/DSC/IC. |
| `requires_precise_birth_time` | `Boolean` | Indique une forte sensibilité à l'heure de naissance. |
| `sort_order` | `Integer` | Ordre d'affichage UI. |
| `is_active` | `Boolean` | Permet de masquer un système sans supprimer sa référence historique. |

Contraintes :

- Unicité sur `code`.
- Check `astronomical_family IN ('quadrant', 'sign_based', 'ascendant_based')`.

Systèmes seedés :

| Code | Nom | Famille | Régions polaires | Quadrant | Heure précise | Ordre |
| --- | --- | --- | --- | --- | --- | ---: |
| `placidus` | Placidus | `quadrant` | Non | Oui | Oui | 10 |
| `whole_sign` | Whole Sign | `sign_based` | Oui | Non | Non | 20 |
| `equal` | Equal House | `ascendant_based` | Oui | Non | Oui | 30 |
| `porphyry` | Porphyry | `quadrant` | Oui | Oui | Oui | 40 |

Source actuelle : `docs/db_seeder/astrology/astral_house_system.json`, synchronisée par `sync_house_system_seed_data`.

Nuance importante :

- `whole_sign.requires_precise_birth_time = false` ne signifie pas qu'une heure de naissance est inutile.
- Whole Sign dépend encore du signe ascendant ; il est seulement moins sensible à quelques minutes d'écart que Placidus, Porphyry ou Equal House.

Constantes applicatives :

- `backend/app/domain/astrology/house_system_codes.py` expose `HouseSystemCode`.
- Les services continuent à manipuler les codes (`placidus`, `whole_sign`, `equal`, `porphyry`) mais les tables runtime stockent les identifiants SQL.

### `astral_angle_points`

Définie par `AstralAnglePointModel` dans `backend/app/infra/db/models/reference.py`.

Qualification :

- Table stable et non versionnée.
- Seedée depuis `docs/db_seeder/astrology/astral_angle_points.json`.
- Chargée par `AstrologyRuntimeReferenceRepository._load_angle_points`.
- Validée comme obligatoire pour `asc`, `dsc`, `mc` et `ic`.

| Code | Libellé | Axe | Maison associée | Opposé |
| --- | --- | --- | ---: | --- |
| `asc` | ASC / Ascendant | `horizontal` | 1 | `dsc` |
| `dsc` | DSC / Descendant | `horizontal` | 7 | `asc` |
| `mc` | MC / Midheaven | `vertical` | 10 | `ic` |
| `ic` | IC / Imum Coeli | `vertical` | 4 | `mc` |

Ces lignes structurent les angles du thème et les règles d'aspects impliquant des points ou angles. Elles ne stockent pas la longitude réelle des angles d'un thème utilisateur.

### `astral_house_modalities`

Définie par `AstralHouseModalityModel` dans `backend/app/infra/db/models/reference.py`.

Valeurs seedées depuis `docs/db_seeder/astrology/astral_house_modalities.json` :

| id logique | name |
| ---: | --- |
| 1 | `angular` |
| 2 | `succedent` |
| 3 | `cadent` |

La table documente la taxonomie stable. Le profil prédictif `astral_prediction_daily_house_profiles.house_kind` reste actuellement une colonne texte, scindée ensuite dans `HouseAstrologyProfile`.

## Table éditoriale d'interprétation

### `astral_house_interpretation_profiles`

Définie par `HouseInterpretationProfileModel` dans `backend/app/infra/db/models/interpretation_reference.py`.

Créée par `20260514_0096_create_house_interpretation_profiles.py`, renommée par `20260514_0097_rename_astral_house_interpretation_profiles.py`, puis reliée à `astral_systems` par `20260514_0098_reference_house_interpretation_system.py`.

Qualification :

- Table de vocabulaire interprétatif, distincte du runtime astrologique et du scoring produit.
- Versionnée par `reference_version_id` pour permettre l'évolution du ton éditorial, des prompts, des marchés, des langues et des systèmes astrologiques.
- Rattachée à `astral_houses.id`, sans ajouter de contenu interprétatif dans `astral_houses`.
- Rattachée à `astral_systems.id` pour éviter une tradition éditoriale stockée en texte libre.
- Alimentée par `sync_house_interpretation_profiles` depuis `docs/db_seeder/astrology/astral_house_interpretation_profiles.json`. Le JSON peut contenir `"tradition": "modern"`, mais le seed résout cette valeur vers `astral_systems.id` avant insertion.
- Non consommée par `domain/astrology` : le runtime conserve uniquement les faits calculés du thème.

Colonnes principales :

| Colonne | Type | Rôle |
| --- | --- | --- |
| `reference_version_id` | `Integer` | Version éditoriale ou référentielle active. |
| `house_id` | `Integer` | Maison canonique ciblée. |
| `language` | `String(16)` | Langue du profil, par exemple `en` ou `fr`. |
| `astral_system_id` | `ForeignKey(astral_systems.id)` | Système astrologique éditorial, par exemple `modern` ou `traditional`. |
| `title` | `String(128)` | Titre court exploitable en restitution ou prompt. |
| `summary` | `Text` | Synthèse éditoriale de la maison. |
| `*_keywords_json` | `Text` | Listes JSON de mots-clés par axe d'interprétation. |
| `body_parts_json`, `archetypes_json`, `dos_json`, `donts_json`, `prompt_hints_json` | `Text` | Matériau éditorial structuré pour interprétation et prompts IA. |
| `micro_note` | `Text` | Note courte optionnelle. |

Contraintes :

- Unicité sur `(reference_version_id, house_id, language, astral_system_id)`.
- Clés étrangères vers `astral_reference_versions.id`, `astral_houses.id` et `astral_systems.id`.
- Mise à jour bloquée quand la version de référence liée est verrouillée.

## Tables de paramétrage du moteur de prédiction quotidienne

### `astral_prediction_daily_house_profiles`

Définie par `HouseProfileModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Qualification :

- Table de configuration du moteur de prédiction quotidienne.
- Ne calcule pas les cuspides ni l'occupation des maisons.
- Qualifie une maison déjà identifiée par le calcul astrologique, puis alimente deux contrats Python distincts :
  - `HouseAstrologyProfile`, propriétaire des attributs astrologiques stables ;
  - `HousePredictionProfile`, propriétaire des attributs produit de prédiction.

Clés :

- `house_id -> astral_houses.id`
- `reference_version_id -> astral_reference_versions.id`
- Unicité : `(reference_version_id, house_id)`

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `reference_version_id` | Version de référence qui porte ce paramétrage prédictif. |
| `house_id` | Maison canonique concernée. |
| `house_kind` | Type structurel astrologique : `angular`, `succedent` ou `cadent`. Exposé dans `HouseAstrologyProfile.house_kind`. |
| `visibility_weight` | Poids produit de visibilité de la maison. Exposé dans `HousePredictionProfile.visibility_weight`. |
| `base_priority` | Priorité éditoriale ou prédictive de base. Exposée dans `HousePredictionProfile.base_priority`. |
| `keywords_json` | Mots-clés produit optionnels, parsés dans `HousePredictionProfile.keywords`. |
| `micro_note` | Note éditoriale courte, exposée dans `HousePredictionProfile.micro_note`. |

Rôle applicatif :

- Chargée par `PredictionReferenceRepository.get_house_profiles`.
- Scindée par le repository en deux mappings :
  - `PredictionContext.house_astrology_profiles` : `house_number -> HouseAstrologyProfile` ;
  - `PredictionContext.house_prediction_profiles` : `house_number -> HousePredictionProfile`.
- Validée comme obligatoire par `PredictionContextLoader._validate_context`.
- Utilisée par `NatalSensitivityCalculator._house_placement_score` via `house_astrology_profiles` pour donner une force de placement :
  - `angular` : `1.0`
  - `succedent` : `0.2`
  - `cadent` : `-0.5`
- Les champs produit (`visibility_weight`, `base_priority`, `keywords`, `micro_note`) restent dans le contrat prediction et ne doivent pas apparaître sous `backend/app/domain/astrology`.

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
- `reference_version_id -> astral_reference_versions.id`
- Unicité : `(reference_version_id, house_id, category_id)`

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `reference_version_id` | Version de référence active pour les poids de routage. |
| `house_id` | Maison canonique source. |
| `category_id` | Catégorie de prédiction cible. |
| `weight` | Intensité du lien maison -> catégorie. |
| `routing_role` | Rôle qualitatif : `primary` ou `secondary`. Sert de multiplicateur dans certains calculateurs V3. |

Rôle applicatif produit :

- Chargée par `PredictionReferenceRepository.get_house_category_weights`.
- Injectée dans `PredictionContext.house_category_weights`.
- Utilisée par `DomainRouter._project_houses_to_categories` pour transformer le vecteur maison d'un événement en poids par catégorie.
- Utilisée par `TransitSignalBuilder._build_weighted_routing` et `IntradayActivationBuilder._build_weighted_routing` pour construire les index de routage continus.
- Utilisée par `NatalSensitivityCalculator` pour identifier les maisons pertinentes d'une catégorie et calculer, en consommant les faits disponibles dans `NatalChart.houses` :
  - l'occupation natale `Occ(c)`,
  - les maîtrises de maisons `Rul(c)`,
  - l'angularité des significateurs `Ang(c)`.

Logique de routage :

- Pour un événement avec cible natale, `DomainRouter` construit un vecteur maison :
  - il lit en priorité les métadonnées runtime `natal_house_runtime_target` et `natal_house_runtime_transited` ;
  - il accepte aussi une maison runtime sérialisée ou un numéro brut, pour les payloads JSON ;
  - `1.0` sur la maison cible si la maison transitée est absente ou identique ;
  - `0.70` sur la maison natale cible et `0.30` sur la maison natale transitée si elles diffèrent.
- Chaque maison du vecteur est projetée vers les catégories via `astral_house_category_weights`.
- Le résultat maison est combiné avec le blend planète -> catégorie.
- `DomainRouter` reste propriétaire du mapping produit maison -> catégorie ; il ne recalcule ni signe de cuspide ni maître de maison.
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

### `astral_reference_versions`

Rôle :

- Versionne les paramètres de prédiction, pas le vocabulaire stable `astral_houses`.
- Verrouille les versions via `is_locked`.
- Les mises à jour de `astral_house_interpretation_profiles`, `astral_prediction_daily_house_profiles` et `astral_house_category_weights` passent par `_ensure_reference_version_is_mutable`.

Tables liées aux maisons versionnées via `reference_version_id` :

- `astral_prediction_daily_house_profiles`
- `astral_house_category_weights`
- `astral_house_interpretation_profiles`

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

### `astral_house_axis_definitions` et `astral_house_axis_members`

Définies par `AstralHouseAxisDefinitionModel` et `AstralHouseAxisMemberModel` dans `backend/app/infra/db/models/interpretation_reference.py`.

Qualification :

- Tables stables et non versionnées depuis `20260515_0111_deversion_astral_house_axis_definitions.py`.
- Seedées par `ReferenceRepository.seed_house_axis_defaults`.
- Sources : `docs/db_seeder/astrology/astral_house_axis_definitions.json` et `docs/db_seeder/astrology/astral_house_axis_members.json`.
- `astral_house_axis_definitions` est localisée par `astral_system_id`, `language_id` et `key`.
- `astral_house_axis_members` impose une ligne par maison (`house_id` unique) et une maison opposée distincte.

Axes seedés :

| Maisons | Clé | Titre |
| --- | --- | --- |
| 1 / 7 | `self_relationship` | Self and Relationship |
| 2 / 8 | `resources_sharing` | Resources and Sharing |
| 3 / 9 | `local_distant` | Local and Distant |
| 4 / 10 | `private_public` | Private and Public |
| 5 / 11 | `creation_collective` | Creation and Collective |
| 6 / 12 | `control_surrender` | Control and Surrender |

`ReferenceRepository._get_house_axes` expose au runtime la projection moderne anglophone `house_number`, `opposite_house`, `theme`. `HouseRuntimeData.axis` consomme ensuite cette donnée sous forme `HouseAxisRuntimeData`.

### `prediction_rulesets`

Rôle :

- Porte le système de maisons demandé via `house_system_id -> astral_house_systems.id`.
- `RulesetData.house_system` expose toujours le code applicatif pour les services.
- Ce système est transmis au moteur de prédiction quotidienne comme `house_system_requested`.
- Le système effectivement utilisé peut différer en cas de repli runtime.

Limite actuelle :

- Le ruleset peut référencer les quatre systèmes seedés (`placidus`, `equal`, `whole_sign`, `porphyry`).
- Le calcul natal sait déléguer ces quatre systèmes à `houses_provider`.
- Le calcul daily ne consomme pas encore `house_system_requested` pour choisir le système des cuspides courantes : `AstroCalculator` tente toujours Placidus, puis Porphyry en fallback si Placidus échoue.
- En conséquence, `equal` et `whole_sign` sont des références canoniques disponibles pour le natal et l'UI, mais ils ne sont pas encore supportés comme systèmes effectifs de calcul daily.

## Données de calcul et de résultat

### Cuspides calculées

Les cuspides ne sont pas des lignes SQL. Elles sont produites à l'exécution :

- Côté thème natal, `build_natal_result` appelle `houses_provider.calculate_houses` en mode `swisseph`.
- `houses_provider.calculate_houses` appelle `swe.houses_ex` et retourne `HouseData`.
- `HouseData.cusps` contient les 12 cuspides normalisées dans `[0, 360)`.
- `HouseData.ascendant_longitude` et `HouseData.mc_longitude` exposent ASC et MC.
- Les systèmes publiquement supportés par `houses_provider` sont `placidus`, `equal`, `whole_sign` et `porphyry`.

En moteur daily V1/V3 :

- `AstroCalculator` reçoit les `natal_cusps` calculées pour le thème natal.
- À chaque pas temporel, il calcule les cuspides courantes via `swe.houses`.
- Il tente `placidus` puis replie sur `porphyry` si Placidus échoue.
- Il calcule `natal_house_transited` pour chaque planète transitante en comparant sa longitude aux cuspides natales.
- Cette limite est volontairement documentée tant que le daily ne route pas explicitement vers les quatre systèmes canoniques depuis `house_system_requested`.

#### Processus détaillé du calcul des cuspides natales

1. `backend/app/services/natal/calculation_service.py` résout les options de calcul (`zodiac`, `frame`, `house_system`) puis choisit le moteur avec `_resolve_engine`.

   Extrait :

   ```python
   requires_accurate = (
       zodiac == ZodiacType.SIDEREAL
       or frame == FrameType.TOPOCENTRIC
       or house_system != HouseSystemType.EQUAL
   )
   ```

   Conséquence : un système de maisons non `equal` impose le moteur précis SwissEph et `accurate=True`.

2. `backend/app/domain/astrology/natal_calculation.py` construit le résultat natal. En mode `swisseph`, `build_natal_result` appelle `_build_swisseph_houses`.

   Extrait :

   ```python
   houses_raw, effective_house_system = _build_swisseph_houses(
       prepared.julian_day,
       birth_lat,
       birth_lon,
       house_numbers,
       house_system=house_system,
       frame=frame,
       altitude_m=altitude_m,
   )
   ```

3. `_build_swisseph_houses` délègue le calcul astronomique à `backend/app/domain/astrology/houses_provider.py`.

   Extrait :

   ```python
   house_data = calc_sw_houses(
       jdut,
       lat,
       lon,
       house_system=house_system,
       frame=frame,
       altitude_m=altitude_m,
   )
   houses_raw = [
       {"number": number, "cusp_longitude": house_data.cusps[number - 1]}
       for number in house_numbers
       if 1 <= number <= 12
   ]
   ```

4. `backend/app/domain/astrology/houses_provider.py` mappe le nom public du système vers le code SwissEph, puis appelle `swe.houses_ex`.

   Extraits :

   ```python
   SWISS_HOUSE_SYSTEM_BYTES = {
       HouseSystemCode.PLACIDUS: b"P",
       HouseSystemCode.EQUAL: b"E",
       HouseSystemCode.WHOLE_SIGN: b"W",
       HouseSystemCode.PORPHYRY: b"O",
   }
   ```

   ```python
   cusps_raw, ascmc_raw = swe.houses_ex(jdut, lat, lon, hsys_code)
   ```

5. Le même fichier extrait 12 cuspides et les normalise dans `[0, 360)`.

   Extrait :

   ```python
   if len(cusps_raw) >= 13:
       source = cusps_raw[1:13]
   elif len(cusps_raw) == 12:
       source = cusps_raw
   return tuple(normalize_360(float(value)) for value in source)
   ```

6. `backend/app/domain/astrology/natal_calculation.py` valide ensuite le résultat avec `_validate_house_cusps` : 12 cuspides, valeurs numériques finies, normalisées et non dupliquées.

7. Les maisons des planètes sont assignées avec `assign_house_number` dans `backend/app/domain/astrology/calculators/houses.py`, en testant la longitude dans l'intervalle entre la cuspide de la maison courante et celle de la maison suivante.

   Extrait :

   ```python
   start = float(house["cusp_longitude"])
   end = float(ordered[(index + 1) % len(ordered)]["cusp_longitude"])
   if contains_angle(longitude, start, end):
       return int(house["number"])
   ```

8. En moteur simplifié, le même fichier fournit un calcul `equal` approximatif, sans SwissEph.

   Extrait :

   ```python
   ascendant_longitude = (julian_day * 0.5) % 360.0
   cusp_longitude = round((ascendant_longitude + (number - 1) * 30.0) % 360.0, 6)
   ```

   Ce chemin est un fallback ou un moteur interne simplifié ; il ne correspond pas au calcul astronomique réel des maisons.

9. Le pipeline enrichit ensuite chaque maison via `backend/app/domain/astrology/builders/house_runtime_builder.py`.

   Pipeline runtime :

   ```text
   cuspides SwissEph ou equal simplifié
   → signe de cuspide
   → signes contenus
   → signes interceptés
   → maître déjà résolu
   → occupants
   → axe opposé
   → score interprétatif
   → HouseRuntimeData
   ```

10. `backend/app/services/chart/json_builder.py` projette la maison runtime dans le JSON public. Il ne recalcule pas la logique astrologique ; il sérialise les champs déjà portés par `HouseRuntimeData`.

   Exemple de payload maison :

   ```json
   {
     "number": 10,
     "cusp_longitude": 15.2,
     "cusp_sign": "aries",
     "sign": "aries",
     "contained_signs": ["aries", "taurus"],
     "intercepted_signs": [],
     "ruler": {
       "planet": "mars",
       "sign": "virgo",
       "house": 6
     },
     "occupants": [
       {
         "planet": "sun",
         "sign": "aries",
         "longitude": 15.2,
         "is_dominant": true
       }
     ],
     "axis": {
       "opposite_house": 4,
       "theme": "private_public"
     },
     "strength": {
       "score": 0.81,
       "dominant": true,
       "reasons": ["angular_house", "luminary_present"]
     }
   }
   ```

   Le champ `sign` est une compatibilité legacy synchronisée avec `cusp_sign`. Le champ canonique à consommer pour les nouveaux usages est `cusp_sign`.

#### Processus daily des cuspides courantes

Le moteur de prédiction quotidienne ne persiste pas les cuspides courantes en SQL. Il les calcule en mémoire dans `backend/app/domain/prediction/astro_calculator.py`.

Extraits :

```python
return self._run_house_calculation(ut_jd, b"P", HOUSE_SYSTEM_PLACIDUS)
```

```python
return self._run_house_calculation(ut_jd, b"O", HOUSE_SYSTEM_PORPHYRY)
```

```python
cusps_raw, ascmc_raw = swe.houses(ut_jd, self.latitude, self.longitude, house_code)
```

Le moteur tente donc Placidus (`b"P"`) puis Porphyry (`b"O"`) si Placidus échoue. Les cuspides natales restent l'entrée de référence pour déterminer la maison natale traversée par une planète transitante :

```python
cusp_start = self.natal_cusps[i]
cusp_end = self.natal_cusps[(i + 1) % 12]
```

Point de compatibilité :

- `house_system_requested` et `house_system_id` restent utiles pour tracer l'intention du ruleset et séparer les baselines.
- Le système effectif daily reflète aujourd'hui le résultat du couple Placidus -> Porphyry.
- Ajouter `equal` ou `whole_sign` au calcul daily nécessitera de faire dépendre `AstroCalculator` du système demandé et de définir la stratégie de fallback propre à chaque système.

### Détermination des maîtres de maison

Le thème natal expose toujours les maîtres de maisons dans `chart_results.result_payload.house_rulers`, et chaque maison runtime porte désormais directement son maître dans `chart_results.result_payload.houses[*].ruler`.

Contrat public à respecter :

```text
Source canonique runtime = houses[*].ruler
Projection legacy = house_rulers[]
```

`house_rulers[]` est un champ de compatibilité historique, conservé pour les anciens consommateurs, les évidences `HOUSE_*_RULER_*` et les prompts ou snapshots qui n'ont pas encore migré. Il ne doit pas devenir une seconde source de vérité : le serializer JSON le projette depuis `HouseRuntimeData.ruler` et ne recalcule jamais le maître depuis `cusp_sign` ou `sign_rulerships`.

La règle métier appliquée est stricte :

```text
maison
→ longitude de cuspide
→ signe de cuspide
→ planète maîtresse du signe
→ position natale de cette planète
```

Le maître d'une maison n'est donc pas stocké dans `astral_houses` et n'est pas une propriété intrinsèque de la maison. Il est calculé à l'exécution à partir du signe placé sur la cuspide.

#### Source canonique des maîtrises

Le mapping signe -> planète maîtresse vient exclusivement des dignités planétaires canoniques :

- table : `astral_planet_sign_dignities`
- filtre : `dignity_type = "domicile"`
- filtre : `is_primary = true`
- système par défaut : `traditional`

La lecture est portée par `backend/app/infra/db/repositories/prediction_reference_repository.py`.

Extraits :

```python
def get_sign_rulerships(self, system: str = "traditional") -> dict[str, str]:
    return self.get_sign_rulerships_from_dignities(system=system)
```

```python
return {
    row.sign_code: row.planet_code
    for row in self.get_planet_sign_dignities(system=system)
    if row.dignity_type == "domicile" and row.is_primary
}
```

Point important : il n'y a plus de fallback local signe -> planète dans le resolver natal. Si les dignités ne fournissent pas les 12 signes attendus, le calcul échoue avec une erreur de référence invalide au lieu d'inventer une valeur applicative parallèle.

`ReferenceDataService.seed_reference_version` synchronise aussi les dignités planétaires stables via `ensure_astral_planet_sign_dignities`, afin que le référentiel SQL reste la source unique même pour les calculs natals simples.

#### Service runtime natal

Le calcul est isolé dans `backend/app/domain/astrology/house_ruler_resolver.py`.

Entrées :

- `houses[]` : objets avec `number` et `cusp_longitude`.
- `planets[]` : objets avec `planet_code`, `sign_code` et `house_number`.
- `sign_rulerships` : mapping strict signe -> planète issu des dignités.

Sortie :

```json
[
  {
    "house_number": 7,
    "cusp_sign": "taurus",
    "ruler_planet": "venus",
    "ruler_planet_sign": "leo",
    "ruler_planet_house": 10
  }
]
```

Processus détaillé :

1. `backend/app/services/natal/calculation_service.py` charge les données de référence stables.
2. Le même service enrichit `reference_data` avec `PredictionReferenceRepository.get_sign_rulerships()`.
3. `backend/app/domain/astrology/natal_calculation.py` calcule les maisons et les positions planétaires.
4. `HouseRulerResolver` convertit chaque `cusp_longitude` en signe via `backend/app/domain/astrology/zodiac.py`.
5. Le resolver lit la planète maîtresse du signe dans `sign_rulerships`.
6. Le resolver retrouve la position de cette planète dans les positions natales.
7. `NatalResult.house_rulers` est rempli avec une ligne par maison.
8. `build_house_runtime_data` injecte le ruler correspondant dans `HouseRuntimeData.ruler`, sans recalculer la maîtrise.
9. `backend/app/services/chart/result_service.py` persiste cette donnée dans `chart_results.result_payload`.
10. `backend/app/services/chart/json_builder.py` expose `houses[*].ruler` comme source canonique et projette `house_rulers[]` depuis cette source pour la compatibilité historique.

#### Exemple complet

Pour une maison VII dont la cuspide est en Taureau :

```text
Maison VII
→ cuspide à 42.5°
→ signe Taureau
→ maître Vénus
→ Vénus natale en Lion maison X
```

Payload produit :

```json
{
  "house_number": 7,
  "cusp_sign": "taurus",
  "ruler_planet": "venus",
  "ruler_planet_sign": "leo",
  "ruler_planet_house": 10
}
```

Payload de la même information dans la maison enrichie :

```json
{
  "number": 7,
  "cusp_sign": "taurus",
  "ruler": {
    "planet": "venus",
    "sign": "leo",
    "house": 10
  }
}
```

#### Contrat public et évidences

`chart_results.result_payload.house_rulers[]` contient la projection legacy de `houses[*].ruler` :

- `house_number`
- `cusp_sign`
- `ruler_planet`
- `ruler_planet_sign`
- `ruler_planet_house`

Le catalogue d'évidence peut produire :

- `HOUSE_{num}_RULER_{PLANET}`
- `HOUSE_{num}_RULER_{PLANET}_H{house}`
- `HOUSE_{num}_RULER_{PLANET}_{SIGN}`

Exemples :

```text
HOUSE_7_RULER_VENUS
HOUSE_7_RULER_VENUS_H10
HOUSE_7_RULER_VENUS_LEO
```

#### Compatibilité avec le moteur de prédiction

Le moteur de prédiction quotidienne conserve son champ interne `NatalChart.house_sign_rulers`.

Ce nom reste ambigu historiquement : dans certains chemins, il transporte encore le signe de cuspide et non directement la planète maîtresse. Depuis CS-158, `NatalSensitivityCalculator` ne doit plus recalculer les maîtres depuis `sign_rulerships` : il lit les maîtres déjà résolus dans `NatalChart.houses[*].ruler` quand le runtime maison est disponible.

Le champ public `house_rulers[]` reste une projection legacy utile aux restitutions et à la compatibilité, mais la source structurelle canonique pour les calculateurs et serializers modernes est `houses[*].ruler`.

### Runtime riche des maisons natales

Depuis la Priorité 3, la maison natale n'est plus seulement une cuspide géométrique. Elle est représentée en mémoire par `HouseRuntimeData`, défini dans `backend/app/domain/astrology/runtime/house_runtime_data.py`.

Structure canonique :

| Champ | Rôle |
| --- | --- |
| `number` | Numéro de maison, de `1` à `12`. |
| `cusp_longitude` | Longitude de cuspide normalisée. |
| `cusp_sign` | Signe zodiacal de la cuspide, champ canonique. |
| `house_kind` | Qualité astrologique canonique : `angular`, `succedent` ou `cadent`. |
| `sign` | Alias legacy sérialisé, synchronisé avec `cusp_sign`. |
| `contained_signs` | Signes zodiacaux traversés par l'intervalle de maison. |
| `intercepted_signs` | Signes entièrement contenus sans être sur la cuspide courante ou suivante. |
| `ruler` | Maître runtime de la maison : planète, signe et maison de placement. |
| `occupants` | Planètes natales assignées à cette maison. |
| `axis` | Maison opposée et thème d'axe. |
| `strength` | Score interprétatif déterministe et raisons de dominance. |
| `metadata` | Extension runtime non relationnelle. |

Sous-structures :

- `HouseRulerRuntimeData` : `planet`, `sign`, `house`.
- `HouseOccupantRuntimeData` : `planet`, `sign`, `longitude`, `is_dominant`.
- `HouseAxisRuntimeData` : `opposite_house`, `theme`.
- `HouseStrengthRuntimeData` : `normalized_score`, `score` comme alias JSON historique, `level`, `dominant`, `reasons`, `modifiers`.

#### Signes contenus

`backend/app/domain/astrology/calculators/contained_signs.py` calcule les signes touchés par l'intervalle entre la cuspide courante et la cuspide suivante.

Exemple :

```text
75° Gémeaux → 142° Lion
→ ["gemini", "cancer", "leo"]
```

Le calcul supporte le passage `360° → 0°`.

#### Signes interceptés

`backend/app/domain/astrology/calculators/intercepted_signs.py` considère comme intercepté tout signe contenu qui n'est ni le signe de cuspide courant ni celui de la cuspide suivante.

Exemple :

```text
Maison 2 : cuspide Gémeaux
Maison 3 : cuspide Lion
Signes contenus : Gémeaux, Cancer, Lion
→ Cancer intercepté
```

Les maisons Whole Sign forcent `intercepted_signs = []`. Le builder normalise le système reçu, y compris quand il arrive sous forme `HouseSystemType.WHOLE_SIGN`.

#### Occupants

`backend/app/domain/astrology/builders/house_occupants_builder.py` regroupe les planètes natales par `planet.house_number` et produit `HouseOccupantRuntimeData`.

Règle actuelle de dominance d'occupant :

- `sun` et `moon` sont marqués `is_dominant = true`.
- Les autres planètes sont conservées comme occupants non dominants.

#### Axes

Les axes miroir sont maintenant portés par les tables canoniques
`astral_house_axis_definitions` et `astral_house_axis_members` :

| Maisons | Thème |
| --- | --- |
| 1 / 7 | `self_relationship` |
| 2 / 8 | `resources_sharing` |
| 3 / 9 | `local_distant` |
| 4 / 10 | `private_public` |
| 5 / 11 | `creation_collective` |
| 6 / 12 | `control_surrender` |

La maison opposée partage le même thème que son miroir.

#### Force interprétative

`backend/app/domain/astrology/interpretation/house_strength.py` produit une force interprétative déterministe. Depuis CS-156, le calcul est porté par `HouseStrengthEvaluator` dans la couche `domain/astrology/interpretation`, et non plus par le builder runtime lui-même.

Depuis CS-160, la force maison utilise un contrat typé :

- `normalized_score` : score normalisé borné entre `0.0` et `1.0`.
- `score` : alias de compatibilité JSON exposant la même valeur normalisée.
- `level` : niveau qualitatif stable, parmi `low`, `moderate` et `dominant`.
- `reasons` : raisons canoniques issues de `HouseStrengthReason`, sérialisées en chaînes stables dans le JSON public.
- `modifiers` : détail structuré des modificateurs astrologiques (`angularity_modifier`, `occupancy_modifier`, `ruler_condition_modifier`).

Sources prises en compte dans la première version :

- angularité : maisons angulaires, succédentes ou cadentes, aussi exposée par `HouseRuntimeData.house_kind` ;
- nombre d'occupants ;
- stellium à partir de trois occupants ;
- présence d'un luminaire ;
- placement du maître en maison angulaire ;
- maître dans son propre signe selon `sign_rulerships` ;
- proximité symbolique des angles ASC et MC pour les maisons 1 et 10.

Les raisons sont toujours explicites dans `strength.reasons`. Le code Python manipule des membres `HouseStrengthReason`; le JSON public garde les valeurs textuelles stables, par exemple :

```json
{
  "score": 1.0,
  "level": "dominant",
  "dominant": true,
  "reasons": [
    "baseline_house",
    "angular_house",
    "occupants_present",
    "stellium_present",
    "luminary_present",
    "ruler_in_own_sign",
    "mc_angle_proximity"
  ]
}
```

Ce score est interprétatif, pas astronomique. Il sert à prioriser la lecture narrative, IA ou prédictive.

Seuils actuels :

| Niveau | Condition sur `normalized_score` |
| --- | --- |
| `low` | `< 0.25` |
| `moderate` | `>= 0.25` et `< 0.60` |
| `dominant` | `>= 0.60` |

### `chart_results`

Définie par `ChartResultModel`.

Colonnes pertinentes :

| Colonne | Rôle |
| --- | --- |
| `reference_version` | Version du référentiel utilisée pour construire le thème. |
| `ruleset_version` | Version de règles utilisée. |
| `result_payload` | Snapshot JSON complet du résultat de thème. |

Rôle des données de maison dans `result_payload` :

- `houses[]` contient les maisons runtime enrichies : `number`, `cusp_longitude`, `cusp_sign`, `house_kind`, `sign`, `contained_signs`, `intercepted_signs`, `ruler`, `occupants`, `axis`, `strength`, `metadata`.
- `houses[].strength` expose `score` pour compatibilité, ajoute `level` et conserve des `reasons` textuelles stables issues de l'enum interne `HouseStrengthReason`.
- `house_rulers[]` conserve la projection historique du maître planétaire de chaque maison et sa position natale : `house_number`, `cusp_sign`, `ruler_planet`, `ruler_planet_sign`, `ruler_planet_house`.
- `planets[]` contient la maison occupée par chaque planète dans `house`, sauf en mode dégradé sans heure.
- `angles` dérive ASC, MC, DSC et IC des cuspides 1, 10, 7 et 4.
- Le catalogue d'évidence peut produire des identifiants `HOUSE_{num}_IN_{SIGN}`, `{PLANET}_H{house}`, `HOUSE_{num}_RULER_{PLANET}`, `HOUSE_{num}_RULER_{PLANET}_H{house}` et `HOUSE_{num}_RULER_{PLANET}_{SIGN}`.

Compatibilité :

- `cusp_sign` est le champ canonique.
- `sign` reste présent dans `houses[]` pour les consommateurs historiques.
- `house_rulers[]` reste présent pendant la transition, mais la maison runtime devient la source structurelle directe pour les moteurs narratifs et IA.

### `daily_prediction_runs`

Définie par `DailyPredictionRunModel`.

Colonne pertinente :

| Colonne | Rôle |
| --- | --- |
| `house_system_effective_id` | FK vers le système de maisons réellement retenu pour le run daily. Peut refléter un repli runtime. |

Rôle :

- Trace l'écart éventuel entre le système demandé et le système réellement appliqué.
- Utile pour diagnostiquer les cas où Placidus ne converge pas et où le moteur retient Porphyry.
- Le modèle expose toujours `house_system_effective` comme propriété Python lisible par les services, mais la persistance relationnelle passe par `house_system_effective_id`.

### `user_prediction_baselines`

Définie par `UserPredictionBaselineModel`.

Colonne pertinente :

| Colonne | Rôle |
| --- | --- |
| `house_system_effective_id` | FK vers le système de maisons utilisé pour calculer la baseline. |

Rôle :

- Empêche de mélanger des baselines issues de systèmes de maisons différents.
- La contrainte d'unicité inclut `house_system_effective_id`.
- `UserPredictionBaselineRepository` résout le code applicatif vers `astral_house_systems.id` avant de filtrer ou d'upserter.

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

1. `ReferenceRepository.seed_version_defaults` garantit les 12 lignes `astral_houses`.
2. La migration `20260513_0095` garantit les lignes `astral_house_systems` et migre les traces runtime vers des clés étrangères.
3. `sync_house_interpretation_profiles` alimente `astral_house_interpretation_profiles` depuis le JSON éditorial en résolvant les maisons par numéro et les traditions par `astral_systems.name`.
4. `PredictionReferenceRepository` charge `astral_prediction_daily_house_profiles` et le scinde en `house_astrology_profiles` et `house_prediction_profiles` pour la version de référence active.
5. Le même repository charge `astral_house_category_weights` comme mapping produit maison -> catégorie.
6. `PredictionContextLoader` valide que les deux familles de profils de maisons existent puis fige le contexte.
7. Pour un thème natal, `build_natal_result` lit `reference_data["houses"]` pour connaître les numéros attendus.
8. `houses_provider.calculate_houses` calcule les cuspides, l'Ascendant et le Milieu du Ciel via SwissEph.
9. `build_natal_result` valide qu'il y a exactement 12 cuspides normalisées et non dupliquées.
10. `assign_house_number` assigne chaque planète natale à une maison à partir de sa longitude et des intervalles de cuspides.
11. `HouseRulerResolver` calcule `house_rulers[]` à partir des cuspides, des positions planétaires et du mapping signe -> maître issu des dignités.
12. `build_house_runtime_data` construit `HouseRuntimeData[]` avec signes contenus, interceptions, ruler intégré, occupants, axe et `house_kind`.
13. `HouseStrengthEvaluator` produit `HouseStrengthRuntimeData` avec score normalisé, niveau, raisons enumérées et modificateurs.
14. `chart_json_builder` projette les maisons enrichies, les maîtres de maisons, la force typée, les maisons des planètes et les angles dans le payload public.
15. Pour la prédiction quotidienne, `EngineOrchestrator` extrait les cuspides natales depuis `house_cusps` ou `houses` et réhydrate les forces maison sérialisées de façon stricte.
16. `AstroCalculator` calcule les états astrologiques par pas temporel et la maison natale transitée par chaque planète.
17. `EventDetector` produit des événements avec une maison cible natale et une maison transitée quand l'information est disponible.
18. `DomainRouter` construit le vecteur maison depuis les métadonnées runtime disponibles puis le projette vers les catégories via `astral_house_category_weights`.
19. `ContributionCalculator`, `TransitSignalBuilder` et `IntradayActivationBuilder` consomment le routage pour produire scores et timelines.
20. `NatalSensitivityCalculator` lit les occupants et maîtres depuis `NatalChart.houses`, puis applique `house_astrology_profiles` et `house_category_weights` pour moduler la sensibilité structurelle par catégorie.
21. `daily_prediction_*` persiste les scores, contributeurs, points de bascule et la trace `house_system_effective_id`.

## Points d'attention

- `astral_houses` est stable et non versionnée. Ne pas réintroduire `reference_version_id` dans cette table sans décision d'architecture.
- `astral_house_systems` est stable et non versionnée. Ne pas stocker de nouveau `house_system = 'placidus'` dans une table runtime relationnelle ; utiliser une FK vers `astral_house_systems`.
- Le garde-fou `test_runtime_models_do_not_store_house_system_codes_as_string_columns` interdit la réintroduction de colonnes SQL relationnelles string `house_system` ou `house_system_effective` dans les modèles SQLAlchemy. Les payloads JSON et propriétés Python calculées restent autorisés.
- `astral_prediction_daily_house_profiles` mélange une source SQL historique de paramétrage, mais le code la scinde immédiatement : `house_kind` devient un fait de profil astrologique stable, tandis que `visibility_weight`, `base_priority`, `keywords` et `micro_note` restent des données produit.
- `astral_house_category_weights` est un paramètre de scoring produit, pas une donnée astronomique.
- `astral_house_systems` ne calcule rien : le calcul reste dans SwissEph, `AstroCalculator` ou le moteur simplifié.
- Les cuspides réelles doivent rester dans les résultats de calcul ou les objets runtime, pas dans `astral_prediction_daily_house_profiles`.
- Les détails runtime riches des maisons (`house_kind`, `contained_signs`, `intercepted_signs`, `ruler`, `occupants`, `axis`, `strength`) restent dans `NatalResult` et les payloads JSON, pas dans de nouvelles tables SQL.
- `astral_house_interpretation_profiles` porte uniquement le vocabulaire éditorial versionné ; il ne doit pas devenir une source de cuspides, maîtres, occupants, force maison ou poids produit.
- `astral_house_interpretation_profiles` référence `astral_systems.id` : ne pas réintroduire une colonne texte `tradition` dans cette table relationnelle.
- `visibility_weight`, `base_priority`, `keywords` et `micro_note` sont exposés par `HousePredictionProfile`; ils ne doivent pas migrer vers `domain/astrology`.
- `HouseProfileData` n'est plus le contrat actif : toute réintroduction doit être traitée comme une régression de séparation des responsabilités.
- Les colonnes JSON (`result_payload`, `contributors_json`, `driver_json`) ne garantissent pas l'intégrité référentielle avec `astral_houses`.
- Les maîtres de maisons natales dépendent strictement de `astral_planet_sign_dignities`. Un référentiel sans 12 domiciles primaires traditionnels rend le calcul invalide au lieu de déclencher un fallback applicatif.
- Les maisons Whole Sign ne produisent pas d'interceptions dans le runtime, même si le système est reçu sous forme d'enum applicatif.
- La force maison est un contrat d'interprétation astrologique typé : les nouvelles raisons doivent passer par `HouseStrengthReason`, pas par des chaînes ad hoc.
- Le scoring produit peut consommer `strength.level` ou les faits runtime, mais ne doit pas comparer directement `strength.score` à des seuils produit.
- Le garde-fou `test_astrology_prediction_boundary.py` matérialise `RG-095` : `domain/astrology` ne doit pas importer `domain/prediction` ni porter les symboles produit `house_category_weights`, `visibility_weight`, `base_priority` ou `routing_role`.
- Le calcul natal public supporte `placidus`, `equal`, `whole_sign` et `porphyry` via `houses_provider`; le calcul daily `AstroCalculator` utilise actuellement Placidus avec repli Porphyry et ne supporte pas encore `equal` ou `whole_sign` comme systèmes effectifs de cuspides courantes.
- Les modes dégradés sans heure ou sans localisation peuvent produire des maisons vides, des angles `null` et des planètes sans maison dans le payload public.
- `PublicAstroFoundationProjector.activated_houses` utilise un mapping public simplifié par domaine, pas une lecture directe de `astral_house_category_weights`.

## Fichiers sources consultés

- `backend/app/infra/db/models/reference.py`
- `backend/app/domain/astrology/house_system_codes.py`
- `backend/app/domain/astrology/reference/house_profiles.py`
- `backend/app/infra/db/models/house_system_resolution.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/models/interpretation_reference.py`
- `backend/app/infra/db/models/daily_prediction.py`
- `backend/app/infra/db/models/chart_result.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/astrology_reference_sources.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/infra/db/repositories/user_prediction_baseline_repository.py`
- `backend/app/services/natal/calculation_service.py`
- `backend/app/services/house_interpretation_seed_service.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/services/prediction/context_loader.py`
- `backend/app/services/prediction/engine_orchestrator.py`
- `backend/app/domain/astrology/house_ruler_resolver.py`
- `backend/app/domain/astrology/houses_provider.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/zodiac.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/astrology/builders/house_runtime_builder.py`
- `backend/app/domain/astrology/builders/house_occupants_builder.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/domain/astrology/interpretation/house_strength.py`
- `backend/app/domain/astrology/interpretation/house_strength_contracts.py`
- `backend/app/domain/astrology/calculators/contained_signs.py`
- `backend/app/domain/astrology/calculators/intercepted_signs.py`
- `backend/app/domain/astrology/calculators/houses.py`
- `backend/app/domain/prediction/astro_calculator.py`
- `backend/app/domain/prediction/schemas.py`
- `backend/app/domain/prediction/domain_router.py`
- `backend/app/domain/prediction/natal_sensitivity.py`
- `backend/app/domain/prediction/transit_signal_builder.py`
- `backend/app/domain/prediction/intraday_activation_builder.py`
- `backend/app/domain/prediction/public_projection.py`
- `backend/app/domain/prediction/public_astro_vocabulary.py`
- `backend/app/tests/unit/test_astrology_prediction_boundary.py`
- `backend/app/services/chart/json_builder.py`
- `backend/migrations/versions/20260218_0001_create_reference_tables.py`
- `backend/migrations/versions/20260307_0032_migration_a_prediction_reference_tables.py`
- `backend/migrations/versions/20260308_0038_add_house_system_effective_to_daily_prediction_runs.py`
- `backend/migrations/versions/20260512_0086_deversion_astrology_structures.py`
- `backend/migrations/versions/20260513_0094_rename_house_tables.py`
- `backend/migrations/versions/20260513_0095_create_astral_house_systems.py`
- `backend/migrations/versions/20260514_0096_create_house_interpretation_profiles.py`
- `backend/migrations/versions/20260514_0097_rename_astral_house_interpretation_profiles.py`
- `backend/migrations/versions/20260514_0098_reference_house_interpretation_system.py`
- `backend/migrations/versions/20260514_0099_rename_astral_reference_tables.py`
- `backend/migrations/versions/20260514_0102_normalize_astral_aspects.py`
- `backend/migrations/versions/20260515_0109_create_astral_house_axis_definitions.py`
- `backend/migrations/versions/20260515_0110_create_astral_house_axis_members.py`
- `backend/migrations/versions/20260515_0111_deversion_astral_house_axis_definitions.py`
- `backend/migrations/versions/20260515_0112_create_astral_object_reference_tables.py`
- `docs/db_seeder/astrology/astral_structural_reference_catalog.json`
- `docs/db_seeder/astrology/astral_house_system.json`
- `docs/db_seeder/astrology/astral_angle_points.json`
- `docs/db_seeder/astrology/astral_house_modalities.json`
- `docs/db_seeder/astrology/astral_house_axis_definitions.json`
- `docs/db_seeder/astrology/astral_house_axis_members.json`
- `docs/db_seeder/astrology/astral_house_interpretation_profiles.json`
