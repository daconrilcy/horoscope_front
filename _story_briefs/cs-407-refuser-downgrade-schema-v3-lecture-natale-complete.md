# CS-407 - Refuser Le Downgrade Schema V3 Des Lectures Natales Completes

<!-- Commentaire global: ce brief cadre le durcissement du service contre les retours V2/V1 silencieux sur les lectures completes Basic/Premium. -->

## Resume

Supprimer le comportement nominal ou une lecture natale `complete` Basic/Premium peut etre
exposee comme reponse publique apres echec de deserialisation `AstroResponseV3` puis fallback
local vers `AstroResponseV2` ou `AstroResponseV1`. Une lecture complete non `free_short` qui
n'est pas compatible V3 doit etre rejetee et auditee, pas convertie en lecture narrative
publique.

## Contexte

Le fallback V2 observe est une consequence du mauvais routage Basic vers l'assembly free, mais
le service rend cette regression difficile a detecter: il tente V3 puis accepte V2/V1 si le
payload court passe ces schemas. Cela masque une erreur de configuration gateway et produit
ensuite un rejet CS-396 tardif ou une experience degradee.

Apres CS-401, Basic complete doit arriver en V3. Cette story verrouille le runtime de
generation pour que toute future desynchronisation assembly/schema soit visible et auditee.
La relecture de payloads historiques reste un sujet separe: elle peut conserver une
compatibilite explicitement testee, mais ne doit pas rendre publics des payloads rejetes ou
semantiquement invalides.

## Analyse Code Actuel

Evidence consultee:

- `_condamad/stories/regression-guardrails.md` - invariants consultes avant cadrage.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - dans `interpret()`,
  le chemin `level == "complete"` tente `AstroResponseV3(**base_output)`, puis
  `AstroErrorResponseV3`, puis `AstroResponseV2(**full_output)`, puis `AstroResponseV1`.
- `backend/app/services/llm_generation/natal/interpretation_service.py` - le fallback est
  ensuite projete vers `narrative_natal_reading_v1`, ou rejete plus tard par integrite
  semantique.
- `backend/app/domain/llm/prompting/schemas.py` - `AstroResponseV3` exige un resume long,
  au moins cinq sections, cinq highlights et cinq advice; V2/V1 acceptent des sorties plus
  courtes.
- `backend/app/domain/llm/runtime/contracts.py` - `GatewayResult.meta.validation_status`,
  `repair_attempted` et `fallback_triggered` permettent de distinguer un fallback gateway
  d'un downgrade local du service.

## Objectif

Garantir:

```text
complete Basic/Premium + gateway non fallback => AstroResponseV3 ou rejet audite
complete free_short => AstroFreeResponseV1 autorise
gateway fallback_triggered => comportement fallback explicite et observable
aucun downgrade local V3 -> V2/V1 expose comme lecture complete acceptee
```

## Perimetre Inclus

1. Identifier le statut attendu par niveau/variant: toute generation `complete` non
   `free_short` exige V3.
2. Remplacer le fallback local V2/V1 nominal du chemin de generation par un rejet audite
   quand V3 echoue.
3. Conserver `AstroErrorResponseV3` uniquement pour les erreurs V3 explicitement conformes.
4. Conserver le chemin `free_short` et les fallbacks gateway explicitement marques.
5. Ajouter une cause de rejet claire, par exemple `natal_complete_schema_mismatch`, reliee a
   l'audit narratif existant.
6. Ne pas persister la sortie V2/V1 comme `UserNatalInterpretationModel` complete acceptee.
7. Ajouter des tests unitaires avec payload V1/V2 court et `fallback_triggered=False`.
8. Ajouter des tests prouvant que le meme payload n'est pas public et vit dans le workflow
   audit/rejet.

## Hors Perimetre

- Modifier le schema `AstroResponseV3`.
- Modifier les prompts.
- Changer les quotas.
- Supprimer les classes `AstroResponseV2` ou `AstroResponseV1`, encore utilisees par des
  surfaces historiques ou courtes.
- Transformer un rejet en exception 500 publique.

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-150` - les payloads rejetes ne doivent pas etre deserialises comme reponses publiques.
  - `RG-152` - `narrative_natal_reading_v1` reste le contrat public des lectures completes
    acceptees.
  - `RG-155` - les lectures completes Basic/Premium sans integrite semantique sont rejetees.
  - `RG-157` - un rejet schema/semantique ne doit pas consommer le quota.
- Required regression evidence:
  - `pytest -q backend/tests/unit/test_natal_interpretation_service_v3_schema_guard.py` (nouveau test attendu)
  - `pytest -q backend/tests/unit/test_natal_interpretation_stored_payload.py`
  - `pytest -q backend/tests/integration/test_natal_interpretation_rejected_public_boundary.py`
  - `pytest -q backend/tests/unit/test_natal_chart_long_quota_on_acceptance.py`
  - `rg -n "AstroResponseV2\\(\\*\\*full_output\\)|AstroResponseV1\\(\\*\\*full_output\\)" backend/app/services/llm_generation/natal/interpretation_service.py` avec hits interdits dans le bloc de generation complete nominale.
- Allowed differences:
  - Une sortie complete non V3 precedemment acceptee en V2/V1 devient rejetee et auditee.
  - `schema_version: "v2"` ne doit plus apparaitre comme resultat nouvellement accepte pour
    Basic/Premium complete hors compatibilite de relecture historique explicitement testee.

## Criteres D'acceptation

1. Une sortie V1/V2 courte provenant d'un appel `complete` non fallback ne peut plus etre
   exposee comme lecture complete acceptee.
2. Le rejet est audite avec une cause explicite et un `request_id`.
3. Le payload rejete n'est pas relu par `POST`, `GET` ou `LIST` publics.
4. Le quota `natal_chart_long` n'est pas consomme pour ce rejet.
5. `free_short` continue de fonctionner avec son schema court.
6. Un vrai `AstroResponseV3` continue d'etre persiste et relu.
7. Les logs/metas permettent de distinguer un fallback gateway explicite d'un mismatch de
   schema local.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/test_natal_interpretation_service_v3_schema_guard.py --tb=short
python -B -m pytest -q tests/unit/test_natal_interpretation_stored_payload.py --tb=short
python -B -m pytest -q tests/integration/test_natal_interpretation_rejected_public_boundary.py --tb=short
python -B -m pytest -q tests/unit/test_natal_chart_long_quota_on_acceptance.py --tb=short
rg -n "AstroResponseV2\\(\\*\\*full_output\\)|AstroResponseV1\\(\\*\\*full_output\\)" app/services/llm_generation/natal/interpretation_service.py
```

## Dependances

- CS-401.

## Risques

Le risque principal est de casser la relecture d'anciennes interpretations V2 legitimes. La
story doit distinguer le runtime de generation complete nominal du chemin de relecture
historique, et documenter toute compatibilite transitoire restante.
