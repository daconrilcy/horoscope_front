# Issue: FE-9 — Widgets & Shared

## Objectif

Implémenter les widgets QuotaBadge et PlanBanner pour la visibilité plan/quotas, ainsi que les composants UI transverses (ErrorBoundary amélioré, Loader, InlineError, CopyButton) avec tests complets.

## Tâches

### 9.1 — QuotaBadge & PlanBanner

#### 9.1.1 — Hook useMultiPaywall
- [ ] Créer `src/features/billing/hooks/useMultiPaywall.ts` :
  - [ ] Utilise `useQueries` de React Query pour fetch parallèle
  - [ ] Props : `features: string[]`
  - [ ] Retourne : tableau de `UsePaywallResult` + `isLoadingAny` + `isErrorAny`
  - [ ] Configuration : `staleTime: 5_000`, `retry: false`, `refetchOnWindowFocus: false`
- [ ] Tests `src/features/billing/hooks/useMultiPaywall.test.tsx`

**AC** :
- [ ] Requêtes parallèles (pas séquentielles)
- [ ] `isLoadingAny` et `isErrorAny` calculés correctement
- [ ] Configuration React Query respectée

#### 9.1.2 — Hook usePlan
- [ ] Ajouter `FEATURES.PRO_SENTINEL` et `FEATURES.PLUS_SENTINEL` dans `src/shared/config/features.ts`
- [ ] Créer `src/features/billing/hooks/usePlan.ts` :
  - [ ] Utilise `useMultiPaywall([PRO_SENTINEL, PLUS_SENTINEL])`
  - [ ] Logique : `allowed(PRO)` → 'pro', `allowed(PLUS)` → 'plus', sinon → 'free'
  - [ ] Retourne : `{ plan: 'free'|'plus'|'pro', isLoading }`
- [ ] Tests `src/features/billing/hooks/usePlan.test.tsx`

**AC** :
- [ ] Plan dérivé correctement via sentinelles
- [ ] Loading state géré

#### 9.1.3 — QuotaBadge
- [ ] Créer `src/widgets/QuotaBadge/QuotaBadge.tsx` :
  - [ ] Utilise `useMultiPaywall` (pas requêtes séquentielles)
  - [ ] Props : `features?: string[]`, `showRetryAfter?: boolean`
  - [ ] Affiche états simples :
    - `allowed: true` → "OK aujourd'hui"
    - `allowed: false & reason='rate'` → "Quota atteint" (+ compte à rebours si `retry_after`)
    - `allowed: false & reason='plan'` → "Fonctionnalité Plus/Pro"
  - [ ] Compte à rebours avec `useEffect` + `setInterval` (s'arrête à 0)
  - [ ] Accessibilité : `role="status"`, `aria-live="polite"`
- [ ] Tests `src/widgets/QuotaBadge/QuotaBadge.test.tsx`

**AC** :
- [ ] S'affiche avec états corrects
- [ ] Compte à rebours fonctionne (429)
- [ ] Accessibilité OK

#### 9.1.4 — PlanBanner
- [ ] Créer `src/widgets/PlanBanner/PlanBanner.tsx` :
  - [ ] Utilise `usePlan()`
  - [ ] Affiche plan (FREE, PLUS, PRO)
  - [ ] CTA Portal via `PortalButton` (visible pour plus/pro)
  - [ ] CTA Upgrade si plan='free'
  - [ ] Gère loading state
- [ ] Tests `src/widgets/PlanBanner/PlanBanner.test.tsx`
- [ ] Intégrer dans `src/pages/app/dashboard/index.tsx`

**AC** :
- [ ] S'affiche sur `/app/dashboard`
- [ ] Plan dérivé correctement
- [ ] CTAs appropriés selon plan

### 9.2 — Composants UI transverses

#### 9.2.1 — ErrorBoundary
- [ ] Améliorer `src/shared/ui/ErrorBoundary.tsx` :
  - [ ] Ajouter prop `onError?(err: Error, info: React.ErrorInfo)`
  - [ ] Afficher `requestId` si erreur est `ApiError`
  - [ ] Fallback accessible : `role="alert"`, `aria-live="assertive"`
  - [ ] Vérifier `resetKeys` fonctionne
- [ ] Créer/vérifier tests `src/shared/ui/ErrorBoundary.test.tsx`

**AC** :
- [ ] `onError` appelé pour journalisation
- [ ] `requestId` affiché si `ApiError`
- [ ] `resetKeys` ré-affiche l'enfant
- [ ] Accessibilité OK

#### 9.2.2 — Loader
- [ ] Créer `src/shared/ui/Loader.tsx` :
  - [ ] Props : `size?: 'sm' | 'md' | 'lg'`, `variant?: 'spinner'|'skeleton'`, `inline?: boolean`
  - [ ] Variante spinner : animation circulaire
  - [ ] Variante skeleton : placeholder grisé
  - [ ] Accessibilité : `aria-busy="true"`, `aria-label="Chargement"`
- [ ] Tests `src/shared/ui/Loader.test.tsx`

**AC** :
- [ ] Deux variantes fonctionnent
- [ ] Tailles et inline OK
- [ ] Accessibilité OK

#### 9.2.3 — InlineError
- [ ] Créer `src/shared/ui/InlineError.tsx` :
  - [ ] Props : `error: string | Error | ApiError`, `retry?: () => void`, `dismissible?: boolean`, `onDismiss?: () => void`
  - [ ] Affiche `requestId` si `ApiError` dans `<small>`
  - [ ] Bouton "Réessayer" optionnel
  - [ ] Dismissible avec X (ESC pour fermer)
  - [ ] `role="alert"`, `aria-live="assertive"`
- [ ] Tests `src/shared/ui/InlineError.test.tsx`

**AC** :
- [ ] Support string/Error/ApiError
- [ ] `requestId` affiché
- [ ] Retry et dismiss fonctionnent
- [ ] Accessibilité OK

#### 9.2.4 — CopyButton
- [ ] Créer `src/shared/ui/CopyButton.tsx` :
  - [ ] Props : `text: string | (() => string | Promise<string>)`, `label?: string`, `onCopy?: () => void`
  - [ ] Support fonction asynchrone
  - [ ] Clipboard API + fallback `document.execCommand`
  - [ ] Feedback visuel (icône check) + `aria-live`
- [ ] Tests `src/shared/ui/CopyButton.test.tsx`

**AC** :
- [ ] Copie fonctionne (statique et async)
- [ ] Feedback visuel
- [ ] Fallback si Clipboard API échoue
- [ ] Accessibilité OK

## Tests

- [ ] Tous les composants ont des tests complets
- [ ] Cas limites couverts (compte à rebours, resetKeys, clipboard mock)
- [ ] Accessibilité testée

## Check-list AC finale

- [ ] QuotaBadge : utilise useMultiPaywall, affiche états corrects, compte à rebours 429, a11y OK
- [ ] PlanBanner : plan dérivé via sentinelles, CTAs corrects, revalidation post-Stripe
- [ ] ErrorBoundary : onError, resetKeys, fallback accessible
- [ ] Loader : spinner + skeleton, aria-busy
- [ ] InlineError : support ApiError + requestId, retry & dismiss
- [ ] CopyButton : Clipboard API robuste + feedback a11y
- [ ] Tests : tous les cas couverts
- [ ] Qualité : lint/type/tests verts

