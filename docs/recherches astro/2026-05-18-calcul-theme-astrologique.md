# Calcul du theme astrologique natal

Date: 2026-05-18  
Perimetre: calcul backend du theme natal, depuis les donnees de naissance jusqu'au `NatalResult`.  
Focus: calcul astronomique/astrologique structurel. Les couches d'interpretation, de narration LLM et d'affichage ne sont pas detaillees sauf lorsqu'elles touchent la persistance du resultat.

Mise a jour CS-189: les etoiles fixes restent hors calcul du theme natal, mais
elles ne sont plus seulement des donnees d'affichage cote prediction quotidienne.
Le runtime daily charge maintenant les tables `astral_fixed_star_*` et leurs
sources pour detecter, filtrer, router et scorer les conjonctions aux etoiles
fixes.

## Vue d'ensemble

Le calcul du theme natal est orchestre cote backend. Le frontend et les routes API ne calculent pas les positions: ils transmettent des donnees, recoivent un resultat et l'affichent.

Le flux nominal est:

1. Validation des donnees de naissance.
2. Conversion temps local vers UTC et jour julien.
3. Chargement du referentiel astrologique runtime depuis la base.
4. Resolution des options de calcul: moteur, zodiaque, ayanamsa, frame, systeme de maisons, ecole d'aspects.
5. Calcul des positions planetaires.
6. Calcul des cuspides de maisons.
7. Calcul des points astraux configures depuis le referentiel runtime.
8. Affectation des planetes et points aux signes et maisons.
9. Calcul des aspects avec orbes, avec inclusion optionnelle des points astraux.
10. Enrichissement structurel: maitres de maisons, runtime maisons, runtime signes, runtime aspects, signature de theme.
11. Persistance du resultat dans `chart_results`.

## Entrees API et services

### Route technique de calcul

Fichier: `backend/app/api/v1/routers/public/astrology_engine.py`

Fonction principale: `calculate_natal`

Role:

- Valide le payload via `NatalCalculateRequest`.
- Construit un `BirthInput`.
- Appelle `NatalCalculationService.calculate`, en propageant `include_points_in_aspects`.
- Persiste la trace via `ChartResultService.persist_trace`.
- Retourne `chart_id`, `NatalResult` et des metadonnees techniques.

Tables touchees:

- Tables de referentiel `astral_*` via `NatalCalculationService`.
- `chart_results` via `ChartResultService.persist_trace`.

### Route utilisateur

Fichier: `backend/app/services/user_profile/natal_chart_service.py`

Fonction principale: `UserNatalChartService.generate_for_user`

Role:

- Charge le profil de naissance utilisateur.
- Exige une heure de naissance pour un theme utilisateur precis.
- Resout les coordonnees de naissance.
- Construit `BirthInput`.
- Appelle `NatalCalculationService.calculate`.
- Persiste le theme avec `user_id`.

Tables touchees:

- Profil utilisateur et lieux resolus via les repositories utilisateur.
- Tables `astral_*` via le calcul.
- `chart_results` pour le resultat final.

## Preparation temps et donnees de naissance

Fichiers:

- `backend/app/domain/astrology/natal_preparation.py`
- `backend/app/services/natal/preparation_service.py`

Fonctions et classes:

- `BirthInput`
- `BirthPreparedData`
- `prepare_birth_data`
- `_parse_birth_time`
- `_assert_local_time_is_valid`
- `_julian_day_from_timestamp`
- `_delta_t_seconds`
- `NatalPreparationService.prepare`

Calcul effectue:

1. Le fuseau horaire est pris depuis `birth_timezone` ou derive depuis `birth_lat`/`birth_lon` si l'option runtime le permet.
2. L'heure locale est parse en `datetime`.
3. Les heures locales ambigues ou inexistantes lors des transitions DST sont refusees.
4. Le temps local est converti en UTC.
5. Le timestamp UTC flottant est transforme en jour julien:

   ```text
   julian_day = timestamp_utc / 86400 + 2440587.5
   ```

6. Si `tt_enabled=True`, le pipeline calcule `delta_t_sec` puis:

   ```text
   jd_tt = jd_ut + delta_t_sec / 86400
   ```

Point important: SwissEph est appele avec le jour julien UT (`calc_ut`). Les champs TT sont produits pour tracabilite, pas comme entree de `swe.calc_ut`.

Tables utilisees:

- Aucune table `astral_*` dans cette etape.

## Chargement du referentiel runtime

Fichiers:

- `backend/app/services/natal/calculation_service.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py`
- `backend/app/infra/db/repositories/reference_repository.py`
- `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py`

Fonctions et classes:

- `NatalCalculationService._load_runtime_reference`
- `AstrologyRuntimeReferenceRepository.load`
- `ReferenceRepository.get_reference_data`
- `ReferenceRepository._get_house_axes`
- `AstrologyRuntimeReferenceRepository._load_astral_points`
- `PredictionReferenceRepository.get_sign_rulerships`
- `AstrologyRuntimeReferenceMapper.map_payload`

Role:

- Charger la version de reference active.
- Construire une photographie immutable `AstrologyRuntimeReference`.
- Verifier les invariants bloquants: 12 signes, 12 maisons, planetes requises, aspects, regles d'orbe, dignites, axes de maisons, points d'angle, systemes de maisons actifs.
- Charger les profils structurels des 12 signes depuis `astral_sign_profiles` et leurs taxonomies DB-backed.
- Refuser un profil de signe incomplet, absent ou contenant une valeur sentinelle comme `unknown`.
- Charger les points astraux depuis les tables `astral_point_*` sous contrats immutables:
  `AstralPointRuntime`, `AstralPointVariantRuntime`, `AstralPointAliasRuntime` et
  `AstralPointReferenceSet`.
- Valider que les regles d'orbe ciblant `source_point_code` ou `target_point_code`
  pointent vers un point astral ou un point d'angle existant.

Tables `astral_*` lues pour le calcul:

- `astral_reference_versions`: resolution de la version.
- `astral_planets`: codes planetaires et `swe_id`.
- `astral_signs`: ordre et codes des signes.
- `astral_sign_profiles`: profil structurel canonique de chaque signe.
- `astral_elements`: element canonique du signe.
- `astral_modalities`: modalite canonique du signe.
- `astral_polarities`: polarite canonique du signe.
- `astral_houses`: numeros et noms des maisons.
- `astral_aspects`: codes et angles des aspects.
- `astral_aspect_families`: famille de chaque aspect.
- `astral_aspect_profiles`: valence et type energetique attaches aux aspects calcules.
- `astral_aspect_definitions`: activation, caractere majeur/mineur et orbe par defaut.
- `astral_aspect_orb_rules`: regles fines d'orbe par systeme, contexte et corps.
- `astral_planet_sign_dignities`: dignites et maitrises de signes.
- `astral_dignity_type`: code du type de dignite lu via la relation `dignity_type`.
- `astral_systems`: systeme astrologique et heritage des regles.
- `astral_planet_definitions`: classification structurelle des planetes.
- `astral_astrological_roles`: classe runtime du corps, par exemple luminaire ou transpersonnelle.
- `astral_angle_points`: ASC/DSC/MC/IC et maisons associees.
- `astral_house_systems`: systemes de maisons actifs/supportes.
- `astral_house_axis_definitions`: themes d'axes de maisons.
- `astral_house_axis_members`: correspondance maison, axe et maison opposee.
- `astral_point_families`: familles de points astraux.
- `astral_points`: points astraux calculables.
- `astral_point_calculation_variants`: variantes de calcul par point.
- `astral_point_aliases`: aliases, noms moteur SwissEph et rattachements de variantes.

## Resolution des options de calcul

Fichier: `backend/app/services/natal/calculation_service.py`

Fonctions:

- `NatalCalculationService.calculate`
- `NatalCalculationService._resolve_calculation_options`
- `NatalCalculationService._resolve_engine`

Options resolues:

- `zodiac`: `tropical` ou `sidereal`.
- `ayanamsa`: requis si le zodiaque sidereal est explicitement demande.
- `frame`: `geocentric` ou `topocentric`.
- `house_system`: `placidus`, `equal`, `whole_sign`, `porphyry` selon configuration.
- `altitude_m`: forcee a `0.0` si `frame=topocentric` et altitude absente.
- `aspect_school`: par defaut via settings, utilise pour filtrer definitions et regles d'aspects.
- `include_points_in_aspects`: `false` par defaut; quand `true`, les points astraux
  calcules sont ajoutes au pool aspectable.

Choix moteur:

- `swisseph`: requis pour sidereal, topocentric ou systeme de maisons non `equal`.
- `simplified`: autorise pour les chemins internes/dev limites a tropical, geocentrique, maisons egales.

Tables utilisees:

- Pas de table nouvelle; cette etape consomme le referentiel runtime deja charge.

## Calcul des positions planetaires

### Moteur SwissEph

Fichiers:

- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/ephemeris_provider.py`
- `backend/app/domain/astrology/planet_catalog.py`
- `backend/app/domain/astrology/zodiac.py`

Fonctions:

- `_build_swisseph_positions`
- `calculate_planets`
- `normalize_360`
- `sign_from_longitude`

Calcul effectue:

1. Les planetes a calculer viennent de `runtime_reference.planets.items`.
2. Chaque code planete est relie a un `swe_id`.
3. `swe.calc_ut(jdut, swe_id, flags)` calcule longitude, latitude et vitesse.
4. La longitude est normalisee dans `[0, 360)`.
5. La retrogradation est deduite par:

   ```text
   is_retrograde = speed_longitude < 0
   ```

6. En sidereal, `swe.set_sid_mode` est applique puis reinitialise apres calcul.
7. En topocentric, `swe.set_topo(lon, lat, altitude)` est applique puis reinitialise.
8. Le signe est recalcule depuis la longitude et l'ordre des `astral_signs`.

Tables utilisees:

- `astral_planets`
- `astral_planet_definitions`
- `astral_astrological_roles`
- `astral_signs`
- `astral_systems` si sidereal/aspect school cohabitent dans le referentiel global.

### Moteur simplifie

Fichier: `backend/app/domain/astrology/calculators/natal.py`

Fonctions:

- `calculate_planet_positions`
- `_sun_longitude`
- `_planet_longitude`

Calcul effectue:

- Calcule des longitudes deterministes a partir du jour julien.
- Le Soleil et la Lune ont des approximations dediees.
- Les autres corps utilisent une formule deterministe simplifiee.
- Le signe est deduit par `sign_from_longitude`.

Tables utilisees:

- `astral_planets` pour la liste des corps.
- `astral_signs` pour l'ordre des signes.

## Calcul des maisons

### Moteur SwissEph

Fichiers:

- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/houses_provider.py`
- `backend/app/domain/astrology/house_system_codes.py`

Fonctions:

- `_build_swisseph_houses`
- `calculate_houses` dans `houses_provider.py`
- `_extract_cusps`

Calcul effectue:

1. Le systeme public est transforme en code SwissEph:

   ```text
   placidus -> P
   equal -> E
   whole_sign -> W
   porphyry -> O
   ```

2. `swe.houses_ex(jdut, lat, lon, hsys_code)` calcule les cuspides.
3. Les 12 cuspides sont extraites et normalisees dans `[0, 360)`.
4. SwissEph calcule aussi ASC et MC dans `HouseData`, mais le `NatalResult` expose principalement les cuspides de maisons.

Tables utilisees:

- `astral_houses`
- `astral_house_systems` pour validation du referentiel runtime.

### Moteur simplifie

Fichier: `backend/app/domain/astrology/calculators/houses.py`

Fonctions:

- `calculate_houses`
- `assign_house_number`

Calcul effectue:

1. Une longitude d'ascendant simplifiee est derivee:

   ```text
   ascendant_longitude = (julian_day * 0.5) % 360
   ```

2. Chaque cuspide est espacee de 30 degres:

   ```text
   cusp_longitude = ascendant_longitude + (house_number - 1) * 30
   ```

3. Le systeme effectif est `equal`.

Tables utilisees:

- `astral_houses` pour la liste des numeros de maisons.

## Calcul des points astraux

Fichiers:

- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/astral_point_calculation_resolver.py`
- `backend/app/domain/astrology/ephemeris_provider.py`
- `backend/app/domain/astrology/runtime/runtime_reference.py`

Fonctions et classes:

- `calculate_astral_points`
- `_engine_point_longitude`
- `_simplified_point_longitude`
- `calculate_astral_point_longitude`
- `AstralPointCalculationResolver`
- `AstralPointCalculationInstruction`
- `NatalAstralPointPosition`

Calcul effectue:

1. Les points a calculer viennent de `runtime_reference.astral_points.items`.
2. Le resolver choisit la variante par defaut DB-backed du point.
3. Une variante directe doit porter une `engine_key` issue de `astral_point_aliases`.
   Aucune cle moteur n'est inferee par constante locale.
4. Une variante derivee produit une instruction source + offset:

   ```text
   south_node = north_node + 180 degres
   lunar_perigee = lunar_apogee + 180 degres
   ```

5. En moteur SwissEph, `calculate_astral_point_longitude` appelle `swe.calc_ut`
   avec la cle moteur DB-backed. Les cles `SE_*` sont adaptees au nommage du
   module `pyswisseph` sans changer la valeur canonique stockee en DB.
6. En moteur simplifie, une longitude deterministe est produite depuis le jour
   julien et l'instruction de calcul.
7. Chaque longitude est normalisee, rattachee a un signe, assignee a une maison,
   puis projetee en `NatalAstralPointPosition`.

Champs produits:

- `code`
- `variant_code`
- `longitude`
- `sign`
- `degree_in_sign`
- `house`
- `is_physical_body`

Garanties:

- `NatalResult.points` est une liste normalisee.
- Aucun champ plat `true_node`, `mean_node` ou `lilith` n'est ajoute au resultat.
- Les keywords et profils editoriaux des points ne sont pas lus dans le calcul natal brut.

Tables utilisees:

- `astral_point_families`
- `astral_points`
- `astral_point_calculation_variants`
- `astral_point_aliases`
- `languages` pour la langue des aliases.
- `astral_signs`
- `astral_houses`

## Affectation signes et maisons

Fichiers:

- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/calculators/houses.py`
- `backend/app/domain/astrology/angle_utils.py`
- `backend/app/domain/astrology/zodiac.py`

Fonctions:

- `assign_house_number`
- `contains_angle`
- `sign_from_longitude`
- `_validate_house_cusps`

Calcul effectue:

1. Les 12 cuspides sont validees: nombre exact, longitudes finies, normalisees, non dupliquees.
2. Pour chaque position planetaire et chaque point astral calcule, `assign_house_number` cherche l'intervalle de cuspides contenant la longitude.
3. Le signe attendu est recalcule depuis la longitude.
4. Le pipeline refuse toute incoherence:

- signe annonce different du signe calcule;
- maison affectee ne contenant pas la longitude;
- cuspide manquante pour l'intervalle.

Tables utilisees:

- `astral_signs`
- `astral_houses`

## Calcul des aspects

Fichiers:

- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/calculators/aspects.py`
- `backend/app/domain/astrology/runtime/aspect_calculation_contracts.py`
- `backend/app/domain/astrology/celestial_runtime_catalog.py`

Fonctions:

- `build_aspect_body_from_position`
- `calculate_major_aspects`
- `_angular_distance`
- `resolve_orb`
- `_system_chain`
- `_definition_for_system`
- `_rule_matches_bodies`

Calcul effectue:

1. Les positions planetaires sont converties en `AspectBodyRuntimeData`.
   Si `include_points_in_aspects=True`, les positions de `NatalResult.points`
   sont converties de la meme maniere et ajoutees au pool aspectable.
2. Les definitions d'aspects actives, majeures et compatibles avec `aspect_school` sont selectionnees.
3. Pour chaque paire de corps, la distance angulaire minimale est calculee:

   ```text
   distance = min(abs(a - b) % 360, 360 - (abs(a - b) % 360))
   ```

4. Pour chaque definition, l'orbe geometrique est:

   ```text
   orb = abs(distance - aspect_angle)
   ```

5. `resolve_orb` choisit l'orbe maximale applicable:

- systeme local puis parents via `astral_systems`;
- contexte `natal` ou `any`;
- type de corps, planete source/cible, point source/cible;
- priorite et specificite.

6. L'aspect est retenu si:

   ```text
   orb <= resolved_orb
   ```

7. Le resultat est trie de maniere deterministe.

Tables utilisees:

- `astral_aspects`
- `astral_aspect_families`
- `astral_aspect_profiles`
- `astral_aspect_definitions`
- `astral_aspect_orb_rules`
- `astral_systems`
- `astral_planets`
- `astral_planet_definitions`
- `astral_astrological_roles`
- `astral_angle_points`
- `astral_points`
- `astral_point_calculation_variants`

## Enrichissement structurel du theme

### Catalogue celeste runtime

Fichier: `backend/app/domain/astrology/celestial_runtime_catalog.py`

Fonctions:

- `CelestialRuntimeCatalog.from_runtime_reference`
- `body_type_for_code`
- `is_luminary`
- `is_transpersonal`
- `is_angle_point`

Role:

- Derive les classifications de corps depuis `astral_planet_definitions`, `astral_astrological_roles` et `astral_angle_points`.
- Sert au calcul de force des aspects, maisons et dominances.

### Maitres de maisons

Fichier: `backend/app/domain/astrology/house_ruler_resolver.py`

Fonctions:

- `HouseRulerResolver.resolve`
- `_normalize_rulerships`

Calcul effectue:

1. Le signe de cuspide de chaque maison est deduit de sa longitude.
2. Le maitre de ce signe est lu depuis les maitrises issues des dignites.
3. La position du maitre est retrouvee dans les positions planetaires.

Tables utilisees:

- `astral_planet_sign_dignities`
- `astral_dignity_type`
- `astral_systems`
- `astral_signs`
- `astral_planets`

### Runtime maisons

Fichiers:

- `backend/app/domain/astrology/builders/house_runtime_builder.py`
- `backend/app/domain/astrology/builders/house_occupants_builder.py`
- `backend/app/domain/astrology/interpretation/house_strength.py`
- `backend/app/domain/astrology/calculators/contained_signs.py`
- `backend/app/domain/astrology/calculators/intercepted_signs.py`

Fonction principale:

- `build_house_runtime_data`

Calcul effectue:

- Signe de cuspide.
- Signes contenus.
- Signes interceptes sauf en `whole_sign`.
- Occupants par maison.
- Maitre de maison.
- Force structurelle de maison.
- Axe de maison.

Tables utilisees:

- `astral_houses`
- `astral_house_axis_definitions`
- `astral_house_axis_members`
- `astral_systems`
- `astral_signs`
- `astral_planets`
- `astral_planet_definitions`
- `astral_astrological_roles`
- `astral_planet_sign_dignities`

### Runtime signes

Fichier: `backend/app/domain/astrology/builders/sign_runtime_builder.py`

Fonction principale:

- `build_sign_runtime_data`

Calcul effectue:

- Regroupe les occupants par signe.
- Active les dignites dont la planete est presente dans le signe.
- Calcule un poids de dominance borne.
- Propage `element`, `modality` et `polarity` depuis `SignReferenceData` vers `SignRuntimeData`.
- Marque les raisons structurelles: occupants, stellium, luminaire, dignite active, profil de reference.

Tables utilisees:

- `astral_signs`
- `astral_sign_profiles`
- `astral_elements`
- `astral_modalities`
- `astral_polarities`
- `astral_planets`
- `astral_planet_sign_dignities`
- `astral_dignity_type`
- `astral_systems`
- `astral_planet_definitions`
- `astral_astrological_roles`

Note: depuis CS-185, `ReferenceRepository.get_reference_data` conserve le payload public `signs[]` sous forme `{code, name}`, mais `AstrologyRuntimeReferenceRepository.load()` remplace le payload interne des signes par un chargement dedie qui joint `astral_sign_profiles`, `astral_elements`, `astral_modalities` et `astral_polarities`. Le changement est interne au runtime natal et ne modifie pas le contrat OpenAPI ni les types frontend.

### Runtime aspects

Fichier: `backend/app/domain/astrology/builders/aspect_runtime_builder.py`

Fonction principale:

- `build_aspect_runtime_data`

Calcul effectue:

- Ratio d'orbe.
- Force d'aspect.
- Modifiers structurels: orbe exacte, orbe serree, luminaire, transpersonnelle.
- Bloc interpretation technique de l'aspect: valence et type energetique.

Tables utilisees:

- `astral_aspects`
- `astral_aspect_families`
- `astral_aspect_profiles`
- `astral_aspect_definitions`
- `astral_aspect_orb_rules`
- `astral_planet_definitions`
- `astral_astrological_roles`

### Signature et balance du theme

Fichier: `backend/app/domain/astrology/interpretation/chart_signature.py`

Fonctions:

- `ChartSignatureCalculator.calculate`
- `_weighted_profile`
- `_planet_scores`
- `_rank_balance`
- `_rank_dominance`

Calcul effectue:

- Dominantes signes.
- Dominantes planetes.
- Dominantes maisons.
- Dominantes aspects.
- Balance elements/modalites depuis les profils de signes runtime DB-backed.
- Synthese primaire: element, modalite, signe, planete, maison.

Tables utilisees:

- Aucune table lue directement; la signature consomme les runtime deja construits.

## Construction du resultat final

Fichier: `backend/app/domain/astrology/natal_calculation.py`

Fonction centrale:

- `build_natal_result`

Classes de sortie:

- `NatalResult`
- `PlanetPosition`
- `NatalAstralPointPosition`
- `HouseRuntimeData`
- `AspectResult`
- `ChartBalanceRuntimeData`

Le `NatalResult` contient:

- versions: `reference_version`, `ruleset_version`, `aspect_rules_version`;
- options: `engine`, `zodiac`, `frame`, `house_system`, `ayanamsa`, `altitude_m`;
- trace ephemerides: `ephemeris_path_version`, `ephemeris_path_hash`;
- trace temps: `prepared_input`;
- faits calcules: `planet_positions`, `points`, `houses`, `aspects`;
- enrichissements: `signs_runtime`, `house_rulers`, `chart_balance`.

Depuis CS-187, `points` contient les points astraux natals calcules depuis le
referentiel DB. Le contrat est additif et conserve le comportement historique:
les aspects restent calcules uniquement entre planetes tant que
`include_points_in_aspects=false`.

## Persistance

Fichiers:

- `backend/app/services/chart/result_service.py`
- `backend/app/infra/db/repositories/chart_result_repository.py`
- `backend/app/infra/db/models/chart_result.py`

Fonctions:

- `ChartResultService.compute_input_hash`
- `ChartResultService.persist_trace`
- `ChartResultRepository.create`

Calcul/persistance effectuee:

1. Un hash SHA-256 est calcule a partir de:

- `birth_input`;
- `reference_version`;
- `ruleset_version`.

2. Un `chart_id` UUID est cree.
3. Le `NatalResult` est serialise.
4. Le payload est stocke dans `chart_results.result_payload`.

Table de sortie:

- `chart_results`

Note: `persist_trace` ajoute aussi une projection legacy `house_rulers` avec des libelles localises via `AstrologyTranslationResolver`. Cette projection est post-calcul et n'intervient pas dans les positions, maisons, aspects ou dominances.

## Tables utilisees dans le calcul

Liste consolidee des tables `astral_` qui participent au calcul ou a la construction structurelle du `NatalResult`:

- `astral_angle_points`
- `astral_aspect_definitions`
- `astral_aspect_families`
- `astral_aspect_orb_rules`
- `astral_aspect_profiles`
- `astral_aspects`
- `astral_astrological_roles`
- `astral_dignity_type`
- `astral_elements`
- `astral_house_axis_definitions`
- `astral_house_axis_members`
- `astral_house_systems`
- `astral_houses`
- `astral_modalities`
- `astral_planet_definitions`
- `astral_planet_sign_dignities`
- `astral_planets`
- `astral_point_aliases`
- `astral_point_calculation_variants`
- `astral_point_families`
- `astral_points`
- `astral_polarities`
- `astral_reference_versions`
- `astral_sign_profiles`
- `astral_signs`
- `astral_systems`

## Tables `astral_` non utilisees dans le calcul

Ces tables existent dans les modeles SQLAlchemy ou les sources de seed, mais ne sont pas lues par la chaine de calcul du `NatalResult` decrite ci-dessus. Elles peuvent servir au seed, a l'interpretation, a la traduction, a la prediction quotidienne, a l'affichage ou a des extensions futures.

Depuis CS-189, les tables d'etoiles fixes ci-dessous restent non utilisees par
le calcul natal, mais elles sont actives dans le runtime prediction daily:

- `astral_fixed_stars`: identifiants canoniques et noms affichables des etoiles.
- `astral_fixed_star_definitions`: longitude ecliptique, magnitude visuelle,
  activation et rattachement a une source de reference.
- `astral_fixed_star_keywords`: mots-cles transmis au contrat runtime fixed star.
- `astral_reference_sources`: categorie et cle de source associees a la definition.

Le flux daily correspondant ne recree pas de catalogue local. Il passe par
`PredictionReferenceRepository.get_fixed_stars()`, puis par
`PredictionContext.fixed_stars`. `EnrichedAstroEventsBuilder` lit l'orbe, le
seuil de magnitude et le poids de base depuis les parametres de ruleset:

- `fixed_star_orb_deg`
- `fixed_star_max_visual_magnitude`
- `fixed_star_base_weight`
- `fixed_star_category_weights`

Les evenements `fixed_star_conjunction` retenus portent notamment `orb_max`,
`star_key`, `star_display_name`, `visual_magnitude`,
`fixed_star_source_category`, `fixed_star_source_key` et
`fixed_star_keywords`. Ils contribuent ensuite au scoring via les owners
existants `DomainRouter` et `ContributionCalculator`; aucun calculateur
specialise ou catalogue `_STAR_DATA` n'est autorise.

- `astral_aspect_interpretation_profile_translations`
- `astral_aspect_interpretation_profiles`
- `astral_aspect_translations`
- `astral_calculation_types`
- `astral_constellations`
- `astral_default_valence`
- `astral_fixed_star_definitions`
- `astral_fixed_star_keyword_translations`
- `astral_fixed_star_keywords`
- `astral_fixed_stars`
- `astral_hemispheres`
- `astral_house_category_weights`
- `astral_house_interpretation_profile_translations`
- `astral_house_interpretation_profiles`
- `astral_house_modalities`
- `astral_house_translations`
- `astral_interpretive_valence`
- `astral_object_types`
- `astral_planet_category_weights`
- `astral_planet_interpretation_profile_translations`
- `astral_planet_interpretation_profiles`
- `astral_planet_translations`
- `astral_point_interpretation_keyword_translations`
- `astral_point_interpretation_keywords`
- `astral_point_interpretation_profile_translations`
- `astral_point_interpretation_profiles`
- `astral_prediction_daily_house_profiles`
- `astral_prediction_daily_planet_profiles`
- `astral_reference_epochs`
- `astral_reference_sources`
- `astral_sign_keywords`
- `astral_sign_translations`
- `astral_speed`
- `astral_structural_reference_catalog`
- `astral_typical_polarities`
- `astral_zodiacal_reference_system_categories`
- `astral_zodiacal_reference_systems`

Precision: `astral_calculation_types`, `astral_object_types`, `astral_speed` et `astral_typical_polarities` alimentent les definitions planetaires lors du seed et restent liees par clefs etrangeres, mais le calcul runtime lit seulement `astral_planet_definitions.is_luminary` et le role via `astral_astrological_roles`.
