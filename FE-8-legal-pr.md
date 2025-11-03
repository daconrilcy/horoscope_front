# PR: FE-8 — Legal Service + Pages Légales

## Description

Implémentation complète du Legal Service et des pages légales (TOS/Privacy) avec sanitization HTML, gestion cache optimisée (ETag/Last-Modified), et UX/A11y complète.

## Type de changement

- [x] 🎉 Nouvelle fonctionnalité
- [ ] 🐛 Correction de bug
- [ ] 📚 Documentation
- [ ] 🎨 Style / Format
- [ ] ♻️ Refactoring
- [ ] ⚡ Performance
- [x] ✅ Tests
- [ ] 🔧 Build / CI

## Issues liées

Closes #24

## Changements

### 8.1 — Mini-Sanitizer (`src/shared/utils/sanitizeLegalHtml.ts`)

- ✅ Retrait scripts, iframes, objects, embeds, liens CSS externes
- ✅ Suppression attributs on\* (onclick, onload, etc.)
- ✅ Neutralisation javascript: dans href/src
- ✅ 26 tests unitaires complets

### 8.2 — LegalService (`src/shared/api/legal.service.ts`)

- ✅ Méthodes `getTos()` et `getPrivacy()` avec fetch direct
- ✅ Lecture headers ETag, Last-Modified, X-Legal-Version
- ✅ Vérification Content-Type (text/html ou text/plain)
- ✅ Gestion erreurs ApiError/NetworkError
- ✅ 14 tests unitaires complets

### 8.3 — Hooks React Query (`src/features/legal/hooks/`)

- ✅ `useTos()` et `usePrivacy()` avec React Query
- ✅ staleTime: 24h (1 jour), gcTime: 7j (1 semaine)
- ✅ retry: 1 uniquement sur NetworkError (pas sur 4xx)
- ✅ 15 tests unitaires complets (8 useTos + 7 usePrivacy)

### 8.4 — Pages TOS et Privacy (`src/pages/legal/`)

- ✅ Sanitization HTML avant `dangerouslySetInnerHTML`
- ✅ Loader pendant chargement
- ✅ Gestion erreurs avec retry et mailto support
- ✅ Bouton Imprimer (`window.print()`)
- ✅ Structure ARIA (`<article>`, `<h1>`)
- ✅ Sécurisation liens externes (rel="noopener" target="\_blank")
- ✅ Injection `<base>` si liens relatifs détectés
- ✅ 22 tests unitaires complets (11 TOS + 11 Privacy)

## Checklist

- [x] Sécurité : scripts/iframes/attrs on\* retirés, pas de javascript:
- [x] Caching : staleTime 24h, gcTime 7j ; ETag/Last-Modified lus
- [x] Robustesse : check Content-Type ; `<base>` injecté si nécessaire
- [x] UX/A11y : titre, loader, erreurs claires, bouton Imprimer, structure ARIA
- [x] Tests : service (200/Content-Type/headers), sanitizer, pages (loader/erreur/print)
- [x] Code formaté avec Prettier
- [x] Code linté sans erreurs (ESLint)
- [x] Tests passent (77 nouveaux tests, tous passent)

## Tests

```bash
# Tests passent
npm run test

# Lint passe
npm run lint

# Format vérifié
npm run format:check
```

**Résultats** : 77 nouveaux tests passants ✅

- 26 tests sanitizer
- 14 tests service
- 15 tests hooks
- 22 tests pages

## Fichiers créés

- `src/shared/utils/sanitizeLegalHtml.ts` + tests
- `src/shared/api/legal.service.ts` + tests
- `src/features/legal/hooks/useTos.ts` + tests
- `src/features/legal/hooks/usePrivacy.ts` + tests
- `src/pages/legal/tos/index.test.tsx`
- `src/pages/legal/privacy/index.test.tsx`

## Fichiers modifiés

- `src/pages/legal/tos/index.tsx` - Implémentation complète
- `src/pages/legal/privacy/index.tsx` - Implémentation complète
- Corrections format dans fichiers existants

**Total** : 21 fichiers modifiés, 2299 insertions, 86 suppressions

## Notes additionnelles

- Sanitization minimale mais proactive (scripts, iframes, on\*, javascript:)
- ETag/Last-Modified pour optimiser bande passante et fraîcheur
- Content-Type strict pour éviter injection de JSON/autre
- Base href pour liens relatifs si nécessaire
- Liens externes automatiquement sécurisés (rel="noopener" target="\_blank")
