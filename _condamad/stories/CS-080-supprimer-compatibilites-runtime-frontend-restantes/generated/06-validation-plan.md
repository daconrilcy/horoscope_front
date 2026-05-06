# Validation Plan - CS-080

## Frontend targeted checks

```powershell
Push-Location frontend
npm run test -- ConsultationMigration consultationStore TurningPointsEnriched DailyHoroscopePage design-system
npm run test -- ChatPage dailySummaryHelper
npm run lint
Pop-Location
```

## Architecture / negative scans

```powershell
Push-Location frontend
$legacyPattern = "Deprecated:|backwards compatibility|backward compatibility|legacy fallback|Legacy codes|aspectLegacy|compatibility"
rg -n $legacyPattern src
rg -n "astrologerId" src/pages/ChatPage.tsx
rg -n "overall_summary" src
rg -n "aspectLegacy" src/components/NatalInterpretation.tsx
rg -n "eventType\s*===\s*['\"]exact['\"]|^\s*(exact|enter_orb|exit_orb|generic_event):" src/utils/predictionI18n.ts src/i18n/predictions.ts src/tests/predictionI18n.test.ts src/tests/DailyHoroscopePage.test.tsx
rg -n "backward compatibility|export default" src/components/DailyInsightsSection.tsx
rg -n "Legacy codes|compatibility|legacy" src/i18n/predictions.ts
Pop-Location
```

## Story quality checks

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-080-supprimer-compatibilites-runtime-frontend-restantes/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Rule for skipped commands

If a command cannot be run, record the exact command, reason, risk, and
compensating evidence.
