# Engine du theme astral apres CS-193 a CS-207

Date: 2026-05-21  
Perimetre: engine backend du theme natal, runtime astrologique, payload `NatalResult`, projection JSON publique, persistance d'audit, consommation frontend expert.  
Sources consolidees: `docs/recherches astro/2026-05-19-calcul-theme-natal-post-stories.md`, stories CS-193 a CS-207 et evidences associees.

## Synthese

Le theme astral natal reste calcule cote backend. Le frontend ne calcule pas les positions, maisons, aspects, dignites, conditions traditionnelles, conditions avancees, dominances ou signaux: il declenche la generation, recupere le dernier resultat persiste et affiche les faits publics deja projetes.

Depuis le document du 2026-05-19, la pile "dignites, profils, signaux, conditions avancees, dominances, adapter" a ete stabilisee par CS-193 a CS-207. Les changements importants sont:

- les signaux conditionnels planetaires sont gouvernes par runtime et exposes sans seuil local;
- les dominantes planetaires sont calculees depuis les faits natals et le runtime de dominance;
- les conditions avancees sont enrichies par une couche traditionnelle plus explicite;
- la secte du theme est devenue un contrat strict `ChartSectResult`;
- chaque planete porte une condition de secte explicite `PlanetSectCondition`;
- hayz, rejoicing et les conditions traditionnelles sont normalises dans un bloc public `traditional_conditions`;
- les cas golden hellenistiques/medievaux et les cas de triplicite dependante de la secte verrouillent les comportements attendus;
- la projection JSON publique a ete nettoyee pour rester une projection serialize-only;
- le frontend expose un panneau expert display-only qui consomme ces faits;
- les resultats de dignites peuvent etre persistes dans `astral_chart_planet_dignity_results` en audit detaille, en plus du snapshot `chart_results.result_payload`;
- les benefiques/malefiques recoivent des signaux de mitigation par la secte depuis le runtime, sans constantes locales;
- CS-207 cloture la chaine traditionnelle avancee comme auditee, testee et sans blocker in-domain restant.

Le moteur actuel n'est plus seulement un calcul astronomique enrichi. C'est un graphe factuel: geometrie natale, runtime astrologique, dignites, secte, conditions traditionnelles, conditions avancees, profils conditionnels, signaux, dominances, adaptation semantique et surfaces de projection. Cette pile reste objective: elle ne genere pas de narration finale, de conseil utilisateur ou de prompt LLM.

## Flux nominal actualise

1. L'utilisateur renseigne ses donnees de naissance via `PUT /v1/users/me/birth-data`.
2. Le frontend appelle `POST /v1/users/me/natal-chart` avec les options de calcul.
3. `UserNatalChartService.generate_for_user` valide le profil, exige les donnees necessaires et construit un `BirthInput`.
4. `NatalCalculationService.calculate` resout les options astrologiques, charge `AstrologyRuntimeReference`, selectionne le moteur et appelle `build_natal_result`.
5. `build_natal_result` prepare le temps, calcule positions, maisons, points astraux, aspects et enrichissements runtime.
6. Le moteur de dignites calcule une seule fois la secte du theme sous forme de `ChartSectResult`.
7. `PlanetSectConditionCalculator` derive la condition de secte par planete depuis la secte du theme et les donnees runtime.
8. `PlanetDignityScoringService` calcule les dignites essentielles, accidentelles et les scores par planete avec la secte et la condition de secte precalculees.
9. `AdvancedConditionEngine` detecte les conditions avancees: hayz, out-of-sect, vitesse, reception, phases/orientations, conditions relationnelles, mitigation benefique/malefique par secte, etc.
10. `TraditionalConditionNormalizer` produit `traditional_conditions` depuis les faits deja calcules: dignites, secte, hayz, rejoicing, conditions avancees.
11. `PlanetConditionProfileService` enrichit les profils conditionnels depuis les dignites et conditions avancees.
12. `PlanetConditionSignalBuilder` transforme les profils en signaux conditionnels gouvernes par `condition_signal_profiles`.
13. `ChartSignatureCalculator` et `PlanetDominanceEngine` calculent la balance et les planetes dominantes.
14. `InterpretationAdapterEngine` transforme les faits disponibles en signaux semantiques et themes actives, sans narration editoriale.
15. `ChartResultService.persist_trace` persiste le payload complet dans `chart_results`.
16. Si les dignites sont presentes, `ChartResultService` upsert aussi les resultats d'audit dans `astral_chart_planet_dignity_results`.
17. `GET /v1/users/me/natal-chart/latest` renvoie la projection publique serialize-only.
18. Le frontend, notamment `NatalExpertPanel`, affiche les faits publics sans recalculer de doctrine astrologique.

## Socle astronomique

La preparation des donnees natales reste inchangee:

- validation stricte de `BirthInput`;
- resolution du fuseau IANA;
- refus des heures locales ambigues ou inexistantes pendant les transitions DST;
- conversion local vers UTC;
- calcul du jour julien UT;
- trace optionnelle `delta_t_sec` et `jd_tt`.

SwissEph reste le moteur de production pour le mode accurate. Il recoit le jour julien UT via `swe.calc_ut`, normalise les longitudes, calcule la vitesse longitudinale et expose la retrogradation. Les maisons sont calculees via `swe.houses_ex` quand le systeme demande le support SwissEph.

Le moteur simplifie reste un chemin interne ou de fallback encadre. Il ne doit pas remplacer silencieusement le moteur accurate.

## Runtime astrologique

`AstrologyRuntimeReference` reste la source de verite. Il charge notamment:

- signes, maisons, planetes, roles et systemes astrologiques;
- definitions d'aspects, familles, profils et orbes;
- profils de signes, elements, modalites et polarites;
- points astraux, variantes et aliases moteur;
- axes de maisons et points d'angle;
- referentiel de dignites: types, regles, termes, decans, triplicites, scoring, secte;
- profils de signaux conditionnels;
- referentiel de dominance;
- referentiel de conditions avancees;
- referentiel d'adaptation interpretative;
- natures planetaires, conditions heliacales, relations de vitesse, positions d'horizon et operateurs.

Les stories recentes ont renforce la regle d'ownership: le runtime porte les donnees doctrinales, les domaines purs calculent, les services projettent ou persistent, le frontend affiche.

## Dignites, secte et conditions traditionnelles

### Secte du theme

Depuis CS-197, la secte n'est plus un simple champ implicite. `SectCalculator` retourne un contrat strict `ChartSectResult`, partage par tous les resultats de dignites d'un meme theme.

Le contrat expose notamment:

- le code de secte du theme;
- les booleens jour/nuit ou horizon;
- les faits necessaires aux calculateurs aval;
- une validation stricte des valeurs coherentes.

Les regles d'horizon viennent du runtime. Les constantes locales de type maisons au-dessus ou au-dessous de l'horizon sont interdites dans le domaine.

### Condition de secte par planete

Depuis CS-198, chaque `PlanetDignityResult` peut porter une `PlanetSectCondition`:

- `in_sect` pour une planete conforme a la secte active;
- `out_of_sect` pour une planete hors secte;
- `common` ou comportement variable pour les cas comme Mercure selon le runtime;
- `unknown` quand le runtime ne permet pas d'evaluer proprement.

La projection publique expose ce fait sous `dignities.planets[*].sect_condition`. Les couches aval consomment ce contrat et ne recalculent pas la condition de secte.

### Dignites essentielles

`EssentialDignityCalculator` calcule toujours:

- domicile;
- exaltation;
- detriment;
- fall;
- triplicity;
- term;
- face/decan;
- peregrine.

CS-205 verrouille le cas important de la triplicite dependante de la secte. Le choix du maitre de triplicite se fait depuis `AstrologyRuntimeReference.dignity_reference.triplicity_rulers` et la secte active du theme. Les cas day/night/participating sont couverts par tests golden, sans table locale element -> maitre.

### Dignites accidentelles

`AccidentalDignityCalculator` reste responsable des conditions factuelles comme:

- angularite, succedence, cadence;
- mouvement direct ou retrograde;
- joies planetaires;
- conditions solaires exclusives;
- exclusions necessaires pour eviter les auto-matchs du Soleil.

Les regles viennent du runtime, pas de constantes locales.

### Hayz et rejoicing

CS-199 et CS-204 rendent hayz et rejoicing explicites:

- hayz est evalue dans le domaine `advanced_conditions`;
- hayz depend de la condition de secte canonique `PlanetSectCondition`;
- les facteurs non-secte de hayz restent runtime-backed;
- une condition de secte manquante provoque une erreur explicite dans les chemins qui l'exigent;
- rejoicing est normalise comme fait traditionnel explicite;
- `rejoicing_house` est lu depuis les regles accidentelles runtime quand disponible.

Le bloc public `traditional_conditions` expose ces contrats par `planet_code`. En mode sans heure fiable, `traditional_conditions` est neutralise a `null`.

### Conditions traditionnelles normalisees

`TraditionalConditionNormalizer` est le proprietaire canonique de `traditional_conditions`. Il prend des faits deja calcules et produit une structure par planete incluant notamment:

- hayz;
- rejoicing;
- faits de secte utiles;
- conditions de mitigation benefique/malefique quand presentes;
- liens vers les dignites et conditions avancees pertinentes.

Cette couche ne lit pas la DB, ne recalcule pas les dignites et ne genere pas de texte interpretatif.

## Conditions avancees et mitigation par secte

`AdvancedConditionEngine` produit les conditions avancees depuis les positions, dignites, aspects et runtime:

- reception mutuelle;
- hayz;
- out of sect;
- vitesse stationnaire, rapide ou lente;
- phases et orientations heliacales;
- besiegement, bonification et maltreatment;
- mitigation benefique/malefique par la secte depuis CS-206.

CS-206 ajoute `SectNatureMitigationCondition`. Le detecteur lit la nature planetaire depuis `AstrologyRuntimeReference.planet_natures` et combine cette nature avec la condition de secte:

- malefique en secte: condition mitigee;
- malefique hors secte: condition aggravee;
- benefique en secte: supportee;
- benefique hors secte: affaiblie;
- nature neutre, mixte, luminaire ou inconnue: neutre ou non evaluable selon le contrat.

Le poids runtime parent a ete garde neutre pour eviter un effet de score partage non desire. En mode sans heure, les faits CS-206 sont filtres de la projection publique quand ils ne sont pas fiables.

## Profils et signaux conditionnels

### Profils conditionnels

`PlanetConditionProfileService` derive des axes factuels par planete:

- `functional_strength`;
- `visibility`;
- `stability`;
- `intensity`;
- `coherence`;
- `support`;
- `constraint`;
- `ranking_score`;
- `condition_level`.

Depuis CS-199 et CS-206, ces profils peuvent etre enrichis par les conditions avancees, dont hayz et mitigation benefique/malefique. Les contributions avancees restent tracees comme faits de breakdown, pas comme narration.

### Signaux conditionnels

CS-193 ajoute et stabilise `PlanetConditionSignalBuilder`. Il lit les plages inclusives du runtime `condition_signal_profiles` et produit des signaux sous forme de faits techniques:

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

Le champ `prompt_hint` est un champ contractuel runtime-backed. Il ne signifie pas que le domaine appelle un LLM ou construit une narration.

Les signaux publics sont exposes sous `planet_condition_signals`.

## Dominantes planetaires

CS-194 ajoute `PlanetDominanceEngine`. Le moteur classe les planetes depuis les faits deja calcules:

- maitre de l'Ascendant;
- angularite;
- force conditionnelle et visibilite;
- planete la plus elevee;
- emphase des luminaires;
- charge de maitrise des maisons;
- centralite dans les aspects;
- poids des conditions avancees.

Les facteurs, profils et poids viennent de `AstrologyRuntimeReference.dominance_reference`. La projection publique expose `dominant_planets`, avec neutralisation en mode sans heure fiable.

## Adaptation interpretative non narrative

CS-196 introduit `InterpretationAdapterEngine`. Cette couche ne redige pas d'interpretation utilisateur. Elle transforme les faits objectifs en objets semantiques normalises:

- `signals`;
- `activated_themes`;
- `dominant_topics`;
- `dominant_axes`;
- `tension_patterns`;
- `support_patterns`;
- `critical_patterns`;
- `narrative_priorities`.

Elle consomme profils, signaux, conditions avancees, dominances, dignites, aspects et positions. Elle reste gouvernee par `interpretation_adapter_reference`. En mode sans heure fiable, la projection publique peut la neutraliser a `null`.

## Projection JSON publique

CS-201 stabilise `json_builder.py` comme couche de projection serialize-only. Il ne doit pas:

- instancier les calculateurs;
- recalculer la secte;
- deduire des conditions traditionnelles;
- comparer des seuils;
- backfiller des payloads anciens en stockage;
- creer des alias publics legacy.

La projection publique expose maintenant les blocs principaux:

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

Les payloads anciens restent lus sans backfill en stockage. Les champs non calculables ou non fiables sans heure sont neutralises dans la projection publique.

## Persistance

### Snapshot principal

`chart_results.result_payload` reste le snapshot complet du theme calcule. Il contient le resultat effectif du calcul et sert de source a la restitution du dernier theme.

### Audit des dignites

CS-203 active la persistance d'audit des dignites dans `astral_chart_planet_dignity_results`.

Le flux est volontairement limite:

- `ChartResultService.persist_trace` persiste d'abord le snapshot principal;
- si des dignites sont presentes, un mapper transforme les `PlanetDignityResult` deja calcules en DTO d'audit;
- le repository fait un upsert idempotent;
- les echecs d'ecriture audit sont classes comme `ChartResultServiceError`;
- aucun calculateur de dignites, conditions, dominance ou adapter n'est importe dans la couche de persistance d'audit.

Cette table ne remplace pas `chart_results.result_payload`. Elle sert a l'audit detaille, aux analyses et a la tracabilite par planete.

## Frontend

CS-202 ajoute `NatalExpertPanel`, un panneau expert display-only. Il consomme le JSON public deja charge par la page du theme natal.

Le panneau peut afficher notamment:

- secte du theme;
- condition de secte par planete;
- conditions avancees comme hayz/out-of-sect;
- contrats traditionnels;
- scores de dignites;
- profils conditionnels;
- dominantes planetaires;
- adapter interpretatif factuel.

Le frontend ne contient pas de constantes doctrinales, ne derive pas les conditions astrologiques et n'appelle pas un endpoint dedie pour recalculer ces faits. Il gere les payloads legacy, les blocs vides, le mode sans heure fiable, les erreurs API, le chargement et l'absence de theme.

## Construction finale de `NatalResult`

Le `NatalResult` consolide aujourd'hui:

- metadonnees: versions, moteur, zodiaque, frame, systeme de maisons, ayanamsa, altitude, traces ephemerides;
- entree preparee: temps local, UTC, jour julien, traces TT si activees;
- faits astronomiques: positions planetaires, maisons, angles, points astraux;
- relations: aspects;
- runtime structurel: signes runtime, maitres de maisons, balance et signature;
- dignites: score profile, tradition, reference version, secte, resultats par planete;
- conditions traditionnelles: hayz, rejoicing, secte et faits associes par planete;
- profils conditionnels;
- signaux conditionnels;
- conditions avancees;
- dominantes planetaires;
- adaptation interpretative non narrative.

## Tables et seeds concernes

Le calcul natal objectif consomme ou produit notamment:

- tables de runtime structurel: signes, maisons, planetes, roles, aspects, points, axes;
- tables de dignites: types essentiels/accidentels, regles, poids, termes, decans, triplicites, secte;
- tables de conditions: `astral_advanced_condition_types`, `astral_advanced_condition_score_profiles`, `astral_advanced_condition_weights`;
- tables de signaux conditionnels: `astral_planet_condition_signal_profiles`;
- tables de dominance: `astral_dominance_factor_types`, `astral_dominance_score_profiles`, `astral_dominance_score_weights`;
- tables d'adaptation: `astral_interpretation_signal_types`, `astral_interpretation_themes`, `astral_interpretation_adapter_rules`;
- lookups associes: natures planetaires, positions d'horizon, conditions heliacales, relations de vitesse, operateurs;
- persistance principale: `chart_results`;
- persistance d'audit dignites: `astral_chart_planet_dignity_results`.

CS-206 modifie le runtime de conditions avancees et les poids associes pour declarer la mitigation benefique/malefique par secte. Les resultats restent calcules a la volee puis serialises; les tables runtime ne stockent pas le resultat final d'un theme.

## Garde-fous maintenus

Les garde-fous actuels sont:

- les domaines purs `dignities`, `condition`, `advanced_conditions`, `dominance` et `interpretation_adapters` ne doivent pas importer infra DB, API, services applicatifs, prediction ou LLM;
- les constantes doctrinales locales sont interdites;
- les couches aval ne recalculent pas la secte ou la condition de secte;
- `json_builder.py` projette uniquement des faits deja presents;
- la persistance d'audit consomme des resultats precomputes;
- le frontend affiche les faits publics sans doctrine locale;
- les modes sans heure fiable neutralisent les blocs dependants des maisons, angles ou conditions horaires;
- les snapshots et golden cases verrouillent les contrats publics et les comportements traditionnels.

## Validation recente

Les evidences CS-207 consolident la chaine CS-197 a CS-206:

- suite backend ciblee: 100 tests passes;
- tests frontend `NatalExpertPanel`: 4 tests passes;
- `ruff format .` et `ruff check .`: OK;
- lint frontend et build frontend: OK;
- scans de constantes doctrinales, fuites de calculateurs, derivation frontend et legacy: OK apres classification;
- status final JSON CS-207 valide;
- aucun fichier de production, migration, seed, route, dependance ou contrat public modifie par CS-207.

Les stories precedentes ont aussi valide:

- CS-193: signaux conditionnels runtime-backed;
- CS-194: moteur de dominantes planetaires;
- CS-195: conditions planetaires avancees;
- CS-196: adaptation interpretative;
- CS-197: contrat explicite de secte;
- CS-198: condition de secte par planete;
- CS-199: integration de la secte dans hayz et scoring avance;
- CS-200: golden cases traditionnels;
- CS-201: projection publique serialize-only;
- CS-202: panneau expert frontend display-only;
- CS-203: persistance d'audit des dignites;
- CS-204: hayz/rejoicing et `traditional_conditions`;
- CS-205: triplicite dependante de la secte;
- CS-206: mitigation benefique/malefique par secte;
- CS-207: audit final de la chaine traditionnelle avancee.

## Limites actuelles

1. Le panneau expert frontend affiche les faits, mais l'experience produit peut encore decider comment vulgariser ces blocs pour un utilisateur non expert.
2. `interpretation_adapter` reste une preparation semantique, pas une interpretation editoriale finale.
3. La precision astronomique reste dependante de SwissEph, des fichiers d'ephemerides, de la configuration runtime et du bootstrap de reference.
4. Les etoiles fixes restent hors `NatalResult`; elles sont branchees dans le runtime et le scoring de prediction quotidienne, pas dans le calcul natal public.
5. `astral_chart_planet_dignity_results` audite les dignites, mais ne remplace pas l'historique complet du payload natal.
6. Le frontend maintient encore des types API manuels pour cette surface; toute evolution de payload doit rester synchronisee avec les tests.
7. Certains blocs restent neutralises sans heure fiable, ce qui est voulu mais doit rester clair dans l'UX.

## Conclusion

Au 2026-05-21, l'engine du theme astral est une chaine backend fortement structuree: calcul astronomique SwissEph, runtime astrologique DB-backed, enrichissements structurels, dignites, secte, conditions traditionnelles, conditions avancees, profils, signaux, dominances, adapter semantique, projection publique et persistance d'audit.

Les stories CS-193 a CS-207 ont surtout ferme les risques de duplication et de doctrine locale: chaque fait a un proprietaire canonique, les couches aval consomment des contrats explicites, la projection ne calcule pas, la persistance audite des resultats precomputes et le frontend reste display-only.

Le prochain travail utile n'est pas de refondre le moteur. Les priorites probables sont l'ergonomie frontend autour de ces faits, la documentation produit des modes sans heure fiable, et l'ajout continu de cas golden externes pour verrouiller la precision astronomique et traditionnelle.
