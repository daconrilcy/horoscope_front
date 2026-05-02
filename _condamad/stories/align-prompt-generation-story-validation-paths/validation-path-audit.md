# Validation Path Audit

## Scope

Audit des chemins de validation prompt-generation obsoletes listes par SC-002.

Canonical replacements:

| Obsolete path | Canonical collected path |
|---|---|
| `tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py` | `app/tests/unit/test_seed_horoscope_narrator_assembly.py` |
| `tests/unit/test_guidance_service.py` | `app/tests/unit/test_guidance_service.py` |
| `tests/unit/test_consultation_generation_service.py` | `app/tests/unit/test_consultation_generation_service.py` |

## Before active references

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `_condamad/stories/converge-horoscope-daily-narration-assembly/00-story.md` AC2 validation | active validation command | dead | story validation plan | `pytest -q app/tests/unit/test_seed_horoscope_narrator_assembly.py` | replace-consumer | Pre-change scan showed `pytest -q tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py`; `backend/tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py` does not exist. | Story validation could fail even though the collected test exists. |
| `_condamad/stories/converge-horoscope-daily-narration-assembly/00-story.md` expected test path | active file reference | dead | story expected files | `backend/app/tests/unit/test_seed_horoscope_narrator_assembly.py` | replace-consumer | Pre-change scan showed `backend/tests/llm_orchestration/test_seed_horoscope_narrator_assembly.py`; canonical file exists. | Reviewer could inspect or run the wrong path. |
| `_condamad/stories/formalize-consultation-guidance-prompt-ownership/00-story.md` guidance validation | active validation command | dead | story acceptance criteria and validation plan | `pytest -q app/tests/unit/test_guidance_service.py` | replace-consumer | Pre-change scan showed `pytest -q tests/unit/test_guidance_service.py`; `backend/tests/unit/test_guidance_service.py` does not exist. | Story validation could fail even though the collected test exists. |
| `_condamad/stories/formalize-consultation-guidance-prompt-ownership/00-story.md` consultation validation | active validation command | dead | story acceptance criteria and validation plan | `pytest -q app/tests/unit/test_consultation_generation_service.py` | replace-consumer | Pre-change scan showed `pytest -q tests/unit/test_consultation_generation_service.py`; `backend/tests/unit/test_consultation_generation_service.py` does not exist. | Story validation could fail even though the collected test exists. |
| `_condamad/stories/regression-guardrails.md` RG-020 | active guard command | dead | shared regression guardrail registry | `pytest -q app/tests/unit/test_guidance_service.py` | replace-consumer | Pre-change scan showed `pytest -q tests/unit/test_guidance_service.py`; canonical file exists under `backend/app/tests/unit`. | Shared guard could instruct future agents to run a non-collected path. |

## After active references

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `_condamad/stories/converge-horoscope-daily-narration-assembly/00-story.md` AC2 validation | active validation command | canonical-active | story validation plan | `pytest -q app/tests/unit/test_seed_horoscope_narrator_assembly.py` | keep | Post-change scan shows the active command now uses `app/tests/unit`. | Low. |
| `_condamad/stories/formalize-consultation-guidance-prompt-ownership/00-story.md` AC2 validation | active validation command | canonical-active | story acceptance criteria and validation plan | `pytest -q app/tests/unit/test_guidance_service.py` | keep | Post-change scan shows the active command now uses `app/tests/unit`. | Low. |
| `_condamad/stories/formalize-consultation-guidance-prompt-ownership/00-story.md` AC3 validation | active validation command | canonical-active | story acceptance criteria and validation plan | `pytest -q app/tests/unit/test_consultation_generation_service.py` | keep | Post-change scan shows the active command now uses `app/tests/unit`. | Low. |
| `_condamad/stories/regression-guardrails.md` RG-020 | active guard command | canonical-active | shared regression guardrail registry | `pytest -q app/tests/unit/test_guidance_service.py` | keep | Post-change scan shows RG-020 now uses `app/tests/unit`. | Low. |

## Historical and forbidden-reference allowlist

| Reference | Classification | Decision | Proof |
|---|---|---|---|
| `_condamad/stories/converge-horoscope-daily-narration-assembly/generated/10-final-evidence.md` old seed command | historical-facade | keep | The row explicitly states the story-listed path did not exist and that the equivalent `app/tests/unit` path was run. |
| `_condamad/stories/align-prompt-generation-story-validation-paths/00-story.md` forbidden command examples | forbidden-example | keep | The story uses these exact strings as forbidden examples and scan inputs, not as active expected commands. |
| `_condamad/stories/align-prompt-generation-story-validation-paths/generated/06-validation-plan.md` scan command | reintroduction-guard | keep | The command scans for obsolete paths to block active reintroduction. |
| `_condamad/stories/align-prompt-generation-story-validation-paths/generated/07-no-legacy-dry-guardrails.md` forbidden command list | forbidden-example | keep | The file lists the commands as forbidden active validation commands. |

## Collection proof

| File | Exists at canonical path | Obsolete path exists | Decision |
|---|---:|---:|---|
| `backend/app/tests/unit/test_seed_horoscope_narrator_assembly.py` | yes | no | use canonical path |
| `backend/app/tests/unit/test_guidance_service.py` | yes | no | use canonical path |
| `backend/app/tests/unit/test_consultation_generation_service.py` | yes | no | use canonical path |

## Guard invariant

Active prompt-generation validation commands must use files collected from `backend/`.
Obsolete paths may remain only as historical failed evidence, forbidden examples,
or deterministic reintroduction scans labelled as such.
