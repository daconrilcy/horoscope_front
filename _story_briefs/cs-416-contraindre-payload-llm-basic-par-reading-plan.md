# CS-416 - Contraindre Le Payload LLM Basic Par Le Reading Plan

<!-- Commentaire global: ce brief cadre le handoff LLM controle par le plan de lecture Basic. -->

## Resume

Brancher le `BasicNatalReadingPlan` dans le payload LLM Basic afin que le provider ne recoive
que les faits selectionnes, les syntheses resolues, les preuves editoriales et les contraintes
de style. Le LLM doit rester redacteur controle, sans acces aux donnees personnelles brutes ni
au theme runtime complet.

## Contexte

Le plan source identifie le risque P1 d'une refonte trop dependante du LLM et le risque P3 de
confidentialite. Le prompt ne doit pas recevoir email, user id, identifiant de lieu,
coordonnees exactes non necessaires, scores internes ou donnees runtime completes.

## Objectif

Faire du `ReadingPlan` la seule source de selection narrative Basic:

```text
BasicNatalReadingPlan -> BasicNatalPromptPayload -> Provider -> NarrativeDraft
```

Le payload doit contenir les sections attendues, les syntheses resolues, les preuves
editoriales, les limitations, les disclaimers et les contraintes de style.

## Perimetre Inclus

1. Ajouter un builder de payload LLM Basic depuis `BasicNatalReadingPlan`.
2. Supprimer tout acces direct du prompt builder Basic au `NatalResult` brut pour choisir de
   nouveaux faits.
3. Filtrer les donnees personnelles: email, user id, place id interne, coordonnees exactes et
   identifiants non necessaires.
4. Transmettre uniquement les `editorial_evidence`, pas les scores internes.
5. Aligner le seed de prompt ou l'assembly Basic pour demander 900 a 1300 mots, six a huit
   sections maximum, ton en `vous`, aucune prediction ferme et aucun conseil prescriptif.
6. Ajouter des tests de payload prouvant que les champs interdits sont absents.
7. Ajouter une garde contre le retour de `chart_json` ou `natal_data` prompt-visible pour le
   natal moderne.
8. Conserver les routes et assemblies Basic/Premium existantes sans regression.

## Hors Perimetre

- Implementer le validateur post-generation.
- Modifier la projection frontend.
- Appeler un provider reel en test unitaire.
- Changer la politique commerciale Basic.
- Ajouter une migration de donnees.

## Sources Obligatoires

- `docs/recherches astro/2026-05-31-review-adversariale-refacto-interpretation-natale-basic.md`
- `_story_briefs/cs-415-reading-plan-basic-natal-inspectable.md`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/domain/llm/runtime/adapter.py`
- `backend/app/services/llm_generation/natal/interpretation_service.py`
- `backend/app/ops/llm/bootstrap/seed_66_20_taxonomy.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-149` - `chart_json` et `natal_data` ne redeviennent pas prompt-visibles pour le natal
    moderne.
  - `RG-152` - les lectures acceptees ne doivent pas exposer `audit_input` ou codes moteur.
  - `RG-154` - les identifiants evidence bruts restent hors public.
  - `RG-156` - le payload Basic conserve la diversite astrologique selectionnee.
- Required regression evidence:
  - `pytest -q backend/tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py`
  - `pytest -q backend/tests/architecture/test_llm_astrology_input_payload_boundaries.py`
  - `pytest -q backend/tests/llm_orchestration/test_theme_astral_provider_payload_builder.py -k "natal or basic"`
  - `rg -n "chart_json|natal_data|email|user_id|place_id|latitude|longitude" backend/app/domain/llm backend/app/services/llm_generation/natal`
- Registry enrichment expected:
  - Ajouter un `RG-XXX` protegeant le handoff Basic par `ReadingPlan` et l'absence de donnees
    personnelles dans le payload.
- Allowed differences:
  - Le payload provider Basic contient moins de donnees brutes et plus de contraintes
    editoriales structurees.

## Criteres D'acceptation

1. Le payload LLM Basic est derive du `ReadingPlan`, pas du `NatalResult` brut.
2. Les donnees personnelles et coordonnees exactes interdites sont absentes.
3. Les scores internes et source paths internes sont absents du payload provider.
4. Les sections, preuves editoriales et syntheses attendues sont presentes.
5. Les contraintes de style et disclaimers sont transmis.
6. Le prompt ne peut pas demander une section interdite par le plan.
7. Les tests echouent si `chart_json` ou `natal_data` redeviennent prompt-visibles.

## Commandes De Validation Minimales

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/llm_orchestration/test_basic_natal_prompt_payload_builder.py --tb=short
python -B -m pytest -q tests/architecture/test_llm_astrology_input_payload_boundaries.py --tb=short
python -B -m pytest -q tests/llm_orchestration/test_theme_astral_provider_payload_builder.py -k "natal or basic" --tb=short
```

## Dependances

- CS-410.
- CS-401.

## Risques

Le risque principal est de laisser deux chemins concurrents: un prompt moderne par plan et un
ancien prompt qui reparcourt le theme. La story doit faire echouer les tests si le chemin Basic
complete contourne le `ReadingPlan`.
