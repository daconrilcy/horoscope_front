# Traditional Advanced Scan Results

## Commands

| Scan | Command | Result | Classification |
|---|---|---|---|
| Doctrine constants | `rg -n $doctrine backend/app frontend -g "*.py" -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"` | exit 1, zero hits | PASS: no local doctrine constants in audited non-owner surfaces |
| Legacy aliases | `rg -n $legacy backend/app backend/tests frontend -g "*.py" -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"` | exit 0, classified hits | PASS: hits are runtime field names, canonical owner code, or targeted tests/fixtures |
| Calculator leakage | `rg -n $calculators backend/app/services/chart frontend backend/app/infra/db/repositories -g "*.py" -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"` | exit 1, zero hits | PASS: no forbidden calculator imports in projection/frontend/persistence repositories |
| Frontend derivation | `rg -n $frontendDerivation frontend -g "*.ts" -g "*.tsx" -g "*.js" -g "*.jsx"` | exit 1, zero hits | PASS: no frontend derivation from planet code, sect, sun house, planet house, or house comparisons |

## Legacy Hit Classification

| File | Lines | Hit | Owner / reason | Status |
|---|---:|---|---|---|
| `backend/tests/factories/astrology_runtime_reference_factory.py` | 1046, 1053, 1218, 1367, 1370 | `sect_code`, `chart_sect_code` | Runtime test factory creates canonical reference conditions for dignity/triplicity tests. | allowed |
| `backend/tests/unit/domain/astrology/test_essential_dignity_calculator.py` | 188 | `ruler.sect_code` | Test inspects runtime triplicity ruler data, not an application fallback. | allowed |
| `backend/tests/unit/domain/astrology/fixtures/triplicity_seed_cases.py` | 46 | `sect_code` | Fixture field mirrors runtime reference schema for triplicity cases. | allowed |
| `backend/tests/unit/domain/astrology/fixtures/traditional_golden_cases.py` | 86 | `ruler.sect_code` | Golden fixture reads runtime reference ruler metadata. | allowed |
| `backend/tests/unit/domain/astrology/test_triplicity_golden_cases.py` | 44, 125, 137, 165, 188, 263, 298, 304 | `sect_code` | Triplicity guard verifies runtime sect-aware ruler selection. | allowed |
| `backend/tests/unit/domain/astrology/test_hayz_calculator.py` | 115 | `chart_sect_code` | Hayz test uses canonical condition key from runtime-style rule conditions. | allowed |
| `backend/app/infra/db/repositories/astrology_runtime_reference_repository.py` | 771 | `sect_code` | Repository maps canonical DB/runtime reference field. | allowed |
| `backend/app/infra/db/repositories/astrology_runtime_reference_mapper.py` | 445 | `sect_code` | Mapper serializes canonical runtime reference field. | allowed |
| `backend/app/tests/unit/test_astrology_runtime_reference_repository.py` | 169 | `chart_sect_code` | Repository test asserts canonical runtime condition data. | allowed |
| `backend/app/domain/astrology/dignities/accidental_dignity_calculator.py` | 107, 108, 114 | `chart_sect_code` | Canonical dignity owner evaluates runtime accidental dignity conditions. | allowed |
| `backend/app/domain/astrology/dignities/planet_sect_condition_calculator.py` | 49, 54, 55, 57, 66, 68, 70, 74, 77 | `chart_sect_code`, `in_sect_codes` | Canonical planet sect condition owner derives per-planet condition from runtime conditions. | allowed |
| `backend/app/domain/astrology/dignities/essential_dignity_calculator.py` | 58 | `ruler.sect_code` | Canonical essential dignity owner consumes runtime triplicity ruler sect. | allowed |
| `backend/app/domain/astrology/runtime/runtime_reference.py` | 604 | `sect_code` | Runtime reference contract field. | allowed |

## Blockers

Aucun blocker de scan identifie.

