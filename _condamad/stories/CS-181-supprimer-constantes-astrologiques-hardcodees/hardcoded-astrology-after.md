# Hardcoded Astrology After

| Élément | Décision finale | Preuve après | Statut |
|---|---|---|---|
| `_legacy_payload_for_mock_db` | supprimé | scan `_legacy_payload_for_mock_db` dans `backend/app/services/natal` zéro-hit | PASS |
| `sign_rulerships = {...}` service natal | supprimé | scan natal ciblé zéro-hit | PASS |
| fallback `house_axes` service natal | supprimé | scan natal ciblé zéro-hit | PASS |
| fallback `aspect_orb_rules` service natal | supprimé | scan natal ciblé zéro-hit | PASS |
| `EventDetector.ASPECTS_V1` | remplacé par `major_aspect_angles(ctx.prediction_context)` | scan `ASPECTS_V1` zéro-hit dans `backend/app` et `backend/tests` | PASS |
| `EnrichedAstroEventsBuilder.ASPECTS` | remplacé par `major_aspect_angles()` injecté depuis `LoadedPredictionContext` | scan `ASPECTS\s*=` zéro-hit dans runtime prediction | PASS |
| fallback `orb_max=2.0` | supprimé; absence d'orbe runtime lève `PredictionContextError` | scan `orb_max_fallback.*2.0` zéro-hit | PASS |
| `_STAR_DATA` | conservé et classé | `astrology-constant-exceptions.md` ligne exacte | PASS |
| `_ASPECT_TONES` | conservé et classé | `astrology-constant-exceptions.md` ligne exacte | PASS |
| constantes de routage planétaire/hourly | conservées et classées | `astrology-constant-exceptions.md` lignes exactes | PASS |

## Scans après patch

- `rg -n 'sign_rulerships\s*=\s*\{|payload\.setdefault\("sign_rulerships"|payload\["house_axes"\]\s*=|payload\["aspect_orb_rules"\]\s*=' backend/app/services/natal -g '*.py'`: zero hit.
- `rg -n 'ASPECTS_V1|ASPECTS\s*=\s*\{|orb_max_fallback.*2\.0' backend/app/domain/astrology backend/app/domain/prediction -g '*.py'`: zero hit.
- `rg -n 'app\.domain\.prediction|app\.services\.prediction' backend/app/domain/astrology -g '*.py'`: zero hit.
