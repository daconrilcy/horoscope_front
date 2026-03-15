import { describe, expect, it } from "vitest"
import { fireEvent, render, screen } from "@testing-library/react"

import { SidebarProvider, useSidebarContext } from "../state/SidebarContext"

function SidebarContextHarness() {
  const { sidebarState, toggleSidebar, collapseSidebar, closeSidebar } = useSidebarContext()

  return (
    <div>
      <span>{sidebarState}</span>
      <button type="button" onClick={toggleSidebar}>toggle</button>
      <button type="button" onClick={collapseSidebar}>collapse</button>
      <button type="button" onClick={closeSidebar}>close</button>
    </div>
  )
}

describe("SidebarContext", () => {
  it("throws when used outside SidebarProvider", () => {
    expect(() => render(<SidebarContextHarness />)).toThrow(
      "useSidebarContext must be used within SidebarProvider",
    )
  })

  it("applies the documented state transitions", () => {
    render(
      <SidebarProvider>
        <SidebarContextHarness />
      </SidebarProvider>,
    )

    expect(screen.getByText("hidden")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "toggle" }))
    expect(screen.getByText("expanded")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "collapse" }))
    expect(screen.getByText("icon-only")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "toggle" }))
    expect(screen.getByText("hidden")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "toggle" }))
    expect(screen.getByText("expanded")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "close" }))
    expect(screen.getByText("hidden")).toBeInTheDocument()
  })
})
