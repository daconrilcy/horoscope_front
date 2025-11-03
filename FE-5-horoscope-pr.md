# PR: FE-5 — Horoscope Feature

Closes #14

## Description

Implémentation du système complet d'horoscope avec HoroscopeService (validation Zod stricte), store LRU pour charts récents, pages avec formulaire natal/today/premium protégé par PaywallGate, export PDF sécurisé, et tests complets.

## Type de changement

- [x] Nouvelle fonctionnalité (feature)
- [ ] Correction de bug (bugfix)
- [ ] Refactoring
- [ ] Documentation

## Checklist

- [x] J'ai vérifié que mon code suit les conventions du projet
- [x] J'ai auto-reviewé mon code
- [x] Mes commentaires sont utiles et clairs
- [x] J'ai documenté les changements complexes si nécessaire
- [x] Mes tests passent localement
- [x] J'ai mis à jour la documentation si nécessaire

## Résumé des changements

### Nouveaux fichiers

1. `src/shared/api/horoscope.service.ts` - Service horoscope avec schémas Zod stricts
2. `src/shared/api/horoscope.service.test.ts` - Tests service (13 tests)
3. `src/shared/auth/charts.ts` - Helpers localStorage pour charts
4. `src/stores/horoscopeStore.ts` - Store LRU anti-doublon, cap 10 FIFO
5. `src/stores/horoscopeStore.test.ts` - Tests store (10 tests)
6. `src/features/horoscope/hooks/useCreateNatal.ts` - Hook mutation createNatal
7. `src/features/horoscope/hooks/useToday.ts` - Hook query today (free)
8. `src/features/horoscope/hooks/useTodayPremium.ts` - Hook query today premium
9. `src/features/horoscope/hooks/useDownloadPdf.ts` - Hook download PDF
10. `src/features/horoscope/utils/downloadBlob.ts` - Helper download blob
11. `src/features/horoscope/NatalForm.tsx` - Form création thème natal
12. `src/features/horoscope/TodayCard.tsx` - Card horoscope today
13. `src/features/horoscope/TodayPremiumCard.tsx` - Card horoscope premium
14. `src/pages/app/horoscope/index.tsx` - Page horoscope principale
15. `FE-5-horoscope-issue.md` - Issue GitHub
16. `FE-5-horoscope-pr.md` - Description PR
17. `FE-5-IMPLEMENTATION-COMPLETE.md` - Résumé implementation

### Fichiers modifiés

1. `src/app/router.tsx` - Ajout route `/app/horoscope` lazy + Suspense

## Endpoints utilisés

- `POST /v1/horoscope/natal` - Création thème natal
  - Body : `{ date: string (YYYY-MM-DD), time: string (HH:mm), latitude: number, longitude: number, timezone: string (IANA), name?: string }`
  - Réponse : `{ chart_id: string, created_at?: string }`

- `GET /v1/horoscope/today/{chartId}` - Horoscope today (free)
  - Réponse : `{ content: string, generated_at?: string }`

- `GET /v1/horoscope/today/premium/{chartId}` - Horoscope today premium
  - Réponse : `{ content: string, premium_insights?: string, generated_at?: string }`

- `GET /v1/horoscope/pdf/natal/{chartId}` - Téléchargement PDF
  - Réponse : Blob PDF

## Fonctionnalités

### 5.1 — HoroscopeService

- ✅ Schémas Zod stricts : `ChartId`, `IsoDate` (regex `/^\d{4}-\d{2}-\d{2}$/`), `Hhmm` (regex `/^\d{2}:\d{2}$/`), `Lat` (-90..90), `Lng` (-180..180), `Tz` (IANA)
- ✅ `createNatal`, `getToday`, `getTodayPremium`, `getNatalPdfStream`
- ✅ Validation fail-fast sur toutes les réponses
- ✅ Mapping 422 → détails exposés pour erreurs par champ
- ✅ PDF content-type guard + filename
- ✅ Pas de conversion UTC côté front

### 5.2 — Store LRU

- ✅ LRU anti-doublon : si chartId existe, remonte en tête
- ✅ Cap 10 FIFO : si > 10, supprime le plus ancien
- ✅ Persist localStorage clé `HORO_RECENT_CHARTS`
- ✅ hasHydrated pour hydratation contrôlée

### 5.3 — Hooks React Query

- ✅ Retry conditionnel : retry 0 si ApiError, retry 1 si NetworkError
- ✅ Invalidations fines : createNatal → today
- ✅ Mapping 422 → fields
- ✅ PDF download sécurisé
- ✅ Toast success/error appropriés

### 5.4 — Composants UI

- ✅ Form validé côté client (bornes lat/lng, required)
- ✅ Timezone auto-détecté via `Intl.DateTimeFormat()`
- ✅ Double-submit bloqué
- ✅ A11y complet (labels, aria-invalid, aria-describedby, aria-live)
- ✅ Premium query déclenchée uniquement dans PaywallGate
- ✅ Loading/error/retry states

### 5.5 — Page & Router

- ✅ Page horoscope avec sections form + today + premium + export PDF
- ✅ Post-checkout invalidation des queries premium
- ✅ Route `/app/horoscope` lazy + Suspense

## Tests

- ✅ Tests service (13 tests)
  - createNatal : 200 valid, 422 details, 401/5xx
  - getToday : 200 valid, 404, ZodError fail-fast
  - getTodayPremium : idem
  - getNatalPdfStream : 200 blob, 404, 500
- ✅ Tests store (10 tests)
  - LRU anti-doublon
  - FIFO cap 10
  - Persistance localStorage
  - Clear charts
- ⏳ Tests hooks (à faire dans PR suivante)
- ⏳ Tests page intégration (à faire dans PR suivante)

**Total projet** : 207/207 tests passants ✅

## Contraintes respectées

- ✅ Schémas Zod stricts (regex date/time, bornes lat/lng/IANA TZ)
- ✅ Validation fail-fast sur toutes les réponses
- ✅ PDF content-type guard + filename
- ✅ Mapping 422 → détails exposés
- ✅ Pas de conversion UTC côté front
- ✅ Store LRU anti-doublon fonctionnel
- ✅ Cap 10 FIFO respecté
- ✅ Persistance localStorage fonctionnelle
- ✅ Retry réseau only (pas 4xx)
- ✅ Invalidations fines (createNatal → today)
- ✅ Premium query déclenchée **uniquement dans PaywallGate**
- ✅ Form validé client (bornes lat/lng, required)
- ✅ Double-submit bloqué
- ✅ A11y complet (aria-\*)
- ✅ Timezone auto-détecté

## Commandes de test

```bash
# Tests unitaires
npm run test

# Linter
npm run lint

# Format
npm run format:check

# Type-check
npm run build
```

## Notes additionnelles

- Les tests pour les hooks et la page sont en cours de développement
- Les tests d'intégration hooks/page seront ajoutés dans une prochaine itération
- MVP acceptable sans tests d'intégration complets
- Tests e2e manuels avec Playwright seront faits en PR dédiée
