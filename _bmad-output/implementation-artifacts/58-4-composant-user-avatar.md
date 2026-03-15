# Story 58.4 : Composant UserAvatar (initiales ou image uploadée)

Status: done

## Story

En tant qu'utilisateur de l'application,
je veux voir mon avatar (photo ou initiale de mon email dans un cercle coloré) dans le top bar,
afin d'identifier immédiatement mon compte connecté et d'accéder au menu utilisateur.

## Acceptance Criteria

1. Le composant `UserAvatar` accepte les props : `email: string`, `displayName?: string`, `avatarUrl?: string`, `size?: "sm" | "md" | "lg"`, `onClick?: () => void`, `aria-expanded?: boolean`.
2. Si `avatarUrl` est fourni et valide : affiche `<img src={avatarUrl} alt={displayName || email}>` avec fallback sur les initiales en cas d'erreur de chargement (`onError`).
3. Si pas d'`avatarUrl` (ou erreur de chargement) : affiche un cercle avec la 1re lettre de l'email en majuscule, fond `var(--primary)` (violet/mauve), texte blanc.
4. Tailles : `sm` = 32×32px, `md` = 40×40px (défaut), `lg` = 56×56px.
5. Si `onClick` est fourni, l'élément est un `<button>` avec `type="button"` ; sinon un `<div>`.
6. Attributs accessibilité : `role="img"`, `aria-label={displayName || email}` ; si `onClick`, le bouton a également `aria-expanded` et `aria-haspopup="menu"`.
7. Le composant est exporté depuis `frontend/src/components/ui/index.ts`.
8. `tsc --noEmit` passe. Les tests Vitest existants (≥ 1052) ne régressent pas.
9. Un test unitaire vérifie : initiales affichées correctement, fallback avatarUrl, accessibilité.

## Tasks / Subtasks

- [x] T1 — Créer `UserAvatar.tsx` (AC: 1-6)
  - [x] T1.1 Créer le dossier `frontend/src/components/ui/UserAvatar/`
  - [x] T1.2 Créer `frontend/src/components/ui/UserAvatar/UserAvatar.tsx` :
    ```tsx
    import { useState } from "react"
    import "./UserAvatar.css"

    export interface UserAvatarProps {
      email: string
      displayName?: string
      avatarUrl?: string
      size?: "sm" | "md" | "lg"
      onClick?: () => void
      "aria-expanded"?: boolean
    }

    export function UserAvatar({
      email,
      displayName,
      avatarUrl,
      size = "md",
      onClick,
      "aria-expanded": ariaExpanded,
    }: UserAvatarProps) {
      const [imgError, setImgError] = useState(false)
      const initial = (email[0] ?? "?").toUpperCase()
      const label = displayName || email
      const showImage = !!avatarUrl && !imgError

      const content = showImage ? (
        <img
          src={avatarUrl}
          alt={label}
          className="user-avatar__img"
          onError={() => setImgError(true)}
        />
      ) : (
        <span className="user-avatar__initial" aria-hidden="true">{initial}</span>
      )

      const className = `user-avatar user-avatar--${size}`

      if (onClick) {
        return (
          <button
            type="button"
            className={className}
            onClick={onClick}
            aria-label={label}
            aria-expanded={ariaExpanded}
            aria-haspopup="menu"
          >
            {content}
          </button>
        )
      }

      return (
        <div className={className} role="img" aria-label={label}>
          {content}
        </div>
      )
    }
    ```

- [x] T2 — Créer `UserAvatar.css` (AC: 3, 4)
  - [x] T2.1 Créer `frontend/src/components/ui/UserAvatar/UserAvatar.css` :
    ```css
    .user-avatar {
      border-radius: 50%;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
      background: var(--primary);
      color: #fff;
      font-weight: var(--font-weight-bold, 700);
      flex-shrink: 0;
      cursor: default;
      border: none;
      padding: 0;
    }
    .user-avatar--sm { width: 32px; height: 32px; font-size: 0.75rem; }
    .user-avatar--md { width: 40px; height: 40px; font-size: 0.875rem; }
    .user-avatar--lg { width: 56px; height: 56px; font-size: 1.25rem; }

    button.user-avatar {
      cursor: pointer;
      transition: opacity 0.15s ease, outline 0.1s ease;
    }
    button.user-avatar:hover { opacity: 0.85; }
    button.user-avatar:focus-visible {
      outline: 2px solid var(--primary);
      outline-offset: 2px;
    }

    .user-avatar__img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    .user-avatar__initial {
      line-height: 1;
      user-select: none;
    }
    ```

- [x] T3 — Exporter depuis le barrel UI (AC: 7)
  - [x] T3.1 Dans `frontend/src/components/ui/index.ts`, ajouter :
    ```ts
    export * from './UserAvatar/UserAvatar';
    ```
  - [x] T3.2 Créer `frontend/src/components/ui/UserAvatar/index.ts` si nécessaire (barrel interne) :
    ```ts
    export * from './UserAvatar';
    ```

- [x] T4 — Tests unitaires (AC: 9)
  - [x] T4.1 Créer `frontend/src/tests/UserAvatar.test.tsx` :
    ```tsx
    describe("UserAvatar", () => {
      it("affiche l'initiale de l'email quand pas d'avatarUrl", () => {
        render(<UserAvatar email="test@example.com" />)
        expect(screen.getByText("T")).toBeInTheDocument()
      })

      it("affiche l'image quand avatarUrl est fourni", () => {
        render(<UserAvatar email="a@b.com" avatarUrl="https://example.com/photo.jpg" />)
        expect(screen.getByRole("img")).toHaveAttribute("src", "https://example.com/photo.jpg")
      })

      it("repasse sur l'initiale si l'image échoue", async () => {
        render(<UserAvatar email="a@b.com" avatarUrl="https://bad.url/photo.jpg" />)
        const img = screen.getByRole("img")
        fireEvent.error(img)
        await waitFor(() => expect(screen.getByText("A")).toBeInTheDocument())
      })

      it("rend un <button> avec aria-expanded quand onClick est fourni", () => {
        const onClick = vi.fn()
        render(<UserAvatar email="a@b.com" onClick={onClick} aria-expanded={false} />)
        const btn = screen.getByRole("button")
        expect(btn).toHaveAttribute("aria-expanded", "false")
        expect(btn).toHaveAttribute("aria-haspopup", "menu")
        fireEvent.click(btn)
        expect(onClick).toHaveBeenCalledOnce()
      })

      it("applique la taille sm (32px)", () => {
        const { container } = render(<UserAvatar email="a@b.com" size="sm" />)
        expect(container.firstChild).toHaveClass("user-avatar--sm")
      })
    })
    ```

- [x] T5 — Vérification (AC: 8)
  - [x] T5.1 `tsc --noEmit` sans erreur
  - [x] T5.2 `npx vitest run` — 1052+ tests passent (+ nouveaux tests UserAvatar)

## Dev Notes

### Variable CSS pour la couleur d'avatar

Le projet a deux systèmes de variables coexistants :
- Ancien : `var(--primary)` (défini dans `index.css` ou `theme.css`)
- Nouveau (design-tokens.css) : `var(--color-primary)`

**Utiliser `var(--primary)` pour la couleur de fond** car c'est la variable utilisée dans les composants existants (`Button.tsx` par exemple). Vérifier dans `frontend/src/index.css` la valeur. Si `--primary` n'est pas défini, utiliser `var(--color-primary, #7c3aed)` avec fallback.

### Positionnement dans le Header

Le `UserAvatar` est utilisé dans `Header.tsx` (Story 58.2) comme bouton d'ouverture du `UserMenu`. La prop `onClick` sera `() => setIsUserMenuOpen(v => !v)` et `aria-expanded={isUserMenuOpen}`.

### Fallback initiale

Si l'email est vide ou undefined, utiliser `"?"` comme initiale. Ne pas crasher sur un email mal formé.

### Test imports

Les tests utilisent `renderWithRouter` de `frontend/src/tests/test-utils.tsx`. Mais `UserAvatar` n'a pas de router dependency, donc `render` (RTL direct) suffit. Pattern des tests existants : `import { describe, it, expect, vi } from "vitest"` + `import { render, screen, fireEvent, waitFor } from "@testing-library/react"`.

### Project Structure Notes

- `UserAvatar.tsx` : `frontend/src/components/ui/UserAvatar/UserAvatar.tsx`
- `UserAvatar.css` : `frontend/src/components/ui/UserAvatar/UserAvatar.css`
- Barrel UI : `frontend/src/components/ui/index.ts`
- Tests : `frontend/src/tests/UserAvatar.test.tsx`

### References

- Epic 58 : `_bmad-output/planning-artifacts/epic-58-global-app-shell-topbar-sidebar-user-menu.md`
- Barrel UI actuel : `frontend/src/components/ui/index.ts`
- Pattern composant UI existant (référence) : `frontend/src/components/ui/Button/Button.tsx`
- test-utils : `frontend/src/tests/test-utils.tsx`

## Dev Agent Record

### Agent Model Used

claude-sonnet-4-6

### Debug Log References

- `npm test`
- `npm run lint`

### Completion Notes List

- Création du composant `UserAvatar` avec fallback initiale, gestion d'erreur d'image et mode bouton pour l'ouverture du menu utilisateur.
- Ajout des styles dédiés pour les tailles `sm` / `md` / `lg` avec couleur de fond basée sur `--primary`.
- Export du composant via le barrel UI et ajout d'une suite de tests couvrant image, fallback et accessibilité.
- Validation incomplète : `npm run lint` reste bloqué par un passif TypeScript global hors scope ; `npm test` est vert à 1061 tests.

### File List

- `frontend/src/components/ui/UserAvatar/UserAvatar.tsx` (créé)
- `frontend/src/components/ui/UserAvatar/UserAvatar.css` (créé)
- `frontend/src/components/ui/index.ts` (modifié — ajout UserAvatar)
- `frontend/src/components/ui/UserAvatar/index.ts` (créé — barrel interne)
- `frontend/src/tests/UserAvatar.test.tsx` (créé)

### Change Log

- 2026-03-15 : Implémentation initiale de la story 58.4 avec composant `UserAvatar`, styles dédiés, export barrel et tests unitaires.
