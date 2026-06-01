# CS-430 - Basic Full Reading Runtime With Fake Provider

<!-- Commentaire global: ce brief cadre le premier runtime Basic Big Bang sans provider live. -->

## Resume

Implementer le flux `theme_natal.reading.basic_full_reading.v1` avec fake provider deterministe,
afin de valider le contrat produit, les slots, les runs, les schemas et la projection publique sans
dependre du provider reel.

## Perimetre Inclus

1. Brancher `generate_full` Basic vers le contrat `basic_full_reading`.
2. Construire le payload prompt-visible Basic depuis les donnees existantes.
3. Utiliser un fake provider qui retourne un JSON strict representatif.
4. Parser, valider, projeter et persister:
   - run LLM technique;
   - public reading acceptee.
5. Tester l'idempotence et les statuts slot.
6. Prouver qu'aucun ancien use case natal n'est appele.
7. Le fake provider doit couvrir plusieurs modes de sortie:
   - reponse valide;
   - JSON invalide;
   - champ inconnu;
   - source vide;
   - fait astrologique invente;
   - fuite technique;
   - phrase mecanique interdite;
   - section trop courte.
8. Fournir une Free preview minimale/fake/contractuelle si necessaire aux tests de parcours, sans
   passer par `natal_long_free` generatif legacy.

## Hors Perimetre

- Provider OpenAI reel.
- Prompt editorial final live.
- Frontend cutover.
- Suppression physique legacy.
- Premium et Free runtime complet.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md`
- `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md`
- `_story_briefs/cs-429-theme-natal-generation-contracts-strict-schemas.md`
- `backend/app/domain/astrology/interpretation/basic_natal_reading_plan.py`
- `backend/app/domain/astrology/reading/basic_natal_contracts.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-150` - rejets non publics.
  - `RG-152` - pas de fuites techniques publiques.
  - `RG-155` - pas de padding/sources vides.
  - `RG-157` - quota apres acceptance.
  - `RG-164` - Basic via `BasicNatalReadingPlan`.
  - `RG-165` - payload Basic prive.
  - `RG-166` - validation Basic.
  - `RG-167` - Basic complete persiste et reutilise moteur Basic.
  - `RG-168` - contrat public Basic strict.
  - `RG-169` - qualite redactionnelle Basic.
- Required regression evidence:
  - Tests integration fake provider.
  - Tests no legacy call.
  - Tests public accepted-only.
- Allowed differences:
  - Nouveau runtime non live provider pour Basic.

## Criteres D'acceptation

1. `basic + generate_full` produit une lecture publique acceptee via fake provider.
2. Un run LLM est persiste avec contrat, hash, schema et data hash.
3. Le public payload ne contient pas le raw provider response.
4. Une reponse fake invalide est rejetee et absente des routes publiques.
5. Aucune branche `natal_interpretation` ou `natal_interpretation_short` n'est appelee.
6. Le quota est consomme seulement apres acceptation.
7. Chaque mode invalide du fake provider est couvert par au moins un test.
8. La Free preview utilisee pour les tests de parcours ne passe pas par `natal_long_free` generateur.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration -k "basic_full_reading or fake_provider or theme_natal" --tb=short
```

Scans:

```powershell
rg -n "natal_interpretation_short|natal_long_free|natal_interpretation" backend/app/services backend/tests/integration
rg -n "basic_full_reading|fake_provider|ThemeNatalReadingSlot|LlmGenerationRun|free_preview" backend/app backend/tests
```

## Dependances

- CS-427.
- CS-428.
- CS-429.

## Risques

Le risque est de tester uniquement des composants unitaires sans prouver un flux applicatif. Cette
story exige un chemin integration complet mais sans provider live.
