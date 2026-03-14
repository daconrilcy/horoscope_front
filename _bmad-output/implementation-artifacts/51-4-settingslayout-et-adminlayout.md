# Story 51.4: Créer SettingsLayout et AdminLayout

Status: ready-for-dev

## Story

En tant que développeur frontend,
je veux des layouts `SettingsLayout` et `AdminLayout` extrayant la structure de leurs pages respectives,
afin que la mise en page des onglets de Settings et du hub Admin soit réutilisable indépendamment du contenu.

## Acceptance Criteria

1. `frontend/src/layouts/SettingsLayout.tsx` existe avec les props `title`, `tabs` (config de navigation), `children`.
2. `frontend/src/layouts/AdminLayout.tsx` existe avec les props `title`, `sections` (config de navigation), `backLabel?`, `children`.
3. `SettingsPage.tsx` est simplifié pour utiliser `SettingsLayout` — son code se réduit à brancher les props et les sous-routes.
4. `AdminPage.tsx` est simplifié pour utiliser `AdminLayout` — son code se réduit à brancher les props et les sous-routes.
5. Le rendu visuel de Settings et Admin est identique avant/après.
6. Les onglets de Settings (Account, Subscription, Usage) et les sections Admin (Pricing, Monitoring, Personas, Reconciliation) fonctionnent correctement.
7. Les tests existants passent sans modification.

## Tasks / Subtasks

- [ ] Tâche 1 : Lire `SettingsPage.tsx` et `SettingsTabs.tsx` (AC: 1, 3)
  - [ ] Identifier la structure actuelle : titre + tabs + `<Outlet />`
  - [ ] Lire `SettingsTabs.tsx` pour comprendre la navigation par onglets
  - [ ] Identifier les classes CSS utilisées (`.settings-layout`, `.settings-title`, `.settings-content`)

- [ ] Tâche 2 : Lire `AdminPage.tsx` et `AdminPage.css` (AC: 2, 4)
  - [ ] Identifier la structure : header + hub (grille de cards) ou detail (outlet)
  - [ ] Identifier les classes CSS spécifiques au layout admin

- [ ] Tâche 3 : Créer `SettingsLayout.tsx` (AC: 1)
  - [ ] Interface : `{ title: string; children: ReactNode; className?: string }`
  - [ ] Intégrer `SettingsTabs` directement dans `SettingsLayout` (les onglets sont une partie du layout)
  - [ ] OU exposer les tabs comme slot si la configuration doit être dynamique
  - [ ] CSS : réutiliser les classes `.settings-layout`, `.settings-title`, `.settings-content` existantes

- [ ] Tâche 4 : Créer `AdminLayout.tsx` (AC: 2)
  - [ ] Interface : `{ title: string; sections: AdminSection[]; children: ReactNode; backLabel?: string; className?: string }`
  - [ ] `AdminSection` : `{ path: string; label: string; icon: ReactNode }`
  - [ ] Extraire la logique hub/detail (isHub) dans le layout
  - [ ] CSS : réutiliser les classes `.admin-page`, `.admin-header`, `.admin-grid`, `.admin-card` existantes

- [ ] Tâche 5 : Simplifier `SettingsPage.tsx` (AC: 3)
  - [ ] Remplacer le JSX par `<SettingsLayout title={t.title}><Outlet /></SettingsLayout>`
  - [ ] La traduction du titre reste dans `SettingsPage`

- [ ] Tâche 6 : Simplifier `AdminPage.tsx` (AC: 4)
  - [ ] Passer la config des sections comme prop `sections` à `AdminLayout`
  - [ ] Les icônes SVG (PricingIcon, etc.) peuvent rester dans `AdminPage.tsx` ou être déplacées dans `AdminLayout.tsx`

- [ ] Tâche 7 : Validation (AC: 5, 6, 7)
  - [ ] Naviguer entre tous les onglets de Settings
  - [ ] Naviguer entre toutes les sections Admin et vérifier le retour au hub
  - [ ] `npm run test` — tous les tests passent

## Dev Notes

### Contexte technique

**Prérequis** : Story 51.2 `done` (PageLayout établi — SettingsLayout et AdminLayout peuvent l'utiliser comme base).

### SettingsPage.tsx actuel (19 lignes — très simple)

```tsx
export function SettingsPage() {
  const lang = detectLang()
  const { title } = settingsTranslations.page[lang]
  return (
    <div className="settings-layout">
      <h1 className="settings-title">{title}</h1>
      <SettingsTabs />
      <div className="settings-content">
        <Outlet />
      </div>
    </div>
  )
}
```

`SettingsLayout` = ce wrapper + `SettingsTabs` intégré. Après migration :

```tsx
// SettingsPage.tsx simplifié
export function SettingsPage() {
  const lang = detectLang()
  const { title } = settingsTranslations.page[lang]
  return (
    <SettingsLayout title={title}>
      <Outlet />
    </SettingsLayout>
  )
}
```

### SettingsTabs — décision d'architecture

`SettingsTabs` est un composant de navigation spécifique aux settings. Deux options :
1. **L'intégrer dans `SettingsLayout`** : `SettingsLayout` inclut `<SettingsTabs />` — simple mais couple le layout aux routes settings.
2. **Le passer en prop** : `<SettingsLayout tabs={<SettingsTabs />}>` — plus flexible.

**Recommandation** : Option 1 — `SettingsLayout` intègre `SettingsTabs`. C'est le layout du module Settings et les onglets font partie de ce layout. Si d'autres modules ont besoin d'un layout similaire, créer un `TabLayout` générique à ce moment-là (YAGNI).

### AdminPage.tsx — logique hub vs détail

`AdminPage.tsx` détecte si on est sur `/admin` (hub) ou sur une sous-route (détail) via `useLocation`. Cette logique fait partie du **layout** Admin, pas de la page de contenu. Elle doit donc aller dans `AdminLayout`.

```tsx
// AdminLayout.tsx
const location = useLocation()
const isHub = location.pathname.replace(/\/$/, '') === '/admin'

return (
  <div className="admin-page">
    <header className="admin-header">
      <h1>{title}</h1>
      {!isHub && backLabel && (
        <Link to="/admin" className="admin-back-link">{backLabel}</Link>
      )}
    </header>
    {isHub ? (
      <section className="admin-hub">
        <div className="admin-grid">
          {sections.map(section => (
            <Link key={section.path} to={section.path} className="admin-card">
              {section.icon}
              <span className="admin-card-label">{section.label}</span>
            </Link>
          ))}
        </div>
      </section>
    ) : (
      <div className="admin-content">
        {children}
      </div>
    )}
  </div>
)
```

### CSS — réutilisation des classes existantes

Ne pas créer de nouvelles classes CSS pour SettingsLayout et AdminLayout — **réutiliser les classes existantes** de `AdminPage.css` et de `App.css`. Les layouts importeront les mêmes fichiers CSS que les pages actuelles.

`AdminLayout.tsx` : `import './AdminLayout.css'` ou garder `import '../pages/AdminPage.css'`
→ Préférer créer un `AdminLayout.css` qui reprend les styles de `AdminPage.css`, puis supprimer `AdminPage.css` si AdminPage n'en a plus besoin.

### Fichiers à créer / modifier

| Action | Fichier |
|--------|---------|
| Créer | `frontend/src/layouts/SettingsLayout.tsx` |
| Créer | `frontend/src/layouts/AdminLayout.tsx` |
| Créer | `frontend/src/layouts/AdminLayout.css` |
| Modifier | `frontend/src/layouts/index.ts` |
| Modifier | `frontend/src/pages/SettingsPage.tsx` |
| Modifier | `frontend/src/pages/AdminPage.tsx` |
| Potentiellement supprimer | `frontend/src/pages/AdminPage.css` (si migré dans AdminLayout.css) |

### Project Structure Notes

- `SettingsTabs.tsx` reste dans `frontend/src/components/settings/` — `SettingsLayout` l'importe
- Les classes CSS `.settings-layout`, `.settings-title`, `.settings-content` sont probablement dans `App.css` — vérifier avant de créer un nouveau fichier CSS pour SettingsLayout
- `AdminLayout` utilise `useLocation` de React Router — déjà une dépendance du projet

### References

- [Source: frontend/src/pages/SettingsPage.tsx]
- [Source: frontend/src/pages/AdminPage.tsx]
- [Source: frontend/src/pages/AdminPage.css]
- [Source: frontend/src/components/settings/SettingsTabs.tsx]
- [Source: frontend/src/App.css]
- [Source: frontend/src/i18n/settings.ts]
- [Source: frontend/src/i18n/admin.ts]
- [Source: _bmad-output/planning-artifacts/epic-51-architecture-layouts.md]

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List
