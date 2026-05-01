# Implementation Plan

## Findings

- `backend/app/prediction/llm_narrator.py` owns both useful dataclasses and the deprecated executable runtime.
- Canonical gateway narration already exists in `backend/app/services/llm_generation/horoscope_daily/narration_service.py`.
- `backend/app/domain/llm/prompting/narrator_contract.py` already exists for narrative schema ownership and is the smallest canonical destination for dataclasses.
- Tests already prove nominal adapter routing, but some still import the contract from the legacy module.

## Proposed changes

- Move `NarratorAdvice` and `NarratorResult` dataclasses into `narrator_contract.py`.
- Update app and test imports to use `app.domain.llm.prompting.narrator_contract`.
- Delete `backend/app/prediction/llm_narrator.py`.
- Delete obsolete direct narrator unit tests.
- Harden `test_llm_narrator_deprecation_guard.py` to check app and test sources for forbidden class/import/provider symbols.

## Tests to update

- `backend/tests/llm_orchestration/test_narrator_migration.py`
- `backend/tests/unit/prediction/test_llm_narrator_deprecation_guard.py`
- Tests under `backend/app/tests` importing `NarratorResult`.

## No Legacy stance

The old module is deleted, not repointed. No compatibility import or alias is introduced.

## Rollback strategy

Revert only this story's import migration, dataclass move, guard change, and file deletion if validation reveals an external active dependency.
