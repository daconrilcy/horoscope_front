# CS-137 dark mode before

Source: `.codex-artifacts/dark-mode-audit-2026-05-10/audit-results.json`

Generated at: `2026-05-10T19:12:28.161Z`

Base URL: `http://127.0.0.1:5173`

## Summary

- Audited routes: 33
- Total contrast issues: 395
- Total light surface findings: 127
- Theme state: `html.dark`
- Screenshots: `.codex-artifacts/dark-mode-audit-2026-05-10/*.png`

## Highest priority routes

| Label | Route | Final URL | Issues | Light surfaces | Screenshot |
|---|---|---|---:|---:|---|
| `auth:/help/subscriptions` | `/help/subscriptions` | `http://127.0.0.1:5173/help/subscriptions` | 72 | 16 | `auth-help__subscriptions.png` |
| `auth:/help` | `/help` | `http://127.0.0.1:5173/help` | 70 | 6 | `auth-help.png` |
| `auth:/settings/subscription` | `/settings/subscription` | `http://127.0.0.1:5173/settings/subscription` | 47 | 11 | `auth-settings__subscription.png` |
| `auth:/natal` | `/natal` | `http://127.0.0.1:5173/natal` | 44 | 12 | `auth-natal.png` |
| `auth:/consultations` | `/consultations` | `http://127.0.0.1:5173/consultations` | 33 | 0 | `auth-consultations.png` |
| `auth:/astrologers` | `/astrologers` | `http://127.0.0.1:5173/astrologers` | 32 | 19 | `auth-astrologers.png` |
| `auth:/settings/account` | `/settings/account` | `http://127.0.0.1:5173/settings/account` | 18 | 3 | `auth-settings__account.png` |
| `public:/` | `/` | `http://127.0.0.1:5173/` | 16 | 12 | `public-root.png` |
| `auth:/settings/usage` | `/settings/usage` | `http://127.0.0.1:5173/settings/usage` | 5 | 1 | `auth-settings__usage.png` |

## Main issue families

- Public landing and privacy routes expose browser-default blue links and light landing surfaces in dark mode.
- Help and subscription help surfaces keep light glass variables in `html.dark`.
- Settings subscription/account/usage surfaces keep light card and accent variables in `html.dark`.
- Natal page and interpretation controls keep light card backgrounds and weak accent contrast.
- Dashboard-derived routes expose user avatar contrast and summary panel light surfaces.
- Astrologer catalog cards keep light card variables in dark mode.

## Candidate owners

- `frontend/src/layouts/LandingLayout.css`
- `frontend/src/pages/PrivacyPolicyPage.css`
- `frontend/src/pages/HelpPage.css`
- `frontend/src/pages/settings/Settings.css`
- `frontend/src/pages/NatalChartPage.css`
- `frontend/src/features/natal-chart/NatalInterpretation.css`
- `frontend/src/components/ui/UserAvatar/UserAvatar.css`
- `frontend/src/pages/ChatPage.css`
- `frontend/src/pages/ConsultationResultPage.css`
- `frontend/src/styles/app/tokens.css`
