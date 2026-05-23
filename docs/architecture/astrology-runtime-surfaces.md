# Surfaces runtime astrologiques

Ce document fixe le statut des surfaces runtime du theme natal pendant la transition vers `NatalResult.chart_objects`.

## Regle canonique

`NatalResult.chart_objects` est la source canonique interne pour les nouveaux calculateurs astrologiques. Les calculateurs selectionnent les objets par `ChartObjectCapabilities` et lisent les faits via `ChartObjectPayloads`, sans recreer de branchement metier par famille d'objet.

Les collections historiques restent exposees uniquement comme projections de compatibilite, projections d'API publique, resultats chart-level ou supports de diagnostic. Leur presence ne les rend pas sources metier primaires pour de nouveaux calculateurs.

Vocabulaire de statut autorise: `canonical`, `compatibility projection`, `public API projection`, `chart-level result`, `legacy`.

## Inventaire

| Surface | Statut | Source cible | Autorisee dans calculateurs | Owner | Allowlist reason | Commentaire |
|---|---|---|---|---|---|---|
| `chart_objects` | canonical | runtime builder | oui | `backend/app/domain/astrology/natal_calculation.py` | Source interne cible. | Graphe unifie consomme par aspects, dignites, dominance, fixed stars et input interpretatif. |
| `planet_positions` | compatibility projection | `chart_objects` / bridge natal historique | non | `backend/app/domain/astrology/natal_calculation.py` | Public API projection and compatibility snapshot. | Conservé pour API/front, debug et non-regression; les nouveaux calculateurs ne doivent pas le lire via `natal_result`. |
| `astral_points` | compatibility projection | `chart_objects` / bridge natal historique | non | `backend/app/domain/astrology/natal_calculation.py` | Public API projection and existing interpretation compatibility. | Conservé pour API/front et pour le service interpretatif legacy allowliste. |
| `houses` | compatibility projection | `chart_objects` / house runtime | non | `backend/app/domain/astrology/natal_calculation.py` | Public API projection and house runtime compatibility. | Conservé comme projection publique des maisons enrichies. |
| `angles` | legacy | `chart_objects` angle payloads | non | `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | Migration bridge only if a public adapter requires it. | Les angles sont projetes comme objets `asc`, `dsc`, `mc`, `ic`; aucune collection publique `angles` n'est ajoutee par CS-224. |
| `aspects` | chart-level result | `chart_objects` via aspect selector/projector | lecture controlee | `backend/app/domain/astrology/natal_calculation.py` | Public result and downstream interpretation input. | Resultat calcule depuis les candidats `chart_objects`, pas depuis les collections historiques. |
| `dignity_results` | compatibility projection | `payloads.dignity` / `dignities` | non | `backend/app/domain/astrology/dignities` | Public compatibility while `NatalResult.dignities` exists. | Nom de gouvernance pour les resultats de dignite historiques; dans le modele courant la surface exposee est `dignities`. |
| `dominance_result` | chart-level result | dominance calculator | lecture controlee | `backend/app/domain/astrology/dominance` | Public result and interpretation input. | Dans le modele courant la surface exposee est `dominant_planets`; les contributions objet restent dans `payloads.dominance`. |
| `advanced_conditions` | compatibility projection | motion/visibility/condition payloads | non | `backend/app/domain/astrology/advanced_conditions` | Public compatibility and traditional-condition bridge. | Conservé temporairement comme sortie historique; les nouveaux calculateurs doivent preferer payloads et facts canoniques. |
| `fixed_star_conjunctions` | compatibility projection | `payloads.fixed_star_conjunctions` | non | `backend/app/domain/astrology/fixed_stars` | Payload projection; no top-level public field is introduced. | Les contacts sont rattaches aux objets eligibles et adaptes vers l'input interpretatif. |

## Exceptions allowlistees

| Chemin | Surface | Raison | Decision de sortie |
|---|---|---|---|
| `backend/app/domain/astrology/builders/chart_object_runtime_builder.py` | collections historiques en entree | Projection canonique des collections natales historiques vers `chart_objects`. | Permanent tant que le contrat de transition existe. |
| `backend/app/domain/astrology/natal_calculation.py` | construction des projections publiques | Orchestration du resultat natal et preservation des sorties publiques. | Permanent tant que les sorties publiques existent. |
| `backend/app/domain/astrology/interpretation/astral_point_interpretation.py` | `natal_result.astral_points` | Service interpretatif existant qui assemble une vue editoriale depuis la projection publique. | Temporary; sortie apres story approuvee de migration vers `chart_objects`. |
| `backend/app/services/chart/json_builder.py` et serializers API publics | projections historiques | Serialization publique stable pour front/API. | Permanent tant que le contrat public existe. |
| `backend/tests/**` et fixtures | projections historiques | Non-regression, compatibilite et diagnostic. | Borne aux tests. |

## Trajectoire

Toute suppression future d'une surface historique doit etre portee par une story dediee avec preuve de non-usage public, comparaison OpenAPI et validation front/API. CS-224 ne supprime pas de champ public et n'ajoute pas d'alias, shim ou fallback legacy.

## Aspect runtime layers

CS-229 a separe les couches aspectuelles pour que les calculateurs structurels ne deviennent pas owners de lecture interpretative. CS-233 ferme les bridges de transition restants. Les termes officiels sont `structural runtime`, `interpretive runtime`, `public projection` et `legacy projection`.

| Couche | Contenu | Owner | Consommateurs autorises |
|---|---|---|---|
| Structural aspect runtime | geometrie, orbe, participants, force technique et modifiers factuels | astrology runtime | calculateurs, dominance, graph |
| Interpretive aspect runtime | valence, energy type, axes semantiques, poids interpretatifs et sources | interpretation adapter | prompts, interpretation input |
| Public aspect projection | contrat API stable et champs historiques exposes | chart json builder | front/API |
| Legacy aspect projection | compatibilite historique bornee hors runtime structurel | adapters allowlistes | transition uniquement |

Le runtime structurel cible est `AspectStructuralRuntimeData`. Il porte uniquement `aspect`, `participants`, `orb`, `metadata`, `strength`, `phase` et `modifiers`. Les champs `default_valence`, `interpretive_valence`, `energy_type`, `interpretive_weight`, `meaning`, `narrative`, `prompt` et `llm` ne sont pas autorises dans ce contrat.

Le runtime interpretatif cible est `AspectInterpretiveHintsRuntimeData`. Il porte des hints types et sources, par exemple les valences, l'energy type, les axes semantiques et le poids interpretatif optionnel. Ces hints ne sont pas un texte narratif et ne produisent pas de prompt.

Le referentiel d'aspects est scinde en deux vues portees par `AspectReferenceSet`: `structural_definitions` contient des `AspectStructuralDefinitionRuntimeData` pour le calcul geometrique et `interpretive_profiles` contient des `AspectInterpretiveProfileRuntimeData` pour les resolvers de hints. Le bridge `AspectDefinitionRuntimeData` et le helper `_aspect_definition` ne sont plus des surfaces runtime actives.

`AspectStrengthRuntimeData` reste une force technique: score normalise, niveau et raisons enumerees. La dominance d'aspect reste chart-level et ne devient pas owner de valence. Les modifiers structurels portent uniquement type, source, intensite, raison et cible factuelle.

Le domaine prediction peut continuer a utiliser des valences ou energy types, mais via ses contrats de prediction ou via les hints interpretatifs, jamais via le runtime structurel d'aspects.

## Runtime boundary matrix CS-231

CS-231 etend la gouvernance des surfaces au runtime astrologique complet. La frontiere reste testable par chemins explicites: les calculateurs, builders, contrats runtime, dominance, dignites, fixed stars et conditions avancées appartiennent au `structural runtime`; les modules d'enrichissement d'input, de signaux et d'adaptation appartiennent au `interpretive runtime`; les serializers API restent des `public projection`; les anciens contrats conserves pour compatibilite restent des `legacy projection`.

| Couche | Chemins owners | Champs autorises | Champs interdits |
|---|---|---|---|
| `structural runtime` | `backend/app/domain/astrology/calculators`, `runtime`, `builders`, `dominance`, `fixed_stars`, `dignities`, `planetary_conditions`, `advanced_conditions` | faits calculatoires, identifiants runtime, positions, objets, orbes, angles, forces techniques, dignites, dominance et conditions factuelles | `default_valence`, `interpretive_valence`, `energy_type`, `interpretive_weight`, `meaning`, `narrative`, `prompt`, `llm`, `OpenAI`, `AIEngineAdapter` hors exceptions nommees |
| `interpretive runtime` | `backend/app/domain/astrology/interpretation`, `backend/app/domain/astrology/interpretation_adapters` | hints courts, axes semantiques, profils, priorites et signaux sources depuis faits structurels | recalcul d'orbe, aspects, dignites, dominance, fixed stars ou conditions structurelles |
| `public projection` | `backend/app/services/chart/json_builder.py` et serializers API publics | champs JSON historiques, dont valences et energy type publics | source metier canonique ou recalcul local |
| `legacy projection` | contrats legacy nommes et adapters historiques allowlistes | compatibilite bornee pendant migration | nouvelle source metier non bornee ou fallback silencieux |

### Allowed interpretive field paths

| Chemin | Champ | Raison | Decision de sortie |
|---|---|---|---|
| `backend/app/domain/astrology/runtime/aspect_calculation_contracts.py` / `AspectInterpretiveProfileRuntimeData` | `default_valence`, `interpretive_valence`, `energy_type` | Profil interpretatif separe de la definition structurelle. | Permanent. |
| `backend/app/domain/astrology/runtime/aspect_runtime_data.py` / `AspectInterpretiveHintsRuntimeData` | `default_valence`, `interpretive_valence`, `energy_type`, `interpretive_weight` | Hints interpretatifs types pour adapters et prompts, sans recalcul structurel. | Permanent. |

Les champs publics `interpretive_valence` et `energy_type` restent projetes par `backend/app/services/chart/json_builder.py`, mais leur source unique est `AspectResult.aspect_interpretive_hints`. Une absence de hints sur un aspect public est une erreur de contrat explicite, pas un fallback vers des champs plats.
