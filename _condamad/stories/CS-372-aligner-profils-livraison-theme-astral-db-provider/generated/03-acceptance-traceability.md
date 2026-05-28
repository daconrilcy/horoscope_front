# Acceptance Traceability

| AC | Requirement | Code evidence | Validation evidence | Status |
|---|---|---|---|---|
| AC1 | Persisted active depths are canonical. | `THEME_ASTRAL_DELIVERY_PROFILES` exposes `essential`, `expanded`, `complete`; seed publishes those plans. | Targeted persistence pytest PASS; full backend pytest PASS; `depths-after.txt`. | PASS |
| AC2 | Provider depths match persisted depths. | Provider test asserts payload depths equal `set(THEME_ASTRAL_DELIVERY_PROFILES)`. | Provider pytest PASS. | PASS |
| AC3 | Seed publishes one assembly per depth. | Seed iterates canonical constants and idempotence test expects three active assemblies. | Persistence pytest PASS. | PASS |
| AC4 | Active resolution accepts canonical depths. | Active resolver still accepts only keys from canonical constants; test loops all three depths. | Persistence pytest PASS. | PASS |
| AC5 | Active `deep` is not published after seed. | Seed archives published assemblies whose plan is outside canonical constants; test creates and archives stale `deep`. | Runtime `rg deep` on constants/seed returns no matches; persistence pytest PASS. | PASS |
| AC6 | Provider payloads do not expose commercial labels. | Provider payload privacy tests preserved and strengthened by canonical-depth comparison. | Provider pytest PASS; provider JSON value scan returns no matches. | PASS |
| AC7 | Documentation matches canonical depths. | Prompt-generation doc names `essential`, `expanded`, `complete` as DB/provider canonical set. | Scoped docs/examples scan captured in `depths-after.txt`. | PASS |
| AC8 | Examples match canonical depths. | Structure comparison notes canonical depths and no active `deep`; provider examples already emit `essential`, `expanded`, `complete`. | Provider pytest PASS; provider JSON scans PASS. | PASS |
| AC9 | Delivery report matches canonical depths. | CS-361..CS-371 report has CS-372 follow-up alignment note for canonical DB/provider depths. | Delivery report scan captured in `depths-after.txt`. | PASS |
| AC10 | Story evidence artifacts are persisted. | `evidence/depths-before.txt`, `depths-after.txt`, `deep-consumption-audit.md`, `validation.txt` and this traceability were written. | Capsule validation PASS. | PASS |

Status values: `PASS`, `PASS_WITH_LIMITATIONS`, `FAIL`, `BLOCKED`.
