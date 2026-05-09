<!-- Inventaire avant implementation de la taxonomie App CSS pour CS-125. -->

# CS-125 App Prefix Taxonomy Before

## Commands

```powershell
$css = Get-Content -Raw 'frontend\src\App.css'
[regex]::Matches($css, '(--app-([a-zA-Z0-9]+)[a-zA-Z0-9_-]*)\s*:') |
  ForEach-Object { $_.Groups[2].Value } |
  Group-Object |
  Sort-Object Count -Descending

Push-Location frontend
rg -n -- "--app-(person|people|activity|premium|flow|summary|precision|evidence|chat|usage)-" src/App.css
rg -n "app-(page|section|stack|grid|card|panel|state|badge|avatar|modal|actions|list)|precision-badge|evidence-pill|evidence-tags" src -g "*.tsx"
Pop-Location
```

## Declaration Prefix Counts

| Prefix | Count | Initial classification |
|---|---:|---|
| person | 124 | requires final decision |
| activity | 59 | requires final decision |
| summary | 26 | requires final decision |
| flow | 17 | requires final decision |
| premium | 15 | requires final decision |
| precision | 14 | requires final decision; class policy in CS-126 |
| evidence | 13 | requires final decision; class policy in CS-126 |
| modal | 13 | App primitive candidate |
| people | 13 | requires final decision |
| activities | 12 | requires final decision |
| validation | 11 | App flow validation candidate |
| chat | 11 | requires final decision |
| usage | 9 | requires final decision |
| state | 7 | App primitive candidate |
| type | 7 | App flow type candidate |
| drawing | 7 | App flow candidate |
| button | 6 | App primitive candidate |
| form | 6 | App form primitive candidate |
| other | 5 | App flow candidate |
| message | 5 | App messaging candidate |
| nothing | 4 | App state candidate |
| interaction | 4 | App flow candidate |
| error | 4 | App state candidate |
| astro | 4 | documented semantic extension |
| banner | 4 | App state/banner candidate |
| user | 4 | App account candidate |
| control | 4 | App settings/control candidate |
| btn | 4 | App button candidate |
| degraded | 4 | App state candidate |
| skeleton | 3 | App primitive candidate |
| mobile | 3 | App navigation candidate |
| typing | 3 | App chat primitive candidate |
| account | 3 | App account candidate |
| panel | 2 | App primitive candidate |
| section | 2 | App primitive candidate |
| shell | 2 | App shell candidate |
| danger | 2 | App button state candidate |
| day | 1 | App day state candidate |
| checkbox | 1 | App form primitive candidate |
| card | 1 | App primitive candidate |
| nickname | 1 | App form candidate |
| bottom | 1 | App navigation candidate |
| admin | 1 | App admin heading candidate |

## Baseline Conclusion

The baseline reproduces audit `E-013`: `person`, `activity`, `summary`,
`flow`, `premium`, `precision`, `evidence`, `people`, `chat`, and `usage`
remain active in `frontend/src/App.css` and require a final exact owner
decision.
