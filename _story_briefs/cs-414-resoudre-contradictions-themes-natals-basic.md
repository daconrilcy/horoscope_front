# CS-414 - Resoudre Les Contradictions Des Themes Natals Basic

<!-- Commentaire global: ce brief cadre le resolver qui transforme des signaux mixtes en syntheses nuancees. -->

## Resume

Ajouter `SynthesisResolver` pour combiner ressources, contraintes et tensions dans chaque
theme narratif. Le mode Basic ne doit plus produire de phrases unilateralement positives ou
negatives lorsqu'un theme contient des signaux contradictoires.

## Contexte

Le plan source identifie un risque P1: extraire et scorer des faits ne suffit pas. Venus en
domicile mais combuste, Lune importante mais contrainte, Jupiter fort mais carre aux
luminaires ou une dominante maison 10 avec tensions relationnelles exigent une synthese
explicite.

## Objectif

Produire pour chaque theme:

- `core_statement`;
- `resource_statement`;
- `constraint_statement`;
- `integration_statement`;
- `confidence`.

Ces elements restent editoriaux et controles: ils alimentent le plan ou le LLM, mais ne
deviennent pas automatiquement du texte public sans validation.

## Perimetre Inclus

1. Implementer le resolver a partir des themes actives, de leurs resources, constraints et
   tensions.
2. Definir des regles adversariales: dignite forte + contrainte forte impose une nuance.
3. Interdire une section autonome pour un theme fonde sur un seul fait faible.
4. Fusionner deux themes qui racontent la meme chose avec les memes faits.
5. Retrograder ou supprimer un theme dependant des maisons indisponibles.
6. Produire une synthese date-only sans Ascendant, maisons ou MC.
7. Ajouter des tests pour Venus forte mais combuste, Lune contrainte, Jupiter carre et theme
   relationnel mixte.
8. Ajouter une denylist de formulations trop absolues, fatalistes ou prescriptives.

## Hors Perimetre

- Construire le `ReadingPlan` complet.
- Generer la prose finale.
- Modifier le prompt provider.
- Ajouter des recommandations medicales, juridiques, financieres ou psychologiques.
- Changer le frontend.

## Sources Obligatoires

- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_story_briefs/cs-413-definir-taxonomie-themes-narratifs-basic.md`
- `backend/app/services/llm_generation/natal/narrative_semantic_integrity.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`
- `backend/tests/unit/domain/astrology/test_traditional_golden_cases.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-152` - les syntheses ne doivent pas exposer de scores ou codes moteur.
  - `RG-154` - les textes publics restent sans identifiants evidence bruts.
  - `RG-155` - pas de padding semantique ni chapitres dupliques.
  - `RG-156` - la richesse Basic reste fondee sur plusieurs familles.
- Required regression evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py`
  - `rg -n "toujours|jamais|destin|oblige|doit absolument|medical|juridique|financier" backend/app/domain/astrology/interpretation backend/app/services/llm_generation/natal`
- Registry enrichment expected:
  - Ajouter un `RG-XXX` protegeant la nuance obligatoire des themes mixtes.
- Allowed differences:
  - Les payloads editoriaux peuvent contenir des syntheses structurees, mais le public ne voit
    que la projection validee.

## Criteres D'acceptation

1. Un theme avec ressource et contrainte fortes contient une nuance obligatoire.
2. Un theme sans preuve suffisante ne produit pas de section autonome.
3. Deux themes redondants sont fusionnes ou relies explicitement.
4. Les syntheses n'emploient pas de ton fataliste ou prescriptif.
5. Les syntheses date-only n'interpretent pas les maisons, ASC ou MC.
6. Les tests couvrent des contradictions astrologiques representatives.
7. Les syntheses restent separees du rendu final utilisateur.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_resolver.py --tb=short
python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_synthesis_contradictions.py --tb=short
```

## Dependances

- CS-408.

## Risques

Le risque principal est de transformer le resolver en redacteur deterministe complet. Il doit
produire des lignes de lecture structurees et validables, pas remplacer a lui seul la
generation narrative.
