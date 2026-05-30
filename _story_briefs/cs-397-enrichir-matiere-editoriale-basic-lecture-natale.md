# CS-397 - Enrichir La Matiere Editoriale Basic De La Lecture Natale

<!-- Commentaire global: ce brief cadre l'exploitation effective de la richesse astrologique dans la lecture Basic. -->

## Resume

Garantir qu'une lecture natale Basic exploite une matiere astrologique diversifiee et
repartie par chapitre. Le budget Basic existant autorise six sections et vingt-quatre sources:
la generation ne doit plus se reduire a trois paragraphes generiques alors que le calcul
natal contient maisons, aspects, dominantes, dignites et conditions.

## Contexte

La QA live du 2026-05-30 montre que la lecture Basic mobilise surtout Ascendant Cancer,
Soleil/Venus maison 10, MC Belier et Jupiter maison 7. Le theme calcule contient pourtant
10 planetes, 12 maisons, 10 aspects majeurs, dignites, conditions avancees, dominantes et
regences. Le profil Basic declare deja `max_source_items=24`, `max_sections=6` et jusqu'a
six `support_elements`.

## Objectif

Construire une matiere editoriale Basic equilibree:

```text
personnalite + emotions + relations + vocation + evolution
= faits astrologiques distincts, priorises et vulgarisables
```

## Perimetre inclus

1. Auditer le passage `client_interpretation_projection_v1` vers `llm_astrology_input_v1`.
2. Garantir la population de `support_elements` pour Basic et Premium lorsque des faits
   exploitables existent.
3. Selectionner une couverture thematique, pas seulement les faits globalement les mieux
   classes.
4. Inclure au minimum les familles pertinentes: big three, rulers, maisons dominantes,
   aspects majeurs, dominantes planetaires et tensions structurantes.
5. Aligner prompt, payload provider et schema nominal pour demander les cinq familles de
   sections sources requises par la lecture narrative.
6. Preferer `AstroResponseV3` pour les lectures completes et documenter le comportement
   explicite des schemas historiques V1/V2.
7. Ajouter une fixture riche representative et verifier la repartition par chapitre.
8. Ajouter des metriques auditables: familles selectionnees, nombre de faits, chapitres
   couverts et sources publiques produites.

## Hors perimetre

- Ajouter des calculs astrologiques.
- Produire une narration deterministe cote domaine.
- Exposer codes moteur, scores ou `evidence_refs` au frontend.
- Augmenter arbitrairement les budgets Basic.
- Modifier les quotas ou le rendu React.

## Sources obligatoires

- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/domain/astrology/interpretation_adapters/signal_builder.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`
- `backend/scripts/seed_30_3_gpt5_prompts.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-149` - `llm_astrology_input_v1` reste l'entree moderne canonique sans carriers legacy.
  - `RG-152` - aucun fait technique ne fuit dans le contrat narratif public.
  - `RG-144` a `RG-148` - consommer les projections runtime existantes sans recalcul local.
  - `RG-156` - la couverture editoriale Basic reste diversifiee dans les budgets existants.
- Needs-investigation invariants:
  - Auditer si la faible diversite vient aussi du catalogue de regles active de
    `interpretation_adapter`; corriger uniquement dans son owner canonique si confirme.
- Required regression evidence:
  - `pytest -q backend/tests/llm_orchestration -k "natal or theme_astral"`
  - `pytest -q backend/tests/unit/domain/astrology/test_client_interpretation_support_elements.py`
  - `rg -n "chart_json|natal_data" backend/app/domain/llm backend/app/services/llm_generation/natal`
- Registry enrichment completed:
  - `RG-156` protege la couverture editoriale minimale des lectures completes Basic.
- Allowed differences:
  - Les payloads provider modernes contiennent davantage de faits structures dans les
    budgets existants.

## Criteres d'acceptation

1. Une fixture riche Basic produit cinq chapitres alimentes par des familles de faits
   distinctes.
2. Les sources vulgarisees Basic sont non vides et limitees par le budget commercial.
3. Les aspects ou tensions ne remplacent pas les big three, rulers et maisons dominantes:
   la selection couvre plusieurs familles.
4. Le prompt nominal complet demande explicitement les cinq sections sources.
5. Les schemas historiques incomplets ne sont ni promus ni paddes silencieusement.
6. Aucun calcul, score ou texte final utilisateur n'est ajoute au domaine astrologique pur.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/llm_orchestration --tb=short -k "natal or theme_astral"
python -B -m pytest -q tests/unit/domain/astrology/test_client_interpretation_support_elements.py --tb=short
```

## Dependances

- CS-396.

## Risques

Le risque principal est de confondre richesse et volume. La story doit augmenter la
couverture thematique utile sans exposer un dump astrologique ni gonfler le prompt sans
budget.
