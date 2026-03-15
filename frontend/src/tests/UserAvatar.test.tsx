import { describe, expect, it, vi } from "vitest"
import { fireEvent, render, screen, waitFor } from "@testing-library/react"

import { UserAvatar } from "../components/ui/UserAvatar/UserAvatar"

describe("UserAvatar", () => {
  it("affiche l'initiale de l'email quand aucun avatarUrl n'est fourni", () => {
    render(<UserAvatar email="test@example.com" />)

    expect(screen.getByText("T")).toBeInTheDocument()
    expect(screen.getByRole("img", { name: "test@example.com" })).toBeInTheDocument()
  })

  it("affiche l'image quand avatarUrl est fourni", () => {
    render(<UserAvatar email="a@b.com" avatarUrl="https://example.com/photo.jpg" />)

    expect(screen.getByRole("img", { name: "a@b.com" })).toHaveAttribute(
      "src",
      "https://example.com/photo.jpg",
    )
  })

  it("repasse sur l'initiale si l'image échoue", async () => {
    render(<UserAvatar email="a@b.com" avatarUrl="https://bad.url/photo.jpg" />)

    fireEvent.error(screen.getByRole("img", { name: "a@b.com" }))

    await waitFor(() => {
      expect(screen.getByText("A")).toBeInTheDocument()
    })
    expect(screen.getByRole("img", { name: "a@b.com" })).toBeInTheDocument()
  })

  it("rend un bouton avec aria-expanded quand onClick est fourni", () => {
    const onClick = vi.fn()

    render(<UserAvatar email="a@b.com" onClick={onClick} aria-expanded={false} />)

    const button = screen.getByRole("button", { name: "a@b.com" })
    expect(button).toHaveAttribute("aria-expanded", "false")
    expect(button).toHaveAttribute("aria-haspopup", "menu")

    fireEvent.click(button)
    expect(onClick).toHaveBeenCalledOnce()
  })

  it("applique la taille sm", () => {
    const { container } = render(<UserAvatar email="a@b.com" size="sm" />)

    expect(container.firstChild).toHaveClass("user-avatar--sm")
  })
})
