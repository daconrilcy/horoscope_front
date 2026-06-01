# CS-429 - Theme Natal Generation Contracts And Strict Schemas

<!-- Commentaire global: ce brief cadre les contrats LLM versionnes et schemas JSON stricts du theme natal. -->

## Resume

Definir les contrats de generation LLM cible pour `theme_natal.reading.*` et leurs schemas JSON
stricts. Basic et Premium ne doivent plus partager le meme contrat de sortie.

## Perimetre Inclus

1. Definir les contrats:
   - `theme_natal.reading.free_preview.v1`;
   - `theme_natal.reading.basic_full_reading.v1`;
   - `theme_natal.reading.premium_full_reading.v1`.
2. Definir `engine_profile`, `data_contract`, `prompt_contract`, `output_contract` et
   `persistence_contract`.
3. Definir les schemas raw provider et schemas publics projetes.
4. Interdire `additionalProperties`.
5. Ajouter hash/snapshot contractuel:
   - `generation_contract_key`;
   - `generation_contract_version`;
   - `generation_contract_snapshot_id`;
   - `generation_contract_hash`;
   - `prompt_contract_version`;
   - `output_schema_version`;
   - `data_contract_version`;
   - `engine_profile_version`.
6. Garantir qu'une generation reference un snapshot immuable du contrat resolu, jamais un contrat
   mutable directement.
7. Ajouter tests de coherence contrat/schema/prompt.

Precision schema: `additionalProperties: false` doit etre applique recursivement a tous les objets
imbriques du schema raw provider et du schema public projete.

## Hors Perimetre

- Appel provider reel.
- Persistence slots/runs si CS-428 non livree.
- Cutover API public.
- Suppression legacy physique.

## Sources Obligatoires

- `_condamad/stories/regression-guardrails.md`
- `_condamad/reports/2026-06-01-refonte-big-bang-generation-prompt-reponse-llm.md`
- `_story_briefs/cs-427-theme-natal-product-contract-action-resolver.md`
- `_story_briefs/cs-428-public-reading-slots-llm-generation-runs.md`
- `backend/app/domain/llm/configuration/canonical_use_case_registry.py`
- `backend/app/domain/llm/configuration/theme_astral_contracts.py`
- `backend/app/domain/llm/prompting/schemas.py`
- `backend/app/domain/astrology/reading/basic_natal_contracts.py`

## Regression Guardrails

- Guardrail source: `_condamad/stories/regression-guardrails.md`
- Applicable invariants:
  - `RG-018` - pas de prompt fallback pour famille supportee.
  - `RG-021` - fallback classifie.
  - `RG-149` - cartographie prompt-generation explicite.
  - `RG-150` - rejets non publics.
  - `RG-152` - pas de fuites techniques.
  - `RG-155` - pas de padding semantique.
  - `RG-164` - Basic plan-backed.
  - `RG-165` - payload Basic sans PII/scores/IDs.
  - `RG-168` - contrat public Basic strict.
  - `RG-171` - Basic ne route pas par anciennes cles natal.
- Required regression evidence:
- Tests de schema strict.
- Tests anti-collision Basic/Premium.
- Test snapshot immuable.
- Scans contre `AstroResponse_v3` dans contrat Basic.
- Allowed differences:
  - Nouveaux contrats et schemas cibles.

## Criteres D'acceptation

1. Free, Basic et Premium ont des contrats LLM distincts.
2. Basic ne reference pas `AstroResponse_v3`, `EXIGENCE PREMIUM` ou `natal_interpretation`.
3. Les schemas refusent les champs inconnus.
4. Le public schema est distinct du raw provider schema.
5. Les versions et hashes de contrat sont stockables/auditables.
6. Les contrats declarent explicitement les donnees prompt-visible, validation-only et audit-only.
7. Modifier le registre de contrat apres un run ne modifie pas le snapshot associe au run existant.
8. La stricte interdiction des champs inconnus est recursive sur les objets imbriques.

## Commandes De Validation Minimales

Backend:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
ruff format .
ruff check .
python -B -m pytest -q tests/unit tests/llm_orchestration -k "theme_natal or generation_contract or schema" --tb=short
```

Scans:

```powershell
rg -n "theme_natal\\.reading\\.(free_preview|basic_full_reading|premium_full_reading)\\.v1" backend/app backend/tests
rg -n "generation_contract_snapshot_id|generation_contract_hash|additionalProperties" backend/app backend/tests
rg -n "AstroResponse_v3|EXIGENCE PREMIUM|natal_interpretation" backend/app/domain backend/tests/llm_orchestration
```

## Dependances

- CS-427.
- CS-428 recommandé pour ancrer persistence/audit.

## Risques

Le risque est de renommer les use cases sans separer les contrats. Cette story exige une separation
schema/prompt/contract reelle.
