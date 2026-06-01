# CS-432 - Public API Cutover To Product Actions

<!-- Commentaire global: ce brief cadre la bascule API publique vers les actions produit theme natal. -->

## Resume

Basculer l'API publique de generation natale vers des actions produit backend. Les endpoints publics
ne doivent plus accepter `use_case`, `use_case_level`, `variant_code`, `plan` ou `forceRefresh`.

## Perimetre Inclus

1. Ajouter ou remplacer l'endpoint public cible, par exemple `POST /v1/theme-natal/readings`.
2. Recevoir:
   - `chart_id`;
   - `action`;
   - `persona_profile_id`;
   - `locale`;
   - `client_request_id`.
3. Utiliser `ThemeNatalReadingProductContract`.
4. Utiliser slots/runs pour reponse publique.
5. Renvoyer uniquement public payload accepted ou etat controle.
6. Ajouter compat readonly si necessaire pour anciennes lectures, sans generation legacy.
7. Mettre a jour OpenAPI/tests API.
8. Neutraliser immediatement l'ancien endpoint generateur:
   - `POST /v1/natal/interpretation` ne peut plus declencher de generation legacy;
   - il retourne `410 Gone` / deprecated, ou delegue strictement vers le nouveau command service
     produit, ou reste limite a une compatibilite readonly sans appel provider.
9. Refuser explicitement les champs legacy dans le body au lieu de les ignorer silencieusement.

## Hors Perimetre

- Frontend cutover complet.
- Suppression physique finale legacy.
- Provider live QA.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md`
- `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md`
- `_story_briefs/cs-430-basic-full-reading-runtime-fake-provider.md`
- `backend/app/api/v1/routers/public/natal_interpretation.py`
- `backend/app/services/api_contracts/public/natal_interpretation.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-002` - routeurs adapteurs.
  - `RG-004` - erreurs API centralisees.
  - `RG-005` - pas de logique metier dans routes.
  - `RG-006` - frontiere API stricte.
  - `RG-150` - rejets non publics.
  - `RG-157` - quota transactionnel.
  - `RG-170` - rendu Basic deduplique sources/mentions si touche.
- Required regression evidence:
- Tests API action produit.
- Tests 422 sur champs legacy.
- Test ancien endpoint non generateur.
- OpenAPI diff filtre.
- Scan DTO publics legacy.
- Allowed differences:
  - Nouveau contrat API produit.
  - Ancien endpoint peut devenir readonly/deprecated si generation legacy impossible.

## Criteres D'acceptation

1. L'API produit n'accepte pas `use_case_level`, `variant_code`, `plan` ni `forceRefresh`.
2. `generate_full` Basic passe par `basic_full_reading`.
3. `preview` Basic ne genere pas de short.
4. Les routes publiques ne retournent que les slots accepted.
5. Un run rejete retourne un etat controle, pas un payload provider.
6. Les erreurs sont centralisees.
7. L'OpenAPI documente les actions produit.
8. L'ancien `POST /v1/natal/interpretation` ne peut plus generer via legacy des cette story.
9. `POST /v1/theme-natal/readings` avec `use_case_level`, `variant_code`, `plan`, `forceRefresh`
   ou `use_case` retourne une erreur de validation explicite, par exemple 422.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/integration -k "theme_natal and api" --tb=short
```

Scans:

```powershell
rg -n "use_case_level|variant_code|forceRefresh|plan" backend/app/services/api_contracts backend/app/api/v1/routers/public
rg -n "410|Gone|deprecated|readonly|client_request_id" backend/app/api/v1/routers/public backend/tests
rg -n "POST /v1/theme-natal/readings|ThemeNatalReadingAction|generate_full" backend/app backend/tests
```

## Dependances

- CS-427.
- CS-428.
- CS-430.

## Risques

Le risque est de conserver deux endpoints generateurs. Cette story doit rendre impossible le choix
public entre ancien et nouveau runtime.
