# Story 16.6: Settings Pages — Compte, Abonnement, Usage

Status: done

## Story

As a utilisateur,
I want accéder à mes paramètres de compte, abonnement et usage dans des pages dédiées,
So that je puisse gérer mon profil et mes données facilement.

## Contexte

Les panneaux BillingPanel et PrivacyPanel existent comme composants mais sont affichés via le state dans App.tsx. Cette story les migre vers des pages dédiées avec sous-routes.

## Scope

### In-Scope
- Page `/settings` avec layout tabs/sous-routes
- Sous-page `/settings/account` — infos compte, suppression
- Sous-page `/settings/subscription` — gestion abonnement
- Sous-page `/settings/usage` — statistiques usage
- Double confirmation pour suppression compte
- Migration des composants existants (BillingPanel, PrivacyPanel)

### Out-of-Scope
- Nouvelles fonctionnalités de gestion compte
- Notifications par email

**Note:** Une modification mineure de l'API backend `/v1/auth/me` a été effectuée pour retourner `email` et `created_at` afin de satisfaire AC2.

## Acceptance Criteria

### AC1: Navigation settings
**Given** un utilisateur sur `/settings`
**When** la page se charge
**Then** il voit des onglets/liens : Compte, Abonnement, Usage
**And** il est redirigé vers `/settings/account` par défaut

### AC2: Page compte
**Given** un utilisateur sur `/settings/account`
**When** la page se charge
**Then** il voit ses informations de compte (email, date inscription)
**And** un bouton "Supprimer mon compte"

### AC3: Suppression compte
**Given** un utilisateur cliquant "Supprimer mon compte"
**When** la modal de confirmation s'ouvre
**Then** il doit confirmer deux fois (double validation)
**And** après suppression, il est déconnecté et redirigé vers `/login`

### AC4: Page abonnement
**Given** un utilisateur sur `/settings/subscription`
**When** la page se charge
**Then** il voit son plan actuel, son statut, et options de modification
**And** le composant BillingPanel existant est réutilisé

### AC5: Page usage
**Given** un utilisateur sur `/settings/usage`
**When** la page se charge
**Then** il voit sa consommation (quotas, messages envoyés, etc.)

## Tasks

- [x] Task 1: Créer layout settings (AC: #1)
  - [x] 1.1 Créer `src/pages/SettingsPage.tsx` avec Outlet
  - [x] 1.2 Créer `src/components/settings/SettingsTabs.tsx`
  - [x] 1.3 Configurer sous-routes dans routes.tsx

- [x] Task 2: Créer sous-pages (AC: #2, #4, #5)
  - [x] 2.1 Créer `src/pages/settings/AccountSettings.tsx`
  - [x] 2.2 Créer `src/pages/settings/SubscriptionSettings.tsx`
  - [x] 2.3 Créer `src/pages/settings/UsageSettings.tsx`

- [x] Task 3: Suppression compte (AC: #3)
  - [x] 3.1 Créer `src/components/settings/DeleteAccountModal.tsx`
  - [x] 3.2 Implémenter double confirmation
  - [x] 3.3 Appeler API suppression + logout + redirect

- [x] Task 4: Migration composants (AC: #4, #5)
  - [x] 4.1 Intégrer BillingPanel dans SubscriptionSettings
  - [x] 4.2 Intégrer PrivacyPanel dans AccountSettings
  - [x] 4.3 Créer composant UsageStats si non existant

- [x] Task 5: Tests (AC: tous)
  - [x] 5.1 Test navigation entre onglets
  - [x] 5.2 Test affichage compte
  - [x] 5.3 Test double confirmation suppression

## Dev Notes

### Routes settings

```typescript
// Dans routes.tsx
{
  path: "/settings",
  element: <SettingsPage />,
  children: [
    { index: true, element: <Navigate to="account" /> },
    { path: "account", element: <AccountSettings /> },
    { path: "subscription", element: <SubscriptionSettings /> },
    { path: "usage", element: <UsageSettings /> },
  ]
}
```

### Structure fichiers

```
frontend/src/
├── pages/
│   ├── SettingsPage.tsx
│   └── settings/
│       ├── AccountSettings.tsx
│       ├── SubscriptionSettings.tsx
│       └── UsageSettings.tsx
├── components/
│   └── settings/
│       ├── SettingsTabs.tsx
│       └── DeleteAccountModal.tsx
```

### SettingsPage layout

```tsx
// SettingsPage.tsx
export function SettingsPage() {
  return (
    <div className="settings-layout">
      <h1>Paramètres</h1>
      <SettingsTabs />
      <Outlet />
    </div>
  )
}
```

### SettingsTabs

```tsx
const tabs = [
  { path: "account", label: "Compte" },
  { path: "subscription", label: "Abonnement" },
  { path: "usage", label: "Usage" },
]

export function SettingsTabs() {
  const location = useLocation()
  return (
    <nav className="settings-tabs">
      {tabs.map(tab => (
        <NavLink 
          key={tab.path}
          to={tab.path}
          className={({ isActive }) => isActive ? "active" : ""}
        >
          {tab.label}
        </NavLink>
      ))}
    </nav>
  )
}
```

### Double confirmation pattern

```tsx
// DeleteAccountModal.tsx
const [step, setStep] = useState<"initial" | "confirm" | "final">("initial")

// Step 1: "Êtes-vous sûr de vouloir supprimer votre compte ?"
// Step 2: "Cette action est irréversible. Tapez 'SUPPRIMER' pour confirmer."
// Step 3: Appel API, logout, redirect
```

### Réutilisation composants existants

```tsx
// SubscriptionSettings.tsx
import { BillingPanel } from "../../components/BillingPanel"

export function SubscriptionSettings() {
  return (
    <section>
      <h2>Mon abonnement</h2>
      <BillingPanel />
    </section>
  )
}
```

## Dev Agent Record

### Agent Model Used
Claude Opus 4.5

### Debug Log References
- Tests échouaient à cause de la langue (detectLang retournait "en" au lieu de "fr")
- Ajout de beforeEach avec localStorage.setItem("lang", "fr") dans App.test.tsx et router.test.tsx
- Ajout des mocks billing/privacy dans les tests pour supporter les nouvelles routes settings

### Completion Notes List
- Implémenté layout Settings avec tabs et sous-routes (account, subscription, usage)
- Créé DeleteAccountModal avec double confirmation (étape initiale + saisie du mot "SUPPRIMER")
- Intégré BillingPanel dans SubscriptionSettings et PrivacyPanel dans AccountSettings
- Créé UsageSettings avec affichage des quotas et barre de progression
- Ajouté styles CSS pour settings, modal, et boutons danger
- Tests complets : 18 tests pour SettingsPage couvrant tous les ACs
- Correction des tests existants (DashboardPage, App, router) pour compatibilité

### File List
- frontend/src/pages/SettingsPage.tsx (modifié)
- frontend/src/pages/settings/AccountSettings.tsx (créé)
- frontend/src/pages/settings/SubscriptionSettings.tsx (créé)
- frontend/src/pages/settings/UsageSettings.tsx (créé)
- frontend/src/components/settings/SettingsTabs.tsx (créé)
- frontend/src/components/settings/DeleteAccountModal.tsx (créé)
- frontend/src/i18n/settings.ts (créé)
- frontend/src/utils/locale.ts (créé)
- frontend/src/app/routes.tsx (modifié)
- frontend/src/App.css (modifié)
- frontend/src/api/authMe.ts (modifié)
- frontend/src/tests/SettingsPage.test.tsx (créé)
- frontend/src/tests/DashboardPage.test.tsx (modifié)
- frontend/src/tests/App.test.tsx (modifié)
- frontend/src/tests/router.test.tsx (modifié)
- backend/app/api/dependencies/auth.py (modifié)
- backend/app/api/v1/routers/auth.py (modifié)
- backend/app/tests/integration/test_auth_api.py (modifié)

### Change Log
- 2026-02-23: Story 16-6 implementée - Pages Settings avec sous-routes account/subscription/usage, double confirmation suppression compte, migration BillingPanel et PrivacyPanel
- 2026-02-23: [Code Review #1] Corrections appliquées:
  - HIGH-1: AC2 complété - ajout email et date inscription via modification API /v1/auth/me
  - HIGH-2: Normalisation robuste de la comparaison du mot de confirmation (suppression accents)
  - HIGH-3: Focus trap implémenté dans DeleteAccountModal pour accessibilité WCAG
  - HIGH-4: Gestion d'erreurs améliorée avec messages localisés dans UsageSettings
  - MEDIUM-1: Test ajouté pour erreur API lors de la suppression de compte
  - MEDIUM-2: Attributs aria-selected ajoutés aux SettingsTabs
  - MEDIUM-3: Test ajouté pour fermeture modal via touche Escape
  - MEDIUM-4: Division par zéro corrigée dans la barre de progression
  - LOW-1: Traductions centralisées dans i18n/settings.ts
  - LOW-2: CSS variable --usage-progress pour la barre de progression
- 2026-02-23: [Code Review #2] Corrections finales:
  - MEDIUM-1: Variable inutilisée `index` supprimée dans SettingsTabs
  - MEDIUM-2: Gestion d'erreur ajoutée dans AccountSettings (authMe.isError)
  - MEDIUM-3: aria-controls supprimé (IDs inexistants dans DOM)
  - LOW-1: autoFocus remplacé par useEffect + inputRef pour cohérence focus management
  - Test ajouté: erreur chargement informations compte
- 2026-02-23: [Code Review #3] Nettoyage final:
  - LOW-1: Import inutilisé `clearAccessToken` supprimé dans SettingsPage.test.tsx
  - LOW-2: Utilitaire `getLocale` centralisé dans utils/locale.ts (suppression duplication)
  - LOW-3: Test ajouté pour erreur quota dans UsageSettings
- 2026-02-23: [Code Review #4] Accessibilité clavier:
  - MEDIUM-1: Navigation clavier (flèches, Home, End) ajoutée dans SettingsTabs
  - LOW-1: Validation date invalide ajoutée dans formatDate (AccountSettings)
  - LOW-2: Test ajouté pour navigation clavier avec flèches
- 2026-02-23: [Code Review #5] Polish final:
  - LOW-1: isActive et activeIndex correctement mémorisés avec useCallback/useMemo
  - LOW-2: Test ajouté pour navigation Home/End
  - LOW-3: aria-label ajouté au progressbar pour accessibilité
- 2026-02-23: [Code Review #6] Adversarial review — corrections appliquées:
  - MEDIUM-1: DeleteAccountModal — overlay onClick + Escape bloqués pendant step="processing" pour éviter interruption d'une suppression en cours
  - MEDIUM-2: SettingsTabs — role="tab" sans aria-controls remplacé par nav+aria-label+aria-current="page"; i18n/settings.ts enrichi de navLabel (fr/en/es); tests mis à jour (getByRole("navigation")/getByRole("link"))
  - MEDIUM-3: DeleteAccountModal — aria-live="polite" ajouté au paragraphe processing pour annonce aux lecteurs d'écran
  - LOW-1: AccountSettings — formatDate retourne "—" au lieu du isoDate brut si date invalide
  - LOW-2: DeleteAccountModal — handleFirstConfirm/handleFinalConfirm wrappés dans useCallback; isMountedRef ajouté pour protéger le catch asynchrone contre les setState sur composant démonté; normalizeConfirmInput extraite hors du composant
