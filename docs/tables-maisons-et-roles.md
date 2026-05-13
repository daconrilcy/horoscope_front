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
| `chart_results` | JSON `result_payload.houses`, `result_payload.house_rulers`, `result_payload.angles`, `result_payload.planets[*].house` | Snapshot du calcul natal : cuspides, signes des cuspides, maîtres de maisons, angles et maison des planètes | Version texte dans payload et colonnes |
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
   _HOUSE_SYSTEM_CODES = {
       "placidus": b"P",
       "equal": b"E",
       "whole_sign": b"W",
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
   return tuple(_normalize_longitude(float(value)) for value in source)
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

9. `backend/app/services/chart/json_builder.py` sérialise les cuspides dans le payload public et déduit le signe de chaque cuspide par découpage zodiacal de 30 degrés.

   Extraits :

   ```python
   def _longitude_to_sign(longitude: float) -> str:
       index = int((longitude % 360.0) // 30.0) % 12
       return SIGNS[index]
   ```

   ```python
   {
       "number": h.number,
       "cusp_longitude": round(h.cusp_longitude, 2),
       "sign": _longitude_to_sign(h.cusp_longitude),
   }
   ```

#### Processus daily des cuspides courantes

Le moteur de prédiction quotidienne ne persiste pas les cuspides courantes en SQL. Il les calcule en mémoire dans `backend/app/domain/prediction/astro_calculator.py`.

Extraits :

```python
return self._run_house_calculation(ut_jd, b"P", HOUSE_SYSTEM_PLACIDUS)
```

```python
return self._run_house_calculation(ut_jd, b"O", HOUSE_SYSTEM_PORPHYRE)
```

```python
cusps_raw, ascmc_raw = swe.houses(ut_jd, self.latitude, self.longitude, house_code)
```

Le moteur tente donc Placidus (`b"P"`) puis Porphyre (`b"O"`) si Placidus échoue. Les cuspides natales restent l'entrée de référence pour déterminer la maison natale traversée par une planète transitante :

```python
cusp_start = self.natal_cusps[i]
cusp_end = self.natal_cusps[(i + 1) % 12]
```

### Détermination des maîtres de maison

Le thème natal expose désormais explicitement les maîtres de maisons dans `chart_results.result_payload.house_rulers`.

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
8. `backend/app/services/chart/result_service.py` persiste cette donnée dans `chart_results.result_payload`.
9. `backend/app/services/chart/json_builder.py` expose aussi `house_rulers[]` dans le JSON public utilisé par l'interprétation.

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

#### Contrat public et évidences

`chart_results.result_payload.house_rulers[]` contient :

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

Ce nom reste ambigu historiquement : dans certains chemins, il transporte encore le signe de cuspide et non directement la planète maîtresse. La résolution prédictive continue donc à passer par `PredictionContext.sign_rulerships` dans `backend/app/domain/prediction/natal_sensitivity.py`.

Le nouveau champ public `house_rulers[]` ne remplace pas ce contrat interne prédictif. Il rend seulement explicite et sérialisée la donnée natale finale utile aux restitutions publiques.

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
- `house_rulers[]` contient le maître planétaire de chaque maison et sa position natale : `house_number`, `cusp_sign`, `ruler_planet`, `ruler_planet_sign`, `ruler_planet_house`.
- `planets[]` contient la maison occupée par chaque planète dans `house`, sauf en mode dégradé sans heure.
- `angles` dérive ASC, MC, DSC et IC des cuspides 1, 10, 7 et 4.
- Le catalogue d'évidence peut produire des identifiants `HOUSE_{num}_IN_{SIGN}`, `{PLANET}_H{house}`, `HOUSE_{num}_RULER_{PLANET}`, `HOUSE_{num}_RULER_{PLANET}_H{house}` et `HOUSE_{num}_RULER_{PLANET}_{SIGN}`.

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
8. `HouseRulerResolver` calcule `house_rulers[]` à partir des cuspides, des positions planétaires et du mapping signe -> maître issu des dignités.
9. `chart_json_builder` sérialise les maisons, les maîtres de maisons, les maisons des planètes et les angles dans le payload public.
10. Pour la prédiction quotidienne, `EngineOrchestrator` extrait les cuspides natales depuis `house_cusps` ou `houses`.
11. `AstroCalculator` calcule les états astrologiques par pas temporel et la maison natale transitée par chaque planète.
12. `EventDetector` produit des événements avec une maison cible natale et une maison transitée quand l'information est disponible.
13. `DomainRouter` construit le vecteur maison puis le projette vers les catégories via `astral_house_category_weights`.
14. `ContributionCalculator`, `TransitSignalBuilder` et `IntradayActivationBuilder` consomment le routage pour produire scores et timelines.
15. `NatalSensitivityCalculator` utilise `astral_prediction_daily_house_profiles` et `astral_house_category_weights` pour moduler la sensibilité structurelle par catégorie.
16. `daily_prediction_*` persiste les scores, contributeurs, points de bascule et la trace `house_system_effective`.

## Points d'attention

- `astral_houses` est stable et non versionnée. Ne pas réintroduire `reference_version_id` dans cette table sans décision d'architecture.
- `astral_prediction_daily_house_profiles` et `astral_house_category_weights` sont des paramètres de scoring, pas des données astronomiques.
- Les cuspides réelles doivent rester dans les résultats de calcul ou les objets runtime, pas dans `astral_prediction_daily_house_profiles`.
- `visibility_weight` et `base_priority` sont seedés mais leur consommation directe n'a pas été identifiée dans les calculateurs de scoring actuels.
- `micro_note` existe en SQL pour `astral_prediction_daily_house_profiles`, mais n'est pas exposé dans `HouseProfileData`.
- Les colonnes JSON (`result_payload`, `contributors_json`, `driver_json`) ne garantissent pas l'intégrité référentielle avec `astral_houses`.
- Les maîtres de maisons natales dépendent strictement de `astral_planet_sign_dignities`. Un référentiel sans 12 domiciles primaires traditionnels rend le calcul invalide au lieu de déclencher un fallback applicatif.
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
- `backend/app/services/natal/calculation_service.py`
- `backend/app/services/prediction/reference_seed_service.py`
- `backend/app/services/prediction/context_loader.py`
- `backend/app/services/prediction/engine_orchestrator.py`
- `backend/app/domain/astrology/house_ruler_resolver.py`
- `backend/app/domain/astrology/houses_provider.py`
- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/zodiac.py`
- `backend/app/domain/astrology/calculators/houses.py`
- `backend/app/domain/prediction/astro_calculator.py`
- `backend/app/domain/prediction/schemas.py`
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
