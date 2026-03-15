# Story 58.3 : SidebarContext et Sidebar overlay à 3 états

Status: in-progress

## Story

En tant qu'utilisateur de l'application,
je veux que le menu latéral gauche soit navigable en 3 états (caché / overlay étendu avec backdrop / icônes seules),
afin de bénéficier d'un accès contextuel à la navigation sans perdre la visibilité sur le contenu principal.

## Acceptance Criteria

1. Un `SidebarContext` expose : `sidebarState: "hidden" | "expanded" | "icon-only"`, `toggleSidebar()`, `collapseSidebar()`, `closeSidebar()`.
2. **Transitions d'état** :
   - `hidden` → `toggleSidebar()` → `expanded`
   - `expanded` → `toggleSidebar()` → `hidden`
   - `icon-only` → `toggleSidebar()` → `hidden`
   - `expanded` → `collapseSidebar()` → `icon-only` (appelé par chaque NavLink onClick)
   - `any` → `closeSidebar()` → `hidden` (backdrop click ou fermeture explicite)
3. **État `expanded`** : la sidebar apparaît en `position: fixed` à gauche, avec un backdrop semi-transparent derrière elle qui assombrit le reste de la page. Chaque item affiche icône + label. Cliquer le backdrop appelle `closeSidebar()`.
4. **État `icon-only`** : bande fixe de 48px de large, visible en permanence, affiche uniquement les icônes (pas de backdrop). Un tooltip (title HTML) sur chaque icône indique le label.
5. **État `hidden`** : aucun élément de la sidebar n'est visible (`display: none` ou `transform: translateX(-100%)`).
6. Les transitions CSS sont animées (transform + opacity, durée ≈ 200ms, `ease-out`).
7. Les items de navigation utilisent les `NavItem.icon` (LucideIcon) et `NavItem.key` (pour la traduction) existants depuis `@ui/nav`.
8. Le `SidebarProvider` est un wrapper de context qui doit être intégré dans `AppLayout` (Story 58.6).
9. `useSidebarContext()` lance une erreur si utilisé hors du `SidebarProvider`.
10. `tsc --noEmit` passe. Les tests Vitest existants (≥ 1052) ne régressent pas.

## Tasks / Subtasks

- [x] T1 — Créer `SidebarContext.tsx` (AC: 1, 2, 8, 9)
  - [x] T1.1 Créer `frontend/src/state/SidebarContext.tsx` :
    ```ts
    export type SidebarState = "hidden" | "expanded" | "icon-only"

    export interface SidebarContextValue {
      sidebarState: SidebarState
      toggleSidebar: () => void
      collapseSidebar: () => void
      closeSidebar: () => void
    }

    const SidebarContext = createContext<SidebarContextValue | undefined>(undefined)

    export function SidebarProvider({ children }: { children: ReactNode }) {
      const [sidebarState, setSidebarState] = useState<SidebarState>("hidden")

      const toggleSidebar = useCallback(() => {
        setSidebarState(s => s === "hidden" ? "expanded" : "hidden")
      }, [])

      const collapseSidebar = useCallback(() => {
        setSidebarState(s => s === "expanded" ? "icon-only" : s)
      }, [])

      const closeSidebar = useCallback(() => {
        setSidebarState("hidden")
      }, [])

      return (
        <SidebarContext.Provider value={{ sidebarState, toggleSidebar, collapseSidebar, closeSidebar }}>
          {children}
        </SidebarContext.Provider>
      )
    }

    export function useSidebarContext(): SidebarContextValue {
      const ctx = useContext(SidebarContext)
      if (!ctx) throw new Error("useSidebarContext must be used within SidebarProvider")
      return ctx
    }
    ```
  - [x] T1.2 Exporter `SidebarProvider`, `useSidebarContext`, `type SidebarState` depuis ce fichier

- [x] T2 — Réécrire `Sidebar.tsx` (AC: 3, 4, 5, 6, 7)
  - [x] T2.1 Importer `useSidebarContext` depuis `@state/SidebarContext`
  - [x] T2.2 Importer `getAllNavItems` depuis `@ui/nav`
  - [x] T2.3 Importer `navigationTranslations` depuis `@i18n/navigation`
  - [x] T2.4 Importer `useAuthMe`, `useAccessTokenSnapshot` pour le filtrage par rôle
  - [x] T2.5 Structure JSX :
    ```tsx
    <>
      {/* Backdrop — visible uniquement en état expanded */}
      {sidebarState === "expanded" && (
        <div
          className="sidebar-backdrop"
          onClick={closeSidebar}
          aria-hidden="true"
        />
      )}

      {/* Sidebar panel */}
      <aside
        className={`app-sidebar app-sidebar--${sidebarState}`}
        aria-hidden={sidebarState === "hidden"}
      >
        <nav aria-label="Navigation principale">
          {navItems.map(item => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={collapseSidebar}
              className={({ isActive }) =>
                `app-sidebar-link${isActive ? " app-sidebar-link--active" : ""}`
              }
              title={translatedLabel} // tooltip en icon-only
            >
              <item.icon size={20} aria-hidden="true" />
              <span className="app-sidebar-link__label">{translatedLabel}</span>
            </NavLink>
          ))}
        </nav>
      </aside>
    </>
    ```
  - [x] T2.6 Ajouter `import "./Sidebar.css"`

- [x] T3 — Créer `Sidebar.css` (AC: 3, 4, 5, 6)
  - [x] T3.1 CSS complet :
    ```css
    /* Backdrop */
    .sidebar-backdrop {
      position: fixed;
      inset: 0;
      background: rgba(0, 0, 0, 0.5);
      z-index: 200;
      animation: fadeIn 0.2s ease-out;
    }
    @keyframes fadeIn { from { opacity: 0 } to { opacity: 1 } }

    /* Sidebar panel — base */
    .app-sidebar {
      position: fixed;
      top: 56px; /* hauteur du header */
      left: 0;
      bottom: 0;
      background: var(--glass);
      backdrop-filter: blur(var(--glass-blur));
      -webkit-backdrop-filter: blur(var(--glass-blur));
      border-right: 1px solid var(--glass-border);
      overflow: hidden;
      z-index: 201;
      transition: width 0.2s ease-out, transform 0.2s ease-out, opacity 0.2s ease-out;
    }

    /* État hidden */
    .app-sidebar--hidden {
      width: 0;
      opacity: 0;
      pointer-events: none;
      transform: translateX(-100%);
    }

    /* État expanded */
    .app-sidebar--expanded {
      width: 240px;
      opacity: 1;
      transform: translateX(0);
    }

    /* État icon-only */
    .app-sidebar--icon-only {
      width: 48px;
      opacity: 1;
      transform: translateX(0);
    }

    /* Nav items */
    .app-sidebar-link {
      display: flex;
      align-items: center;
      gap: var(--space-3);
      padding: var(--space-3) var(--space-3);
      color: var(--text-2);
      text-decoration: none;
      border-left: 3px solid transparent;
      transition: all 0.15s ease;
      white-space: nowrap;
      overflow: hidden;
    }
    .app-sidebar-link:hover {
      color: var(--text-1);
      background: var(--glass-2);
    }
    .app-sidebar-link--active {
      color: var(--text-1);
      background: var(--glass-2);
      border-left-color: var(--cta-l);
    }

    /* Label masqué en icon-only */
    .app-sidebar--icon-only .app-sidebar-link__label {
      display: none;
    }
    .app-sidebar--icon-only .app-sidebar-link {
      justify-content: center;
      padding: var(--space-3);
      border-left: none;
    }
    .app-sidebar--icon-only .app-sidebar-link--active {
      border-left: none;
      border-radius: var(--radius-md);
    }

    /* Responsive : masquer sur mobile (BottomNav prend le relai) */
    @media (max-width: 768px) {
      .app-sidebar--icon-only {
        display: none;
      }
    }
    ```

- [x] T4 — Ajuster `AppLayout.tsx` pour le décalage du contenu (AC: 8)
  - [x] T4.1 Importer `SidebarProvider` et l'utiliser comme wrapper dans `AppLayout`
  - [x] T4.2 Ajouter un `style` dynamique sur `.app-shell-main` pour le margin-left :
    ```tsx
    // Dans AppLayout, après intégration SidebarContext :
    // margin-left: 0 si hidden, 48px si icon-only, 0 si expanded (overlay)
    ```
  - **Note** : l'intégration complète de AppLayout est dans Story 58.6. Dans cette story, implémenter uniquement le SidebarProvider et les composants Sidebar/SidebarContext.

- [ ] T5 — Vérification (AC: 10)
  - [ ] T5.1 `tsc --noEmit` sans erreur
  - [x] T5.2 `npx vitest run` — 1052+ tests passent

## Dev Notes

### Machine d'état SidebarContext — récapitulatif

```
hidden ──toggleSidebar──► expanded ──toggleSidebar──► hidden
expanded ──collapseSidebar──► icon-only ──toggleSidebar──► hidden
any ──closeSidebar──► hidden
```

**Cas `icon-only` + hamburger click → `hidden`** (pas `expanded`) : cohérent avec l'UX décrite ("si l'utilisateur clique de nouveau sur l'accordéon, le menu disparaît complètement").

### Alignement z-index avec le Header

Le Header a `z-index: 100`. La sidebar doit être visible par-dessus le contenu principal mais en-dessous du Header dans certains cas (la sidebar commence sous le Header).

Valeurs z-index recommandées :
- Header : `z-index: 100` (existant)
- Backdrop : `z-index: 200`
- Sidebar panel : `z-index: 201`

La sidebar commence à `top: 56px` pour ne pas recouvrir le Header.

### Suppression anciens styles Sidebar de App.css

Les anciens styles `.app-sidebar`, `.app-sidebar-nav`, `.app-sidebar-link`, `.app-sidebar-link--active` dans `App.css` seront en conflit avec le nouveau `Sidebar.css`. **Dans cette story**, importer `Sidebar.css` dans `Sidebar.tsx` et supprimer les styles correspondants de `App.css` (ou les commenter en attendant 58.6).

Pour identifier les lignes à supprimer : chercher `/* Sidebar */` dans `App.css` (environ lignes 80-120).

### Contraintes critiques

- **`verbatimModuleSyntax: true`** : `import type { SidebarState } from "@state/SidebarContext"` pour les types purs. Pour les hooks/composants : `import { useSidebarContext, SidebarProvider } from "@state/SidebarContext"`.
- **Pas de Tailwind** — toutes les classes CSS sont définies dans `Sidebar.css`.
- **Alias `@state`** → `frontend/src/state/` — vérifier dans `vite.config.ts` et `tsconfig.json`.
- **Alias `@i18n`** → `frontend/src/i18n/` — utilisé par le Sidebar pour les traductions.

### Gestion du focus (accessibilité)

Quand la sidebar passe en état `expanded`, donner le focus au premier lien de navigation (useEffect + ref). Quand elle se ferme, redonner le focus au bouton hamburger.

### BottomNav desktop

La BottomNav existante a `display: none` sur desktop (elle s'affiche via media query ≤ 768px). Le nouveau système sidebar coexiste sans conflit.

### Project Structure Notes

- `SidebarContext.tsx` : `frontend/src/state/SidebarContext.tsx`
- `Sidebar.tsx` : `frontend/src/components/layout/Sidebar.tsx` (réécrit)
- `Sidebar.css` : `frontend/src/components/layout/Sidebar.css` (créé)
- Alias `@state` : `frontend/src/state/`
- Alias `@i18n` : `frontend/src/i18n/`
- Alias `@ui` : `frontend/src/components/ui/` ET `frontend/src/ui/` (vérifier le mapping)

### References

- Epic 58 : `_bmad-output/planning-artifacts/epic-58-global-app-shell-topbar-sidebar-user-menu.md`
- Sidebar actuelle : `frontend/src/components/layout/Sidebar.tsx`
- App.css (styles sidebar à remplacer) : `frontend/src/App.css` lignes ~80-120
- nav.ts (NavItem avec icon) : `frontend/src/ui/nav.ts`
- ThemeProvider (pattern context) : `frontend/src/state/ThemeProvider.tsx`
- navigation i18n : `frontend/src/i18n/navigation.ts`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- `npm test`
- `npm run lint`

### Completion Notes List

- Création de `SidebarContext` avec la machine d'état `hidden` / `expanded` / `icon-only` et les gardes d'usage hors provider.
- Refonte de `Sidebar.tsx` en overlay piloté par contexte avec backdrop, icônes Lucide, labels traduits et collapse sur clic de navigation.
- Intégration minimale dans `AppLayout` via `SidebarProvider` et décalage dynamique du contenu en mode `icon-only`.
- Le décalage du contenu est neutralisé sur mobile pour rester cohérent avec le masquage CSS du rail `icon-only`.
- Validation incomplète : `npm run lint` reste bloqué par un passif TypeScript global hors scope ; `npm test` est vert à 1056 tests.

### File List

- `frontend/src/state/SidebarContext.tsx` (créé)
- `frontend/src/components/layout/Sidebar.tsx` (réécrit)
- `frontend/src/components/layout/Sidebar.css` (créé)
- `frontend/src/App.css` (suppressions styles sidebar obsolètes)
- `frontend/src/layouts/AppLayout.tsx` (modifié — intégration du provider et margin-left dynamique)
- `frontend/src/tests/SidebarContext.test.tsx` (créé)
- `frontend/src/tests/layout/Sidebar.test.tsx` (créé)

### Change Log

- 2026-03-15 : Implémentation initiale de la story 58.3 avec contexte sidebar, overlay 3 états, styles dédiés et tests ciblés.
