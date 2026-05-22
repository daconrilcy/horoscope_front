# Synthese des calculs astrologiques apres CS-207 a CS-216

Date: 2026-05-22
Perimetre: moteur backend du theme natal, conditions traditionnelles avancees, nouvelles conditions planetaires avancees, dignites accidentelles, profils d'interpretation pre-narratifs.
Document source: `docs/recherches astro/2026-05-21-engine-theme-astral-post-cs-207.md`.
Stories consolidees: CS-207 a CS-216.

## Synthese

Apres CS-216, le calcul astrologique du theme natal reste concentre cote backend. Le frontend ne calcule toujours pas les positions, maisons, aspects, dignites, conditions, dominantes ou profils astrologiques: il consomme une projection publique deja produite par le backend.

La chaine post-CS-207 ajoute un nouveau sous-systeme interne, `planetary_conditions`, qui calcule des faits planetaires avances a partir des positions et vitesses deja produites par le moteur natal. Ces faits couvrent la proximite solaire, la relation oriental/occidental au Soleil, le mouvement apparent, la visibilite heliacale simplifiee et la phase lunaire. Ils sont ensuite utilises par deux couches aval:

- le scoring de dignites accidentelles, via des modificateurs internes;
- les profils d'interpretation avances, sous forme de fragments symboliques non narratifs.

Point important: `advanced_planetary_conditions` et `interpretation_profiles_by_planet` sont volontairement exclus du dump JSON, du schema `NatalResult` et de l'OpenAPI. Les stories CS-214 a CS-216 branchent donc des faits internes dans le graphe de calcul sans ouvrir un nouveau contrat public frontend/API.

## Flux actuel du theme natal

Le flux nominal reste celui documente le 2026-05-21, avec trois ajouts internes importants:

1. `build_natal_result` prepare les donnees natales, calcule les positions planetaires, maisons, points astraux et aspects.
2. Les positions sont validees et converties en `PlanetPosition`.
3. `calculate_advanced_planetary_conditions` assemble les calculateurs purs de `planetary_conditions`.
4. Le resultat interne `AdvancedPlanetaryConditionsResult` est passe a `PlanetDignityScoringService`.
5. Les dignites essentielles et accidentelles sont calculees; les conditions planetaires avancees ajoutent des modificateurs accidentels internes.
6. `resolve_advanced_condition_profiles` produit des profils symboliques par planete depuis les bundles deja calcules.
7. La suite existante reste active: profils conditionnels, signaux conditionnels, conditions avancees traditionnelles, dominantes, adapter interpretatif et conditions traditionnelles normalisees.
8. `NatalResult` conserve les nouveaux blocs internes en champs exclus, puis expose seulement la projection publique deja stabilisee.

## Nouveau sous-systeme `planetary_conditions`

CS-208 a cree les contrats immuables. Les objets sont des dataclasses `frozen=True, slots=True`, avec collections figees en tuples ou mappings read-only. Le package ne depend pas de FastAPI, SQLAlchemy, Pydantic, DB, services applicatifs, scoring, prompt ou frontend.

Les contrats principaux sont:

- `SolarProximityCondition`;
- `PlanetarySolarPhaseRelation`;
- `PlanetaryMotionCondition`;
- `PlanetVisibilityCondition`;
- `MoonPhaseCondition`;
- `PlanetaryConditionSignal`;
- `PlanetaryConditionsBundle`;
- `AdvancedPlanetaryConditionsResult`.

Les enums normalisent les familles et etats: proximite solaire, relation solaire, direction de mouvement, vitesse, visibilite, phase lunaire, severite, confiance et famille de condition.

## Calculateurs purs ajoutes

### Proximite solaire

CS-209 ajoute `solar_proximity_calculator.py`.

Le calcul mesure la distance angulaire minimale entre chaque planete et le Soleil, avec gestion du wrap-around zodiacal. Les seuils par defaut sont portes par `SolarProximityThresholds`:

- cazimi jusqu'a 17 minutes d'arc;
- combust jusqu'a 8,5 degres;
- under beams jusqu'a 15 degres;
- none au-dela.

Le Soleil retourne une condition inactive `none`. Les seuils sont inclusifs et personnalisables via contrat.

### Mouvement planetaire

CS-210 ajoute `planetary_motion_calculator.py` et `planetary_motion_profiles.py`.

Le calcul classe:

- direction directe;
- retrogradation;
- stationnarite prioritaire;
- vitesse tres lente, lente, normale, rapide ou tres rapide;
- ratio de vitesse normalise quand la vitesse moyenne est exploitable.

Le catalogue `DEFAULT_PLANETARY_MOTION_PROFILES` porte les profils par planete. Les profils invalides ou incompatibles echouent explicitement au lieu de produire un fallback silencieux.

### Relation solaire oriental/occidental

CS-211 ajoute `solar_phase_relation_calculator.py`.

Le calcul utilise l'angle relatif `(planete - soleil) % 360`:

- conjonction solaire autour de 0/360 selon tolerance;
- occidental pour `0 < angle <= 180`;
- oriental pour `180 < angle < 360`.

Le Soleil est traite comme `conjunct_solar`. La tolerance de conjonction est bornee pour ne pas absorber le demi-cercle.

### Phase lunaire

CS-212 ajoute `moon_phase_calculator.py`.

Le calcul utilise l'angle Soleil-Lune:

- nouvelle lune;
- croissant;
- premier quartier;
- gibbeuse croissante;
- pleine lune;
- gibbeuse decroissante;
- dernier quartier;
- croissant decroissant;
- balsamique.

Il expose aussi l'etat croissant/decroissant/exact, l'illumination approximative par formule cosinus et un `phase_index` stable.

### Visibilite planetaire

CS-213 ajoute `planetary_visibility_calculator.py`.

Cette couche compose la proximite solaire et la relation solaire deja calculees. Elle classe notamment:

- visible;
- conjunct solar;
- invisible;
- under beams;
- emerging.

Le batch exige les relations necessaires et echoue explicitement en cas de donnees manquantes, plutot que masquer le probleme par `unknown`.

## Orchestration interne dans le calcul natal

CS-214 ajoute `advanced_planetary_conditions_runtime.py`.

`calculate_advanced_planetary_conditions` recoit:

- `planetary_positions`, sous forme de mapping planete -> objet portant une longitude;
- `planetary_speeds_deg_per_day`, sous forme de mapping planete -> vitesse.

Il extrait les longitudes finies, exige la presence du Soleil, puis assemble:

- conditions de proximite solaire;
- relations solaires;
- conditions de mouvement;
- conditions de visibilite;
- phase lunaire si Soleil et Lune sont disponibles;
- signaux techniques par planete;
- signaux globaux lies a la phase lunaire.

Le resultat est stocke dans `NatalResult.advanced_planetary_conditions`, mais avec `SkipJsonSchema` et `Field(exclude=True)`. Il ne sort donc pas dans `model_dump(mode="json")`, ni dans le schema JSON, ni dans OpenAPI.

## Signaux techniques internes

`signal_factory.py` transforme certains faits en `PlanetaryConditionSignal`:

- combust;
- under beams;
- retrograde;
- stationary;
- oriental;
- occidental;
- emerging;
- waxing moon;
- waning moon.

Ces signaux restent techniques et non narratifs. Ils portent condition, famille, severite, confiance, activation, valeur, unite et metadata eventuelle.

## Effet sur les dignites accidentelles

CS-215 branche les nouvelles conditions planetaires avancees dans `PlanetDignityScoringService`.

La couche `dignities/advanced_condition_modifiers.py` consomme les bundles deja calcules et produit des `AccidentalDignityModifier`. Elle ne recalcule ni positions, ni vitesses, ni phases.

Les modificateurs V1 sont portes par `advanced_condition_modifier_profiles.py`:

- `cazimi_bonus`: +5;
- `combust_penalty`: -5;
- `under_beams_penalty`: -2;
- `retrograde_penalty`: -3;
- `stationary_bonus`: +2;
- `very_fast_bonus`: +1;
- `very_slow_penalty`: -1;
- `invisible_penalty`: -4;
- `emerging_bonus`: +2;
- `oriental_superior_bonus`: +1 pour Mars, Jupiter, Saturne;
- `occidental_superior_penalty`: -1 pour Mars, Jupiter, Saturne;
- `full_moon_bonus`: +2 pour la Lune;
- `new_moon_penalty`: -2 pour la Lune.

Ces modificateurs alimentent le score accidentel sans changer le contrat public JSON: le champ interne `advanced_condition_modifiers` est exclu des dumps et schemas.

## Profils d'interpretation pre-narratifs

CS-216 ajoute `app/domain/astrology/interpretation/advanced_conditions`.

Cette couche ne produit pas un texte utilisateur final. Elle transforme des faits deja calcules en profils symboliques bornes:

- polarite;
- intensite;
- mots-cles;
- themes;
- manifestations;
- axes psychologiques;
- axes comportementaux;
- notes optionnelles.

Le runtime `resolve_advanced_condition_profiles` lit les conditions presentes dans le bundle:

- cazimi, combust, under beams;
- retrograde, stationary;
- invisible, emerging;
- oriental, occidental;
- pleine lune et nouvelle lune pour la Lune.

La resolution priorise les profils exacts `planete + tradition`, puis `planete`, puis `tradition`, puis generique. Le catalogue contient notamment des variantes Mercure combust et medievales, des profils retrogrades, stationnaires, emerging, pleine lune et nouvelle lune.

Le resultat est stocke dans `NatalResult.interpretation_profiles_by_planet`, egalement exclu du JSON et du schema.

## Contrats publics inchanges

Le contrat public stabilise par CS-201 reste le contrat expose. Les nouveaux blocs CS-214 a CS-216 ne sont pas ajoutes a la projection publique.

Les sorties publiques conservent notamment:

- `planet_positions`;
- `houses`;
- `angles`;
- `astral_points`;
- `signs_runtime`;
- `aspects`;
- `dignities`;
- `traditional_conditions`;
- `planet_condition_profiles`;
- `planet_condition_signals`;
- `advanced_conditions`;
- `dominant_planets`;
- `interpretation_adapter`.

Les nouvelles conditions planetaires avancees influencent donc le calcul interne, surtout les dignites accidentelles et les profils pre-narratifs, sans ajouter de nouvelle surface frontend.

## Separation des responsabilites

La separation actuelle est nette:

- `calculators` et ephemerides produisent la geometrie natale;
- `planetary_conditions` calcule des faits astronomico-astrologiques purs depuis positions et vitesses;
- `dignities` consomme ces faits pour modifier le score accidentel;
- `interpretation/advanced_conditions` produit des profils symboliques internes;
- `advanced_conditions` conserve la chaine traditionnelle avancee precedente: hayz, secte, mitigation benefique/malefique, reception, vitesse traditionnelle, phases/orientations heliacales, besiegement, bonification, maltreatment;
- `json_builder.py` reste une projection serialize-only;
- le frontend reste display-only.

Cette separation evite trois risques: duplication doctrinale, recalcul dans les couches aval, et ouverture prematuree d'un contrat public.

## Garde-fous maintenus

Les stories CS-207 a CS-216 ajoutent ou confirment les garde-fous suivants:

- aucun calculateur `planetary_conditions` ne depend de DB, API, frontend, Pydantic, FastAPI ou SQLAlchemy;
- aucun calculateur pur ne contient de logique de scoring, narration, prompt ou LLM;
- les conditions planetaires avancees ne sont pas exposees en OpenAPI;
- les modificateurs de dignites consomment des faits deja calcules;
- les profils d'interpretation ne recalculent pas les conditions;
- les erreurs de donnees manquantes sont explicites dans les batchs importants;
- les nouveaux champs internes de `NatalResult` sont exclus des dumps et schemas;
- aucun contrat public frontend n'a ete ajoute pour CS-214 a CS-216.

## Validation constatee dans les stories

Les evidences de fermeture indiquent:

- CS-207: audit final de la chaine traditionnelle avancee, sans blocker in-domain;
- CS-208: contrats immuables purs, full backend suite OK;
- CS-209: proximite solaire testee, OpenAPI smoke OK;
- CS-210: mouvement planetaire et profils de vitesse testes;
- CS-211: relation solaire oriental/occidental testee, cas 180 degres corrige;
- CS-212: phase lunaire testee, tolerances d'angles exacts corrigees;
- CS-213: visibilite planetaire testee, backend smoke OK;
- CS-214: integration interne dans `NatalResult`, absence de schema public verifiee;
- CS-215: integration scoring accidentel, smoke `/health` OK;
- CS-216: profils d'interpretation internes, full backend suite OK.

La derniere evidence CS-216 annonce `2942 passed, 1 skipped, 1177 deselected` sur la suite backend complete.

## Limites actuelles

1. Les conditions planetaires avancees CS-214 ne sont pas encore une surface publique. C'est volontaire, mais le frontend ne peut pas les afficher directement.
2. Les seuils et deltas V1 sont codifies dans des profils statiques Python, contrairement a une partie du runtime astrologique DB-backed precedent.
3. La visibilite reste une composition geometrique simplifiee; elle ne remplace pas une modelisation astronomique complete des levers/couchers heliacaux selon latitude, atmosphere et magnitude.
4. Les profils d'interpretation sont pre-narratifs: ils ne constituent pas encore une interpretation editoriale utilisateur.
5. Les nouvelles conditions internes coexistent avec `advanced_conditions`, qui porte deja certaines notions traditionnelles proches. Le garde-fou essentiel est de conserver un proprietaire clair pour chaque usage.

## Conclusion

Au 2026-05-22, le moteur natal est devenu une chaine en deux niveaux.

Le premier niveau, deja stabilise par CS-193 a CS-207, expose les faits publics du theme: geometrie, dignites, secte, conditions traditionnelles, conditions avancees, profils, signaux, dominantes et adapter interpretatif.

Le second niveau, ajoute par CS-208 a CS-216, calcule des conditions planetaires avancees internes plus fines: proximite solaire, mouvement, relation solaire, visibilite et phase lunaire. Ces faits enrichissent deja les dignites accidentelles et preparent des profils symboliques, mais restent hors JSON public et hors frontend.

Le prochain travail utile serait de decider si ces nouveaux faits doivent rester uniquement internes au scoring ou devenir une surface publique documentee. Tant que ce choix produit n'est pas tranche, la contrainte saine est de garder `planetary_conditions` comme moteur pur, sans narration, sans persistence propre et sans exposition API implicite.
