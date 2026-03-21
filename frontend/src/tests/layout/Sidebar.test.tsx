import { describe, expect, it, vi } from "vitest"
import { fireEvent, render, screen } from "@testing-library/react"
import { MemoryRouter } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

import { Sidebar } from "../../components/layout/Sidebar"
import { SidebarProvider, useSidebarContext } from "../../state/SidebarContext"
import * as prefetchHelpers from "../../utils/prefetchHelpers"

vi.mock("../../utils/authToken", () => ({
  useAccessTokenSnapshot: () => "mock-token",
  getSubjectFromAccessToken: () => "mock-user-id",
}))

vi.mock("../../api/authMe", () => ({
  useAuthMe: () => ({
    data: { role: "user" },
  }),
}))

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
})

function SidebarHarness() {
  const { toggleSidebar } = useSidebarContext()

  return (
    <QueryClientProvider client={queryClient}>
      <MemoryRouter initialEntries={["/dashboard"]} future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <button type="button" onClick={toggleSidebar}>toggle sidebar</button>
        <Sidebar />
      </MemoryRouter>
    </QueryClientProvider>
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

  it("déclenche le préchargement lors du clic sur l'horoscope", () => {
    const prefetchSpy = vi.spyOn(prefetchHelpers, "prefetchDailyHoroscope")
    
    render(
      <SidebarProvider>
        <SidebarHarness />
      </SidebarProvider>,
    )

    fireEvent.click(screen.getByRole("button", { name: "toggle sidebar" }))
    fireEvent.click(screen.getByRole("link", { name: /Aujourd'hui/i }))

    expect(prefetchSpy).toHaveBeenCalledWith(expect.any(QueryClient), "mock-token")
  })
})
