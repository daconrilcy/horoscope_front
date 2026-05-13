# Acceptance Traceability

| AC | Requirement | Expected code impact | Required validation evidence | Status |
|---|---|---|---|---|
| AC1 | `signs` devient `astral_signs` avec 12 signes conservés. | `AstralSignModel`, migration `20260513_0087`, seed stable. | Migration pytest + seed pytest + `schema-before.md` / `schema-after.md`. | PASS |
| AC2 | Les trois taxonomies `astral_*` existent avec les valeurs demandées. | Modèles `AstralElementModel`, `AstralModalityModel`, `AstralPolarityModel` + seed. | Migration pytest + seed pytest. | PASS |
| AC3 | `astral_sign_profiles` contient les 12 profils demandés. | `AstralSignProfileModel` + `_ensure_astral_sign_profiles`. | Seed pytest + `reference-seed-after.md`. | PASS |
| AC4 | Seul `astral_sign_id` est unique dans `astral_sign_profiles`. | Migration et modèle sans unicité sur élément/modalité/polarité. | Test inspectant les contraintes. | PASS |
| AC5 | `sign_rulerships` est renommé en `astral_sign_rulerships`. | Migration, modèle `AstralSignRulershipModel` et repository convergent. | Migration pytest + scans. | PASS |
| AC6 | Les maîtrises utilisent les valeurs obligatoires. | Seed `rulership_type`, `system`, `weight`, `is_primary`. | Seed pytest. | PASS |
| AC7 | Le repository lit les maîtrises sans filtre de version. | `get_sign_rulerships()` sans paramètre de version. | Unit pytest. | PASS |
| AC8 | Aucun shim/vue ne garde les anciens noms. | Anciennes tablenames absentes du runtime actif. | Scans anti-retour. | PASS |
| AC9 | `RG-091`, `RG-092`, `RG-093` restent satisfaits. | Tests et scans de garde. | Guardrails ciblés. | PASS |
