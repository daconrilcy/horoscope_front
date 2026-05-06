<!-- Audit final d'extinction des compatibilites runtime frontend restantes. -->

# CS-080 - Evidence after

## Extinction audit

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `ChatPage.tsx` `astrologerId` URL param | runtime payload | historical-facade | chat redirect/get-or-create path | `personaId` | delete | `rg -n "Deprecated:|backwards compatibility" src/pages/ChatPage.tsx` zero hit; `rg -n "astrologerId" src/pages/ChatPage.tsx` zero hit | callers must use `personaId` |
| `dailySummaryHelper.ts` `summary.overall_summary` | runtime payload | historical-facade | daily summary helper | `daily_synthesis`, then `day_climate.summary`, then empty string | delete | `rg -n "legacy fallback|overall_summary" src/utils/dailySummaryHelper.ts` zero hit; `dailySummaryHelper.test.ts` covers canonical priority | old summary field no longer displayed |
| `predictions.ts` old category/note/driver codes | i18n mapping | historical-facade | prediction labels | canonical dictionaries | delete | `rg -n "Legacy codes|compatibility|legacy" src/i18n/predictions.ts` zero hit | old codes render as raw unknown codes |
| `DailyInsightsSection.tsx` compatibility wording | component export evidence | historical-facade | internal imports | named export | delete | `rg -n "backward compatibility|export default" src/components/DailyInsightsSection.tsx` zero hit; no active default export facade existed in the inspected diff | no default export compatibility promise remains |
| `NatalInterpretation.tsx` `aspectLegacy` parser | runtime parser | historical-facade | natal evidence formatter/category | `ASPECT_*` IDs | delete | `rg -n "aspectLegacy|legacy|compatibility" src/components/NatalInterpretation.tsx` zero hit | old aspect IDs are formatted generically |
| `predictionI18n.ts` old driver event types | runtime mapper | historical-facade | turning point driver labels | `aspect_*`, `moon_sign_ingress`, `asc_sign_change`, `planetary_hour_change` | delete | scan for `eventType === "exact"`, `enter_orb`, `exit_orb`, `generic_event` in runtime/i18n/test targets is zero hit | old driver codes are no longer humanized |

## Global scan evidence

```powershell
Push-Location frontend
$legacyPattern = "Deprecated:|backwards compatibility|backward compatibility|legacy fallback|Legacy codes|aspectLegacy|compatibility"
rg -n $legacyPattern src
rg -n "astrologerId" src/pages/ChatPage.tsx
rg -n "overall_summary" src
rg -n "aspectLegacy" src/components/NatalInterpretation.tsx
Pop-Location
```

Resultat: zero hit.

## Reintroduction guard

`frontend/src/tests/design-system-guards.test.ts` contient le guard
`bloque le retour des surfaces runtime E-009 fermees par CS-080`, qui scanne
les fichiers `.ts`, `.tsx`, `.md` et `.json` sous `frontend/src`, puis verifie
les formes contractuelles supprimees dans leurs fichiers owners.

## Validation

- `npm run test -- ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage design-system` - PASS, 62 tests.
- `npm run test -- ChatPage dailySummaryHelper` - PASS, 25 tests.
- `npm run lint` - PASS.
- Local Vite startup: PASS via subagent, HTTP 200 on `127.0.0.1:5180`, server stopped.

## Limitation marker scan

The final limitation marker scan returns zero hit for limitation, task-marker,
and short-lived-change vocabulary.
