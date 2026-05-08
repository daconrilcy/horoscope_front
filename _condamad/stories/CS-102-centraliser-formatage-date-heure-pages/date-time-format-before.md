<!-- Inventaire initial du formatage date/heure inline dans les pages React. -->

# CS-102 - Before date/time inventory

Commande de selection:

```powershell
Push-Location frontend
rg -n "new Date\([^\n]+\)\.toLocale(DateString|String)|Intl\.DateTimeFormat|\.toLocaleString\(" src/pages -g "*.tsx"
Pop-Location
```

## Classification initiale

| Hit | Classification | Output attendu | Helper cible / decision |
|---|---|---|---|
| `src/pages/admin/AdminAiGenerationsPage.tsx:111` | date-time-ui | `new Date(f.timestamp).toLocaleString()` | `formatLocalDateTime(f.timestamp)` |
| `src/pages/admin/AdminLogsPage.tsx:146` | date-time-ui | `new Date(log.timestamp).toLocaleString()` | `formatLocalDateTime(log.timestamp)` |
| `src/pages/admin/AdminLogsPage.tsx:434` | date-time-ui | `new Date(log.timestamp).toLocaleString()` | `formatLocalDateTime(log.timestamp)` |
| `src/pages/admin/AdminLogsPage.tsx:470` | date-time-ui | `new Date(log.timestamp).toLocaleString()` | `formatLocalDateTime(log.timestamp)` |
| `src/pages/admin/AdminLogsPage.tsx:517` | date-time-ui | `new Date(event.received_at).toLocaleString()` | `formatLocalDateTime(event.received_at)` |
| `src/pages/admin/AdminPromptsPage.tsx:2019` | date-time-ui | `new Date(row.period_start_utc).toLocaleString()` | `formatLocalDateTime(row.period_start_utc)` |
| `src/pages/admin/AdminPromptsPage.tsx:2083` | date-time-ui | `new Date(row.period_start_utc).toLocaleString()` | `formatLocalDateTime(row.period_start_utc)` |
| `src/pages/admin/AdminPromptsPage.tsx:2145` | date-time-ui | `new Date(selectedConsumptionRow.period_start_utc).toLocaleString()` | `formatLocalDateTime(selectedConsumptionRow.period_start_utc)` |
| `src/pages/admin/AdminPromptsPage.tsx:2174` | date-time-ui | `new Date(item.timestamp).toLocaleString()` | `formatLocalDateTime(item.timestamp)` |
| `src/pages/admin/AdminPromptsPage.tsx:2450` | date-time-ui | `new Date(item.occurred_at).toLocaleString()` | `formatLocalDateTime(item.occurred_at)` |
| `src/pages/admin/AdminSupportPage.tsx:102` | date-time-ui | `new Date(ticket.created_at).toLocaleDateString()` | `formatLocalDate(ticket.created_at)` |
| `src/pages/admin/AdminSupportPage.tsx:127` | date-time-ui | `new Date(content.reported_at).toLocaleString()` | `formatLocalDateTime(content.reported_at)` |
| `src/pages/admin/AdminUserDetailPage.tsx:291` | date-time-ui | `new Date(user.created_at).toLocaleString()` | `formatLocalDateTime(user.created_at)` |
| `src/pages/admin/AdminUserDetailPage.tsx:459` | date-time-ui | `new Date(ticket.created_at).toLocaleDateString()` | `formatLocalDate(ticket.created_at)` |
| `src/pages/admin/AdminUserDetailPage.tsx:479` | date-time-ui | `new Date(event.created_at).toLocaleString()` | `formatLocalDateTime(event.created_at)` |
| `src/pages/admin/AdminUsersPage.tsx:72` | date-time-ui | `new Date(user.created_at).toLocaleDateString()` | `formatLocalDate(user.created_at)` |
| `src/pages/PrivacyPolicyPage.tsx:30` | date-time-ui | `new Date().toLocaleDateString()` | `formatLocalDate(new Date().toISOString())` |
| `src/pages/settings/SubscriptionSettings.tsx:260` | date-time-ui | `new Date(dateStr).toLocaleDateString(locale, options)` | `formatDateWithOptions(dateStr, locale, options)` |
| `src/pages/settings/UsageSettings.tsx:16` | date-time-ui | `Intl.DateTimeFormat(getLocale(lang), options).format(new Date(value))` | `formatDateWithOptions(value, getLocale(lang), options)` |
| `src/pages/admin/AdminDashboardPage.tsx` money rows | numeric-only | Montants en euros | Retenu, hors domaine date/time |
| `src/pages/SubscriptionGuidePage.tsx:357` | numeric-only | Quota localise | Retenu, hors domaine date/time |
| `src/pages/settings/UsageSettings.tsx:13` | numeric-only | Tokens formates | Retenu, hors domaine date/time |

## Decision

Tous les hits `date-time-ui` partages sont migrables vers `frontend/src/utils/formatDate.ts`.
Aucun hit `page-specific-retained` ou `needs-user-decision` n'est requis.
