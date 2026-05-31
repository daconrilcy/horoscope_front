# CS-421 Scan Classification

<!-- Commentaire global: ce fichier classe les hits de scans CS-421 apres la verification d'alignement code-vs-brief. -->

Date: 2026-06-01

## Mechanical Phrases

Command:

```powershell
rg -n "cette lecture s'appuie uniquement|Ce repere retient|avec une confiance editoriale controlee|Luminaire: moon|Position planetaire:|north node|south node" backend/app backend/tests
```

Classification: PASS.

- `backend/app/domain/llm/runtime/theme_astral_provider_payload_builder.py`: provider denylist constants only.
- `backend/app/services/llm_generation/natal/narrative_natal_reading_validator.py`: validator regex denylist only.
- `backend/tests/unit/test_basic_natal_narrative_validator.py`: negative tests and fallback absence assertion only.

## Unaccented Public Forms

Command:

```powershell
rg -n "\b(Synthese|theme|themes|repere|planetaire|a integrer)\b" backend/app/domain/astrology/interpretation backend/app/domain/llm/runtime backend/app/services/llm_generation/natal backend/tests
```

Classification: PASS with expected non-public hits.

- Runtime/public CS-421 strings were corrected to accented French forms for `repère`, `thème`, `thèmes`, `synthèse`, `prédiction`, and related visible prose.
- Remaining CS-421 hits are denylist constants, validator regexes, test helper names, field names such as `theme`/`themes`, docstrings, or broader pre-existing runtime/test terminology outside public prose.
- Snapshot check over `basic-payload-after.json` and `basic-public-contract-after.json` leaves only contract keys `theme`/`themes` and denylist entries under `forbidden_template_phrases`.

## Technical Markers

Command:

```powershell
rg -n "ranking_score|condition_axis|score_profile|weighted_score|prompt_hint|audit_input|chart_json|natal_data" backend/app/domain/astrology/reading backend/app/domain/llm/runtime backend/app/services/llm_generation/natal
```

Classification: PASS.

- `basic_natal_contracts.py`: forbidden public key guard.
- `narrative_natal_reading_validator.py`: technical leak and Basic denylist regexes.
- `interpretation_service.py`, `adapter.py`, `gateway.py`, and runtime contracts: existing private runtime carriers outside the public Basic payload.

## Local Astrology Reference Tables

Command:

```powershell
rg -n "SIGN_NAMES_FR|SIGN_LABELS|PLANET_LABELS|NODE_LABELS|ASPECT_LABELS|\bSIGNS\s*=\s*\[" backend/app/domain/astrology backend/app/domain/llm/runtime backend/app/services/llm_generation/natal
```

Classification: PASS.

- No scoped hits. No competing local astrology label/reference table was introduced for CS-421.
