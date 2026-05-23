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
