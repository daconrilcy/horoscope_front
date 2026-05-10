# CS-130 - Validation plan

Commands run from `frontend/`:

```powershell
npm run test -- design-system page-architecture layout
npm run test -- AppShell visual-smoke
npm run test -- AstrologersPage AstrologerProfilePage DailyHoroscopePage NatalChartPage SubscriptionGuidePage ConsultationResultPage
rg -n -g "*.css" -- "max-width:\s*(900px|1100px|1200px|none\s*!important)|--layout-max-width|app-bg-container:has|overflow-x:\s*hidden" src/pages src/layouts src/styles
rg -n -g "*.css" -g "*.tsx" -- "layout-admin-max-width|app-bg-container--admin|admin-container" src/layouts src/styles src/pages/admin
npm run lint
npm run test
```

Python story validation:

```powershell
.\.venv\Scripts\Activate.ps1
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py _condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/00-story.md
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict _condamad/stories/CS-130-uniformiser-largeur-corps-central-frontend/00-story.md
```

E2E:
- `npm run test:e2e` not required for this CSS ownership story unless local browser validation finds route/runtime breakage.
