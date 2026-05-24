<!-- Commentaire global: ce rapport decrit le process astrologique backend actuel apres la transition runtime canonique CS-237 a CS-254. -->

# Rapport sur le process astrologique backend apres CS-254

Date: 2026-05-24

Perimetre: backend astrologique, calcul natal, runtime canonique, familles de graphes, projections publiques, trace, preuve astronomique, gouvernance doctrinale, preparation narrative IA.

Sources principales:

- `docs/recherches astro/2026-05-23-audit-calcul-theme-astral-post-cs-236.md`
- `docs/architecture/product-architecture-current-state-2026-05-24.md`
- `_condamad/reports/astro-canonical-runtime-transition-CS237-CS254-delivery-report.md`

## Synthese executive

Le process astrologique backend repose maintenant sur une chaine explicite:

`donnees de naissance -> preparation -> graphe de calcul -> runtime canonique -> faits/signaux -> projections publiques ou inputs narratifs`.

Le changement majeur post-CS-236 n'est pas l'ajout d'un calcul astrologique isole. C'est la stabilisation d'une architecture produit autour de primitives internes gouvernees:

- `natal_chart_v1` reste le seul graphe executable livre.
- `ChartObjectRuntimeData` reste la surface canonique interne pour les objets astrologiques.
- `CalculationGraph` devient la primitive d'orchestration.
- Les manifestes, traces, preuves astronomiques, taxonomies et gouvernances doctrinales encadrent l'extension du moteur.
- Les sorties publiques doivent passer par des projections explicites, jamais par l'exposition brute du runtime.
- `transit_chart_v1` est choisi comme premier chemin temporel, mais il n'est pas expose publiquement.
- Le contrat `llm_input` structure les faits et signaux pour la narration IA sans faire de l'IA une source de verite astrologique.

La regle produit centrale est donc: le backend calcule des faits, derive des signaux, puis expose seulement des projections controlees.

## Vue d'ensemble du process backend

Le flux nominal du theme natal est le suivant:

1. Les entrees utilisateur sont preparees par les services de preparation natale: date, heure, fuseau, lieu, coordonnees, options de maisons et de zodiaque.
2. La facade `build_natal_result` construit le contexte de calcul.
3. Le runner execute le graphe `natal_chart_v1` en respectant les dependances declarees.
4. Les nodes produisent les positions, maisons, points, objets runtime, aspects, dignites, conditions, dominance, signatures et inputs interpretatifs.
5. `NatalResultAssembler` reconstruit un `NatalResult` compatible avec les contrats existants.
6. Les services API et serializers exposent seulement des sorties publiques historiques ou des projections nommees.
7. Les contrats IA consomment des faits/signaux versionnes, avec politique de masquage et liens vers projections publiques.

Les fichiers centraux observes sont:

- `backend/app/domain/astrology/natal_calculation.py`
- `backend/app/domain/astrology/runtime/natal_calculation_graph.py`
- `backend/app/domain/astrology/runtime/natal_calculation_nodes.py`
- `backend/app/domain/astrology/runtime/calculation_graph_runner.py`
- `backend/app/domain/astrology/runtime/natal_result_assembler.py`
- `backend/app/domain/astrology/runtime/chart_object_runtime_data.py`
- `backend/app/domain/astrology/runtime/astrology_graph_family_registry.py`
- `backend/app/domain/astrology/runtime/calculation_graph_manifest.py`
- `backend/app/domain/astrology/runtime/calculation_graph_execution_trace.py`
- `backend/app/domain/astrology/runtime/temporal_technique_selection.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_contracts.py`

## Process natal canonique

`natal_chart_v1` est le process backend actuellement executable. Il organise le calcul en nodes plutot qu'en sequence procedurale implicite.

Les grandes etapes sont:

| Etape | Role | Nature de sortie |
| --- | --- | --- |
| Preparation natale | Normaliser les donnees de naissance et options de calcul. | Contexte d'entree backend |
| Maisons brutes | Calculer ou recuperer les cuspides selon le moteur actif. | Faits astronomiques/astrologiques |
| Positions planetaires | Calculer les longitudes, signes, vitesses et maisons. | Positions structurelles |
| Points astraux | Resoudre les points directs ou derives. | Objets calculables supplementaires |
| Maisons runtime | Construire la representation runtime des maisons. | Runtime interne |
| Conditions motion/visibility | Deriver mouvement, proximite solaire, phase lunaire, visibilite simplifiee. | Payloads techniques |
| Chart objects | Unifier planetes, points, maisons, angles et etoiles fixes dans le runtime canonique. | `ChartObjectRuntimeData` |
| Etoiles fixes | Calculer les conjonctions aux cibles eligibles. | Contacts internes |
| Aspects | Calculer la geometrie structurelle et rattacher les hints interpretatifs. | Runtime + projection compatible |
| Dignites | Evaluer dignites essentielles/accidentelles et profils de condition. | Scores et payloads |
| Conditions avancees | Produire conditions traditionnelles et signaux techniques. | Signaux interpretatifs |
| Dominance | Calculer dominantes planetaires, maisons et signatures. | Resultats chart-level |
| Interpretation input | Assembler les faits et signaux pour l'interpretation. | Input interne |
| Projection publique | Construire le `NatalResult` et JSON public compatibles. | Contrat public controle |

Cette structure rend le process auditable: chaque node a des entrees, sorties et dependances identifiables.

## Runtime canonique interne

Le runtime canonique est centre sur `ChartObjectRuntimeData`.

Un objet runtime porte:

- un code canonique;
- un type d'objet;
- des capacites;
- des classifications;
- des payloads types;
- une source de provenance;
- des donnees positionnelles quand elles existent.

La discipline post-CS-236 est renforcee par CS-249: les nouveaux calculateurs ne doivent pas selectionner les objets par nom historique ou par branche `object_type` opportuniste. Ils doivent s'appuyer sur la taxonomie de capacites et lire les payloads appropries.

Exemples de capacites et payloads structurants:

- aspectabilite;
- eligibilite dignites;
- eligibilite dominance;
- contact aux etoiles fixes;
- mouvement;
- visibilite;
- position en maison;
- rulership;
- cuspide;
- angle;
- payload fixed-star.

Cette couche est volontairement interne. Elle donne une base robuste au backend, mais elle n'est pas une API publique.

## Registre des familles astrologiques

CS-246 a ajoute un registre canonique des familles de graphes. Son role est d'empecher les familles non natales d'apparaitre sous forme de raccourcis non gouvernes.

Etat observe:

| Famille | Statut produit/backend |
| --- | --- |
| `natal_chart_v1` | Active et executable |
| `transit_chart_v1` | Selectionnee comme premier chemin temporel, bloquee pour exposition publique |
| `synastry_chart_v1` | Bloquee par decision multi-chart |
| `solar_return_v1` | Bloquee par preuve astronomique et politique cache |
| `lunar_return_v1` | Bloquee par preuve astronomique et politique cache |
| `progressed_chart_v1` | Bloquee par preuve astronomique et gouvernance methode |
| `composite_chart_v1` | Bloquee par decision multi-chart |
| `profection_v1` | Bloquee par preuve astronomique et doctrine |
| `forecasting_v1` | Bloquee par decision produit |
| `ai_scoring_v1` | Bloquee par decision de trace/scoring |
| `narrative_generation_v1` | Bloquee par frontiere produit narration |

Le registre dit explicitement ce qui existe, ce qui est actif, ce qui est ferme, et pourquoi. C'est un garde-fou contre l'extension implicite du moteur astrologique.

## Manifestes, schemas IO et compatibilite

CS-247 a introduit un manifeste de graphe derive depuis la definition executable.

Le manifeste porte:

- `graph_code`;
- `graph_version`;
- `family_code`;
- entrees globales requises;
- liste des nodes;
- schema d'entree et de sortie par node;
- dependances obligatoires et optionnelles;
- politique de compatibilite.

Le point important est que le manifeste est derive du graphe, pas recopie a la main. Il sert a comparer les evolutions et a classer les deltas comme compatibles ou breaking.

Pour le process astrologique, cela signifie qu'un changement de node, d'entree requise, de sortie ou de version devient une decision visible, testable et documentable.

## Trace d'execution

CS-248 a ajoute un contrat de trace interne. Cette trace ne contient pas les valeurs brutes d'entree ou de sortie.

Elle expose seulement:

- version de trace;
- code et version du graphe;
- `run_id` optionnel;
- nodes executes;
- statut du node;
- statut cache hit/miss;
- duree;
- cles d'entree;
- cles de sortie;
- erreur normalisee eventuelle;
- references de provenance;
- politique de redaction.

La distinction est essentielle:

- trace: faits d'execution rediges;
- provenance: references de source;
- replay: non implemente;
- cache durable: non autorise tant que les cles d'invalidation ne sont pas decidees.

Le cache du runner reste local a l'execution. Il ne remplace pas un cache applicatif.

## Preuve astronomique et moteurs de calcul

Le backend garde deux postures de calcul:

- moteur simplifie historique, deterministe mais non astronomique;
- moteur `swisseph` quand la configuration et les ephemerides le permettent.

CS-250 a durci la posture avant toute exposition temporelle publique. La preuve astronomique devient un gate pour les futurs usages publics des transits ou autres familles temporelles.

Les points surveilles sont:

- mode ephemeride;
- hash/version de chemin ephemeride quand disponible;
- cas golden sensibles;
- tolerances;
- preuve reproductible;
- absence de route publique temporelle avant validation.

Limite actuelle: l'usage de donnees Moshier integrees par `pyswisseph` est note comme risque restant lorsque le deploiement d'ephemerides externes versionnees n'est pas etabli.

## Conditions, aspects, dignites et dominance

Le process backend separe les calculs structurels, les enrichissements runtime et les signaux interpretatifs.

### Conditions planetaires

Les conditions motion/visibility calculent notamment:

- proximite solaire;
- relation solaire oriental/occidental;
- mouvement apparent;
- phase lunaire;
- visibilite simplifiee;
- signaux techniques par planete.

Ces donnees alimentent les payloads runtime, les dignites et l'input interpretatif. Elles restent exclues du JSON public brut.

### Aspects

Les aspects sont separes en deux couches:

- runtime structurel: geometrie, participants, orbe, force technique, metadata;
- hints interpretatifs: valence, energie, poids et axes semantiques.

Cette separation evite de melanger calcul geometrico-technique et narration.

### Dignites

Les dignites sont calculees depuis les chart objects eligibles, puis rattachees sous forme de payloads. Les enrichers ne recalculent pas les scores; ils projettent les resultats calcules.

### Dominance

La dominance suit la meme logique: selection par capacites, projection d'entrees, calcul centralise, enrichissement runtime, puis sortie chart-level compatible.

## Etoiles fixes

Les etoiles fixes sont integrees au runtime canonique, mais leur couverture reste limitee.

Actuellement:

- les etoiles sont modelisees comme objets runtime;
- seules les conjonctions zodiacales simples sont calculees;
- les cibles sont selectionnees par capacite;
- les contacts sont rattaches comme payloads aux objets cibles.

Non couvert:

- parans;
- oppositions ou autres aspects aux etoiles fixes;
- levers heliacaux;
- politique publique definitive.

La projection `fixed_star_contacts` reste en statut `needs-user-decision`.

## Projections publiques

CS-251 formalise le principe suivant: le public ne consomme pas les primitives internes, mais des projections nommees.

Surfaces autorisees ou candidates:

| Projection | Statut |
| --- | --- |
| `structured_facts` | Roadmap publique |
| `expert_technical_projection` | Roadmap publique, champ exact a decider |
| `beginner_summary` | Roadmap publique, masquage a decider |
| `fixed_star_contacts` | Bloquee par decision produit/securite |
| `astrologer_debug_data` | Bloquee par decision produit/securite |
| `llm_input` | Interne / LLM-only |

Surfaces interdites comme API publique brute:

- `ChartObjectRuntimeData`;
- `chart_objects`;
- raw graph payloads;
- traces brutes;
- `interpretation_input`;
- payloads internes de dignite, dominance ou fixed-star.

Le frontend React doit rester consommateur de contrats publics. Il ne doit pas inferer une feature depuis une surface runtime disponible.

## Frontiere calcul, interpretation et IA

La direction autorisee est:

`calcul -> faits -> signaux -> narration/projection`.

Le backend ne doit pas inverser cette direction. Un prompt, un texte narratif ou un provider IA ne peut pas devenir source de verite astrologique.

CS-254 ajoute un contrat `ai_narrative_input.v1` compose de:

- faits structurels;
- signaux interpretatifs;
- readiness flags;
- versions de sources;
- politique de masquage;
- liens vers projections publiques;
- contexte debug borne.

Ce contrat est provider-neutral. Il prepare le scoring ou la narration, mais ne definit pas une route publique ni une generation finale utilisateur.

## Gouvernance doctrinale

CS-252 formalise la gouvernance des regles astrologiques.

Le probleme traite est le risque de sources multiples:

- seuils Python;
- references DB;
- profils statiques;
- seeders;
- documents;
- interpretations historiques.

La regle cible est qu'une famille de regles doit avoir:

- un owner;
- un statut doctrinal;
- une source d'autorite;
- une politique de transition;
- des tests ou garde-fous.

Sans cette gouvernance, ajouter des objets ou techniques traditionnelles peut modifier silencieusement la doctrine du produit.

## Process API et services produit

Les routes et services publics doivent rester en aval du moteur.

Le process attendu est:

1. Calculer les faits dans le domaine astrologique.
2. Assembler un resultat compatible ou une projection officielle.
3. Serialiser avec un client public stable.
4. Interdire les noms et payloads runtime non publics dans OpenAPI.
5. Faire evoluer le frontend seulement apres contrat API explicite.

Les services tels que `backend/app/services/chart/json_builder.py`, les contrats API publics et les routers ne doivent pas recalculer les faits astrologiques. Leur responsabilite est la projection, la compatibilite et la presentation des erreurs.

## Garde-fous actifs

Les garde-fous identifies couvrent:

- exclusion JSON/OpenAPI de `chart_objects`;
- non-exposition publique de `ChartObjectRuntimeData`;
- tests d'architecture sur la frontiere runtime;
- tests d'architecture sur les surfaces publiques;
- interdiction de remettre la narration dans le calcul structurel;
- separation structural runtime / interpretive runtime;
- registre des familles astrologiques;
- manifestes de graphes;
- trace redigee;
- gate de preuve astronomique;
- taxonomie de capacites;
- gouvernance doctrinale;
- absence de route publique pour `transit_chart_v1`.

Ces garde-fous sont plus importants que les tests unitaires isoles: ils protegent la direction d'architecture.

## Risques residuels

1. Le moteur simplifie existe toujours; les garanties astronomiques dependent du mode `swisseph` et de la preuve ephemeride.
2. Le cache est local au runner; aucun cache durable n'est gouverne.
3. `transit_chart_v1` est selectionne mais non executable publiquement.
4. Les projections `expert_technical_projection` et `beginner_summary` ne sont pas encore des routes publiques livrees.
5. `fixed_star_contacts` et `astrologer_debug_data` attendent une decision produit/securite.
6. Les etoiles fixes ne couvrent que les conjonctions.
7. La gouvernance des regles doit rester stricte avant d'ajouter lots, asteroides, Chiron, midpoints, profections ou progressions.
8. Le contrat IA structure les faits, mais ne remplace pas un systeme de narration utilisateur final.
9. L'exact commit range de CS-237..CS-254 n'est pas documente dans le delivery report.

## Evaluation

Points solides:

- process natal explicite et testable;
- runtime interne unifie;
- registre de familles qui bloque les extensions non gouvernees;
- manifestes comparables;
- trace redigee distincte du replay;
- preuve astronomique traitee comme gate;
- separation nette entre calcul, signaux, projections et IA;
- doctrine et sources de regles rendues visibles.

Points a surveiller:

- ne pas exposer le runtime brut pour accelerer une feature frontend;
- ne pas implementer les transits avant contrat public, preuve et projection;
- ne pas multiplier les sources de regles astrologiques;
- ne pas ajouter de narration dans les calculateurs;
- ne pas refaire des calculs dans les serializers;
- ne pas utiliser les traces comme snapshots de replay.

## Recommandations

Ordre recommande pour la suite:

1. Decider les champs exacts de `expert_technical_projection`.
2. Decider la politique de masquage de `beginner_summary`.
3. Trancher `fixed_star_contacts`: public, gated ou rejected.
4. Trancher `astrologer_debug_data`: audience, authz, retention, redaction.
5. Stabiliser la preuve ephemeride externe avant toute promesse publique temporelle.
6. Produire un contrat API public avant tout travail frontend sur les nouvelles projections.
7. Garder `transit_chart_v1` non public tant que la projection, la preuve et la doctrine ne sont pas fermees.

## Conclusion

Au 2026-05-24, le process astrologique backend est passe d'un moteur natal enrichi a une plateforme runtime gouvernee.

La valeur principale n'est plus seulement dans les calculateurs individuels, mais dans l'encadrement du flux complet: graphes declares, objets runtime canoniques, payloads types, manifestes, traces redigees, preuve astronomique, gouvernance doctrinale et projections publiques controlees.

Le backend est pret a evoluer vers des projections produit plus riches et vers un premier chemin temporel, mais seulement si les decisions produit, securite, doctrine et preuve restent explicites. La contrainte saine a conserver est simple: les faits restent calcules par le backend, les signaux restent derives depuis ces faits, et le public ne voit que des projections nommees.
