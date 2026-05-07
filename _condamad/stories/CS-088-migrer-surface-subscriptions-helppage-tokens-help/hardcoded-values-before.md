# Hardcoded Values Before

## Scope

- File: `frontend/src/pages/HelpPage.css`
- Section: `/* --- Help Subscriptions Page (AC7, AC9) --- */`
- Captured before implementation on 2026-05-07.

## Commands

```powershell
rg -n "#[0-9A-Fa-f]{3,8}|rgba?\(|hsla?\(" frontend\src\pages\HelpPage.css
rg -n "font-size:|font-weight:|line-height:|letter-spacing:" frontend\src\pages\HelpPage.css
rg -n "box-shadow:|border-radius:|linear-gradient|radial-gradient|var\(\s*--[a-zA-Z0-9_-]+\s*," frontend\src\pages\HelpPage.css
```

## Before findings for subscriptions

| Category | Lines | Examples | Initial decision |
|---|---|---|---|
| Glass borders and surfaces | 861, 883-885, 900-901, 952, 962-963, 1033-1034, 1353, 1372-1377, 1415-1422, 1526-1528, 1585-1588 | `rgba(255, 255, 255, 0.34)`, `rgba(205, 217, 240, 0.72)`, `rgba(134, 108, 208, 0.12)` | migrate to `--help-subscriptions-*` owners or reuse existing `--help-*`. |
| Subscription gradients | 874, 883-884, 977-979, 1013, 1080, 1114-1115, 1163, 1169-1180, 1189-1196, 1206-1207, 1270, 1372-1373, 1415-1416, 1464, 1541-1567, 1594 | radial and linear gradient literals | migrate to `--help-subscriptions-*` owners. |
| Shadows and elevation | 887-888, 941-942, 981-984, 1015-1016, 1023-1024, 1081, 1145, 1153-1155, 1171-1173, 1183-1184, 1209-1211, 1273, 1298, 1305-1306, 1375-1390, 1420-1422, 1460-1472, 1544-1555, 1595-1604 | `0 26px 54px rgba(132, 150, 190, 0.18)`, inset highlights | migrate to `--help-subscriptions-*` owners. |
| Radius literals | 881, 975, 1110, 1370 | `36px`, `32px`, `18px` | migrate to existing `--help-radius-*`. |
| Ink and accent colors | 1208, 1259, 1271 | `#fff`, `#6d56bf`, `#85531a` | migrate to Help owner/global color token. |
| Typography literals | 903-905, 911-922, 928-929, 1036-1055, 1213-1215, 1239-1325, 1345-1346, 1364, 1399, 1439-1454, 1485, 1514-1530, 1610, 1648-1653 | local font sizes, weights, line heights and letter spacing | migrate to global type tokens or `--help-subscriptions-type-*` owners documented as Help-scoped roles. |
| Motion/layout timing and transforms | 1122-1129, 1131-1139, 1144, 1152, 1357, 1397-1405, 1710-1729 | animation durations, transform distances, rotation and opacity keyframes | kept-one-off-final; behavior/layout timing, not tokenized in this story. |
| Layout spacing and dimensions | 836-1705 | margins, padding, widths, heights, gaps, min heights | kept-one-off-final unless already using global spacing tokens; preserving rendered layout is required. |

## Guardrail classification

- Applicable: `RG-044`, `RG-045`, `RG-046`, `RG-047`, `RG-048`, `RG-049`, `RG-050`, `RG-051`, `RG-052`, `RG-060`.
- Non-applicable: `RG-053`, `RG-054`, `RG-055`, `RG-056`, `RG-057`, `RG-058`, `RG-059`.
