# CS-331 - Mapper La Richesse Astrologique Vers llm_astrology_input_v1

<!-- Commentaire global: ce brief organise le mapping des calculs et interpretations recentes vers le contrat d'entree LLM. -->

## Resume

Implementer le builder/adaptateur qui transforme les donnees astrologiques et interpretations pre-narratives existantes en `llm_astrology_input_v1`.

L'objectif est que le futur prompt LLM beneficie de la richesse deja calculee: faits structuraux, dominantes, dignites/forces si disponibles, aspects, maisons, axes, signaux interpretatifs, donnees manquantes et evidence refs.

## Contexte

CS-330 definit le contrat cible. Cette story doit l'alimenter depuis les surfaces recentes, sans exposer les objets runtime bruts et sans s'appuyer sur `chart_json` comme source principale.

Le rapport de transition recommande le flux:

```text
CalculationGraph / ChartObjectRuntimeData
-> ChartInterpretationInputRuntimeData
-> AINarrativeInputContract
-> llm_astrology_input_v1
```

## Source obligatoire

Lire avant implementation:

- `_story_briefs/cs-330-definir-contrat-llm-astrology-input-v1.md`
- `_condamad/reports/calculs-interpretations-vers-prompts-llm/2026-05-26-0000/rapport-transition-injection-prompts-llm.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/00-architecture.md`
- `_condamad/architecture/calculs-interpretations-injection-llm/2026-05-26-0000/02-target-contract.md`

Relire les builders et contrats existants:

- `backend/app/domain/astrology/interpretation/structured_facts_v1_builder.py`
- `backend/app/domain/astrology/interpretation/ai_narrative_input_builder.py`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/interpretation/evidence_refs.py`

## Objectif

Creer un mapping deterministe entre les surfaces recentes et `llm_astrology_input_v1`, avec une selection de donnees utile au LLM et lisible dans le prompt final.

## Perimetre inclus

1. Creer ou completer un builder `llm_astrology_input_v1`.
2. Alimenter le bloc `facts` depuis `structured_facts_v1`.
3. Alimenter le bloc `signals` depuis `AINarrativeInputContract`.
4. Alimenter le bloc `limits` avec les donnees absentes, incertaines ou volontairement exclues.
5. Alimenter le bloc `evidence` avec les `evidence_refs` pertinentes.
6. Alimenter le bloc `shaping` avec les informations de plan/module utiles a la profondeur narrative, sans en faire une source factuelle.
7. Ajouter des tests de mapping sur un profil natal representatif.
8. Ajouter des tests de non-duplication entre facts et signals quand une meme notion existe dans les deux surfaces.

## Hors perimetre

- Modifier les prompts redactionnels.
- Modifier le process general de generation de prompt LLM.
- Traiter la securite, le CI ou les profils astrologues.
- Modifier les endpoints publics ou le frontend.
- Supprimer les surfaces legacy.
- Ajouter de nouveaux calculs astrologiques.

## Donnees a evaluer pour inclusion

Le mapping doit examiner, selon ce qui existe deja dans le runtime:

- positions planetaires et points natals;
- maisons, axes et placements par maison;
- aspects et orbes;
- signes, elements, modalites et polarites;
- dominantes ou signatures synthetiques deja calculees;
- dignites, forces, poids ou scores deja produits;
- interpretations pre-narratives par objet/aspect/maison;
- warnings, missing data et limites de calcul;
- references d'evidence associees.

## Criteres d'acceptation

1. Un builder/adaptateur produit `llm_astrology_input_v1` sans consommer `chart_json` comme source canonique.
2. Les faits stables sont issus de `structured_facts_v1`.
3. Les signaux interpretatifs sont issus du contrat narratif interne existant.
4. Les limites/missing data sont prompt-visibles dans une forme exploitable.
5. Les donnees de shaping restent separees des faits.
6. Les tests couvrent un cas natal complet et un cas avec donnees manquantes.
7. Les objets runtime bruts ne sont pas serialises dans le contrat LLM.

## Validation attendue

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
pytest -q tests --tb=short
rg -n "llm_astrology_input_v1|structured_facts_v1|signals|limits|evidence_refs|chart_json|natal_data" app tests
```

## Risques

Le risque principal est de perdre la nuance interpretative en reduisant le mapping a une copie de faits plats. Le builder doit donner au LLM des faits precis et des signaux pre-narratifs lisibles, tout en gardant la frontiere entre calcul, interpretation et shaping.
