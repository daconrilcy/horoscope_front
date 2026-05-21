<!-- Audit initial CS-204 hayz/rejoicing. -->

# Hayz Rejoicing Audit Before

- Hayz existed as an `advanced_conditions` condition but did not expose its
  component facts in a stable public contract.
- Rejoicing existed through `accidental_breakdown` entries with
  `dignity_type_code=planetary_joy`.
- The frontend could only show dispersed technical breakdowns.
- The public payload lacked a dedicated `traditional_conditions` block.
- The base brief gap also required sect-aware triplicity day/night golden
  evidence, closed through G13/G14.

## Baseline Questions

- Where is hayz currently detected? `AdvancedConditionEngine` delegates hayz
  detection to `HayzCalculator` under `advanced_conditions`.
- Where is rejoicing currently detected? `AccidentalDignityCalculator` emits
  `AccidentalDignityMatch(dignity_type_code="planetary_joy")`.
- Where is hayz exposed in JSON today? Only as a generic
  `advanced_conditions` item.
- Where is rejoicing exposed in JSON today? Only inside
  `dignities.planets[*].accidental_breakdown`.
- Which facts are available to explain hayz? `PlanetSectCondition`,
  chart-level sect, runtime horizon rules and runtime sign polarity.
- Which facts are available to explain rejoicing? The current house from natal
  positions and the runtime/breakdown `house_code` for `planetary_joy`.
- Can rejoicing house be sourced from runtime? Yes when a runtime
  `planetary_joy` rule exists for the planet; otherwise `null` is documented.
- Can planet horizon position be sourced without local constants? Yes, by
  resolving the planet house through runtime `above_horizon` /
  `below_horizon` accidental rules.
