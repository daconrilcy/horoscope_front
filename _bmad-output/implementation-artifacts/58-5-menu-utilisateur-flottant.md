# Story 58.5 : Menu utilisateur flottant (overlay au clic sur l'avatar)

Status: ready-for-dev

## Story

En tant qu'utilisateur connecté,
je veux que cliquer sur mon avatar ouvre un menu flottant avec mes informations et des actions rapides,
afin d'accéder à mon profil, mes paramètres et la déconnexion sans quitter la page courante.

## Acceptance Criteria

1. Le composant `UserMenu` est un overlay flottant qui s'affiche sous l'avatar dans le Header.
2. **En-tête du menu** : `UserAvatar` (taille `lg`) + email de l'utilisateur + rôle (traduit).
3. **Trois items** (dans l'ordre) :
   - "Modifier mon compte" → navigate `/settings`
   - "Déconnexion" → `clearAccessToken()` + navigate `/login`
   - "Paramètres" → navigate `/settings` (page dédiée future ; pour l'instant même route que Modifier)
4. Le menu se ferme sur : clic en dehors du menu (`mousedown` + `touchstart`), touche `Escape`, clic sur un item.
5. Le menu est accessible : `role="menu"`, chaque item a `role="menuitem"`, navigation clavier possible (Tab/Shift+Tab).
6. Animations d'apparition : `opacity 0→1` + légère translation verticale (`translateY(-8px)→translateY(0)`), durée 150ms.
7. Les labels sont traduits en fr/en/es via `useTranslation('common')` (extension de `CommonTranslation`).
8. La déconnexion appelle `clearAccessToken()` (depuis `@utils/authToken`) puis `navigate("/login", { replace: true })`.
9. `tsc --noEmit` passe. Les tests Vitest existants (≥ 1052) ne régressent pas.
10. Tests unitaires : menu s'ouvre/ferme, déconnexion efface le token, navigation fonctionne.

## Tasks / Subtasks

- [ ] T1 — Étendre `CommonTranslation` avec les labels du menu utilisateur (AC: 7)
  - [ ] T1.1 Dans `frontend/src/i18n/common.ts`, ajouter dans l'interface :
    ```ts
    userMenu: {
      editAccount: string    // "Modifier mon compte" / "Edit account" / "Editar cuenta"
      logout: string         // "Se déconnecter" / "Log out" / "Cerrar sesión"
      settings: string       // "Paramètres" / "Settings" / "Configuración"
    }
    ```
  - [ ] T1.2 Ajouter les traductions pour fr, en, es
  - [ ] T1.3 Note : `header.logout` existant peut rester (utilisé ailleurs) — `userMenu.logout` peut avoir le même libellé

- [ ] T2 — Créer `UserMenu.tsx` (AC: 1-8)
  - [ ] T2.1 Créer le dossier `frontend/src/components/ui/UserMenu/`
  - [ ] T2.2 Créer `frontend/src/components/ui/UserMenu/UserMenu.tsx` :
    ```tsx
    import { useEffect, useRef } from "react"
    import { useNavigate } from "react-router-dom"
    import { UserAvatar } from "../UserAvatar/UserAvatar"
    import { clearAccessToken } from "@utils/authToken"
    import { useTranslation } from "@i18n"
    import "./UserMenu.css"

    export interface UserMenuProps {
      email: string
      role: string
      avatarUrl?: string
      isOpen: boolean
      onClose: () => void
    }

    export function UserMenu({ email, role, avatarUrl, isOpen, onClose }: UserMenuProps) {
      const navigate = useNavigate()
      const t = useTranslation("common")
      const menuRef = useRef<HTMLDivElement>(null)

      // Fermeture sur clic extérieur
      useEffect(() => {
        if (!isOpen) return
        const handleOutside = (e: MouseEvent | TouchEvent) => {
          if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
            onClose()
          }
        }
        document.addEventListener("mousedown", handleOutside)
        document.addEventListener("touchstart", handleOutside)
        return () => {
          document.removeEventListener("mousedown", handleOutside)
          document.removeEventListener("touchstart", handleOutside)
        }
      }, [isOpen, onClose])

      // Fermeture sur Escape
      useEffect(() => {
        if (!isOpen) return
        const handleKey = (e: KeyboardEvent) => {
          if (e.key === "Escape") onClose()
        }
        document.addEventListener("keydown", handleKey)
        return () => document.removeEventListener("keydown", handleKey)
      }, [isOpen, onClose])

      if (!isOpen) return null

      const handleLogout = () => {
        clearAccessToken()
        onClose()
        navigate("/login", { replace: true })
      }

      const handleNavigate = (path: string) => {
        onClose()
        navigate(path)
      }

      return (
        <div
          ref={menuRef}
          className="user-menu"
          role="menu"
          aria-label="Menu utilisateur"
        >
          {/* En-tête */}
          <div className="user-menu__header">
            <UserAvatar email={email} avatarUrl={avatarUrl} size="lg" />
            <div className="user-menu__user-info">
              <span className="user-menu__email">{email}</span>
              <span className="user-menu__role">{role}</span>
            </div>
          </div>

          {/* Séparateur */}
          <div className="user-menu__divider" role="separator" />

          {/* Items */}
          <button
            type="button"
            role="menuitem"
            className="user-menu__item"
            onClick={() => handleNavigate("/settings")}
          >
            {t.userMenu.editAccount}
          </button>
          <button
            type="button"
            role="menuitem"
            className="user-menu__item"
            onClick={handleLogout}
          >
            {t.userMenu.logout}
          </button>
          <button
            type="button"
            role="menuitem"
            className="user-menu__item"
            onClick={() => handleNavigate("/settings")}
          >
            {t.userMenu.settings}
          </button>
        </div>
      )
    }
    ```

- [ ] T3 — Créer `UserMenu.css` (AC: 1, 6)
  - [ ] T3.1 Créer `frontend/src/components/ui/UserMenu/UserMenu.css` :
    ```css
    .user-menu {
      position: absolute;
      top: calc(100% + var(--space-2));
      right: 0;
      min-width: 220px;
      background: var(--glass);
      backdrop-filter: blur(var(--glass-blur));
      -webkit-backdrop-filter: blur(var(--glass-blur));
      border: 1px solid var(--glass-border);
      border-radius: var(--radius-lg, 12px);
      box-shadow: 0 8px 32px rgba(0,0,0,0.2);
      z-index: 300;
      overflow: hidden;
      animation: userMenuEnter 0.15s ease-out;
    }
    @keyframes userMenuEnter {
      from { opacity: 0; transform: translateY(-8px); }
      to   { opacity: 1; transform: translateY(0); }
    }

    .user-menu__header {
      display: flex;
      align-items: center;
      gap: var(--space-3);
      padding: var(--space-4);
    }

    .user-menu__user-info {
      display: flex;
      flex-direction: column;
      gap: var(--space-1);
      overflow: hidden;
    }
    .user-menu__email {
      font-size: var(--font-size-sm, 0.875rem);
      color: var(--text-1);
      font-weight: var(--font-weight-semibold, 600);
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
    .user-menu__role {
      font-size: var(--font-size-xs, 0.75rem);
      color: var(--text-2);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }

    .user-menu__divider {
      height: 1px;
      background: var(--glass-border);
      margin: 0;
    }

    .user-menu__item {
      display: flex;
      align-items: center;
      width: 100%;
      padding: var(--space-3) var(--space-4);
      background: none;
      border: none;
      color: var(--text-1);
      font-size: var(--font-size-sm, 0.875rem);
      cursor: pointer;
      text-align: left;
      transition: background 0.15s ease;
    }
    .user-menu__item:hover {
      background: var(--glass-2);
    }
    .user-menu__item:focus-visible {
      outline: 2px solid var(--primary);
      outline-offset: -2px;
    }
    ```

- [ ] T4 — Exporter depuis le barrel UI (AC: 7)
  - [ ] T4.1 Dans `frontend/src/components/ui/index.ts`, ajouter :
    ```ts
    export * from './UserMenu/UserMenu';
    ```

- [ ] T5 — Tests unitaires (AC: 10)
  - [ ] T5.1 Créer `frontend/src/tests/UserMenu.test.tsx` :
    ```tsx
    // Mock navigate
    const mockNavigate = vi.fn()
    vi.mock("react-router-dom", async () => {
      const actual = await vi.importActual("react-router-dom")
      return { ...actual, useNavigate: () => mockNavigate }
    })

    describe("UserMenu", () => {
      afterEach(() => {
        cleanup()
        vi.clearAllMocks()
        localStorage.clear()
      })

      it("affiche email et rôle dans l'en-tête", () => {
        renderWithRouter(
          <UserMenu email="user@example.com" role="user" isOpen onClose={vi.fn()} />
        )
        expect(screen.getByText("user@example.com")).toBeInTheDocument()
        expect(screen.getByText("user")).toBeInTheDocument()
      })

      it("ne rend rien quand isOpen=false", () => {
        renderWithRouter(
          <UserMenu email="a@b.com" role="user" isOpen={false} onClose={vi.fn()} />
        )
        expect(screen.queryByRole("menu")).not.toBeInTheDocument()
      })

      it("appelle clearAccessToken et navigue vers /login au clic Déconnexion", async () => {
        localStorage.setItem("access_token", "fake-token")
        const onClose = vi.fn()
        renderWithRouter(
          <UserMenu email="a@b.com" role="user" isOpen onClose={onClose} />
        )
        fireEvent.click(screen.getByText("Se déconnecter"))
        expect(localStorage.getItem("access_token")).toBeNull()
        expect(mockNavigate).toHaveBeenCalledWith("/login", { replace: true })
        expect(onClose).toHaveBeenCalled()
      })

      it("se ferme sur touche Escape", async () => {
        const onClose = vi.fn()
        renderWithRouter(
          <UserMenu email="a@b.com" role="user" isOpen onClose={onClose} />
        )
        fireEvent.keyDown(document, { key: "Escape" })
        expect(onClose).toHaveBeenCalled()
      })

      it("navigue vers /settings au clic Modifier mon compte", () => {
        const onClose = vi.fn()
        renderWithRouter(
          <UserMenu email="a@b.com" role="user" isOpen onClose={onClose} />
        )
        fireEvent.click(screen.getByText("Modifier mon compte"))
        expect(mockNavigate).toHaveBeenCalledWith("/settings")
        expect(onClose).toHaveBeenCalled()
      })
    })
    ```

- [ ] T6 — Vérification (AC: 9)
  - [ ] T6.1 `tsc --noEmit` sans erreur
  - [ ] T6.2 `npx vitest run` — 1052+ tests passent (+ nouveaux tests UserMenu)

## Dev Notes

### Positionnement absolu du menu

Le `UserMenu` est positionné `absolute` par rapport à son parent `.app-header-avatar-wrapper` (qui doit avoir `position: relative`). C'est géré dans Story 58.2 (`Header.tsx`). Ne pas mettre `position: fixed` sur le UserMenu — il doit rester ancré à l'avatar.

### `useTranslation` et accès aux nouveaux labels

`useTranslation("common")` retourne `CommonTranslation`. Les nouveaux champs `userMenu.*` doivent être ajoutés à l'interface `CommonTranslation` dans `common.ts` (T1) **avant** d'écrire le composant pour que TypeScript valide l'accès.

Sinon, utiliser une solution de contournement temporaire :
```ts
const t = useTranslation("common")
const menuLabels = (t as any).userMenu || {
  editAccount: "Modifier mon compte",
  logout: "Se déconnecter",
  settings: "Paramètres"
}
```

### Fermeture sur clic extérieur — pattern de référence

Ce pattern est identique à celui utilisé dans `VersionSelector` de `NatalInterpretation.tsx` :
```ts
useEffect(() => {
  if (!isOpen) return
  const handleOutsideClick = (event: MouseEvent | TouchEvent) => {
    if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
      onClose()
    }
  }
  document.addEventListener("mousedown", handleOutsideClick)
  document.addEventListener("touchstart", handleOutsideClick)
  return () => {
    document.removeEventListener("mousedown", handleOutsideClick)
    document.removeEventListener("touchstart", handleOutsideClick)
  }
}, [isOpen, onClose])
```

### Mock `useNavigate` dans les tests

`UserMenu` appelle `useNavigate()`. Dans les tests RTL, utiliser `renderWithRouter` (qui encapsule dans `MemoryRouter`). Pour capturer les navigations, mocker `useNavigate` comme montré dans T5.1.

Alternative : utiliser `renderWithRouter` avec `initialEntries` et vérifier que `window.location` change — mais le mock est plus fiable.

### Contraintes critiques

- **`clearAccessToken()`** : importé depuis `@utils/authToken` (pas de logique locale).
- **`verbatimModuleSyntax`** : `import type { UserMenuProps }` pour les types, `import { UserMenu }` pour la valeur.
- **Pas de Tailwind** — CSS custom uniquement.

### Project Structure Notes

- `UserMenu.tsx` : `frontend/src/components/ui/UserMenu/UserMenu.tsx`
- `UserMenu.css` : `frontend/src/components/ui/UserMenu/UserMenu.css`
- Tests : `frontend/src/tests/UserMenu.test.tsx`
- `clearAccessToken` : `frontend/src/utils/authToken.ts`

### References

- Epic 58 : `_bmad-output/planning-artifacts/epic-58-global-app-shell-topbar-sidebar-user-menu.md`
- Pattern fermeture clic extérieur : `frontend/src/components/NatalInterpretation.tsx` (VersionSelector)
- `clearAccessToken` : `frontend/src/utils/authToken.ts`
- `useTranslation` hook : `frontend/src/i18n/index.ts`
- `common.ts` i18n : `frontend/src/i18n/common.ts`
- `UserAvatar` (dépendance) : `frontend/src/components/ui/UserAvatar/UserAvatar.tsx`
- test-utils : `frontend/src/tests/test-utils.tsx`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

### Completion Notes List

### File List

- `frontend/src/components/ui/UserMenu/UserMenu.tsx` (créé)
- `frontend/src/components/ui/UserMenu/UserMenu.css` (créé)
- `frontend/src/components/ui/index.ts` (modifié — ajout UserMenu)
- `frontend/src/i18n/common.ts` (modifié — ajout userMenu translations)
- `frontend/src/tests/UserMenu.test.tsx` (créé)
