# Tables liées aux aspects astrologiques et rôles

## Périmètre

Ce document recense les tables du backend liées directement ou indirectement aux aspects astrologiques dans l'état courant du schéma Alembic, après les migrations `20260514_0099_rename_astral_reference_tables.py`, `20260514_0102_normalize_astral_aspects.py`, `20260514_0104_add_astral_aspect_orb_rules.py`, `20260514_0105_add_astral_system_inheritance.py`, `20260514_0106_create_astral_aspect_interpretation_profiles.py`, `20260515_0112_create_astral_object_reference_tables.py`, `20260515_0114_create_astral_planet_reference_tables.py` et `20260515_0115_simplify_daily_planet_profiles.py`.

Deux catégories sont distinguées :

- Tables SQL qui décrivent le vocabulaire stable des aspects, leurs familles et leurs profils de scoring.
- Payloads et objets runtime qui calculent, transportent ou restituent des aspects sous forme de JSON ou d'événements.

Point important : les aspects réels d'un thème ne sont pas stockés dans une table relationnelle dédiée. Ils sont calculés à l'exécution à partir des longitudes planétaires ou des états temporels, puis transportés dans `NatalResult.aspects`, `chart_results.result_payload.aspects`, les événements de prédiction et les payloads publics.

Depuis le refactor runtime, les payloads SQL/JSON libres restent confinés à l'infra. `AstrologyRuntimeReferenceRepository` charge `ReferenceRepository.get_reference_data`, les dignités, les points d'angle et les systèmes de maisons, puis `AstrologyRuntimeReferenceMapper` retourne une photographie immutable consommée par le domaine.

Les sources JSON canoniques utilisées par le seed applicatif sont désormais sous `docs/db_seeder/astrology/`. Les anciens chemins `docs/recherches astro/*.json` ne doivent plus être considérés comme sources actives pour les seeds.

## Héritage des systèmes astrologiques

`astral_systems.inherits_from_system_id` porte l'héritage des règles d'orbes entre systèmes astrologiques. `modern` et `traditional` restent racines. `hellenistic` hérite de `traditional`, et `medieval` hérite de `traditional`.

Les règles physiques de `astral_aspect_orb_rules` restent locales au système qui les possède : `modern` conserve ses 39 règles, `traditional` conserve ses 40 règles, tandis que `hellenistic` et `medieval` ne stockent pas de copie complète de `traditional`. Un système enfant peut seulement ajouter des overrides locaux explicites, qui gagnent avant les règles héritées.

## Vue d'ensemble

| Table ou payload | Lien aux aspects | Rôle principal | Versionné |
| --- | --- | --- | --- |
| `astral_aspect_families` | Référencé par `astral_aspects.family` | Catalogue des familles `major`, `minor`, `advanced` | Non |
| `astral_aspects` | Table canonique des aspects | Vocabulaire stable : code, nom, angle exact et famille | Non |
| `astral_default_valence` | Catalogue id/name | Valences par défaut autorisées pour les profils d'aspects | Non |
| `astral_interpretive_valence` | Catalogue id/name | Valences interprétatives principales | Non |
| `astral_aspect_profiles` | `aspect_id -> astral_aspects.id` | Paramétrage du moteur daily : intensité, valence, polarité, énergie, orbe, phase | Oui, via `reference_version_id` |
| `astral_aspect_interpretation_profiles` | `aspect_id -> astral_aspects.id`, `astral_system_id -> astral_systems.id` | Vocabulaire éditorial d'interprétation des aspects pour prompts et synthèses | Oui, via `reference_version_id` |
| `astral_aspect_definitions` | `aspect_id -> astral_aspects.id`, `astral_system_id -> astral_systems.id` | Activation et qualification des aspects par système astrologique | Oui, via `reference_version_id` |
| `astral_aspect_orb_rules` | `aspect_id -> astral_aspects.id`, `astral_system_id -> astral_systems.id` | Exceptions ciblées à l'orbe standard des définitions | Oui, via `reference_version_id` |
| `astral_planet_definitions` | Joint par les règles d'orbe via les planètes impliquées | Classe les corps en luminaire, personnelle, sociale, transpersonnelle pour les règles corps/type | Non |
| `astral_angle_points` | Codes `asc`, `dsc`, `mc`, `ic` utilisés par les règles `angle` ou `point` | Référentiel stable des points angulaires pouvant être sources ou cibles d'aspect | Non |
| `ruleset_event_types` | Codes d'événements d'aspect | Pondération et priorité des événements `aspect_*` | Indirectement via le ruleset |
| `ruleset_parameters` | Paramètres de phase/orbe | Multiplicateurs runtime applicables à certains événements | Indirectement via le ruleset |
| `chart_results` | JSON `result_payload.aspects` | Snapshot des aspects natals calculés pour un thème | Version texte dans payload et colonnes |
| `daily_prediction_category_scores` | JSON `contributors_json` | Historique des contributeurs pouvant inclure des événements d'aspect | Indirectement via le run |
| `daily_prediction_turning_points` | JSON `driver_json` | Historique des événements conducteurs, souvent des aspects exacts | Indirectement via le run |

## Tables de référence directes

### `astral_aspect_families`

Définie par `AstralAspectFamilyModel` dans `backend/app/infra/db/models/reference.py`.

La table corrige le nom fautif temporaire `astal_aspect_families`.

Colonnes :

| Colonne | Type | Rôle |
| --- | --- | --- |
| `id` | `Integer` | Identifiant technique référencé par `astral_aspects.family`. |
| `name` | `String(32)` | Nom stable de famille. |

Valeurs seedées depuis `docs/db_seeder/astrology/astral_aspect_families.json` :

| id logique | name |
| --- | --- |
| 1 | `major` |
| 2 | `minor` |
| 3 | `advanced` |

### `astral_aspects`

Définie par `AspectModel` dans `backend/app/infra/db/models/reference.py`.

Historique :

- Créée initialement sous `aspects` par `20260218_0001_create_reference_tables.py`.
- Déversionnée par `20260512_0086_deversion_astrology_structures.py`.
- Renommée en `astral_aspects` par `20260514_0099_rename_astral_reference_tables.py`.
- Refactorée par `20260514_0102_normalize_astral_aspects.py` : suppression de `default_orb_deg`, ajout de `family`, passage de `angle` en `Float`, seed des 20 aspects depuis `docs/db_seeder/astrology/aspects.json`.

Colonnes principales :

| Colonne | Type | Rôle |
| --- | --- | --- |
| `id` | `Integer` | Identifiant technique utilisé par les clés étrangères. |
| `code` | `String(32)` | Code applicatif stable, par exemple `trine`, `quincunx` ou `septile`. |
| `name` | `String(64)` | Nom lisible. |
| `angle` | `Float` | Angle exact de référence sur le cercle zodiacal. |
| `family` | `Integer` | FK vers `astral_aspect_families.id`. |

Contraintes :

- Unicité sur `code`.
- Index sur `code`.
- Plus de `reference_version_id`.
- Plus de `default_orb_deg` : l'orbe par défaut dépend maintenant de `astral_aspect_definitions`.

Aspects seedés depuis `docs/db_seeder/astrology/aspects.json` :

| Code | Nom SQL | Angle | Famille |
| --- | --- | ---: | --- |
| `conjunction` | `Conjunction` | 0 | `major` |
| `sextile` | `Sextile` | 60 | `major` |
| `square` | `Square` | 90 | `major` |
| `trine` | `Trine` | 120 | `major` |
| `opposition` | `Opposition` | 180 | `major` |
| `semi_sextile` | `Semi-sextile` | 30 | `minor` |
| `semi_square` | `Semi-square` | 45 | `minor` |
| `quintile` | `Quintile` | 72 | `minor` |
| `sesquiquadrate` | `Sesquiquadrate` | 135 | `minor` |
| `quincunx` | `Quincunx` | 150 | `minor` |
| `biquintile` | `Biquintile` | 144 | `minor` |
| `septile` | `Septile` | 51.428571 | `advanced` |
| `biseptile` | `Biseptile` | 102.857143 | `advanced` |
| `triseptile` | `Triseptile` | 154.285714 | `advanced` |
| `novile` | `Novile` | 40 | `advanced` |
| `binovile` | `Binovile` | 80 | `advanced` |
| `quadranovile` | `Quadranovile` | 160 | `advanced` |
| `decile` | `Decile` | 36 | `advanced` |
| `tredecile` | `Tredecile` | 108 | `advanced` |
| `quindecile` | `Quindecile` | 165 | `advanced` |

Rôle métier :

- Sert de dictionnaire canonique des aspects disponibles.
- Sert de cible relationnelle à `astral_aspect_profiles` et `astral_aspect_definitions`.
- Ne stocke pas de planète, de paire planétaire, d'orbe observé, de phase applying/separating ou de résultat utilisateur.

## Tables de valence

### `astral_default_valence`

Structure : `id | name`.

Valeurs seedées :

- `positive`
- `negative`
- `neutral`
- `contextual`

Cette table documente les valeurs normalisées attendues par `astral_aspect_profiles.default_valence`.

### `astral_interpretive_valence`

Structure : `id | name`.

Valeurs seedées :

- `supportive`
- `harmonious`
- `dynamic_challenging`
- `polarizing`
- `amplifying`

Cette table porte le vocabulaire interprétatif principal. Le JSON de profils contient aussi des valeurs plus fines comme `creative`, `adjustment`, `symbolic_fated` ou `obsessive_focus`; elles restent stockées en texte dans `astral_aspect_profiles.interpretive_valence` tant qu'elles ne sont pas normalisées dans ce catalogue principal.

## Tables de paramétrage du moteur de prédiction quotidienne

### `astral_aspect_profiles`

Définie par `AspectProfileModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Qualification :

- Table de configuration du moteur de prédiction quotidienne.
- Ne calcule aucun aspect : elle qualifie un aspect déjà identifié par le calcul natal ou par `EventDetector`.
- Versionnée par `reference_version_id`.
- Verrouillée via `_ensure_reference_version_is_mutable` quand la version de référence est verrouillée.
- Seedée depuis `docs/db_seeder/astrology/astral_aspect_profiles.json`.

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `reference_version_id` | Version de référence qui porte ce paramétrage prédictif. |
| `aspect_id` | Aspect canonique concerné. |
| `intensity_weight` | Poids d'intensité utilisé dans les contributions et certains calculs de sensibilité natale. |
| `default_valence` | Valence de base : `positive`, `negative`, `neutral` ou `contextual`. |
| `interpretive_valence` | Qualification interprétative textuelle, par exemple `harmonious`, `dynamic_challenging`, `creative`. |
| `polarity_score` | Score signé de polarité interprétative. |
| `energy_type` | Type d'énergie interprétative, par exemple `harmonious_flow` ou `friction_activation`. |
| `orb_multiplier` | Multiplicateur appliqué à l'orbe actif dans le moteur daily. |
| `phase_sensitive` | Indique si l'aspect doit être sensible à la phase. |
| `phase_behavior_json` | Multiplicateurs applying/exact/separating. |
| `strength_thresholds_json` | Seuils d'intensité par orbe. |
| `micro_note` | Note éditoriale optionnelle. |

Seed attendu :

- 20 profils par version de référence complète.
- Unicité `(reference_version_id, aspect_id)`.

Exemples de valeurs seedées :

| Aspect | Intensité | Valence défaut | Valence interprétative | Polarité | Orbe | Phase |
| --- | ---: | --- | --- | ---: | ---: | --- |
| `conjunction` | 1.5 | `contextual` | `amplifying` | 0.0 | 1.0 | Oui |
| `sextile` | 0.8 | `positive` | `supportive` | 0.55 | 0.9 | Non |
| `square` | 1.25 | `negative` | `dynamic_challenging` | -0.65 | 1.0 | Oui |
| `trine` | 1.0 | `positive` | `harmonious` | 0.75 | 1.0 | Non |
| `opposition` | 1.35 | `contextual` | `polarizing` | -0.35 | 1.0 | Oui |
| `quincunx` | 0.65 | `contextual` | `adjustment` | -0.2 | 0.65 | Oui |
| `quindecile` | 0.3 | `contextual` | `obsessive_focus` | -0.1 | 0.4 | Oui |

Rôle runtime :

- Chargée par `PredictionReferenceRepository.get_aspect_profiles`.
- Injectée dans `PredictionContext.aspect_profiles` sous forme de mapping `code -> AspectProfileData`.

### `astral_aspect_interpretation_profiles`

Cette table porte le vocabulaire éditorial versionné des aspects. Elle est
distincte de `astral_aspect_profiles`, qui reste réservé au scoring prédictif.

| Colonne | Rôle |
|---|---|
| `reference_version_id` | Version de référence propriétaire du vocabulaire éditorial. |
| `aspect_id` | Aspect canonique ciblé dans `astral_aspects`. |
| `astral_system_id` | Système astrologique de l'interprétation éditoriale. |
| `language` | Langue du profil, actuellement seedée en `en`. |
| `title`, `summary`, `micro_note` | Texte éditorial court exploitable par l'interprétation et les prompts. |
| `*_json` | Listes JSON stockées en texte pour mots-clés, dynamiques, patterns, archétypes et consignes de prompt. |

- Seedée depuis `docs/db_seeder/astrology/astral_aspect_interpretation_profiles.json`.
- Synchronisée par `sync_aspect_interpretation_profiles` pendant le seed des versions de référence.
- Unicité : `(reference_version_id, aspect_id, astral_system_id, language)`.
- Elle ne doit pas devenir une source d'orbes, de poids produit, de valence de scoring ou de calcul runtime.
- Utilisée comme vocabulaire éditorial par les prompts et synthèses d'interprétation. Elle n'est pas utilisée par `EventDetector`, `ContributionCalculator` ou `calculate_major_aspects` pour calculer les aspects.

Les usages de scoring et de seuils restent portés par `astral_aspect_profiles` :

- `EventDetector._orb_max` pour son fallback profil historique quand aucune règle d'orbe ne matche ;
- `ContributionCalculator._w_aspect` pour pondérer les contributions ;
- `ContributionCalculator._pol` pour résoudre la polarité de l'événement ;
- `IntradayActivationBuilder` pour construire les activations lunaires intraday ;
- `TransitSignalBuilder` via les mêmes événements/contributions ;
- `NatalSensitivityCalculator._compute_natal_aspects_contribution` pour moduler la sensibilité structurelle par thème ;
- `EngineOrchestrator._compute_natal_aspects` pour enrichir le `NatalChart` interne du moteur daily.

### `astral_aspect_definitions`

Définie par `AstralAspectDefinitionModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Qualification :

- Table de qualification d'un aspect par système astrologique.
- Versionnée par `reference_version_id`.
- Reliée à `astral_systems.id`.
- Seedée depuis `docs/db_seeder/astrology/astral_aspect_definitions.json`.

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `reference_version_id` | Version de référence qui porte la définition. |
| `aspect_id` | Aspect canonique concerné. |
| `astral_system_id` | Système astrologique concerné : `modern`, `traditional`, `hellenistic`, `medieval`. |
| `is_enabled` | Indique si l'aspect est activé dans ce système. |
| `is_major` | Indique si l'aspect est majeur dans ce système. |
| `is_minor` | Indique si l'aspect est mineur dans ce système. |
| `default_orb_deg` | Orbe par défaut applicable dans ce système. Remplace l'ancien `astral_aspects.default_orb_deg`. |
| `display_priority` | Priorité d'affichage. |
| `interpretation_weight` | Poids interprétatif. |
| `scoring_weight` | Poids de scoring. |
| `micro_note` | Note éditoriale optionnelle. |

Contraintes :

- Unicité `(reference_version_id, aspect_id, astral_system_id)`.
- Index sur `reference_version_id`, `aspect_id`, `astral_system_id`.
- `default_orb_deg` obligatoire pour tout aspect activé via la contrainte `ck_astral_aspect_definitions_enabled_default_orb`.
- Mise à jour bloquée quand la version de référence liée est verrouillée.

Seed attendu :

- 80 définitions par version de référence complète : 20 aspects x 4 systèmes.
- Pour `modern`, les 20 aspects sont définis ; les aspects avancés sont généralement `is_enabled = false`.
- Pour `traditional`, `hellenistic` et `medieval`, les cinq aspects majeurs sont actifs et les autres aspects sont injectés comme désactivés pour garder une matrice complète.

### `astral_aspect_orb_rules`

Définie par `AstralAspectOrbRuleModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Qualification :

- Table de surcharges ciblées de l'orbe standard.
- Versionnée par `reference_version_id`.
- Reliée à `astral_systems.id`, `astral_aspects.id` et optionnellement à `astral_planets.id`.
- Seedée depuis `docs/db_seeder/astrology/astral_aspect_orb_rules.json`.
- Synchronisée par `ensure_astral_aspect_reference_data`.
- Consommée par le calcul natal via `ReferenceRepository.get_reference_data -> build_natal_result -> calculate_major_aspects`.

Rôle métier :

- `astral_aspect_definitions.default_orb_deg` reste l'orbe standard obligatoire pour chaque aspect activé.
- `astral_aspect_orb_rules` ne stocke que les exceptions plus spécifiques.
- Les orbes observés d'un aspect réel restent dans les payloads runtime (`AspectResult.orb`, événements daily) et ne doivent pas être persistés dans cette table.

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `reference_version_id` | Version de référence qui porte la surcharge. |
| `astral_system_id` | Système astrologique concerné. |
| `aspect_id` | Aspect canonique concerné. |
| `calculation_context` | Contexte d'application : `natal`, `transit_to_natal`, `sky_to_sky`, `progression_to_natal` ou `any`. |
| `source_body_type` | Type du corps source : `any`, `planet`, `luminary`, `personal_planet`, `social_planet`, `transpersonal_planet`, `angle` ou `point`. |
| `source_planet_id` | Planète source exacte optionnelle. |
| `source_point_code` | Point source exact optionnel, par exemple `asc` ou `mc`. |
| `target_body_type` | Type du corps cible. |
| `target_planet_id` | Planète cible exacte optionnelle. |
| `target_point_code` | Point cible exact optionnel. |
| `orb_deg` | Orbe de calcul à utiliser quand la règle matche. |
| `priority` | Priorité de résolution. |
| `is_enabled` | Active ou désactive la règle. |
| `micro_note` | Note éditoriale optionnelle. |

Contraintes :

- Unicité sur la clé naturelle complète `(reference_version_id, astral_system_id, aspect_id, calculation_context, source_body_type, source_planet_id, source_point_code, target_body_type, target_planet_id, target_point_code)`.
- `orb_deg > 0`.
- `priority >= 0`.
- Si une planète exacte est renseignée, le type associé doit être compatible avec une planète (`planet`, `luminary`, `personal_planet`, `social_planet`, `transpersonal_planet`).
- Mise à jour bloquée quand la version de référence liée est verrouillée.

Seed attendu :

- 79 règles physiques par version de référence complète.
- `modern` définit 39 règles.
- `traditional` définit 40 règles locales : les 39 règles standards plus la désactivation traditionnelle du `quincunx`.
- `hellenistic` et `medieval` stockent 0 règle physique quand ils n'ont pas d'override local ; ils héritent de `traditional` via `astral_systems.inherits_from_system_id`.

Résolution runtime :

1. Charger la définition `(aspect_code, system_code)` depuis `astral_aspect_definitions`.
2. Si la définition est absente ou désactivée, ne pas calculer l'aspect.
3. Construire la chaîne système locale puis parente via `astral_systems.inherits_from_system_id`, en refusant les cycles.
4. Filtrer les règles activées sur l'aspect, la chaîne de systèmes, le contexte (`context` ou `any`) et les corps source/cible.
5. Trier les règles candidates par profondeur d'héritage ascendante, puis par priorité effective descendante, puis par spécificité descendante.
6. Retourner `rule.orb_deg` si une règle matche.
7. Sinon retourner `astral_aspect_definitions.default_orb_deg`.

Priorités fonctionnelles appliquées par le resolver :

| Cas | Priorité effective |
| --- | ---: |
| Paire planète-planète exacte | 1000 |
| Règle impliquant un angle | 900 |
| Règle impliquant un luminaire | 800 à 899 |
| Règle de classe planétaire | 700 |
| Fallback `default_orb_deg` | 0 |

Exemple :

- `square` en `modern` a `default_orb_deg = 6.0`.
- Mars carré Saturne sans règle spécifique donne `orb_max = 6.0`.
- Soleil carré Saturne matche la règle luminaire et donne `orb_max = 8.0`.
- Uranus carré Neptune matche la règle transpersonnelle et donne `orb_max = 3.0`.
- Lune carré ASC matche à la fois une règle luminaire et une règle angle ; la règle angle gagne et donne `orb_max = 5.0`.

Direction source/cible :

- En contexte `natal` ou `any`, les aspects géométriques sont traités de manière symétrique.
- En contexte orienté comme `transit_to_natal`, le sens source -> cible est respecté. Une règle `any -> luminary` ne doit pas matcher automatiquement `luminary -> any`.

Relation avec `astral_aspect_profiles.orb_multiplier` :

Pour le calcul natal pur, la résolution s'arrête à l'orbe astrologique :

```text
orb_max = resolved_orb_deg
```

Pour le moteur prédictif ou produit, un seuil dérivé peut ensuite appliquer le profil d'aspect :

```text
predictive_orb_max = resolved_orb_deg x astral_aspect_profiles.orb_multiplier
```

`resolved_orb_deg` est l'orbe astrologique de calcul. `orb_multiplier` est une modulation prédictive ou produit. Ces deux dimensions ne doivent pas être fusionnées dans une seule valeur de référence, ni injecter la logique de scoring daily dans le calcul natal pur.

## Tables adjacentes nécessaires au fonctionnement

### Référentiels de corps et points

Les règles d'orbes manipulent des types de corps (`luminary`, `personal_planet`, `social_planet`, `transpersonal_planet`, `angle`, `point`) et parfois des planètes ou points exacts.

Ces types sont maintenant adossés aux tables stables suivantes :

| Table | Rôle pour les aspects |
| --- | --- |
| `astral_astrological_roles` | Définit les rôles `luminary`, `personal_planet`, `social_planet`, `transpersonal_planet`, `angle`, `lunar_node`. |
| `astral_object_types` | Distingue `celestial_body`, `chart_angle` et `mathematical_point`. |
| `astral_planet_definitions` | Relie chaque planète à son rôle, son type d'objet, sa vitesse structurelle et sa polarité typique. |
| `astral_angle_points` | Porte les quatre angles `asc`, `dsc`, `mc`, `ic`, leur axe et leur maison associée. |

`PredictionReferenceRepository.get_planet_profiles` joint `astral_prediction_daily_planet_profiles` à `astral_planet_definitions`, `astral_astrological_roles`, `astral_speed` et `astral_typical_polarities`. Une définition planétaire incomplète devient bloquante.

### `astral_reference_versions`

Rôle :

- Versionne les paramètres de prédiction, pas le vocabulaire stable `astral_aspects` ni `astral_aspect_families`.
- Verrouille les versions via `is_locked`.
- Les mises à jour de `astral_aspect_profiles` et `astral_aspect_definitions` passent par `_ensure_reference_version_is_mutable`.

### `astral_systems`

Rôle :

- Référentiel stable des systèmes astrologiques.
- Sert à qualifier les définitions d'aspects par tradition ou école.
- Les valeurs courantes sont `traditional`, `modern`, `hellenistic`, `medieval`.

### `ruleset_event_types`

Rôle :

- Porte les priorités et poids de base des événements du moteur daily.
- Les événements d'aspect seedés sont :

| Code | Groupe | Priorité | Poids de base |
| --- | --- | ---: | ---: |
| `aspect_exact_to_angle` | `aspect` | 80 | 2.0 |
| `aspect_exact_to_luminary` | `aspect` | 75 | 1.8 |
| `aspect_exact_to_personal` | `aspect` | 68 | 1.5 |
| `aspect_enter_orb` | `aspect` | 40 | 1.0 |
| `aspect_exit_orb` | `aspect` | 25 | 0.5 |

Ces lignes ne définissent pas ce qu'est un trigone ou un carré. Elles qualifient les types d'événements produits quand un aspect entre en orbe, devient exact ou sort d'orbe.

### `ruleset_parameters`

Rôle :

- Porte les paramètres génériques du ruleset, dont `orb_multiplier_applying`, `orb_multiplier_exact` et `orb_multiplier_separating`.
- Ces paramètres relèvent du comportement moteur, pas du vocabulaire canonique des aspects.

## Données de calcul et de résultat

### Calcul natal

Le calcul natal est porté par `build_natal_result` dans `backend/app/domain/astrology/natal_calculation.py`.

Flux courant :

1. `ReferenceRepository.get_reference_data` expose `aspects[]` depuis `astral_aspects`, enrichi avec `family` et `default_orb_deg` moderne depuis `astral_aspect_definitions`.
2. Le même payload expose `aspect_orb_rules[]` depuis `astral_aspect_orb_rules`.
3. `build_natal_result` vérifie que `aspects[]` existe et que chaque entrée contient un `code`, un `angle` et un `default_orb_deg` valide.
4. Si `aspect_orb_rules[]` est présent, `build_natal_result` valide les règles et les transmet au calculateur.
5. Le calcul filtre explicitement via le helper runtime canonique des aspects majeurs, soit `conjunction`, `sextile`, `square`, `trine`, `opposition`.
6. `calculate_major_aspects` compare toutes les paires de positions planétaires et applique la résolution hiérarchique des orbes.
7. Les résultats sont convertis en `AspectResult`.

Contrat `AspectResult` :

| Champ | Rôle |
| --- | --- |
| `aspect_code` | Code canonique de l'aspect détecté. |
| `planet_a`, `planet_b` | Corps impliqués, triés pour stabilité de sortie. |
| `angle` | Angle théorique de l'aspect. |
| `orb` | Écart angulaire réel historique. |
| `orb_used` | Même écart réel, champ plus explicite ajouté pour compatibilité. |
| `orb_max` | Seuil d'orbe résolu pour cette paire. |

Nuance importante :

- Le référentiel relationnel contient maintenant les aspects majeurs, mineurs et avancés.
- Le calcul natal public reste limité aux cinq aspects majeurs par le helper runtime canonique.
- Les orbes par défaut ne vivent plus dans `astral_aspects`; ils sont résolus via `astral_aspect_definitions`.
- Les exceptions d'orbe ne vivent pas dans `aspects[]`; elles sont transportées par `aspect_orb_rules[]`.

### `chart_results`

Définie par `ChartResultModel`.

Rôle des aspects dans `result_payload` :

- `aspects[]` contient les aspects natals majeurs exposés publiquement.
- `chart_json_builder` filtre encore sur les aspects majeurs avant sérialisation.
- Chaque aspect public contient `type`, `planet_a`, `planet_b`, `angle`, `orb` et `applying`.
- `applying` vaut actuellement `null` pour le natal, car le statut applying/separating n'est pas connu dans ce contexte.

Exemple de projection publique :

```json
{
  "type": "trine",
  "planet_a": "moon",
  "planet_b": "sun",
  "angle": 120.0,
  "orb": 1.4,
  "applying": null
}
```

### Catalogue d'évidence

`build_enriched_evidence_catalog` transforme les aspects du JSON de thème en identifiants stables.

Format :

- `ASPECT_{PLANET_A}_{PLANET_B}_{TYPE}`
- `ASPECT_{PLANET_A}_{PLANET_B}_{TYPE}_ORB{orb_int}`

Exemples :

```text
ASPECT_MOON_SUN_TRINE
ASPECT_MOON_SUN_TRINE_ORB1
```

Les paires sont triées pour stabiliser les identifiants.

## Moteur de prédiction quotidienne

### Détection des aspects transit -> natal

`EventDetector` détecte les aspects à partir d'une séquence de `StepAstroState`.

Aspects supportés par la détection V1 :

| Angle | Code |
| ---: | --- |
| 0 | `conjunction` |
| 60 | `sextile` |
| 90 | `square` |
| 120 | `trine` |
| 180 | `opposition` |

Même si `astral_aspects` contient 20 aspects, la détection runtime V1 reste centrée sur les cinq majeurs. Les aspects mineurs et avancés sont disponibles comme référentiel et définitions, mais ne doivent pas être considérés comme calculés partout tant que les constantes et calculateurs V1 ne sont pas étendus.

Métadonnées principales :

| Métadonnée | Rôle |
| --- | --- |
| `natal_house_target` | Maison natale de la cible. |
| `natal_house_transited` | Maison natale traversée par la planète transitante. |
| `orb_max` | Seuil actif résolu via planète et profil d'aspect. |
| `phase` | `applying` ou `separating` selon l'évolution de l'orbe. |

### Contribution numérique

`ContributionCalculator` combine l'aspect avec les autres facteurs :

```text
w_event x w_planet x w_aspect x f_orb x f_phase x f_target x NS(c) x D(e,c) x Pol(e,c)
```

Rôle de l'aspect :

- `w_aspect` vient de `AspectProfileData.intensity_weight`.
- `f_orb` décroît selon l'écart à `orb_max`.
- `f_phase` dépend de `metadata.phase`.
- `Pol(e,c)` lit `AspectProfileData.default_valence`, puis éventuellement la polarité typique de la planète pour les valences contextuelles.

Point d'attention :

- Les valeurs `default_valence` seedées sont désormais alignées sur les branches explicites `positive`, `negative`, `neutral`, `contextual`.
- `interpretive_valence` est plus riche et ne doit pas être confondue avec la polarité numérique.

## Restitution publique et frontend

### Vocabulaire public

`public_astro_vocabulary.py` définit les libellés et tonalités :

| Aspect | Libellé FR | Tonalité |
| --- | --- | --- |
| `conjunction` | Conjonction | intensification |
| `sextile` | Sextile | fluidité |
| `square` | Carré | ajustement |
| `trine` | Trigone | fluidité |
| `opposition` | Opposition | ajustement |
| `quincunx` | Quinconce | adaptation |

Point d'attention :

- `quincunx` est maintenant présent dans le référentiel relationnel, dans la famille `minor`.
- Sa présence en table ne signifie pas que le calcul natal public l'émet : le helper runtime canonique reste le garde-fou des aspects majeurs calculés.

## Étapes où les aspects interviennent dans les calculs

1. `ReferenceRepository.seed_version_defaults` garantit les familles et les 20 lignes `astral_aspects`.
2. `ensure_astral_aspect_reference_data` garantit les valences, profils, définitions et règles d'orbes par version.
3. `ReferenceRepository.get_reference_data` expose les aspects stables avec l'orbe moderne issu des définitions.
4. `ReferenceRepository.get_reference_data` expose aussi les règles `aspect_orb_rules[]`.
5. `build_natal_result` valide les définitions d'aspect, les règles d'orbes et filtre les aspects majeurs.
6. `calculate_major_aspects` compare toutes les paires de positions et résout les orbes par règle ou fallback.
7. `NatalResult.aspects` transporte les `AspectResult`.
8. `chart_json_builder` sérialise les aspects majeurs dans `result_payload.aspects`.
9. `build_enriched_evidence_catalog` produit les preuves `ASPECT_*`.
10. `PredictionReferenceRepository.get_aspect_profiles` charge les profils dans `PredictionContext`.
11. `PredictionContextLoader` fige les profils d'aspect dans le contexte chargé.
12. `EventDetector` détecte les entrées/sorties d'orbe et aspects exacts transit -> natal.
13. `ContributionCalculator` applique `w_aspect`, `f_orb`, `f_phase` et la polarité.
14. `EngineOrchestrator` reconstruit des `natal_aspect` internes pour la sensibilité daily.
15. `NatalSensitivityCalculator` intègre les aspects natals dans la sensibilité par catégorie.
16. `IntradayActivationBuilder` construit les activations lunaires par aspect.
17. `daily_prediction_*` persiste les scores, contributeurs et drivers incluant les événements d'aspect.
18. Les projecteurs publics extraient `aspects`, `sky_aspects` et `dominant_aspects`.
19. Le frontend traduit et affiche les aspects natals et daily.

## Points d'attention

- `astral_aspects` est stable et non versionnée. Ne pas réintroduire `reference_version_id` dans cette table sans décision d'architecture.
- Les paramètres de scoring quotidien doivent rester dans `astral_aspect_profiles`, pas dans `astral_aspects`.
- Les orbes par système doivent rester dans `astral_aspect_definitions`, pas dans `astral_aspects`.
- Les exceptions d'orbes doivent rester dans `astral_aspect_orb_rules`, pas dans `astral_aspects` ni dans `astral_aspect_profiles`.
- Les orbes observés d'un thème ou d'un événement ne doivent pas être stockés dans `astral_aspects`, `astral_aspect_profiles`, `astral_aspect_definitions` ou `astral_aspect_orb_rules`.
- Ne pas dupliquer toutes les valeurs standards dans `astral_aspect_orb_rules` : cette table ne contient que les dérogations ciblées.
- En calcul natal pur, `orb_max` doit rester égal à `resolved_orb_deg`.
- Ne pas fusionner `resolved_orb_deg` et `astral_aspect_profiles.orb_multiplier`, ni appliquer `orb_multiplier` au calcul natal pur.
- La colonne `astral_aspects.family` est un entier lié à `astral_aspect_families`.
- Le référentiel relationnel contient 20 aspects, mais le calcul natal et la détection V1 restent limités aux cinq majeurs.
- Les aspects mineurs ne doivent pas être activés dans les calculs publics sans mettre à jour le helper runtime canonique, les seeds, les tests, les traductions et les contrats.
- Les colonnes JSON (`result_payload`, `contributors_json`, `driver_json`) ne garantissent pas d'intégrité référentielle avec `astral_aspects`.
- `phase_sensitive` et `phase_behavior_json` documentent une intention de comportement ; vérifier les calculateurs avant de conclure à une exploitation exhaustive.
- Les paires d'aspects dans le catalogue d'évidence sont triées pour stabilité ; ne pas dépendre de l'ordre original des planètes.

## Fichiers sources consultés

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/astrology_reference_sources.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/services/reference_data_service.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/domain/prediction/event_detector.py`
- `backend/app/domain/prediction/contribution_calculator.py`
- `backend/app/services/chart/json_builder.py`
- `backend/migrations/versions/20260514_0102_normalize_astral_aspects.py`
- `backend/migrations/versions/20260514_0104_add_astral_aspect_orb_rules.py`
- `backend/migrations/versions/20260514_0105_add_astral_system_inheritance.py`
- `docs/db_seeder/astrology/aspects.json`
- `docs/db_seeder/astrology/astral_aspect_families.json`
- `docs/db_seeder/astrology/astral_aspect_profiles.json`
- `docs/db_seeder/astrology/astral_aspect_definitions.json`
- `docs/db_seeder/astrology/astral_aspect_orb_rules.json`
- `docs/db_seeder/astrology/astral_angle_points.json`
- `docs/db_seeder/astrology/astral_planet_definitions.json`
