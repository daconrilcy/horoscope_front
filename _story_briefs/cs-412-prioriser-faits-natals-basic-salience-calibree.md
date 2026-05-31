# CS-412 - Prioriser Les Faits Natals Basic Par Salience Calibree

<!-- Commentaire global: ce brief cadre le modele de salience qui priorise les faits natals sans produire de narration. -->

## Resume

Creer `NatalSalienceModel` pour classer les faits du `NatalFactGraph` selon leur importance
interpretative. Le modele doit eviter qu'un fait spectaculaire mais secondaire passe devant
les piliers natals, et il doit etre calibre sur plusieurs archetypes plutot que sur un theme
test unique.

## Contexte

Le plan source signale un risque P1: suradapter le scoring au theme maison 10 teste. Le
mode Basic doit s'adapter a une maison 4, 7, 12, une dominante Feu/Eau, une Lune tres
aspectee, Saturne dominant ou Venus forte mais contrainte.

## Objectif

Attribuer a chaque fait:

- `salience_score`;
- `salience_level`;
- `reason_codes`;
- `exclusion_reason` si le fait ne doit pas alimenter Basic.

Les facteurs de priorite incluent luminaires, maitre d'Ascendant, angularite, maison
dominante, dominante planetaire, dignite forte, contrainte forte, aspect exact, repetition
thematique et disponibilite selon `EligibilityContext`.

## Perimetre Inclus

1. Implementer un scorer deterministe, configurable et versionne.
2. Definir des `reason_codes` stables et documentes.
3. Garantir que Soleil, Lune et Ascendant eligible restent des piliers.
4. Garantir qu'un point mineur ou un detail technique ne depasse pas les piliers.
5. Creer ou enrichir un corpus minimal d'archetypes anonymises partage par la suite du
   pipeline.
6. Ajouter des tests de priorisation pour luminaire angulaire, aspect exact, maison dominante,
   dominante planetaire et signaux faibles.
7. Pour chaque golden chart, stocker facts attendus, themes attendus, sections attendues,
   faits interdits en Basic et assertions de qualite narrative.
8. Ajouter des assertions empechant Lilith, hayz, voices/forms/fertility ou details numeriques
   de dignite de devenir centraux en Basic.
9. Produire un resume audit interne des decisions de salience sans l'exposer au public.

## Hors Perimetre

- Construire des themes narratifs.
- Fusionner les contradictions.
- Choisir l'ordre final des sections.
- Ajouter des calculs astrologiques.
- Modifier les prompts.

## Sources Obligatoires

- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_story_briefs/cs-411-natal-fact-graph-basic-tracable.md`
- `backend/app/domain/astrology/interpretation/client_interpretation_projection_v1_builder.py`
- `backend/app/domain/astrology/interpretation_adapters/signal_builder.py`
- `backend/tests/fixtures/golden/natal_test.yaml`
- `backend/tests/fixtures/golden/natal_premium_test.yaml`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-144` a `RG-148` - le scoring consomme les payloads runtime existants sans recalcul.
  - `RG-151` - les aspects publics gardent une identite stable.
  - `RG-156` - la couverture Basic doit rester diversifiee.
- Required regression evidence:
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_model.py`
  - `pytest -q backend/tests/unit/domain/astrology/test_basic_natal_salience_archetypes.py`
  - `rg -n "lilith|hayz|voices|forms|fertility|ranking_score|weighted_score" backend/app/domain/astrology/interpretation backend/tests/unit/domain/astrology`
- Registry enrichment expected:
  - Ajouter un `RG-XXX` protegeant la non-priorisation des faits mineurs devant les piliers.
- Allowed differences:
  - Les audits internes peuvent contenir des scores, mais les sorties publiques restent sans
    scores.

## Criteres D'acceptation

1. Un luminaire angulaire passe devant un point mineur.
2. Un aspect exact impliquant Soleil ou Lune passe devant un aspect large entre
   transpersonnelles.
3. Une maison dominante active une priorite thematique sans devenir priorite globale fixe.
4. Un theme fonde sur un seul signal faible ne peut pas declencher une section autonome plus
   tard.
5. Les archetypes maison 10, maison 4, maison 7, maison 12, date-only, Feu, Eau, Lune forte,
   Saturne dominant et Venus contrainte sont representes dans les fixtures ou factories.
6. Chaque golden chart declare les facts, themes, sections, faits interdits et assertions
   narratives attendus.
7. Le modele est versionne et ses decisions sont auditables.
8. Aucun score interne n'est expose dans les contrats publics.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_salience_model.py --tb=short
python -B -m pytest -q tests/unit/domain/astrology/test_basic_natal_salience_archetypes.py --tb=short
```

## Dependances

- CS-406.

## Risques

Le risque principal est un scoring qui parait exact sur une fixture mais produit des lectures
monotones. La calibration doit privilegier des regles simples, explicables et verifiees sur
des themes contrastes.
