<!-- Baseline initial des compatibilites runtime frontend restantes. -->

# CS-080 - Baseline before

Commande de baseline:

```powershell
Push-Location frontend
$legacyPattern = "Deprecated:|backwards compatibility|backward compatibility|legacy fallback|Legacy codes|aspectLegacy|compatibility"
rg -n $legacyPattern src/pages/ChatPage.tsx src/utils/dailySummaryHelper.ts src/i18n/predictions.ts src/components/DailyInsightsSection.tsx src/components/NatalInterpretation.tsx
Pop-Location
```

## Surfaces E-009

| Item | Type | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---|---|---|---|---|---|---|
| `ChatPage.tsx` `astrologerId` URL param | runtime payload | historical-facade | chat redirect/get-or-create path | `personaId` | delete | `ChatPage.tsx` contained deprecated comment and `searchParams.get("astrologerId")` | old URL param no longer accepted silently |
| `dailySummaryHelper.ts` `summary.overall_summary` | runtime payload | historical-facade | dashboard/daily summary helper | `daily_synthesis` then `day_climate.summary` | delete | helper returned `prediction.summary.overall_summary` | old summary field no longer displayed |
| `predictions.ts` old category/note/driver codes | i18n mapping | historical-facade | prediction label helper | canonical code dictionaries | delete | `Legacy codes` block and legacy category/note entries present | old labels no longer localized |
| `DailyInsightsSection.tsx` compatibility wording | component export evidence | historical-facade | internal component imports | named `DailyInsightsSection` export | delete | comment claimed a default-export compatibility purpose, while repository inspection showed no active default export facade | no default export compatibility promise remains |
| `predictionI18n.ts` old driver event types | runtime mapper | historical-facade | turning point driver labels | `aspect_*`, `moon_sign_ingress`, `asc_sign_change`, `planetary_hour_change` | delete | `humanizePredictionDriverLabel` accepted `exact`, `enter_orb`, `exit_orb` | old driver codes no longer humanized |
| `NatalInterpretation.tsx` `aspectLegacy` parser | runtime parser | historical-facade | natal evidence formatter/category | `ASPECT_*` canonical IDs | delete | `aspectLegacy` branch parsed old IDs | old aspect IDs no longer categorized as major aspects |

No external-active consumer was found in repository scans. The story decision
therefore applies: all five surfaces are deleted rather than allowlisted.
