# Story 58.6 : Intégration AppLayout, nettoyage CSS et QA complète

Status: ready-for-dev

## Story

En tant que développeur,
je veux intégrer tous les nouveaux composants (SidebarProvider, Header rénové, Sidebar 3 états, UserAvatar, UserMenu) dans AppLayout, nettoyer les styles obsolètes de App.css et valider le tout par des tests et une vérification manuelle,
afin que le nouvel app shell soit cohérent, fonctionnel sur tous les écrans, accessible et sans régression.

## Acceptance Criteria

1. `AppLayout.tsx` encapsule le contenu dans `SidebarProvider` ; `Header`, `Sidebar` et `BottomNav` sont correctement orchestrés.
2. Le `main` content area a un `margin-left` dynamique selon l'état sidebar : `0px` (hidden/expanded) ou `48px` (icon-only), via CSS ou style inline conditionnel.
3. La `BottomNav` reste visible sur mobile (≤ 768px) et est masquée sur desktop (≥ 769px) — comportement inchangé.
4. Les anciens styles Header et Sidebar dans `App.css` (`.app-header-*`, `.app-sidebar`, `.app-sidebar-nav`, etc.) sont supprimés car remplacés par `Header.css` et `Sidebar.css`.
5. L'état sidebar `icon-only` masque la bande icônes sur mobile (la BottomNav suffit).
6. Tests Vitest/RTL pour : cycle complet hamburger (hidden→expanded→icon-only→hidden), UserMenu open/close/logout, UserAvatar affichage, transition dark/light.
7. `tsc --noEmit` passe sans erreur.
8. Les 1052+ tests Vitest existants passent + les nouveaux tests ajoutés dans cette story.
9. Aucune régression visuelle sur les pages : Dashboard, Chat, BirthProfile, Settings, NotFound.

## Tasks / Subtasks

- [ ] T1 — Mettre à jour `AppLayout.tsx` (AC: 1, 2)
  - [ ] T1.1 Importer `SidebarProvider`, `useSidebarContext` depuis `@state/SidebarContext`
  - [ ] T1.2 Encapsuler le rendu dans `<SidebarProvider>` :
    ```tsx
    export function AppLayout() {
      return (
        <SidebarProvider>
          <AppShell />
        </SidebarProvider>
      )
    }

    function AppShell() {
      const { sidebarState } = useSidebarContext()
      const mainMarginLeft = sidebarState === "icon-only" ? 48 : 0

      return (
        <>
          <Header />
          <div className="app-shell-body">
            <Sidebar />
            <main
              className="app-shell-main"
              style={{ marginLeft: mainMarginLeft }}
            >
              <PageErrorBoundary>
                <Outlet />
              </PageErrorBoundary>
            </main>
          </div>
          <BottomNav />
        </>
      )
    }
    ```
  - [ ] T1.3 Retirer l'import de `AppShell` s'il existait comme barrel séparé

- [ ] T2 — Nettoyage `App.css` (AC: 4)
  - [ ] T2.1 Supprimer les blocs CSS obsolètes (maintenant gérés par les fichiers CSS des composants) :
    - Bloc `/* Header */` : `.app-header`, `.app-header-brand`, `.app-header-title`, `.app-header-actions`, `.app-header-user`, `.app-header-role`, `.app-header-logout`, `.app-header--dashboard`
    - Bloc `/* Sidebar */` : `.app-sidebar`, `.app-sidebar-nav`, `.app-sidebar-link`, `.app-sidebar-link--active`
  - [ ] T2.2 Conserver dans `App.css` : `#root`, `.app-shell`, `.app-shell-body`, `.app-shell-main`, et les styles BottomNav
  - [ ] T2.3 S'assurer que la suppression ne casse aucun style visuellement (comparer avant/après)

- [ ] T3 — Transition `margin-left` du main (AC: 2)
  - [ ] T3.1 Dans `App.css`, ajouter une transition sur `.app-shell-main` :
    ```css
    .app-shell-main {
      flex: 1;
      width: 100%;
      padding: 22px 18px;
      transition: margin-left 0.2s ease-out;
    }
    ```
  - [ ] T3.2 Sur mobile (≤ 768px), forcer `margin-left: 0 !important` pour éviter le décalage (la sidebar icon-only est masquée sur mobile)

- [ ] T4 — Tests d'intégration AppLayout (AC: 6)
  - [ ] T4.1 Créer `frontend/src/tests/AppShell.test.tsx` :
    ```tsx
    describe("AppShell — cycle sidebar", () => {
      it("sidebar commence en état hidden", () => {
        renderWithRouter(<AppLayout />)
        expect(document.querySelector(".app-sidebar--hidden")).toBeInTheDocument()
        expect(document.querySelector(".sidebar-backdrop")).not.toBeInTheDocument()
      })

      it("hamburger click → sidebar expanded + backdrop visible", async () => {
        renderWithRouter(<AppLayout />)
        fireEvent.click(screen.getByRole("button", { name: /ouvrir le menu/i }))
        await waitFor(() => {
          expect(document.querySelector(".app-sidebar--expanded")).toBeInTheDocument()
          expect(document.querySelector(".sidebar-backdrop")).toBeInTheDocument()
        })
      })

      it("clic NavLink → sidebar icon-only + backdrop disparu", async () => {
        renderWithRouter(<AppLayout />, { initialEntries: ["/dashboard"] })
        fireEvent.click(screen.getByRole("button", { name: /ouvrir le menu/i }))
        await waitFor(() => expect(document.querySelector(".app-sidebar--expanded")).toBeInTheDocument())
        // clic sur un item de nav
        fireEvent.click(document.querySelector(".app-sidebar-link") as Element)
        await waitFor(() => {
          expect(document.querySelector(".app-sidebar--icon-only")).toBeInTheDocument()
          expect(document.querySelector(".sidebar-backdrop")).not.toBeInTheDocument()
        })
      })

      it("hamburger click depuis icon-only → sidebar hidden", async () => {
        renderWithRouter(<AppLayout />)
        const hamburger = screen.getByRole("button", { name: /ouvrir le menu/i })
        // hidden → expanded
        fireEvent.click(hamburger)
        await waitFor(() => expect(document.querySelector(".app-sidebar--expanded")).toBeInTheDocument())
        // expanded → icon-only (via navlink click)
        fireEvent.click(document.querySelector(".app-sidebar-link") as Element)
        await waitFor(() => expect(document.querySelector(".app-sidebar--icon-only")).toBeInTheDocument())
        // icon-only → hidden
        fireEvent.click(hamburger)
        await waitFor(() => expect(document.querySelector(".app-sidebar--hidden")).toBeInTheDocument())
      })
    })

    describe("AppShell — toggle thème", () => {
      it("bouton toggle thème est cliquable et change le thème", () => {
        renderWithRouter(<AppLayout />)
        const toggle = screen.getByRole("button", { name: /changer le thème/i })
        expect(toggle).toBeInTheDocument()
        fireEvent.click(toggle)
        // vérifier que document.documentElement a/n'a pas la class "dark"
        // (la classe est togglée par ThemeProvider)
      })
    })
    ```

- [ ] T5 — Tests UserMenu dans Header (AC: 6)
  - [ ] T5.1 Dans `AppShell.test.tsx`, ajouter :
    ```tsx
    describe("AppShell — UserMenu", () => {
      it("avatar click → UserMenu visible", async () => {
        vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
          ok: true, status: 200,
          json: async () => ({ data: { id: 1, role: "user", email: "a@b.com" } })
        }))
        renderWithRouter(<AppLayout />)
        await waitFor(() => {
          const avatar = screen.getByRole("button", { name: /menu utilisateur/i })
          fireEvent.click(avatar)
        })
        await waitFor(() => expect(screen.getByRole("menu")).toBeInTheDocument())
      })
    })
    ```

- [ ] T6 — Vérifications finales (AC: 7, 8, 9)
  - [ ] T6.1 `tsc --noEmit` — 0 erreur
  - [ ] T6.2 `npx vitest run` — tous les tests passent (≥ 1052 existants + nouveaux)
  - [ ] T6.3 Vérification manuelle (si serveur dev disponible) :
    - [ ] Dashboard, Chat, Natal, Consultations, Settings → chaque page affiche header + sidebar corrects
    - [ ] Cycle hamburger fonctionne
    - [ ] Avatar menu s'ouvre/ferme/déconnecte
    - [ ] Dark/light toggle fonctionne
    - [ ] Mobile (768px) : BottomNav visible, sidebar icon-only masquée
  - [ ] T6.4 Mettre à jour `sprint-status.yaml` : `epic-58` → toutes stories `done`

## Dev Notes

### Ordre d'implémentation recommandé

Pour éviter les imports cassés pendant le développement, implémenter dans cet ordre :
1. **58.1** → APP_NAME, APP_LOGO
2. **58.4** → UserAvatar (composant indépendant)
3. **58.3** → SidebarContext + Sidebar
4. **58.5** → UserMenu (dépend de UserAvatar)
5. **58.2** → Header (dépend de SidebarContext + UserAvatar + UserMenu)
6. **58.6** → AppLayout integration + QA (dépend de tout)

### Conflit potentiel `margin-left` vs sidebar overlay

La sidebar en état `expanded` est un **overlay** (position: fixed) → pas de changement de layout du contenu.
La sidebar en état `icon-only` est fixe (48px) → le contenu doit décaler de 48px.

Sur desktop, `margin-left: 48px` sur `.app-shell-main` quand `icon-only`. Sur mobile, la sidebar icon-only est masquée (display: none via media query dans Sidebar.css) → pas de décalage.

```tsx
// Dans AppShell (AppLayout.tsx)
const mainStyle = sidebarState === "icon-only"
  ? { marginLeft: 48, transition: "margin-left 0.2s ease-out" }
  : { marginLeft: 0, transition: "margin-left 0.2s ease-out" }
```

### Nettoyage App.css — lignes approximatives à supprimer

Rechercher dans `App.css` :
- `/* Header */` → supprimer jusqu'à la prochaine section commentaire
- `/* Sidebar */` → supprimer jusqu'à `/* === BottomNav ===`
- Garder impérativement : `#root`, `.app-shell`, `.app-shell-body`, `.app-shell-main`, `/* === BottomNav ===` et tout ce qui suit

### Gestion des tests qui utilisent `useAuthMe`

Le Header fait appel à `useAuthMe(token)` qui fait un fetch sur `/v1/auth/me`. Dans les tests AppShell, mocker fetch globalement (comme montré en T5.1). Sans mock, useAuthMe retournera `undefined` et l'avatar affichera "?" — acceptable pour les tests de cycle sidebar.

### Pattern `renderWithRouter` dans les tests

`renderWithRouter` (dans `test-utils.tsx`) encapsule dans `MemoryRouter` + `QueryClientProvider` mais **pas** dans `ThemeProvider`. Si ThemeProvider est requis (pour le toggle dark/light), encapsuler manuellement :
```tsx
import { ThemeProvider } from "@state/ThemeProvider"
render(
  <ThemeProvider>
    {renderWithRouter(/* ... */)}
  </ThemeProvider>
)
```
Ou créer un helper `renderWithProviders` qui inclut ThemeProvider.

### Suppression `AppShell` barrel

`frontend/src/components/AppShell.tsx` était un simple re-export de `AppLayout`. Vérifier s'il existe et s'il est importé quelque part — si oui, rediriger les imports vers `@layouts/AppLayout`.

### Project Structure Notes

- `AppLayout.tsx` : `frontend/src/layouts/AppLayout.tsx`
- `App.css` : `frontend/src/App.css`
- Tests : `frontend/src/tests/AppShell.test.tsx`
- `SidebarContext` : `frontend/src/state/SidebarContext.tsx`
- Alias `@layouts` → `frontend/src/layouts/`
- Alias `@state` → `frontend/src/state/`

### References

- Epic 58 : `_bmad-output/planning-artifacts/epic-58-global-app-shell-topbar-sidebar-user-menu.md`
- AppLayout actuel : `frontend/src/layouts/AppLayout.tsx`
- App.css : `frontend/src/App.css`
- providers.tsx : `frontend/src/state/providers.tsx`
- test-utils : `frontend/src/tests/test-utils.tsx`
- ThemeProvider : `frontend/src/state/ThemeProvider.tsx`
- Story 58.1 : `_bmad-output/implementation-artifacts/58-1-app-name-constante-et-config-centrale.md`
- Story 58.2 : `_bmad-output/implementation-artifacts/58-2-header-hamburger-logo-nom-actions.md`
- Story 58.3 : `_bmad-output/implementation-artifacts/58-3-sidebar-context-et-overlay-3-etats.md`
- Story 58.4 : `_bmad-output/implementation-artifacts/58-4-composant-user-avatar.md`
- Story 58.5 : `_bmad-output/implementation-artifacts/58-5-menu-utilisateur-flottant.md`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `frontend/src/layouts/AppLayout.tsx` (modifié — SidebarProvider + margin dynamique)
- `frontend/src/App.css` (modifié — suppression styles Header/Sidebar obsolètes)
- `frontend/src/tests/AppShell.test.tsx` (créé)
