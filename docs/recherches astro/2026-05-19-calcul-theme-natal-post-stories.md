# Calcul du theme natal apres stories runtime, dignites et signaux

Date: 2026-05-19  
Perimetre: calcul backend du theme natal, referentiel runtime astrologique, payload `NatalResult`, persistance et consommation applicative.  
Sources consolidees: `2026-05-16-audit-chaine-calcul-theme-natal.md`, `2026-05-18-calcul-theme-astrologique.md`, stories CS-185 a CS-196.

## Synthese

Le calcul du theme natal reste orchestre cote backend. Le frontend ne calcule pas les positions, les maisons, les aspects, les points astraux, les dignites, les profils conditionnels, les signaux, les conditions avancees ou les dominances: il declenche la generation, lit le dernier resultat persiste et affiche le payload.

Depuis les dernieres stories implementees, le `NatalResult` ne contient plus seulement la geometrie natale historique. Il expose maintenant une couche runtime plus riche:

- positions planetaires calculees par moteur SwissEph ou moteur simplifie encadre;
- maisons, cuspides, occupants, axes, forces de maisons et maitres;
- aspects calcules depuis les definitions et orbes runtime;
- points astraux natals DB-backed;
- runtime signes avec profils structurels DB-backed;
- signature et balance du theme;
- dignites planetaires essentielles et accidentelles scorees, explicables et fondees sur le referentiel runtime;
- profils conditionnels planetaires derives des dignites et enrichis par les conditions avancees;
- signaux conditionnels gouvernes par referentiel pour transformer les axes de profil en signaux techniques;
- conditions planetaires avancees factuelles: reception mutuelle, hayz, vitesse, phases heliacales/orientation et conditions relationnelles par aspects;
- classement des planetes dominantes;
- couche d'adaptation interpretative objective, prete pour les restitutions aval, sans narration finale.

Le changement majeur post CS-190/CS-196 est le passage d'un theme natal "calcul + dignites" vers un graphe factuel complet: dignites, profils conditionnels, signaux, conditions avancees, dominances et adaptation semantique. Chaque couche reste derivee des faits calcules et du runtime DB-backed; aucune couche ne produit de texte utilisateur final, de prompt LLM ou de decision UI.

## Flux nominal actualise

1. L'utilisateur renseigne ses donnees de naissance via `PUT /v1/users/me/birth-data`.
2. Le front appelle `POST /v1/users/me/natal-chart` avec `accurate=true`.
3. `UserNatalChartService.generate_for_user` charge le profil, exige l'heure de naissance, resout le lieu et construit un `BirthInput`.
4. `NatalCalculationService.calculate` prepare les options astrologiques, charge `AstrologyRuntimeReference`, selectionne le moteur et appelle `build_natal_result`.
5. `build_natal_result` prepare le temps, calcule les positions, maisons, points astraux, aspects et enrichissements runtime.
6. Le moteur de dignites calcule la secte du theme, les dignites essentielles, les dignites accidentelles et les scores agreges par planete.
7. `PlanetConditionProfileService` derive les profils conditionnels depuis les dignites et les poids runtime.
8. `AdvancedConditionEngine` detecte les conditions planetaires avancees, puis enrichit les profils conditionnels.
9. `PlanetConditionSignalBuilder` transforme les profils enrichis en signaux conditionnels gouvernes par `condition_signal_profiles`.
10. `ChartSignatureCalculator` calcule la balance globale et `PlanetDominanceEngine` classe les planetes dominantes.
11. `InterpretationAdapterEngine` transforme les faits disponibles en signaux semantiques et themes actives.
12. `ChartResultService.persist_trace` persiste le payload complet dans `chart_results`.
13. `GET /v1/users/me/natal-chart/latest` restitue le dernier theme, avec projection JSON publique et `astro_profile` derive.
14. Les couches d'interpretation ou LLM consomment le resultat calcule; elles ne modifient pas le calcul astronomique ou astrologique objectif.

## Preparation des donnees

La preparation natale reste identique aux audits precedents:

- validation stricte de `BirthInput`;
- fuseau IANA explicite ou derive depuis les coordonnees quand le chemin l'autorise;
- refus des heures locales ambigues ou inexistantes pendant les transitions DST;
- conversion local vers UTC;
- calcul du jour julien UT;
- calcul optionnel de `delta_t_sec` et `jd_tt` pour tracabilite.

Point important: SwissEph est appele avec le jour julien UT via `swe.calc_ut`. Les champs TT sont conserves dans la trace mais ne remplacent pas l'entree UT du provider.

## Referentiel runtime charge

`AstrologyRuntimeReference` est la source de verite du calcul. Il consolide notamment:

- signes, maisons, planetes, roles astrologiques et systemes;
- definitions d'aspects, familles, profils, regles d'orbes et heritage de systemes;
- dignites historiques signe-planete utilisees par les maitres de maisons et runtime signes;
- profils structurels des signes avec element, modalite et polarite;
- points astraux, variantes de calcul et aliases moteur;
- axes de maisons et points d'angle;
- depuis CS-190/CS-191, referentiel avance de dignites planetaires via `dignity_reference`;
- depuis CS-192/CS-193, axes conditionnels et profils de signaux conditionnels;
- depuis CS-194, facteurs, profils et poids de dominance planetaire;
- depuis CS-195, types, profils et poids de conditions planetaires avancees;
- depuis CS-196, types de signaux, themes et regles de la couche d'adaptation interpretative.

Le runtime de dignites contient les inventaires de types essentiels et accidentels, systemes de termes et decans, profils de scoring, poids de scoring, regles essentielles, maitres de triplicite, bornes de termes, faces/decans et regles accidentelles. Les preuves CS-191 indiquent notamment 5 profils de scoring, 38 regles essentielles, 12 maitres de triplicite, 60 bornes de termes, 36 faces/decans et 41 regles accidentelles dans le snapshot de reference.

Les couches ajoutees apres CS-191 restent elles aussi gouvernees par runtime: les profils de signaux conditionnels viennent de `astral_planet_condition_signal_profiles`, les facteurs de dominance de `astral_dominance_*`, les conditions avancees de `astral_advanced_condition_*`, et l'adaptation interpretative de `astral_interpretation_*`.

## Calcul astronomique

### Positions planetaires

Le moteur SwissEph reste le chemin de production pour le mode accurate. Il calcule les longitudes, latitudes et vitesses avec `swe.calc_ut`, normalise les longitudes en `[0, 360)`, deduit la retrogradation depuis la vitesse longitudinale et rattache chaque corps au signe correspondant.

Le moteur simplifie reste limite aux chemins internes, dev ou fallback encadres. Il supporte un calcul tropical, geocentrique et en maisons egales. Il ne doit pas devenir un remplacement silencieux du moteur accurate.

### Maisons et angles

SwissEph calcule les cuspides via `swe.houses_ex` pour les systemes supportes (`placidus`, `equal`, `whole_sign`, `porphyry`). Les cuspides sont validees, puis chaque planete et point astral est affecte a une maison par intervalle angulaire.

La projection JSON expose maintenant aussi un bloc `angles` dans le payload chart JSON public. Selon le mode et la source, les valeurs peuvent etre nulles, mais l'espace contractuel existe pour ASC/DSC/MC/IC.

### Points astraux

Depuis CS-187, les points astraux natals sont calcules depuis le referentiel DB-backed:

- les points et variantes viennent de `astral_points`, `astral_point_calculation_variants` et `astral_point_aliases`;
- les variantes directes utilisent une cle moteur explicite;
- les variantes derivees produisent une instruction source + offset;
- le champ canonique serialise est `astral_points`;
- `points` reste seulement un alias de compatibilite cote modele Python.

Les points peuvent etre inclus dans le calcul d'aspects uniquement si `include_points_in_aspects=true`. Par defaut, les aspects natals restent calcules entre planetes.

## Calcul astrologique structurel

### Aspects

Les aspects sont calcules a partir des definitions runtime actives, majeures et compatibles avec l'ecole d'aspects. L'orbe maximale est resolue par systeme, contexte, corps source/cible et specificite. Le resultat est trie de maniere deterministe et enrichi par le runtime aspects: ratio d'orbe, force, valence, type energetique et indicateurs d'orbe exacte ou serree.

### Maisons runtime

`build_house_runtime_data` enrichit chaque maison avec:

- signe de cuspide;
- signes contenus et signes interceptes quand le systeme le permet;
- occupants;
- maitre de maison;
- force structurelle;
- axe de maison.

Cette couche consomme les tables `astral_houses`, `astral_house_axis_*`, `astral_signs`, `astral_planets`, roles planetaires et dignites de maitrise.

### Signes runtime et signature

Depuis CS-185, le runtime natal charge les profils structurels de signes depuis `astral_sign_profiles`, `astral_elements`, `astral_modalities` et `astral_polarities`. `build_sign_runtime_data` regroupe les occupants par signe, active les dignites pertinentes, calcule une dominance bornee et propage element, modalite et polarite.

`ChartSignatureCalculator` derive ensuite les dominantes de signes, planetes, maisons, aspects, ainsi que la balance element/modality. Cette signature reste une synthese structurelle, pas une interpretation editoriale.

## Dignites planetaires

### Origine des donnees

CS-190 a ajoute les modeles SQLAlchemy, migrations, seeds et repositories pour les referentiels de dignites:

- effets fonctionnels et effets d'intensite;
- categories et tendances d'expression essentielles/accidentelles;
- types de dignites essentielles et accidentelles;
- schemas de conditions accidentelles;
- regles essentielles;
- bornes de termes;
- faces/decans;
- maitres de triplicite;
- profils et poids de scoring;
- regles accidentelles;
- table runtime/audit `astral_chart_planet_dignity_results`, dont le fichier de seed de structure existe avec `data: []`.

CS-191 branche ces donnees dans `AstrologyRuntimeReference.dignity_reference` et cree le moteur de calcul pur dans `backend/app/domain/astrology/dignities/**`.

### Calcul de secte

`SectCalculator` determine si le theme est diurne ou nocturne depuis la position objective du Soleil et les regles horizon chargees dans le runtime. Il ne code pas localement les maisons au-dessus ou au-dessous de l'horizon: il lit les conditions configurees dans le referentiel de dignites accidentelles.

### Dignites essentielles

`EssentialDignityCalculator` calcule les dignites essentielles depuis le runtime et les positions natales:

- domicile;
- exaltation;
- detriment;
- fall;
- triplicity;
- term;
- face/decan;
- peregrine.

`peregrine` est detecte quand aucune dignite essentielle positive n'est presente, et non quand aucun match essentiel n'existe. Les scores viennent des poids du profil de scoring runtime, par defaut `traditional_standard`.

### Dignites accidentelles

`AccidentalDignityCalculator` detecte les conditions objectives couvertes par CS-191:

- maisons angulaires, succedentes et cadentes;
- mouvement direct ou retrograde;
- joies planetaires;
- conditions solaires exclusives avec priorite cazimi, combust, under sunbeams;
- exclusion du Soleil pour les distances solaires afin d'eviter l'auto-match.

Les conditions sont stockees sous forme de regles runtime. Le calculateur ne lit pas la DB, n'importe pas SQLAlchemy et ne possede pas de mapping local de scores.

### Scoring par planete

`PlanetDignityScoringService` orchestre la secte, les dignites essentielles et accidentelles, puis produit un resultat par planete:

- `essential_score`;
- `accidental_score`;
- `total_score`;
- `functional_strength_score`;
- `expression_quality_score`;
- `intensity_score`;
- `essential_breakdown`;
- `accidental_breakdown`.

Chaque breakdown expose le type, la source, le score et une raison factuelle. Le moteur ne produit pas de texte interpretatif et ne depend ni de prediction, ni de LLM, ni d'API.

### Payload public

Le `NatalResult` expose maintenant:

```text
dignities:
  score_profile
  tradition
  reference_version
  sect
  planets
```

Chaque entree `planets[planet_code]` contient les scores et breakdowns de la planete. Les snapshots CS-191 prouvent que le bloc est additif: les champs natals existants restent stables, seul `dignities` est ajoute.

## Profils conditionnels planetaires

CS-192 ajoute `PlanetConditionProfile`, une synthese factuelle derivee de `PlanetDignityResult`. Le service `PlanetConditionProfileService` ne relit pas la DB et ne recalcule pas les dignites: il consomme les resultats de dignites et les poids deja charges dans `AstrologyRuntimeReference.dignity_reference`.

Chaque profil expose les axes suivants:

- `functional_strength`;
- `visibility`;
- `stability`;
- `intensity`;
- `coherence`;
- `support`;
- `constraint`;
- `ranking_score`;
- `condition_level`.

Le breakdown conserve les contributions de chaque dignite essentielle ou accidentelle avec les poids runtime associes. Les `explanation_facts` restent des faits courts, comme le nombre de dignites ou le score de classement. Le JSON public expose cette couche sous `planet_condition_profiles`.

Depuis CS-195, ces profils ne sont plus seulement la projection directe des dignites: `AdvancedConditionEngine` les enrichit avec les conditions avancees detectees. Les conditions avancees ajoutent des lignes `dignity_family="advanced"` dans le breakdown et ajustent les axes avant la production des signaux conditionnels et des dominances.

## Signaux conditionnels planetaires

CS-193 ajoute `PlanetConditionSignalBuilder`. Il transforme chaque `PlanetConditionProfile` enrichi en signaux techniques via les plages inclusives chargees depuis `AstrologyRuntimeReference.condition_signal_profiles`.

Le builder ne possede pas de seuil local de type `if visibility > ...`. Il lit un axe par son nom contractuel, verifie que la valeur est comprise entre `level_min` et `level_max`, puis produit un signal:

- `code`;
- `label`;
- `axis`;
- `level`;
- `level_min`;
- `level_max`;
- `axis_value`;
- `interpretation_use`;
- `priority_weight`;
- `prompt_hint`.

Les signaux sont tries par `priority_weight`, axe, code. Le `NatalResult` expose `condition_signals`; le JSON public expose `planet_condition_signals`. Cette surface sert aux futurs prompts/UI/adapters sans forcer ces consommateurs a repliquer des seuils ou a inspecter directement les scores.

## Conditions planetaires avancees

CS-195 ajoute `backend/app/domain/astrology/advanced_conditions/**`. Le moteur calcule des conditions supplementaires depuis les faits deja presents:

- reception mutuelle;
- hayz;
- out of sect;
- vitesse stationnaire, rapide ou lente;
- phases/orientations heliacales gouvernees par les faits accidentels;
- besiegement, bonification et maltreatment depuis les aspects configures et les natures planetaires runtime.

Le runtime associe a ces conditions contient les types actifs, un profil de scoring `traditional_advanced_v1` et des poids par axe conditionnel. Le moteur retourne deux choses: la liste `advanced_conditions` et les `condition_profiles` enrichis.

Les conditions avancees sont donc visibles a deux niveaux:

- directement dans `NatalResult.advanced_conditions` et le JSON public `advanced_conditions`;
- indirectement dans les profils conditionnels, les signaux conditionnels, la dominance et l'adaptation interpretative.

Le domaine `advanced_conditions/**` reste pur: pas d'import DB/API/services/prediction, pas de narration, pas de fallback de vocabulaire astrologique local.

## Planetes dominantes

CS-194 ajoute `PlanetDominanceEngine` et les contrats `DominantPlanetsResult`, `PlanetDominanceResult` et `PlanetDominanceFactor`. Le moteur calcule un classement factuel des planetes depuis les faits natals deja disponibles:

- maitre de l'Ascendant (`chart_ruler`) depuis les maitres de maisons resolus;
- angularite depuis les maisons runtime;
- force conditionnelle et visibilite depuis `PlanetConditionProfile`;
- planete la plus elevee;
- emphase des luminaires depuis le runtime planetes;
- charge de maitrise des maisons;
- centralite dans les aspects via `DominantAspectEvaluator`;
- poids des conditions avancees via `advanced_conditions`.

Les facteurs, poids, bornes de normalisation et profil actif viennent de `AstrologyRuntimeReference.dominance_reference`. Le profil actuel charge par seed est `natal_standard_v1`. Le resultat expose `top_planet_code`, `chart_ruler_code`, `most_elevated_planet_code` et la liste classee des planetes avec facteurs explicables.

Le JSON public expose cette couche sous `dominant_planets`, mais la projection est neutralisee en mode sans heure (`no_time` / `no_location_no_time`) car les maisons, l'angularite et l'elevation ne sont pas fiables sans heure.

## Couche d'adaptation interpretative

CS-196 ajoute `backend/app/domain/astrology/interpretation_adapters/**`. Cette couche ne redige pas une interpretation: elle transforme les faits objectifs en signaux semantiques normalises et themes actives.

`InterpretationAdapterEngine` consomme:

- profils conditionnels;
- signaux conditionnels;
- conditions avancees;
- planetes dominantes;
- dignites, aspects et positions passes comme contexte technique.

Il utilise le referentiel runtime `interpretation_adapter_reference`, compose de types de signaux, themes et regles. Le resultat contient:

- `signals`;
- `activated_themes`;
- `dominant_topics`;
- `dominant_axes`;
- `tension_patterns`;
- `support_patterns`;
- `critical_patterns`;
- `narrative_priorities`.

Cette surface est exposee dans `NatalResult.interpretation_adapter` et dans le JSON public `interpretation_adapter`, sauf en mode sans heure ou la projection publique la met a `null`. Elle prepare les couches aval de restitution sans importer LLM, prediction, persona ou texte editorial dans le domaine astrologique.

## Construction finale de `NatalResult`

Le resultat natal consolide aujourd'hui:

- metadonnees: `reference_version`, `ruleset_version`, `aspect_rules_version`, moteur, zodiaque, frame, systeme de maisons, ayanamsa, altitude et traces ephemerides;
- trace temps: `prepared_input`;
- faits astronomiques: `planet_positions`, `houses`, `astral_points`;
- relations: `aspects`;
- enrichissements: `signs_runtime`, `house_rulers`, `chart_balance`;
- scores et profils objectifs: `dignities`, `condition_profiles`, `condition_signals`, `advanced_conditions`, `dominant_planets`;
- preparation semantique non narrative: `interpretation_adapter`.

La persistance dans `chart_results.result_payload` conserve le payload complet avec hash d'entree. La projection JSON chart peut ajouter des libelles localises ou projections legacy, mais elle n'intervient pas dans le calcul lui-meme.

## Tables participant au calcul apres CS-196

En plus des tables deja listees dans la note du 2026-05-18, le calcul natal objectif consomme maintenant les referentiels de dignites, conditions, dominances et adaptation. Les tables directement chargees ou synchronisees par `sync_astral_dignity_seed_data` sont:

- `astral_accidental_dignity_categories`;
- `astral_accidental_dignity_condition_schemas`;
- `astral_accidental_dignity_expression_tendencies`;
- `astral_accidental_dignity_rules`;
- `astral_accidental_dignity_score_weights`;
- `astral_accidental_dignity_types`;
- `astral_advanced_condition_score_profiles`;
- `astral_advanced_condition_types`;
- `astral_advanced_condition_weights`;
- `astral_chart_planet_dignity_results`;
- `astral_decan_system_code`;
- `astral_dignity_functional_effects`;
- `astral_dignity_intensity_effects`;
- `astral_diginity_score_profiles`;
- `astral_dominance_factor_types`;
- `astral_dominance_score_profiles`;
- `astral_dominance_score_weights`;
- `astral_essential_dignity_categories`;
- `astral_essential_dignity_expression_tendencies`;
- `astral_essential_dignity_rules`;
- `astral_essential_dignity_score_weights`;
- `astral_essential_dignity_types`;
- `astral_face_decans`;
- `astral_interpretation_adapter_rules`;
- `astral_interpretation_signal_types`;
- `astral_interpretation_themes`;
- `astral_planet_condition_signal_profiles`;
- `astral_sect`;
- `astral_term_bounds`;
- `astral_term_system_code`;
- `astral_triplicity_ruler_assignments`.

Le meme seed service synchronise aussi des lookups astrologiques adjacents consommes par les dignites et conditions avancees: `astral_sources`, `astral_ruler_assignments_role`, `astral_planet_motion_states`, `astral_speed_relations`, `astral_heliacal_conditions`, `astral_horizon_positions`, `astral_sign_genders`, `astral_planet_natures` et `astral_condition_operators`.

La table `astral_chart_planet_dignity_results` existe pour runtime/audit et possede un fichier de seed declaratif, mais son `data` est vide. CS-191 ne l'utilise pas comme source du calcul natal: le moteur calcule les dignites a la volee depuis le runtime et les donnees natales objectives. Le repository sait ensuite upserter des resultats runtime detailles si un flux d'audit dedie l'appelle.

Les tables `astral_advanced_condition_*`, `astral_dominance_*` et `astral_interpretation_*` jouent le meme role de referentiel: elles gouvernent les poids, types et regles; elles ne stockent pas le resultat final d'un theme. Les resultats effectifs restent serialises dans `chart_results.result_payload`.

### Presence des seeds JSON

Les fichiers de seed suivants sont presents sous `docs/db_seeder/astrology/` pour les nouvelles surfaces CS-190 a CS-196:

- dignites et lookups: `astral_dignity_functional_effects.json`, `astral_dignity_intensity_effects.json`, `astral_essential_dignity_categories.json`, `astral_essential_dignity_expression_tendencies.json`, `astral_accidental_dignity_categories.json`, `astral_accidental_dignity_expression_tendencies.json`, `astral_accidental_dignity_condition_schemas.json`, `astral_essential_dignity_types.json`, `astral_accidental_dignity_types.json`, `astral_diginity_score_profiles.json`, `astral_term_system_code.json`, `astral_decan_system_code.json`, `astral_sect.json`, `astral_term_bounds.json`, `astral_face_decans.json`, `astral_essential_dignity_rules.json`, `astral_triplicity_ruler_assignments.json`, `astral_essential_dignity_score_weights.json`, `astral_accidental_dignity_rules.json`, `astral_accidental_dignity_score_weights.json`, `astral_chart_planet_dignity_results.json`;
- signaux conditionnels: `astral_planet_condition_signal_profiles.json`;
- dominance: `astral_dominance_factor_types.json`, `astral_dominance_score_profiles.json`, `astral_dominance_score_weights.json`;
- conditions avancees: `astral_advanced_condition_types.json`, `astral_advanced_condition_score_profiles.json`, `astral_advanced_condition_weights.json`;
- adaptation interpretative: `astral_interpretation_signal_types.json`, `astral_interpretation_themes.json`, `astral_interpretation_adapter_rules.json`.

## Garde-fous et validations

Les garde-fous importants apres CS-196 sont:

- le domaine `backend/app/domain/astrology/dignities/**` ne doit pas importer `app.infra`, `app.services`, `app.api`, SQLAlchemy ou Session;
- les domaines `condition/**`, `dominance/**`, `advanced_conditions/**` et `interpretation_adapters/**` suivent la meme frontiere: pas d'infra DB, pas d'API, pas de services applicatifs, pas de prediction;
- aucun score astrologique ne doit etre recree en constante Python locale;
- les calculateurs de dignites, conditions, dominances et adapters ne doivent pas contenir de prompt LLM, narration, persona ou micro-note de restitution;
- le runtime doit charger `dignity_reference`, `condition_signal_profiles`, `dominance_reference`, `advanced_condition_reference` et `interpretation_adapter_reference` avant le calcul;
- `json_builder.py` ne doit que projeter les resultats deja presents dans `NatalResult`, sans instancier les moteurs ni comparer des seuils;
- le snapshot du payload doit rester stable hors ajouts contractuels explicites.

Preuves recentes:

- CS-191: moteur de dignites avance valide par tests cibles, backend complet, Ruff, scans anti-import DB/anti-hardcoding/anti-LLM et smoke `/docs`;
- CS-192: profils conditionnels ajoutes, `pytest -q` a passe avec 2693 tests, garde anti frontiere et scans anti seuils locaux;
- CS-193: signaux conditionnels ajoutes, tests cibles 5/20/22 passes, migration `--long` OK, Ruff repo OK, scans anti seuils locaux et anti narration;
- CS-194: dominantes planetaires ajoutees, tests cibles 56 passes, integration migration OK, backend complet 2712 passes;
- CS-195: conditions avancees ajoutees, validations ciblees 80 passes, backend complet 2727 passes, Ruff OK, smoke `/docs` OK;
- CS-196: couche d'adaptation interpretative ajoutee, tests cibles 70 passes, migration `--long` OK, Ruff OK, smoke import backend OK.

## Limites actuelles

1. Le frontend ne consomme pas encore pleinement `dignities`, `planet_condition_profiles`, `planet_condition_signals`, `advanced_conditions`, `dominant_planets`, `interpretation_adapter`, les points astraux et les enrichissements runtime.
2. La table `astral_chart_planet_dignity_results` n'est pas encore une persistance independante des resultats de dignites par theme.
3. Les couches `astral_advanced_condition_*`, `astral_dominance_*` et `astral_interpretation_*` gouvernent le calcul, mais ne stockent pas encore d'historique detaille par theme hors `chart_results.result_payload`.
4. La precision astronomique reste dependante de SwissEph, de ses fichiers d'ephemerides et du bootstrap runtime.
5. Les etoiles fixes restent hors calcul natal; depuis CS-189 elles sont branchees dans le runtime et le scoring de prediction quotidienne, pas dans `NatalResult`.
6. `interpretation_adapter` reste une couche de preparation semantique, pas une interpretation editoriale finale.

## Conclusion

La chaine de calcul du theme natal est maintenant plus complete et plus explicable. Le coeur reste le meme: preparation temporelle robuste, moteur astronomique, referentiel runtime DB-backed, calcul des positions, maisons, aspects et enrichissements structurels. Les stories recentes ajoutent une pile factuelle complete au-dessus des dignites: profils conditionnels, signaux conditionnels, conditions avancees, dominantes planetaires et adaptation semantique.

Le prochain travail utile n'est pas une refonte du calcul. Les priorites sont plutot l'exploitation frontend des nouveaux blocs publics, la decision produit sur une persistance audit detaillee des resultats intermediaires, et le maintien de cas golden SwissEph externes pour verrouiller la precision astronomique.
