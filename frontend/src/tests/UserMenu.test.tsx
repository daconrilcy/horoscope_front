import { afterEach, describe, expect, it, vi } from "vitest"
import { fireEvent, screen } from "@testing-library/react"

import { UserMenu } from "../components/ui/UserMenu/UserMenu"
import { renderWithRouter } from "./test-utils"

const mockNavigate = vi.fn()

vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual<typeof import("react-router-dom")>("react-router-dom")
  return {
    ...actual,
    useNavigate: () => mockNavigate,
  }
})

describe("UserMenu", () => {
  afterEach(() => {
    vi.clearAllMocks()
    localStorage.clear()
  })

  it("affiche email et rôle dans l'en-tête", () => {
    renderWithRouter(
      <UserMenu email="user@example.com" role="user" isOpen onClose={vi.fn()} />,
    )

    expect(screen.getByText("user@example.com")).toBeInTheDocument()
    expect(screen.getByText("Utilisateur")).toBeInTheDocument()
  })

  it("ne rend rien quand isOpen=false", () => {
    renderWithRouter(
      <UserMenu email="a@b.com" role="user" isOpen={false} onClose={vi.fn()} />,
    )

    expect(screen.queryByRole("menu")).not.toBeInTheDocument()
  })

  it("appelle clearAccessToken et navigue vers /login au clic Déconnexion", () => {
    localStorage.setItem("access_token", "fake-token")
    const onClose = vi.fn()

    renderWithRouter(
      <UserMenu email="a@b.com" role="user" isOpen onClose={onClose} />,
    )

    fireEvent.click(screen.getByText("Se déconnecter"))

    expect(localStorage.getItem("access_token")).toBeNull()
    expect(mockNavigate).toHaveBeenCalledWith("/login", { replace: true })
    expect(onClose).toHaveBeenCalled()
  })

  it("se ferme sur touche Escape", () => {
    const onClose = vi.fn()

    renderWithRouter(
      <UserMenu email="a@b.com" role="user" isOpen onClose={onClose} />,
    )

    fireEvent.keyDown(document, { key: "Escape" })
    expect(onClose).toHaveBeenCalled()
  })

  it("navigue vers /settings au clic Modifier mon compte", () => {
    const onClose = vi.fn()

    renderWithRouter(
      <UserMenu email="a@b.com" role="user" isOpen onClose={onClose} />,
    )

    fireEvent.click(screen.getByText("Modifier mon compte"))

    expect(mockNavigate).toHaveBeenCalledWith("/settings")
    expect(onClose).toHaveBeenCalled()
  })

  it("se ferme sur clic extérieur", () => {
    const onClose = vi.fn()

    renderWithRouter(
      <div>
        <button type="button">extérieur</button>
        <UserMenu email="a@b.com" role="user" isOpen onClose={onClose} />
      </div>,
    )

    fireEvent.mouseDown(document.body)
    expect(onClose).toHaveBeenCalled()
  })
})
