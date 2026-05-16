# Tables liées aux signes astrologiques et rôles

## Périmètre

Ce document recense les tables du backend liées directement ou indirectement aux signes astrologiques dans l'état courant du schéma Alembic, après les migrations `20260218_0001_create_reference_tables.py`, `20260512_0086_deversion_astrology_structures.py`, `20260513_0087_normalize_astral_sign_profiles.py`, `20260513_0090_create_astral_systems.py`, `20260513_0092_create_astral_planet_sign_dignities.py`, `20260513_0093_drop_astral_sign_rulerships.py`, `20260515_0112_create_astral_object_reference_tables.py` et `20260515_0114_create_astral_planet_reference_tables.py`.

Deux catégories sont distinguées :

- Tables SQL qui décrivent le vocabulaire stable des signes, leurs profils structurels et leurs dignités planétaires.
- Objets runtime et payloads JSON qui calculent, transportent ou restituent les signes sous forme de `sign_code`, `cusp_sign`, signes contenus ou signes interceptés.

Point important : les positions réelles dans les signes ne sont pas stockées dans une table relationnelle dédiée. Elles sont calculées à l'exécution à partir des longitudes zodiacales, puis transportées dans `NatalResult.planet_positions`, `HouseRuntimeData`, `chart_results.result_payload`, les événements de prédiction et les payloads publics.

Depuis le refactor runtime, les sources JSON canoniques de seed sont sous `docs/db_seeder/astrology/`. Les payloads SQL/JSON libres restent confinés à l'infra : `ReferenceRepository` charge les tables stables, `PredictionReferenceRepository` dérive les maîtrises depuis les dignités, puis `AstrologyRuntimeReferenceMapper` expose au domaine une photographie immutable via `AstrologyRuntimeReference`.

## Vue d'ensemble

| Table ou payload | Lien aux signes | Rôle principal | Versionné |
| --- | --- | --- | --- |
| `astral_signs` | Table canonique des 12 signes | Vocabulaire stable et ordre zodiacal par `id` | Non |
| `astral_elements` | Référencé par `astral_sign_profiles.astral_element_id` | Taxonomie `fire`, `earth`, `air`, `water` | Non |
| `astral_modalities` | Référencé par `astral_sign_profiles.astral_modality_id` | Taxonomie `cardinal`, `fixed`, `mutable` | Non |
| `astral_polarities` | Référencé par `astral_sign_profiles.astral_polarity_id` | Taxonomie `yang`, `yin` | Non |
| `astral_sign_profiles` | `astral_sign_id -> astral_signs.id` | Profil structurel : élément, modalité, polarité, mots-clés et ombres | Non |
| `astral_planet_sign_dignities` | `astral_sign_id -> astral_signs.id` | Dignités planétaires par signe, source canonique des maîtrises signe -> planète | Non |
| `astral_systems` | Référencé par les dignités | Système astrologique de la dignité : `traditional`, `modern`, `hellenistic`, `medieval` | Non |
| `astral_dignity_type` | Référencé par les dignités | Types `domicile`, `detriment`, `exaltation`, `fall` | Non |
| `chart_results` | JSON `result_payload.planets[*].sign`, `houses[*].cusp_sign`, `angles.*.sign` | Snapshot public du thème natal calculé | Version texte dans payload et colonnes |
| `daily_prediction_turning_points` | JSON `driver_json` | Peut contenir des événements d'entrée de Lune ou d'angle en signe | Indirectement via le run |
| `daily_prediction_category_scores` | JSON `contributors_json` | Peut contenir des métadonnées de signe issues d'événements | Indirectement via le run |

## Tables de référence directes

### `astral_signs`

Définie par `AstralSignModel` dans `backend/app/infra/db/models/reference.py`.

Qualification :

- Table stable et non versionnée.
- Seedée depuis `docs/db_seeder/astrology/astral_signs.json`.
- Synchronisée par `ReferenceRepository.seed_version_defaults`.
- Chargée dans le runtime par `ReferenceRepository.get_reference_data`, puis mappée en `SignReferenceSet`.
- Validée par `AstrologyRuntimeReferenceRepository` : le référentiel runtime doit contenir exactement 12 signes.

Colonnes principales :

| Colonne | Type | Rôle |
| --- | --- | --- |
| `id` | `Integer` | Identifiant technique. Son ordre sert aussi d'ordre zodiacal canonique. |
| `code` | `String(32)` | Code stable en minuscules, par exemple `aries` ou `pisces`. Unique. |
| `name` | `String(64)` | Nom lisible en anglais. |

Signes seedés :

| id | Code | Nom | Élément | Modalité | Polarité | Maître traditionnel |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `aries` | Aries | `fire` | `cardinal` | `yang` | `mars` |
| 2 | `taurus` | Taurus | `earth` | `fixed` | `yin` | `venus` |
| 3 | `gemini` | Gemini | `air` | `mutable` | `yang` | `mercury` |
| 4 | `cancer` | Cancer | `water` | `cardinal` | `yin` | `moon` |
| 5 | `leo` | Leo | `fire` | `fixed` | `yang` | `sun` |
| 6 | `virgo` | Virgo | `earth` | `mutable` | `yin` | `mercury` |
| 7 | `libra` | Libra | `air` | `cardinal` | `yang` | `venus` |
| 8 | `scorpio` | Scorpio | `water` | `fixed` | `yin` | `mars` |
| 9 | `sagittarius` | Sagittarius | `fire` | `mutable` | `yang` | `jupiter` |
| 10 | `capricorn` | Capricorn | `earth` | `cardinal` | `yin` | `saturn` |
| 11 | `aquarius` | Aquarius | `air` | `fixed` | `yang` | `saturn` |
| 12 | `pisces` | Pisces | `water` | `mutable` | `yin` | `jupiter` |

Rôle métier :

- Sert de dictionnaire canonique des signes zodiacaux.
- Sert d'ordre canonique pour `zodiac.ordered_sign_codes`.
- Sert de cible relationnelle à `astral_sign_profiles` et `astral_planet_sign_dignities`.
- Ne contient pas de longitude, degré dans le signe, planète, maison, dignité ou donnée utilisateur.

### `astral_sign_profiles`

Définie par `AstralSignProfileModel` dans `backend/app/infra/db/models/reference.py`.

Qualification :

- Table stable et non versionnée.
- Une ligne par signe canonique (`astral_sign_id` unique).
- Créée par `20260513_0087_normalize_astral_sign_profiles.py`.
- Synchronisée par `_ensure_astral_sign_profiles` dans `backend/app/services/prediction/reference_seed_service.py`.
- Alimentée par la matrice `SIGN_PROFILE_DATA` pour élément/modalité/polarité et par `docs/db_seeder/astrology/astral_sign_keywords.json` pour les mots-clés.

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `astral_sign_id` | Signe canonique ciblé. |
| `astral_element_id` | Élément astrologique stable. |
| `astral_modality_id` | Modalité astrologique stable. |
| `astral_polarity_id` | Polarité structurelle stable. |
| `keywords_json` | Mots-clés éditoriaux principaux du signe. |
| `shadow_keywords_json` | Mots-clés d'ombre ou de dérive. |

Rôle métier :

- Documente les attributs structurels classiques des signes.
- Sert de matériau éditorial et de validation de catalogue.
- Ne calcule pas les positions planétaires, les cuspides, les maîtres de maisons ou les scores prédictifs.

### Taxonomies de profils de signes

| Table | Valeurs seedées | Rôle |
| --- | --- | --- |
| `astral_elements` | `fire`, `earth`, `air`, `water` | Élément astrologique associé au signe. |
| `astral_modalities` | `cardinal`, `fixed`, `mutable` | Mode d'expression du signe. |
| `astral_polarities` | `yang`, `yin` | Polarité structurelle du signe. |

Ces taxonomies sont stables et non versionnées. Elles ne doivent pas être confondues avec `astral_typical_polarities`, qui qualifie la polarité typique des planètes dans `astral_planet_definitions`.

## Dignités et maîtrises

### `astral_planet_sign_dignities`

Définie par `AstralPlanetSignDignityModel` dans `backend/app/infra/db/models/prediction_reference.py`.

Qualification :

- Table stable et non versionnée.
- Décrit la condition d'une planète dans un signe pour un système astrologique donné.
- Alimentée depuis `docs/db_seeder/astrology/astral_planet_sign_dignities.json`.
- Remplace l'ancienne table `astral_sign_rulerships`, supprimée par `20260513_0093_drop_astral_sign_rulerships.py`.

Clés :

- `astral_sign_id -> astral_signs.id`
- `astral_planet_id -> astral_planets.id`
- `astral_dignity_type_id -> astral_dignity_type.id`
- `astral_system_id -> astral_systems.id`
- Unicité : `(astral_sign_id, astral_planet_id, astral_dignity_type_id, astral_system_id)`

Colonnes principales :

| Colonne | Rôle |
| --- | --- |
| `astral_sign_id` | Signe dans lequel la planète est évaluée. |
| `astral_planet_id` | Planète concernée. |
| `astral_dignity_type_id` | Dignité : domicile, détriment, exaltation ou chute. |
| `astral_system_id` | Système astrologique applicable. |
| `weight` | Pondération qualitative de la dignité. |
| `is_primary` | Indique si l'association est principale dans son système. |

Comptage attendu :

| Groupe | Nombre de lignes |
| --- | ---: |
| Dignités traditionnelles | 38 |
| Dignités modernes | 12 |
| Total | 50 |

### Vue runtime `sign_rulerships`

La table SQL `astral_sign_rulerships` n'existe plus. Le moteur conserve toutefois le concept métier `sign_rulerships` comme vue dérivée.

Source canonique actuelle :

- Table : `astral_planet_sign_dignities`.
- Filtre métier : `dignity_type = "domicile"`, `system = "traditional"` et `is_primary = true`.
- Méthode spécialisée : `PredictionReferenceRepository.get_sign_rulerships_from_dignities(system="traditional")`.
- Méthode runtime conservée : `PredictionReferenceRepository.get_sign_rulerships(system="traditional")`.
- Contrat runtime : `PredictionContext.sign_rulerships` et `DignityReferenceSet.sign_rulerships`.

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

Rôle runtime :

- `AstrologyRuntimeReferenceRepository._validate` exige 12 maîtrises et vérifie que chaque signe et planète référencés existent dans le runtime.
- `HouseRulerResolver` refuse un mapping incomplet avant de résoudre les maîtres de maisons.
- `build_natal_result` lève `invalid_reference_data/sign_rulerships` si les maîtres de maisons ne sont pas résolubles.

## Calcul zodiacal et runtime

### Ordre zodiacal

`backend/app/domain/astrology/zodiac.py` porte les helpers partagés :

| Fonction | Rôle |
| --- | --- |
| `normalize_360` | Normalise une longitude dans `[0, 360)`. |
| `ordered_sign_codes` | Retourne les 12 codes de signes dans l'ordre zodiacal canonique. |
| `sign_from_longitude` | Transforme une longitude en code de signe par tranche de 30 degrés. |

`ordered_sign_codes` charge `docs/db_seeder/astrology/astral_signs.json` quand aucun catalogue runtime n'est fourni. Il refuse tout catalogue qui ne contient pas exactement 12 codes uniques.

Point important :

- Le choix tropical ou sidéral est appliqué en amont par le provider d'éphémérides.
- Une fois la longitude produite dans le référentiel demandé, `sign_from_longitude` ne fait qu'appliquer l'ordre zodiacal et les tranches de 30 degrés.
- Le même ordre de signes sert au calcul simplifié, à SwissEph, aux maisons, aux signes contenus et aux maîtres de maisons.

### Runtime natal

Dans `build_natal_result` :

1. Les signes sont lus depuis `runtime_reference.signs.items`.
2. Chaque position planétaire reçoit un `sign_code`.
3. Le pipeline vérifie que `sign_from_longitude(longitude, sign_codes)` correspond au `sign_code` reçu.
4. Les cuspides de maisons sont converties en signes via les mêmes helpers.
5. `HouseRulerResolver` utilise `sign_rulerships` pour résoudre le maître de chaque cuspide.
6. `build_house_runtime_data` enrichit chaque maison avec `cusp_sign`, `contained_signs`, `intercepted_signs`, `ruler`, `occupants`, `axis` et `strength`.

Contrats principaux :

| Objet | Champs liés aux signes |
| --- | --- |
| `PlanetPosition` | `sign_code` |
| `HouseRuntimeData` | `cusp_sign`, `sign`, `contained_signs`, `intercepted_signs`, `ruler.sign`, `occupants[*].sign` |
| `HouseRulerResult` | `cusp_sign`, `ruler_planet_sign` |
| `NatalResult` | `planet_positions`, `houses`, `house_rulers` |

### Signes contenus et interceptés

`backend/app/domain/astrology/calculators/contained_signs.py` calcule les signes touchés par l'intervalle entre une cuspide et la suivante.

Exemple :

```text
75° Gémeaux -> 142° Lion
=> ["gemini", "cancer", "leo"]
```

`backend/app/domain/astrology/calculators/intercepted_signs.py` considère comme intercepté tout signe contenu qui n'est ni le signe de cuspide courant ni le signe de cuspide suivant.

Exemple :

```text
Maison 2 : cuspide Gémeaux
Maison 3 : cuspide Lion
Signes contenus : Gémeaux, Cancer, Lion
=> Cancer intercepté
```

Les maisons Whole Sign forcent `intercepted_signs = []` dans le builder de runtime maison.

## Données de résultat et restitution

### `chart_results`

Définie par `ChartResultModel`.

Rôle des signes dans `result_payload` :

- `planets[].sign` contient le signe de chaque planète.
- `planets[].longitude_in_sign` contient le degré dans le signe, dérivé de `longitude % 30`.
- `houses[].cusp_sign` est le champ canonique du signe de cuspide.
- `houses[].sign` reste un alias legacy synchronisé avec `cusp_sign`.
- `houses[].contained_signs` et `houses[].intercepted_signs` exposent les signes traversés par la maison.
- `house_rulers[].cusp_sign` et `house_rulers[].ruler_planet_sign` exposent les signes utiles à la lecture des maîtrises.
- `angles.ASC.sign`, `angles.MC.sign`, `angles.DSC.sign`, `angles.IC.sign` exposent les signes des angles quand l'heure et la localisation sont disponibles.

Exemple de projection publique :

```json
{
  "code": "sun",
  "sign": "gemini",
  "longitude": 84.5,
  "longitude_in_sign": 24.5,
  "house": 10
}
```

### Catalogue d'évidence

`build_enriched_evidence_catalog` transforme les placements en identifiants stables.

Formats liés aux signes :

| Format | Exemple |
| --- | --- |
| `{PLANET}_{SIGN}` | `SUN_GEMINI` |
| `{PLANET}_{SIGN}_H{house}` | `SUN_GEMINI_H10` |
| `{ANGLE}_{SIGN}` | `ASC_LEO` |
| `HOUSE_{num}_IN_{SIGN}` | `HOUSE_1_IN_LEO` |
| `HOUSE_{num}_RULER_{PLANET}_{SIGN}` | `HOUSE_10_RULER_VENUS_TAURUS` |

Les libellés français sont actuellement portés par `SIGN_NAMES_FR` dans `backend/app/services/chart/json_builder.py`, pas par une table SQL localisée.

### Profils publics et B2B

- `UserAstroProfileService` extrait notamment `sun_sign_code` et `ascendant_sign_code` depuis le dernier thème disponible.
- `B2B astrology_service` expose les signes depuis `AstralSignModel` ordonné par `id`.
- Les payloads sans heure ou sans localisation peuvent conserver les signes planétaires tout en omettant les maisons, angles et signes de cuspides.

## Moteur de prédiction quotidienne

### Événements de changement de signe

`EventDetector` détecte notamment :

| Événement | Rôle |
| --- | --- |
| `moon_sign_ingress` | Changement de signe de la Lune dans la séquence temporelle. |
| `asc_sign_change` | Changement de signe de l'Ascendant. |

Point d'attention :

- Ces événements manipulent encore des indices de signe dans certaines métadonnées (`from_sign`, `to_sign`) issus de `int(longitude // 30)`.
- Ils ne constituent pas une FK relationnelle vers `astral_signs`.
- Les signes dans le moteur daily restent du contexte d'événement ; le routage produit principal passe par les planètes, maisons, points, aspects et catégories.

### Sensibilité natale

`NatalSensitivityCalculator` consomme les maisons runtime, leurs occupants et leurs maîtres. Les signes interviennent donc indirectement :

- pour résoudre le maître d'une maison depuis `cusp_sign` ;
- pour qualifier le placement du maître (`ruler.sign`) ;
- pour détecter certains modificateurs comme le maître dans son propre signe via `sign_rulerships`.

Le calcul de sensibilité ne doit pas recalculer les maîtrises depuis une table cachée : il lit les faits runtime déjà exposés par `NatalChart.houses`.

## Étapes où les signes interviennent dans les calculs

1. `ReferenceRepository.seed_version_defaults` synchronise les 12 lignes `astral_signs`.
2. `_ensure_astral_sign_profiles` garantit `astral_elements`, `astral_modalities`, `astral_polarities` et `astral_sign_profiles`.
3. `_ensure_astral_planet_sign_dignities` synchronise les dignités planète -> signe.
4. `PredictionReferenceRepository.get_sign_rulerships_from_dignities` dérive les 12 maîtrises traditionnelles primaires.
5. `AstrologyRuntimeReferenceRepository` charge les signes, dignités et maîtrises dans `AstrologyRuntimeReference`.
6. `zodiac.ordered_sign_codes` valide l'ordre des 12 signes.
7. `calculate_planet_positions` ou SwissEph calcule les longitudes et affecte `sign_code`.
8. `build_natal_result` vérifie la cohérence longitude -> signe.
9. `HouseRulerResolver` résout les maîtres de maisons depuis les signes de cuspide.
10. `build_house_runtime_data` calcule signes contenus, signes interceptés, occupants et rulers intégrés.
11. `chart_json_builder` sérialise les signes planétaires, de maisons, d'angles et de maîtrises.
12. `build_enriched_evidence_catalog` produit les identifiants d'évidence liés aux signes.
13. `EventDetector` et `IntradayActivationBuilder` peuvent détecter les changements de signe de la Lune, de l'ASC ou du MC.
14. `daily_prediction_*` persiste les événements et contributeurs incluant éventuellement ces métadonnées.

## Points d'attention

- `astral_signs` est stable et non versionnée. Ne pas réintroduire `reference_version_id` dans cette table sans décision d'architecture.
- L'ordre des signes est critique : il doit rester Bélier -> Poissons via les `id` 1 à 12 du seed canonique.
- Tout catalogue runtime de signes doit contenir exactement 12 codes uniques ; les fixtures minimales à 1 ou 2 signes sont invalides pour le calcul natal complet.
- Les longitudes, degrés dans le signe, signes de cuspide, signes contenus et signes interceptés relèvent des objets runtime et payloads JSON, pas des tables de référence.
- `astral_sign_profiles` porte des attributs structurels et éditoriaux ; elle ne doit pas devenir une table de positions ou de scoring produit.
- `astral_sign_keywords.json` est une source documentaire de mots-clés, pas une table SQL autonome.
- `astral_planet_sign_dignities` est la source canonique des dignités et maîtrises ; ne pas réintroduire `astral_sign_rulerships`.
- Le runtime courant utilise les maîtrises traditionnelles pour éviter de remplacer `scorpio -> mars`, `aquarius -> saturn` et `pisces -> jupiter` par des maîtrises modernes.
- Les colonnes JSON (`result_payload`, `contributors_json`, `driver_json`) ne garantissent pas l'intégrité référentielle avec `astral_signs`.
- `SIGN_NAMES_FR` dans `chart_json_builder.py` est une table de libellés applicative, pas une source de référence SQL. Toute internationalisation durable devrait passer par un référentiel dédié ou un contrat explicite.
- Les événements daily de changement de signe peuvent utiliser des indices numériques ; ne pas les assimiler automatiquement à des `astral_signs.id`.
- Le choix tropical/sidéral change les longitudes produites en amont, pas la table `astral_signs`.

## Fichiers sources consultés

- `backend/app/infra/db/models/reference.py`
- `backend/app/infra/db/models/prediction_reference.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/astrology_reference_sources.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`
- `backend/app/infra/db/repositories/prediction_reference_repository.py`
- `backend/app/infra/db/repositories/prediction_schemas.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/domain/astrology/zodiac.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/house_ruler_resolver.py`
- `backend/app/domain/astrology/calculators/contained_signs.py`
- `backend/app/domain/astrology/calculators/intercepted_signs.py`
- `backend/app/domain/astrology/builders/house_runtime_builder.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`
- `backend/app/domain/astrology/runtime/house_runtime_data.py`
- `backend/app/domain/prediction/event_detector.py`
- `backend/app/domain/prediction/intraday_activation_builder.py`
- `backend/app/domain/prediction/natal_sensitivity.py`
- `backend/app/services/chart/json_builder.py`
- `backend/app/services/user_profile/astro_profile_service.py`
- `backend/app/services/b2b/astrology_service.py`
- `backend/migrations/versions/20260513_0087_normalize_astral_sign_profiles.py`
- `backend/migrations/versions/20260513_0092_create_astral_planet_sign_dignities.py`
- `backend/migrations/versions/20260513_0093_drop_astral_sign_rulerships.py`
- `docs/db_seeder/astrology/astral_signs.json`
- `docs/db_seeder/astrology/astral_sign_keywords.json`
- `docs/db_seeder/astrology/astral_planet_sign_dignities.json`
- `docs/db_seeder/astrology/astral_structural_reference_catalog.json`
