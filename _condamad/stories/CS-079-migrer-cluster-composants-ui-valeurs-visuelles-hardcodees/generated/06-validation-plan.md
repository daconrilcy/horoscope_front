# Validation Plan - CS-079

## Frontend targeted checks

```powershell
Push-Location frontend
npm run test -- design-system theme-tokens css-fallback legacy-style visual-smoke
npm run lint
Pop-Location
```

## Architecture / negative scans

```powershell
Push-Location frontend
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" src/components/ui -g "*.css" -g "*.tsx"
rg -n "font-size:|font-weight:|line-height:|letter-spacing:" src/components/ui -g "*.css" -g "*.tsx"
rg -n "box-shadow:|border-radius:|var\(\s*--[a-zA-Z0-9_-]+\s*," src/components/ui -g "*.css" -g "*.tsx"
rg -n "legacy|Legacy|alias|compat|compatibility|shim|fallback|migration-only" src/components/ui -g "*.css" -g "*.tsx"
rg -n "#(?:fff|ffffff)\b|rgba\(239,\s*68,\s*68,\s*0\.1\)|rgba\(255,\s*255,\s*255,\s*0\.05\)|rgba\(0,\s*0,\s*0,\s*0\.5\)|box-shadow:\s*(?:none|0\s+10px\s+20px\s+rgba\(134,\s*108,\s*208,\s*0\.3\))|border-radius:\s*(?:50%|16px);|font-size:\s*(?:0\.75rem|0\.875rem|1\.25rem);|font-weight:\s*600;|line-height:\s*(?:1|1\.6);|letter-spacing:\s*(?:0\.04em|0\.05em);|var\(--(?:primary|text-[12]|glass(?:-2|-border|-blur)?|error)\)|var\(\s*--space-2\s*,\s*0\.5rem\s*\)" src/components/ui -g "*.css" -g "*.tsx"
Pop-Location
```

## Story quality checks

```powershell
.\.venv\Scripts\Activate.ps1
$story = "_condamad/stories/CS-079-migrer-cluster-composants-ui-valeurs-visuelles-hardcodees/00-story.md"
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_validate.py $story
python -B .agents/skills/condamad-story-writer/scripts/condamad_story_lint.py --strict $story
```

## Rule for skipped commands

If a command cannot be run, record the exact command, reason, risk, and
compensating evidence.
