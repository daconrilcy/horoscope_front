# Calcul du theme natal apres stories runtime et dignites

Date: 2026-05-19  
Perimetre: calcul backend du theme natal, referentiel runtime astrologique, payload `NatalResult`, persistance et consommation applicative.  
Sources consolidees: `2026-05-16-audit-chaine-calcul-theme-natal.md`, `2026-05-18-calcul-theme-astrologique.md`, stories CS-185 a CS-191.

## Synthese

Le calcul du theme natal reste orchestre cote backend. Le frontend ne calcule pas les positions, les maisons, les aspects, les points astraux, les dominances ou les dignites: il declenche la generation, lit le dernier resultat persiste et affiche le payload.

Depuis les dernieres stories implementees, le `NatalResult` ne contient plus seulement la geometrie natale historique. Il expose maintenant une couche runtime plus riche:

- positions planetaires calculees par moteur SwissEph ou moteur simplifie encadre;
- maisons, cuspides, occupants, axes, forces de maisons et maitres;
- aspects calcules depuis les definitions et orbes runtime;
- points astraux natals DB-backed;
- runtime signes avec profils structurels DB-backed;
- signature et balance du theme;
- dignites planetaires essentielles et accidentelles scorees, explicables et fondees sur le referentiel runtime.

Le changement majeur post CS-190/CS-191 est l'ajout d'un moteur de dignites planetaires avance. Les tables et seeds de dignites sont charges dans le runtime, puis un domaine pur `backend/app/domain/astrology/dignities/**` calcule les scores factuels par planete. Le payload natal gagne un bloc `dignities` sans modifier la semantique des champs existants.

## Flux nominal actualise

1. L'utilisateur renseigne ses donnees de naissance via `PUT /v1/users/me/birth-data`.
2. Le front appelle `POST /v1/users/me/natal-chart` avec `accurate=true`.
3. `UserNatalChartService.generate_for_user` charge le profil, exige l'heure de naissance, resout le lieu et construit un `BirthInput`.
4. `NatalCalculationService.calculate` prepare les options astrologiques, charge `AstrologyRuntimeReference`, selectionne le moteur et appelle `build_natal_result`.
5. `build_natal_result` prepare le temps, calcule les positions, maisons, points astraux, aspects et enrichissements runtime.
6. Le moteur de dignites calcule la secte du theme, les dignites essentielles, les dignites accidentelles et les scores agreges par planete.
7. `ChartResultService.persist_trace` persiste le payload complet dans `chart_results`.
8. `GET /v1/users/me/natal-chart/latest` restitue le dernier theme, avec projection JSON publique et `astro_profile` derive.
9. Les couches d'interpretation ou LLM consomment le resultat calcule; elles ne modifient pas le calcul astronomique ou astrologique objectif.

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
- depuis CS-190/CS-191, referentiel avance de dignites planetaires via `dignity_reference`.

Le runtime de dignites contient les inventaires de types essentiels et accidentels, systemes de termes et decans, profils de scoring, poids de scoring, regles essentielles, maitres de triplicite, bornes de termes, faces/decans et regles accidentelles. Les preuves CS-191 indiquent notamment 5 profils de scoring, 38 regles essentielles, 12 maitres de triplicite, 60 bornes de termes, 36 faces/decans et 41 regles accidentelles dans le snapshot de reference.

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

## Nouveau bloc: dignites planetaires

### Origine des donnees

CS-190 a ajoute les modeles SQLAlchemy, migrations, seeds et repositories pour les referentiels de dignites:

- types de dignites essentielles et accidentelles;
- regles essentielles;
- bornes de termes;
- faces/decans;
- maitres de triplicite;
- profils et poids de scoring;
- regles accidentelles;
- table runtime/audit `astral_chart_planet_dignity_results`, non alimentee par seed obligatoire.

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

## Construction finale de `NatalResult`

Le resultat natal consolide aujourd'hui:

- metadonnees: `reference_version`, `ruleset_version`, `aspect_rules_version`, moteur, zodiaque, frame, systeme de maisons, ayanamsa, altitude et traces ephemerides;
- trace temps: `prepared_input`;
- faits astronomiques: `planet_positions`, `houses`, `astral_points`;
- relations: `aspects`;
- enrichissements: `signs_runtime`, `house_rulers`, `chart_balance`;
- scores objectifs: `dignities`.

La persistance dans `chart_results.result_payload` conserve le payload complet avec hash d'entree. La projection JSON chart peut ajouter des libelles localises ou projections legacy, mais elle n'intervient pas dans le calcul lui-meme.

## Tables participant au calcul apres CS-191

En plus des tables deja listees dans la note du 2026-05-18, le calcul natal objectif consomme maintenant les referentiels de dignites avances:

- `astral_accidental_dignity_condition_schemas`;
- `astral_accidental_dignity_rules`;
- `astral_accidental_dignity_score_weights`;
- `astral_accidental_dignity_types`;
- `astral_decan_system_code`;
- `astral_diginity_score_profiles`;
- `astral_essential_dignity_rules`;
- `astral_essential_dignity_score_weights`;
- `astral_essential_dignity_types`;
- `astral_face_decans`;
- `astral_sect`;
- `astral_term_bounds`;
- `astral_term_system_code`;
- `astral_triplicity_ruler_assignments`.

La table `astral_chart_planet_dignity_results` existe pour runtime/audit, mais CS-191 ne l'utilise pas comme source du calcul natal. Le moteur calcule les dignites a la volee depuis le runtime et les donnees natales objectives.

## Garde-fous et validations

Les garde-fous importants apres CS-191 sont:

- le domaine `backend/app/domain/astrology/dignities/**` ne doit pas importer `app.infra`, `app.services`, `app.api`, SQLAlchemy ou Session;
- aucun score astrologique ne doit etre recree en constante Python locale;
- les calculateurs de dignites ne doivent pas contenir de prompt, LLM, interpretation ou micro-note;
- le runtime doit charger `dignity_reference` avant le calcul;
- le snapshot du payload doit rester stable hors ajouts contractuels explicites.

Preuves CS-191:

- tests cibles: 51 passes;
- backend complet: 2686 passes, 1 skipped, 1177 deselected;
- `ruff format --check` et `ruff check` OK;
- scans anti-import DB, anti-hardcoding de scores et anti-LLM sans hit;
- smoke local backend sur `/docs` OK.

## Limites actuelles

1. Le frontend ne consomme pas encore pleinement le bloc `dignities`, les points astraux et les enrichissements runtime.
2. La table `astral_chart_planet_dignity_results` n'est pas encore une persistance independante des resultats de dignites par theme.
3. La precision astronomique reste dependante de SwissEph, de ses fichiers d'ephemerides et du bootstrap runtime.
4. Les etoiles fixes restent hors calcul natal; depuis CS-189 elles sont branchees dans le runtime et le scoring de prediction quotidienne, pas dans `NatalResult`.
5. Les donnees accidentelles couvertes par CS-191 sont factuelles et scorees, mais elles ne constituent pas encore une couche d'interpretation editoriale.

## Conclusion

La chaine de calcul du theme natal est maintenant plus complete et plus explicable. Le coeur reste le meme: preparation temporelle robuste, moteur astronomique, referentiel runtime DB-backed, calcul des positions, maisons, aspects et enrichissements structurels. Les stories recentes ajoutent une etape importante: les dignites planetaires sont desormais calculees comme faits natals objectifs, scorees depuis des profils runtime et exposees dans `NatalResult`.

Le prochain travail utile n'est pas une refonte du calcul. Les priorites sont plutot l'exploitation frontend du nouveau bloc `dignities`, la decision produit sur la persistance audit detaillee des dignites, et le maintien de cas golden SwissEph externes pour verrouiller la precision astronomique.
