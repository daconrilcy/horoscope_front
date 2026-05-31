# CS-415 - Construire Un Reading Plan Basic Natal Inspectable

<!-- Commentaire global: ce brief cadre la construction du plan de lecture Basic avant toute generation narrative. -->

## Resume

Construire `BasicNatalReadingPlan`, l'objet central qui definit exactement la restitution
avant generation. Le plan doit choisir les sections, leurs themes, les faits obligatoires,
les faits interdits, les preuves publiques et les contraintes de style.

## Contexte

La conclusion du plan source recommande de commencer par la creation du `ReadingPlan` et de
ses tests avant toute generation IA. Cette story est le pivot du refactoring: elle transforme
les faits, scores, themes et syntheses en cahier des charges narratif inspectable.

## Objectif

Produire un plan de lecture:

```json
{
  "level": "basic",
  "locale": "fr-FR",
  "engine_version": "basic-natal-reading-v1",
  "sections": [],
  "public_evidence": [],
  "style_constraints": {}
}
```

Avec heure complete, l'ordre recommande couvre synthese, identite, vie interieure, vocation
si active, relations si active, talents, tensions et croissance. Sans heure, l'ordre remplace
les maisons/angles par Soleil-Lune, elements/modalites, relations/valeurs, mental/action,
aspects majeurs et croissance par signes.

## Perimetre Inclus

1. Creer le builder de `BasicNatalReadingPlan`.
2. Consommer `EligibilityContext`, `NatalFactGraph`, `NatalSalienceModel`, `ThemeModel` et
   `SynthesisResolver`.
3. Produire six a huit sections maximum, avec longueur cible et codes de themes.
4. Associer chaque section a des `required_fact_ids` et `supporting_evidence_ids`.
5. Construire `public_evidence` vulgarisee, distincte de l'evidence interne.
6. Ajouter les limitations publiques et disclaimers requis.
7. Garantir que les faits interdits ne peuvent pas entrer dans les sections.
8. Ajouter des tests de plan sur heure complete, date-only, maison 10, maison 4, maison 7,
   maison 12 et contradictions.

## Hors Perimetre

- Appeler le LLM.
- Rediger le contenu final.
- Persister les interpretations.
- Modifier le frontend.
- Augmenter les budgets Basic.

## Sources Obligatoires

- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_story_briefs/cs-409-contrats-versionnes-lecture-natale-basic-v2.md`
- `_story_briefs/cs-410-classifier-eligibilite-heure-naissance-basic.md`
- `_story_briefs/cs-411-natal-fact-graph-basic-tracable.md`
- `_story_briefs/cs-412-prioriser-faits-natals-basic-salience-calibree.md`
- `_story_briefs/cs-413-definir-taxonomie-themes-narratifs-basic.md`
- `_story_briefs/cs-414-resoudre-contradictions-themes-natals-basic.md`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-149` - le plan remplace les payloads legacy par une entree moderne gouvernee.
  - `RG-152` - les champs techniques restent hors narratif public.
  - `RG-154` - la denylist publique s'applique aux preuves et limitations.
  - `RG-155` - pas de sections dupliquees, padding ou sources vides.
  - `RG-156` - la couverture Basic diversifiee est obligatoire.
- Required regression evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_reading_plan_archetypes.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_public_evidence.py`
  - `rg -n "ranking_score|condition_axis|score_profile|weighted_score|prompt_hint" backend/app/domain/astrology/interpretation backend/app/services/llm_generation/natal`
- Registry enrichment expected:
  - Ajouter un `RG-XXX` protegeant `BasicNatalReadingPlan` comme owner obligatoire de toute
    selection narrative Basic.
- Allowed differences:
  - L'ordre des sections Basic devient dynamique selon les themes actives et l'eligibilite.

## Criteres D'acceptation

1. Le plan est inspectable avant generation.
2. Chaque section a au moins un theme et des preuves quand le contenu l'exige.
3. Le plan complete avec heure couvre les piliers et les themes dominants reels.
4. Le plan date-only exclut maisons, ASC, MC et rulers de maisons.
5. Les preuves publiques sont lisibles et ne contiennent pas de scores internes.
6. Les sections interdites ou insuffisamment prouvees sont absentes.
7. Les tests d'archetypes prouvent que le theme maison 10 ne devient pas le modele unique.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_builder.py --tb=short
python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_reading_plan_archetypes.py --tb=short
python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_public_evidence.py --tb=short
```

## Dependances

- CS-404.
- CS-405.
- CS-406.
- CS-407.
- CS-408.
- CS-409.

## Risques

Le risque principal est un plan trop verbeux qui redeviendrait un dump astrologique. La story
doit rester dans les budgets Basic et prouver que chaque section existe pour une raison
astrologique explicite.
