# CS-383 - Corriger Findings Review Adversariale Generation Theme Natal

<!-- Commentaire global: ce brief cadre la correction des findings issus de la review adversariale generation natale. -->

## Resume

Corriger les findings actionnables identifies par CS-382, puis relancer les validations jusqu'a obtenir une cloture propre de la generation de theme natal et de la non-regression prompt.

## Contexte

CS-382 doit produire une review adversariale post-corrections. Cette story evite que les findings restent documentes sans correction, ou que des corrections partielles referment le crash tout en laissant une regression sur `traditional_conditions` ou `theme_astral_llm_input_v1`.

## Objectif

Atteindre un etat ou:

- aucun finding `Critical`, `High` ou `Medium` actionnable ne reste ouvert;
- les findings `Low` sont corriges ou explicitement acceptes avec justification;
- le `POST /v1/users/me/natal-chart` est valide pour un theme avec heure connue;
- `traditional_conditions` est complet quand il doit etre calculable;
- le front ne crashe pas et n'invente pas de faits;
- l'enrichissement prompt-visible reste intact.

## Perimetre inclus

1. Lire le rapport CS-382.
2. Classer chaque finding: corriger, accepter, faux positif, hors perimetre.
3. Corriger le code, les tests et la documentation impactes.
4. Ajouter un test de regression pour chaque bug corrige.
5. Relancer les validations backend, frontend et scans pertinents.
6. Relancer CS-382 ou une review ciblee equivalente sur les fichiers modifies.
7. Produire une note de cloture.

## Hors perimetre

- Corriger des sujets non relies aux findings CS-382.
- Appeler un provider LLM reel sans opt-in explicite.
- Changer le contrat produit de `traditional_conditions` sans nouvelle decision.
- Refaire les prompts ou le wording redactionnel.
- Masquer un finding par modification du rapport CS-382.

## Sources obligatoires

- `_condamad/reports/cs-382-review-adversariale-generation-theme-natal.md`
- Fichiers modifies par CS-379, CS-380, CS-381 et CS-383
- Tests ajoutes ou modifies par CS-379, CS-380 et CS-381
- `backend/app/services/chart/json_builder.py`
- `backend/app/domain/astrology/advanced_conditions/**`
- `backend/app/domain/astrology/interpretation/llm_astrology_input_v1.py`
- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`
- `frontend/src/features/natal-chart/NatalExpertPanel.tsx`
- `frontend/src/api/natal-chart/index.ts`

## Livrable attendu

Creer:

```text
_condamad/reports/cs-383-corrections-findings-generation-theme-natal.md
```

Le rapport doit contenir:

1. Liste des findings CS-382.
2. Decision pour chaque finding.
3. Correction appliquee ou justification d'acceptation.
4. Tests ajoutes ou modifies.
5. Commandes executees.
6. Resultat de re-review.
7. Risques residuels acceptes.

## Criteres d'acceptation

1. Chaque finding CS-382 a une decision tracee.
2. Aucun finding `Critical`, `High` ou `Medium` actionnable ne reste ouvert.
3. Chaque correction est couverte par un test ou une preuve explicite.
4. Le payload `POST /v1/users/me/natal-chart` reste la preuve prioritaire pour le bug initial.
5. `traditional_conditions` reste absent uniquement quand le calcul fiable est impossible.
6. Le front reste tolerant aux payloads partiels sans officialiser un contrat partiel.
7. Les enrichissements `theme_astral_llm_input_v1` restent presents et les anciens carriers ne redeviennent pas source de verite.
8. Une re-review post-correction prouve que les findings corriges ne restent pas ouverts.

## Commandes de validation minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests --tb=short -k "natal_chart or traditional_conditions or theme_astral or llm_astrology_input"
```

Frontend:

```powershell
cd frontend
pnpm lint
pnpm test -- NatalExpertPanel BirthProfilePage natalChartApi
pnpm build
```

Re-review et scans:

```powershell
rg -n "Critical|High|Medium|open|corrections requises|traditional_conditions|chart_json|natal_data" ..\_condamad\reports\cs-382-review-adversariale-generation-theme-natal.md ..\_condamad\reports\cs-383-corrections-findings-generation-theme-natal.md
```

## Risques

Le risque principal est de traiter CS-383 comme une formalite. Cette story ne doit etre terminee que si les findings CS-382 sont vraiment fermes, faux positifs prouves, ou explicitement acceptes avec justification et owner.
