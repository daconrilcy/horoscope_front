import { describe, expect, it, vi } from "vitest"
import { fireEvent, render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"

import { Sidebar } from "../../components/layout/Sidebar"
import { SidebarProvider, useSidebarContext } from "../../state/SidebarContext"

vi.mock("../../utils/authToken", () => ({
  useAccessTokenSnapshot: () => "mock-token",
}))

vi.mock("../../api/authMe", () => ({
  useAuthMe: () => ({
    data: { role: "user" },
  }),
}))

function SidebarHarness() {
  const { toggleSidebar } = useSidebarContext()

  return (
    <MemoryRouter initialEntries={["/dashboard"]} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
      <button type="button" onClick={toggleSidebar}>toggle sidebar</button>
      <Sidebar />
    </MemoryRouter>
  )
}

describe("Sidebar", () => {
  it("starts hidden and opens as overlay with backdrop", () => {
    const { container } = render(
      <SidebarProvider>
        <SidebarHarness />
      </SidebarProvider>,
    )

    expect(container.querySelector(".app-sidebar--hidden")).toBeInTheDocument()
    expect(container.querySelector(".sidebar-backdrop")).not.toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "toggle sidebar" }))

    expect(container.querySelector(".app-sidebar--expanded")).toBeInTheDocument()
    expect(container.querySelector(".sidebar-backdrop")).toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Chat" })).toBeInTheDocument()
  })

  it("collapses to icon-only after clicking a navigation item", () => {
    const { container } = render(
      <SidebarProvider>
        <SidebarHarness />
      </SidebarProvider>,
    )

    fireEvent.click(screen.getByRole("button", { name: "toggle sidebar" }))
    fireEvent.click(screen.getByRole("link", { name: "Chat" }))

    expect(container.querySelector(".app-sidebar--icon-only")).toBeInTheDocument()
    expect(container.querySelector(".sidebar-backdrop")).not.toBeInTheDocument()
    expect(screen.getByRole("link", { name: "Chat" })).toHaveAttribute("title", "Chat")
  })
})
