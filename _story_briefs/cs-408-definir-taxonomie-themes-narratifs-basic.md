# CS-408 - Definir La Taxonomie Des Themes Narratifs Basic

<!-- Commentaire global: ce brief cadre la taxonomie narrative versionnee qui regroupe les faits natals en themes Basic. -->

## Resume

Creer `NatalNarrativeThemeTaxonomy` et `ThemeModel` pour transformer des faits priorises en
themes narratifs standardises. La taxonomie doit eviter la multiplication de themes voisins,
definir les conditions d'activation et adapter les sections aux donnees disponibles.

## Contexte

Le plan source identifie un risque P2: des codes comme `public_vocation` ou
`emotional_pattern` n'avaient pas de contrat de declenchement, de priorite ou de contenu. La
refonte doit stabiliser ces themes avant de demander au LLM de rediger.

## Objectif

Definir les themes Basic recommandes:

- `core_identity`;
- `emotional_pattern`;
- `public_vocation`;
- `relationship_pattern`;
- `mental_style`;
- `resources_and_values`;
- `action_and_drive`;
- `growth_direction`;
- `tension_to_integrate`;
- `talents_and_supports`.

Chaque theme doit avoir triggers, exclusions, sections compatibles, vocabulaire conseille,
formulations interdites et disponibilite selon l'heure de naissance.

## Perimetre Inclus

1. Creer une taxonomie versionnee des themes Basic.
2. Mapper les familles de faits et niveaux de salience vers des themes.
3. Definir `resources`, `constraints`, `tensions`, `must_mention`, `may_mention` et
   `do_not_mention`.
4. Retrograder ou supprimer les themes dependants des maisons quand `EligibilityContext` les
   interdit.
5. Fusionner les themes voisins lorsque leur matiere astrologique est redondante.
6. Ajouter des tests d'activation pour vocation, relations, mental, action, talents,
   tensions et date-only.
7. Ajouter des tests prouvant qu'un seul signal faible ne cree pas une section.
8. Documenter les formulations interdites pour eviter Barnum, fatalisme et adjectifs sans
   preuve.

## Hors Perimetre

- Rediger le texte final.
- Appeler le LLM.
- Construire le `ReadingPlan` final.
- Changer la page `/natal`.
- Ajouter de nouveaux calculs astrologiques.

## Sources Obligatoires

- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_story_briefs/cs-407-prioriser-faits-natals-basic-par-salience-calibree.md`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/services/llm_generation/natal/narrative_natal_reading_builder.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-149` - la classification du processus natal moderne reste explicite.
  - `RG-152` - les themes ne doivent pas exposer de codes techniques publics.
  - `RG-154` - les identifiants evidence bruts restent hors DOM public.
  - `RG-156` - la lecture Basic couvre plusieurs familles astrologiques.
- Required regression evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_theme_taxonomy.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_theme_activation.py`
  - `rg -n "spirituel|creatif|harmonieux|profond" backend/app/domain/astrology/interpretation backend/app/services/llm_generation/natal`
- Registry enrichment expected:
  - Ajouter un `RG-XXX` protegeant les themes Basic versionnes et leurs conditions
    d'activation.
- Allowed differences:
  - L'ordre des futurs chapitres devient partiellement dynamique selon les themes actives.

## Criteres D'acceptation

1. Chaque theme a des triggers et exclusions explicites.
2. Chaque theme declare sa compatibilite avec `full_birth_time`, `approximate_birth_time` et
   `date_only`.
3. Les themes maison/angle sont absents ou retrogrades sans heure fiable.
4. Les formulations interdites sont testees ou documentees.
5. Les themes actifs conservent les faits `must_mention` et `do_not_mention`.
6. Deux themes redondants sont fusionnes ou hierarchises, pas affiches en doublon.
7. La taxonomie est versionnee.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_theme_taxonomy.py --tb=short
python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_theme_activation.py --tb=short
```

## Dependances

- CS-405.
- CS-407.

## Risques

Le risque principal est une taxonomie trop large qui recrée dix lectures generiques. La story
doit definir peu de themes, fortement contractuels, et laisser le plan final choisir ceux qui
sont vraiment actifs.
