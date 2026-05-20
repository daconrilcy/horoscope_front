# CS-198 No Legacy / DRY Guardrails

## Interdits

- Pas de constantes locales `DIURNAL_PLANETS`, `NOCTURNAL_PLANETS`,
  `COMMON_PLANETS` ou `NEUTRAL_PLANETS`.
- Pas de recalcul de secte globale hors `SectCalculator`.
- Pas de calculateur importe par `json_builder.py`.
- Pas de champ public `sect_code`, `planet_sect_code`, `sect_legacy`,
  `planet_sect_legacy` ou `legacy_sect`.
- Pas de fallback silencieux pour les planetes sans profil runtime.

## Evidence attendue

- Le calculateur lit `dignity_reference.accidental_rules`.
- Les planetes sans regle `in_sect` runtime retournent `unknown`.
- Les scans de garde sont consignes dans
  `evidence/planet-sect-validation.md`.
