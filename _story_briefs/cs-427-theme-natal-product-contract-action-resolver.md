# CS-427 - Theme Natal Product Contract And Action Resolver

<!-- Commentaire global: ce brief cadre le contrat produit de lecture natale qui decide les actions autorisees avant tout appel LLM. -->

## Resume

Introduire le concept `ThemeNatalReadingProductContract` et un resolver d'action produit backend.
Le frontend ne doit plus choisir de niveau LLM, use case, plan ou variant technique; il demande une
action metier comme `preview`, `generate_full`, `regenerate` ou `download`.

## Perimetre Inclus

1. Definir les contrats domaine purs:
   - `ThemeNatalReadingProductContract`;
   - `ThemeNatalReadingAction`;
   - `ThemeNatalReadingKind`;
   - `ThemeNatalOutputVariant`;
   - `ThemeNatalPersonaMode`.
2. Definir les variantes cibles:
   - `free_preview`;
   - `basic_full_reading`;
   - `premium_full_reading`.
3. Implementer un resolver pur qui prend:
   - user;
   - chart;
   - action produit;
   - entitlement frais;
   - locale;
   - persona optionnelle.
4. Retourner une decision:
   - allowed;
   - locked/paywall;
   - existing_reading;
   - generate_with_contract_key;
   - invalid_request.
5. Interdire toute entree frontend technique:
   - `use_case`;
   - `use_case_level`;
   - `variant_code`;
   - `plan`;
   - `forceRefresh`.
6. Ajouter tests de matrice produit.

## Hors Perimetre

- Appel provider.
- Persistence des slots.
- Migration DB.
- Cutover de l'endpoint public.
- Suppression physique legacy.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-426-freeze-inventory-legacy-generation-natal-bigbang.md`
- `backend/app/services/entitlement/natal_chart_long_entitlement_gate.py`
- `backend/app/services/entitlement/effective_entitlement_resolver_service.py`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `frontend/src/api/natal-chart/index.ts`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-002` - routeurs API adapteurs uniquement.
  - `RG-005` - logique metier hors routeurs.
  - `RG-006` - pas d'import API dans services/domain/infra.
  - `RG-149` - la cartographie prompt-generation reste explicite.
  - `RG-157` - quota complete transactionnel.
  - `RG-164` - Basic reste plan-backed.
  - `RG-167` - Basic complete passe par moteur Basic attendu.
- Required regression evidence:
  - Tests unitaires de matrice resolver.
  - Scan zero-hit des DTO publics nouveaux sur `use_case_level|variant_code|forceRefresh`.
- Allowed differences:
  - Nouveaux contrats domaine purs et tests.

## Criteres D'acceptation

1. `free + preview` resout `free_preview`.
2. `free + generate_full` retourne locked/paywall.
3. `basic + preview` ne genere pas de short; retourne preview existante ou action disponible.
4. `basic + generate_full` resout `basic_full_reading`.
5. `premium + generate_full` resout `premium_full_reading`.
6. Persona/style est une dimension separee de `output_variant`.
7. Le resolver ne depend pas du gateway LLM, de SQLAlchemy, de FastAPI ni du frontend.
8. Les entrees techniques legacy sont refusees au niveau contrat.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit -k "theme_natal and product_contract" --tb=short
```

Scans:

```powershell
rg -n "use_case_level|variant_code|forceRefresh" backend/app/services backend/app/domain backend/tests
rg -n "ThemeNatalReadingProductContract|basic_full_reading|premium_full_reading|free_preview" backend/app backend/tests
```

## Dependances

- CS-426 doit fournir la classification initiale.

## Risques

Le risque est de laisser l'API ou le frontend choisir encore une strategie LLM. Cette story place
la souverainete dans un service produit backend testable.
