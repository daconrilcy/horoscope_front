# Daily V3 Migration Gates (Story 42.17)

This document defines the Go/No-Go criteria for migrating from Engine V2 to Engine V3.

## 1. Quality Gates (Product)

| Criterion | Metric | Threshold | Status |
|-----------|--------|-----------|--------|
| **Pivot Sobriety** | Ratio V3/V2 Pivots on calm days | < 0.5 | ✅ |
| **Window Precision** | % actionable windows with confidence > 0.7 | > 80% | ✅ |
| **Scoring Expressivity** | Dispersion (StdDev) of V3 scores vs V2 | > V2 StdDev | ✅ |
| **Flat Day Integrity** | No decision windows on days with Intensity < 3.0 | 100% | ✅ |

## 2. Technical Gates (Performance & Stability)

| Criterion | Metric | Threshold | Status |
|-----------|--------|-----------|--------|
| **Runtime Budget** | Max duration for 96 steps (V3 only) | < 100ms | ✅ |
| **Dual Mode Overhead** | Additional cost of DUAL mode vs V2 | < 150ms | ✅ |
| **Persistence Integrity** | V2 compatibility (null handling) | 100% pass | ✅ |
| **Memory Stability** | Peak memory usage vs V2 | < +20% | ✅ |

## 3. Migration Strategy

1. **Phase 1: Shadow Mode (Current)**
   - Engine runs in `DUAL` mode in production (if enabled by flag).
   - Only V2 results are shown to users.
   - V3 Evidence Pack is persisted for audit.

2. **Phase 2: Canary (Planned)**
   - Set `DAILY_ENGINE_MODE=v3` for internal/beta users.
   - Compare feedback and evidence.

3. **Phase 3: Full Switch**
   - Set `DAILY_ENGINE_MODE=v3` for all users.
   - Maintain V2 path for fallback (via DUAL mode if needed).

## 4. Rollback Plan

- **Trigger:** Regression in pivot quality or runtime > 200ms.
- **Action:** Set `DAILY_ENGINE_MODE=v2` in environment variables.
- **Data:** Persistence is designed to be bi-compatible; no data migration needed for rollback.
