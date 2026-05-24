# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Production astronomy mode is proven. | `backend/app/domain/astrology/runtime/astronomical_proof.py` defines `PRODUCTION_ASTRONOMY_MODE="swisseph"` and builds the proof manifest from `pyswisseph`. | `python -B -m pytest -q tests\unit\domain\astrology\test_astronomical_proof.py` PASS; full `python -B -m pytest -q` PASS. | PASS |
| AC2 | Simplified public temporal use is blocked. | `build_public_temporal_gate` keeps public temporal authorization false until CS-250 is `done`; architecture guard scans for public temporal simplified qualification. | `python -B -m pytest -q tests\architecture\test_temporal_public_runtime_gate.py` PASS; targeted `rg` scan recorded in `evidence/validation.txt`. | PASS |
| AC3 | Sensitive golden cases pass. | `SENSITIVE_GOLDEN_CASES` covers Paris, DST ambiguous, DST after jump, high latitude, Lahiri, topocentric, whole sign, and Placidus edge cases. | `python -B -m pytest -q tests\unit\domain\astrology\test_astronomical_golden_cases.py` PASS. | PASS |
| AC4 | Tolerance policy is canonical. | `PRODUCTION_TOLERANCE` is the single owner reused by every sensitive case; architecture threshold allowlist names this owner. | `test_tolerance_policy_is_single_canonical_owner` PASS; `test_domain_code_does_not_add_local_magic_thresholds` PASS. | PASS |
| AC5 | Ephemeris trace is persisted. | `build_ephemeris_trace` records `swisseph_version`, bootstrap path metadata when present, and a reproducibility note. | `test_ephemeris_trace_contains_reproducibility_metadata` PASS; `_condamad/.../evidence/astronomical-proof.json` generated. | PASS |
| AC6 | CS-253 gate stays closed until proof closure. | `CS253_GATE_MARKER` and `build_public_temporal_gate` model the blocked state before CS-250 is `done` and `proof-closed` after review closure. | `test_cs253_public_gate_stays_blocked_until_cs250_done` PASS; `_condamad/.../evidence/cs-253-gate.md` persisted. | PASS |
| AC7 | Story evidence artifacts exist. | Evidence folder contains `validation.txt`, `astronomical-proof.json`, and `cs-253-gate.md`. | Python path existence check PASS; capsule validation PASS. | PASS |

Status values: `PENDING`, `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
