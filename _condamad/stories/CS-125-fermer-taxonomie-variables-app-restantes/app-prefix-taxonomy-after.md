<!-- Inventaire apres implementation de la taxonomie App CSS pour CS-125. -->

# CS-125 App Prefix Taxonomy After

## Commands

```powershell
$css = Get-Content -Raw 'frontend\src\App.css'
[regex]::Matches($css, '(--app-([a-zA-Z0-9]+)[a-zA-Z0-9_-]*)\s*:') |
  ForEach-Object { $_.Groups[2].Value } |
  Group-Object |
  Sort-Object Count -Descending

Push-Location frontend
rg -n -- "--app-(person|people|activity|premium|flow|summary|precision|evidence|chat|usage)-" src/App.css
rg -n -- "--app-precision-|--app-evidence-|\.precision-badge|\.evidence-tags|\.evidence-pill" src/App.css
Pop-Location
```

## Declaration Prefix Counts

| Prefix | Count | Classification | Consumers | Canonical replacement | Decision | Proof | Risk |
|---|---:|---|---|---|---|---|---|
| person | 124 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| activity | 59 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| summary | 26 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| flow | 17 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| premium | 15 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| modal | 13 | canonical-active | App.css selectors and TSX classes | none | retain App primitive | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| people | 13 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| activities | 12 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| chat | 11 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| validation | 11 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| usage | 9 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| state | 7 | canonical-active | App.css selectors and TSX classes | none | retain App primitive | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| type | 7 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| drawing | 7 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| button | 6 | canonical-active | App.css selectors | none | retain App primitive | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| form | 6 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| other | 5 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| message | 5 | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + registry row | low |
| remaining retained prefixes | 1-4 each | canonical-active | App.css selectors | none | retain App owner | `APP_CSS_ACCEPTED_PREFIXES` + exact `--app-<prefix>-*` rows | low |
| precision | 0 | migrated | consultation consumers | `--consultation-precision-*` and `ConsultationPrecisionBadge` | delete from App.css | zero-hit App.css scan + CS-126 guard | low |
| evidence | 0 | migrated | natal evidence consumer | `ni-evidence-*` classes in `NatalInterpretation.css` | delete from App.css | zero-hit App.css scan + CS-126 guard | low |

## Final Decision

Every active App prefix is now listed in the positive
`APP_CSS_ACCEPTED_PREFIXES` registry and mirrored by an exact
`frontend/src/styles/token-namespace-registry.md` row. `precision` and
`evidence` were removed from App ownership by `CS-126`, so no
`--app-precision-*`, `--app-evidence-*`, `.precision-badge*`,
`.evidence-tags*`, or `.evidence-pill*` remains in `frontend/src/App.css`.

## Guard Evidence

- `design-system-guards.test.ts` compares active App prefixes with
  `APP_CSS_ACCEPTED_PREFIXES`.
- The guard rejects stale accepted prefixes, duplicate accepted prefixes, and
  missing registry rows.
- The precision/evidence guard rejects unclassified App.css hits.
