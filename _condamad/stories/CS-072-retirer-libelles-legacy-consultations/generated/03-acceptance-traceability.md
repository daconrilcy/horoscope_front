# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | Before artifact records every `(Legacy)` consultation label. | `consultation-labels-before.md` added. | Baseline table records all 12 labels. | PASS |
| AC2 | Consultation labels remove legacy vocabulary. | `consultations.ts` labels updated without key changes. | `rg -n "legacy\|Legacy" src/i18n/consultations.ts` zero hit. | PASS |
| AC3 | Consultation identifiers remain stable. | Keys `type_dating`, `type_pro`, `type_event`, `type_free` unchanged. | Vitest `ConsultationMigration consultationStore` PASS. | PASS |
| AC4 | Tests assert final canonical labels. | `ConsultationMigration.test.tsx` adds canonical label assertions and source guard. | Vitest `ConsultationMigration` PASS. | PASS |
| AC5 | Design-system legacy policy remains green. | No design-system exception added. | Vitest `design-system legacy-style` PASS. | PASS |
| AC6 | Final evidence has no deferred decision. | `10-final-evidence.md` and `11-code-review.md` completed. | Story validate/lint PASS. | PASS |

Status used: `PASS`.
