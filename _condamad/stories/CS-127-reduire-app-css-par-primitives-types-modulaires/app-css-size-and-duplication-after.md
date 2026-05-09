# App CSS metrics after CS-127

| Metric | Before | After | Result |
|---|---:|---:|---|
| App.css lines | 4094 | 12 | PASS: below 2600 |
| Total App CSS surface lines | n/a | 4955 | recorded |
| Flat selector blocks | 512 | 494 | reduced |
| Unique declaration bodies | 472 | 477 | recorded |
| Duplicate declaration bodies | 27 | 10 | PASS: 63.0% reduction |
| Duplicate selector membership | 67 | 27 | PASS: 59.7% reduction |
| Duplicate bodies with >=3 selectors | 8 | 4 | PASS: 50.0% reduction |

Import order in App.css:

1. tokens
2. base
3. typography
4. layout
5. buttons
6. cards
7. forms
8. notices
9. states
10. media
11. skeletons

Reason: tokens load before all consumers, base and typography establish global roles, layout/buttons/cards/forms/notices/states/media/skeletons then layer type-specific primitives from broad structure to specialized state/media behavior.
