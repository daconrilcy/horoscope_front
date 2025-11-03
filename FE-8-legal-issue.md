# Issue: FE-8 — Legal Service + Pages Légales

## Objectif

Implémenter le Legal Service et les pages légales (TOS/Privacy) avec fetch HTML depuis le backend, sanitization minimale, gestion cache optimisée (ETag/Last-Modified), et UX/A11y complète.

## Tâches

### 8.1 — LegalService + pages /legal/tos, /legal/privacy

**Objectif**: rendu HTML backend sécurisé.

- **Tâches**:
  - Créer `legal.service.ts` avec `getTos()` et `getPrivacy()` utilisant fetch direct
  - Lire headers `ETag`, `Last-Modified`, `X-Legal-Version` depuis la réponse
  - Vérifier `Content-Type: text/html` ou `text/plain`, sinon lever `ApiError`
  - Créer mini-sanitizer `sanitizeLegalHtml()` (scripts, iframes, on\*, javascript:)
  - Créer hooks `useTos()` et `usePrivacy()` avec React Query (staleTime 24h, gcTime 7j)
  - Mettre à jour pages TOS et Privacy avec:
    - Sanitization du HTML avant `dangerouslySetInnerHTML`
    - Loader pendant chargement
    - Gestion d'erreurs claire avec retry et mailto support
    - Bouton Imprimer (`window.print()`)
    - Structure ARIA (`<article>`, `<h1>`)
    - Sécurisation liens externes (rel="noopener" target="\_blank")
    - Injection `<base>` si liens relatifs détectés

**AC**:

- Pages affichées avec version backend
- Scripts/iframes/attrs on\* retirés, pas de javascript:
- Cache long (staleTime 24h, gcTime 7j)
- Retry uniquement sur NetworkError (pas sur 4xx)
- Loader, erreurs claires, bouton Imprimer, structure ARIA

**Refs**: `/v1/legal/tos`, `/v1/legal/privacy` (GET HTML)

## Tests

- ✅ Sanitizer : 26 tests (scripts, iframes, on\*, javascript:)
- ✅ Service : 14 tests (200, ETag/Last-Modified, Content-Type, 404, 500, NetworkError)
- ✅ Hooks : 15 tests (cache, retry, refetch, NetworkError)
- ✅ Pages : 22 tests (loader, contenu, erreur, print, ARIA, liens externes)

**Total** : 77 tests passants ✅

## Check-list d'acceptation

- [x] **Sécurité** : scripts/iframes/attrs on\* retirés, pas de javascript: ; `dangerouslySetInnerHTML` uniquement après sanitation
- [x] **Caching** : `staleTime` 24h / `gcTime` 7j ; ETag/Last-Modified lus et réutilisés
- [x] **Robustesse** : check `content-type` ; `<base>` injecté si nécessaire pour liens relatifs ; external links sécurisés
- [x] **UX/A11y** : titre, loader, erreurs claires, bouton Imprimer, structure ARIA
- [x] **Tests** : service (200/Content-Type/headers), sanitizer, pages (loader/erreur/print)
- [x] **Qualité** : lint/type/tests ✅

## Labels

`feature`, `legal`, `milestone-fe-8`
