# Audit du calcul du theme astral apres CS-217 a CS-236

Date: 2026-05-23
Perimetre: moteur backend du theme natal, runtime `chart_objects`, graphe de calcul, aspects, dignites, dominance, conditions, etoiles fixes, signatures et input interpretatif.
Document source: `docs/recherches astro/2026-05-22-synthese-calculs-astrologiques-post-cs-216.md`.
Stories consolidees: CS-217 a CS-236.

## Synthese executive

Au 2026-05-23, le moteur de calcul du theme astral a change de nature. La chaine post-CS-216 ne se contente plus d'ajouter des conditions planetaires internes: elle a installe un runtime canonique autour de `ChartObjectRuntimeData`, puis a migre l'orchestration natale vers un graphe declaratif `natal_chart_v1`.

Le frontend reste consommateur de projections publiques. Il ne calcule toujours pas les positions, maisons, aspects, dignites, dominantes, signatures, conditions ou etoiles fixes. Le calcul reste concentre cote backend.

Le coeur actuel est compose de quatre surfaces:

- `build_natal_result`, facade publique mince qui prepare le contexte puis execute le graph runner;
- `natal_chart_v1`, definition declarative des dependances de calcul;
- `chart_objects`, runtime interne canonique pour les nouveaux calculateurs;
- `NatalResult`, contrat compatible qui conserve les sorties publiques historiques et garde certaines surfaces internes exclues du JSON/OpenAPI.

La trajectoire d'architecture est globalement saine: les nouveaux calculateurs selectionnent par capacites (`supports_aspects`, `supports_dignities`, `supports_fixed_star_conjunction`, etc.) et lisent des payloads types, au lieu de rebrancher la logique metier sur des listes historiques de planetes, points ou maisons.

## Etat global du flux natal

Le flux nominal actuellement code est le suivant:

1. `build_natal_result` normalise les options, prepare `BirthPreparedData`, construit un `CalculationGraphContext`, puis appelle `CalculationGraphRunner`.
2. Le graphe `natal_chart_v1` execute des nodes nommes: maisons brutes, positions planetaires, points astraux, rulerships, maisons runtime, conditions motion/visibility, chart objects, etoiles fixes, aspects, dignites, conditions avancees, signature, dominance, input interpretatif et projections.
3. `NatalResultAssembler` reconstruit un `NatalResult` compatible depuis les outputs du graphe.
4. Les champs publics historiques restent presents: `planet_positions`, `houses`, `signs_runtime`, `house_rulers`, `astral_points`, `dignities`, `condition_profiles`, `condition_signals`, `advanced_conditions`, `traditional_conditions`, `dominant_planets`, `interpretation_adapter`, `aspects`.
5. Les surfaces internes restent exclues du JSON public: `advanced_planetary_conditions`, `chart_objects`, `interpretation_profiles_by_planet`, ainsi que les hints/runtime internes d'aspects portes par les champs `exclude=True`.

Le code cle est reparti entre:

- `backend/app/domain/astrology/natal_calculation.py`;
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`;
- `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`;
- `backend/app/domain/astrology/runtime/natal_calculation_registry.py`;
- `backend/app/domain/astrology/runtime/natal_result_assembler.py`;
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`.

## Graphe de calcul natal

CS-225 a CS-228 ont rendu explicite l'ordre de calcul qui etait auparavant implicite dans la facade natale.

Le graphe est declare par `build_natal_calculation_graph_definition()` avec le code `natal_chart_v1` et la version `1`. Les nodes sont etiquetes selon leur role:

- `canonical_runtime` pour les faits internes;
- `compatibility_projection` pour les projections terminales;
- `public_projection` pour `public_natal_result`.

Les dependances importantes sont:

- `planet_positions` depend de `houses_raw`, car les maisons sont assignees et validees sur les positions;
- `chart_objects` depend des positions, points, maisons runtime, rulerships, payloads motion/visibility et referentiel;
- `aspects_runtime` depend des `chart_objects` enrichis par les contacts d'etoiles fixes;
- `dignities` depend de `chart_objects`, des contacts fixed-star et du referentiel;
- `advanced_conditions` depend des positions, aspects et dignites;
- `dominance` depend des chart objects, maisons, rulerships, conditions, aspects, dignites et referentiel;
- `interpretation_input` depend de `chart_objects`, `aspects_runtime`, `dominance` et `advanced_conditions`;
- `public_natal_result` assemble les projections et les sorties chart-level.

Le runner valide le graphe, execute en ordre topologique, isole le contexte par `MappingProxyType`, conserve la provenance minimale des outputs, et remonte les erreurs de node avec `node_code`, `key` et `cause`.

Limite constatee: le cache du runner est local a un appel. Il evite de recalculer un output deja injecte dans le contexte, mais il ne constitue pas un cache applicatif persistant ou partage.

## Runtime canonique `chart_objects`

CS-217 a CS-224 ont fait de `NatalResult.chart_objects` la source canonique interne pour les nouveaux calculateurs.

Un `ChartObjectRuntimeData` porte:

- un `code`;
- un `object_type` canonique;
- une longitude optionnelle;
- une position zodiacale optionnelle;
- une source typee;
- des `ChartObjectCapabilities`;
- des classifications;
- des `ChartObjectPayloads`.

Les payloads actuellement stabilises couvrent:

- mouvement;
- visibilite;
- dignite;
- dominance;
- conditions planetaires;
- etoile fixe;
- conjonctions aux etoiles fixes;
- position en maison;
- rulership;
- cuspide de maison;
- angle.

Le point architectural important est que les calculateurs ne doivent plus decider l'eligibilite par `object_type`. Ils doivent selectionner par capacites et lire les payloads attendus. Les tests d'architecture `test_chart_runtime_surface_guardrails.py` et `test_astrology_runtime_boundary.py` verifient cette discipline.

## Positions, maisons et points astraux

Les positions planetaires restent produites par deux moteurs possibles:

- moteur simplifie historique via `calculate_planet_positions`;
- moteur `swisseph` via `ephemeris_provider.calculate_planets`.

Les maisons suivent la meme logique:

- moteur simplifie via `calculate_houses`;
- moteur `swisseph` via `houses_provider.calculate_houses`.

Les invariants restent explicites:

- les cuspides doivent etre au nombre de 12;
- les longitudes de cuspides doivent etre finies, normalisees et uniques;
- le signe d'une planete doit correspondre a sa longitude;
- la maison assignee doit contenir la longitude selon l'intervalle de cuspides.

Les points astraux sont resolus par `AstralPointCalculationResolver`. Les points derives attendent la disponibilite de leur source, puis appliquent actuellement une longitude opposee via `opposite_longitude`. Les points calcules directement deleguent au moteur actif quand `swisseph` est utilise.

Limite: le moteur simplifie reste deterministe mais non astronomique. Les garanties d'audit-grade dependent du choix effectif `engine="swisseph"` et de la configuration ephemeride.

## Conditions planetaires avancees

Le sous-systeme `planetary_conditions` de CS-208 a CS-216 reste actif et est maintenant raccorde aux `chart_objects`.

Le node `motion_visibility_payloads` appelle `calculate_advanced_planetary_conditions` depuis les positions et vitesses deja calculees. Il produit:

- proximite solaire;
- relation solaire oriental/occidental;
- mouvement apparent;
- visibilite simplifiee;
- phase lunaire;
- signaux techniques par planete;
- signaux globaux de phase lunaire.

Ces faits alimentent:

- `ChartObjectMotionPayload`;
- `ChartObjectVisibilityPayload`;
- `PlanetDignityScoringService`;
- `interpretation_profiles_by_planet`.

Ils restent exclus du JSON public via `NatalResult.advanced_planetary_conditions`.

Limite maintenue: la visibilite est une composition astrologique simplifiee a partir de la proximite solaire et de la relation solaire. Ce n'est pas un calcul astronomique complet de levers/couchers heliacaux selon latitude, magnitude, atmosphere ou horizon.

## Maisons, rulerships et payloads associes

CS-221 a rattache les positions en maison et maitrises aux chart objects.

Le flux actuel:

- `HouseRulerResolver` resout les gouvernances depuis les cuspides, les positions planetaires, les signes et les rulerships de reference;
- `build_house_runtime_data` construit les maisons runtime;
- `RulershipPayloadEnricher` ajoute les payloads de rulership aux objets eligibles;
- `build_house_position_payload` rattache la modalite de maison et les cuspides pertinentes.

Les validations `validate_rulership_payloads` et les validations de dataclasses refusent les incoherences: maison hors `[1, 12]`, ascendant ruler sans maison 1, midheaven ruler sans maison 10, payload rattache sans capacite correspondante.

## Aspects

CS-218 et CS-229 a CS-233 ont separe deux responsabilites:

- le runtime structurel d'aspects: geometrie, participants, orbe, force technique, metadata, modifiers;
- les hints interpretatifs d'aspects: valence, type d'energie, axes semantiques, poids interpretatif optionnel.

Le node `aspects_runtime` selectionne les objets aspectables depuis `chart_objects` via `AspectChartObjectSelector`, les projette via `AspectBodyProjector`, puis appelle `calculate_major_aspects`.

Les definitions structurelles viennent de `runtime_reference.aspects.structural_definitions`. Les profils interpretatifs viennent de `runtime_reference.aspects.interpretive_profiles`.

Les garde-fous importants sont:

- les anciennes surfaces hybrides d'aspects sont retirees des owners actifs;
- les champs `default_valence`, `interpretive_valence`, `energy_type`, `interpretive_weight` restent seulement dans les chemins allowlistes de hints/profils;
- l'absence de profil interpretatif pour un aspect majeur actif est une erreur de reference;
- le JSON public peut conserver des champs de valence, mais ils doivent venir des hints et non du calculateur structurel.

Limite: `AspectResult` reste un objet de compatibilite avec `aspect_runtime` et `aspect_interpretive_hints` exclus du JSON. Il sert de pont public/interne; il ne doit pas redevenir la source metier primaire.

## Etoiles fixes

CS-222 a integre les etoiles fixes dans le runtime unifie.

Le builder produit des etoiles fixes comme `ChartObjectRuntimeData` avec `payloads.fixed_star`. Les contacts sont calcules par `FixedStarConjunctionCalculator` depuis:

- les etoiles selectionnees via `payloads.fixed_star`;
- les cibles selectionnees via `capabilities.supports_fixed_star_conjunction`.

Les contacts sont des `FixedStarConjunctionRuntimePayload` avec:

- code et nom de l'etoile;
- code et nom de la cible;
- longitudes;
- orbe;
- orbe maximum;
- code de regle;
- source.

Les conjonctions sont ensuite rattachees aux cibles par `FixedStarConjunctionEnricher`.

Limites:

- seules les conjonctions sont couvertes;
- pas de parans, oppositions, aspects aux etoiles fixes ou levers heliacaux;
- les longitudes du catalogue sont consommees telles qu'exposees par le referentiel runtime.

## Dignites et dominance

CS-220 a migre les surfaces de dignites et de dominance vers des payloads rattaches aux chart objects, sans supprimer les sorties chart-level historiques.

Le node `dignities`:

- selectionne les objets eligibles via `DignityChartObjectSelector`;
- projette les entrees via `DignityInputProjector`;
- appelle `PlanetDignityScoringService`;
- enrichit les chart objects par `DignityPayloadEnricher`;
- calcule les profils de condition;
- produit `interpretation_profiles_by_planet` depuis les conditions planetaires avancees.

Le node `dominance`:

- selectionne les objets eligibles via `DominanceChartObjectSelector`;
- projette via `DominanceInputProjector`;
- appelle `PlanetDominanceEngine`;
- enrichit les chart objects par `DominancePayloadEnricher`;
- conserve `DominantPlanetsResult` comme resultat chart-level public.

Les scores ne sont pas recalcules par les enrichers. Les payloads sont des projections calculatoires des resultats deja produits.

## Conditions avancees traditionnelles et interpretation interne

Le node `advanced_conditions` conserve la chaine traditionnelle avancee existante via `AdvancedConditionEngine`. Il consomme:

- positions planetaires;
- aspects runtime;
- dignites;
- profils de condition.

Il produit:

- `advanced_conditions`;
- `condition_profiles` enrichis;
- `condition_signals`.

Le node `interpretation_input` construit ensuite un input interne via `ChartInterpretationInputBuilder`, puis calcule:

- `interpretation_adapter`;
- `traditional_conditions`.

`ChartInterpretationInputBuilder` consomme les chart objects selectionnes et projetes via `ChartObjectInterpretationSelector` et `ChartObjectInterpretationProjector`. Il ne doit pas recalculer les faits structurels.

Limite constatee: l'input interpretatif reste interne. Il structure le materiau d'interpretation, mais ne constitue pas une narration utilisateur finale.

## Signes runtime et signatures

CS-234 a CS-236 ont enrichi les profils structurels de signes.

`SignRuntimeData` porte maintenant:

- element;
- modality;
- polarity;
- seasonal_quadrant;
- fertility;
- voice;
- form;
- occupants;
- dignites actives;
- poids;
- raisons de dominance;
- role de synthese.

`build_sign_runtime_data` lit ces valeurs depuis le referentiel runtime DB-backed. Il ne recree pas des tables locales de correspondance signe -> profil.

`ChartSignatureCalculator` agrege ensuite les profils par poids de signe:

- `elements`;
- `modalities`;
- `polarities`;
- `seasonal_quadrants`;
- `fertility`;
- `voices`;
- `forms`;
- `dominant_signs`;
- `dominant_planets`;
- `dominant_houses`;
- `dominant_aspects`.

Le tie-break des balances est stable: score decroissant puis code croissant.

`ChartSignatureRuntimeData` expose les primaires:

- `primary_element`;
- `primary_modality`;
- `primary_polarity`;
- `primary_seasonal_quadrant`;
- `primary_fertility`;
- `primary_voice`;
- `primary_form`;
- `primary_sign`;
- `primary_planet`;
- `primary_house`.

Ces profils sont projetes:

- dans `chart_balance`;
- dans `chart_signature`;
- dans `ChartInterpretationInputRuntimeData.sign_profile_balances`.

Les garde-fous interdisent les mappings locaux du type `FERTILITY_BY_SIGN`, `VOICE_BY_SIGN`, `FORM_BY_SIGN`, `SEASONAL_QUADRANT_BY_SIGN`, `POLARITY_BY_SIGN` dans les serializers et couches interpretatives.

## Projection publique et frontend

Le contrat public reste compatible.

Les serializers, notamment `backend/app/services/chart/json_builder.py`, projettent:

- les positions planetaires;
- les maisons;
- les signes runtime;
- les aspects;
- les dignites;
- les conditions;
- la dominance;
- l'adapter interpretatif;
- `chart_balance`;
- `chart_signature`.

Ils ne doivent pas devenir des calculateurs. Pour CS-236, le serializer lit les balances deja calculees au lieu de refaire les aggregats par signe.

Le frontend React reste display-only pour le theme natal. Aucune trace lue dans ce perimetre ne montre un calcul frontend des positions, aspects, maisons, dignites ou signatures.

## Garde-fous constates

Les garde-fous actifs couvrent:

- exclusion JSON/OpenAPI de `chart_objects` et `advanced_planetary_conditions`;
- absence de consommation metier des surfaces legacy depuis `NatalResult` hors allowlist;
- interdiction des branches metier par `object_type` dans les nouveaux calculateurs;
- separation structural runtime / interpretive runtime;
- interdiction des tokens narratifs ou LLM dans les couches structurelles hors exceptions nommees;
- interdiction de recalcul structurel dans les adapters interpretatifs;
- interdiction de seuils locaux magiques pour certains seuils sensibles;
- interdiction des tables locales de profils de signes dans les serializers/adapters.

Documents et tests de reference:

- `docs/architecture/astrology-runtime-surfaces.md`;
- `backend/tests/architecture/test_chart_runtime_surface_guardrails.py`;
- `backend/tests/architecture/test_astrology_runtime_boundary.py`;
- `backend/tests/architecture/test_aspect_runtime_boundary.py`;
- `backend/tests/architecture/test_structural_runtime_boundary.py`;
- `backend/app/tests/unit/test_astrology_runtime_reference_guard.py`.

## Risques et limites

1. Le moteur simplifie existe toujours. Pour un calcul astronomique robuste, l'usage effectif de `swisseph` et des ephemerides versionnees reste determinant.
2. Le graph runner n'est pas un moteur de cache applicatif. Sa provenance est utile pour debug/audit, mais pas persistante.
3. `chart_objects` est canonique en interne mais exclu du contrat public. Tout besoin frontend de cette surface doit passer par une story API dediee.
4. Les etoiles fixes ne couvrent que les conjonctions zodiacales simples.
5. La visibilite planetaire reste simplifiee.
6. L'input interpretatif structure les faits, mais ne garantit pas encore une interpretation editoriale finale.
7. Certaines sorties historiques restent necessaires comme projections publiques. Leur presence peut entretenir de la confusion si de nouveaux calculateurs les relisent directement; les garde-fous actuels reduisent ce risque.
8. Les seuils et poids de plusieurs sous-systemes restent des profils statiques Python ou des references DB selon les cas. La gouvernance des sources doit rester explicite.

## Evaluation

Points solides:

- orchestration natale rendue explicite par graphe;
- runtime interne unifie;
- separation calcule / interpretation mieux prouvee par les types;
- projections publiques preservees;
- tests d'architecture nombreux et ciblant les regressions critiques;
- signatures de signes enrichies raccordees a l'input interpretatif.

Points a surveiller:

- ne pas exposer `chart_objects` implicitement via JSON;
- ne pas refaire des selections par code nominal ou `object_type`;
- ne pas remettre de valence interpretative dans le runtime structurel d'aspects;
- ne pas dupliquer les profils de signes hors referentiel;
- documenter tout changement de doctrine astrologique separement des migrations techniques.

## Conclusion

Au 2026-05-23, le moteur du theme astral est dans un etat plus maintenable qu'au post-CS-216. La couche post-CS-217 a installe une architecture de calcul en trois niveaux:

1. faits structurels calcules par nodes et calculateurs purs ou quasi purs;
2. runtime canonique interne `chart_objects` avec capacites et payloads types;
3. projections publiques et interpretatives construites depuis ces faits.

La bascule la plus importante est la migration de l'orchestration vers `natal_chart_v1`. Elle donne une base extensible pour de futurs graphes astrologiques sans empiler une nouvelle sequence procedurale dans `build_natal_result`.

Le prochain travail utile n'est pas de changer le calcul actuel, mais de decider quelles surfaces internes meritent une exposition produit: `chart_objects`, conditions planetaires avancees, contacts fixed-star, profils de signes enrichis ou input interpretatif. Tant que cette decision n'est pas prise explicitement, la contrainte saine est de garder ces surfaces internes, typees, testees, et de continuer a faire du JSON public une projection stable plutot qu'une source metier.
