# No Legacy / DRY Guardrails

## Canonical paths

- `backend/app/tests/unit/test_seed_horoscope_narrator_assembly.py`
- `backend/app/tests/unit/test_guidance_service.py`
- `backend/app/tests/unit/test_consultation_generation_service.py`

## Forbidden active validation commands

- `pytest -q tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py`
- `pytest -q tests/unit/test_guidance_service.py`
- `pytest -q tests/unit/test_consultation_generation_service.py`

## Forbidden implementation shortcuts

- Ne pas creer de copies sous `backend/tests/unit`.
- Ne pas ajouter de wrappers ou alias pour faire passer les anciens chemins.
- Ne pas conserver un ancien chemin comme commande active avec un commentaire.
- Ne pas modifier `backend/pyproject.toml` pour collecter une racine obsolete.

## Required negative evidence

- Scanner les anciens chemins dans `_condamad/stories`.
- Classer chaque hit comme `active_legacy_removed`, `allowed_historical_reference`, `forbidden_example`, `canonical_replacement`, ou `out_of_scope`.
- Prouver que les commandes corrigees sont executables depuis `backend/`.

## Applicable regression guardrails

- `RG-010`: topologie de collecte pytest backend.
- `RG-019`: validation seed assembly horoscope daily.
- `RG-020`: validation guidance/consultation.
- `RG-022`: plans de validation prompt-generation alignes sur des fichiers collectes.

## Review checklist

- Les plans actifs pointent vers `app/tests/unit`.
- Les preuves historiques ne sont pas presentees comme commandes attendues.
- Aucun test n'a ete duplique sous une ancienne racine.
- Les scans restants sont classes dans l'audit.
