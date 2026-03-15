import { createContext, useCallback, useContext, useState } from "react"
import type { ReactNode } from "react"

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
    setSidebarState((state) => (state === "hidden" ? "expanded" : "hidden"))
  }, [])

  const collapseSidebar = useCallback(() => {
    setSidebarState((state) => (state === "expanded" ? "icon-only" : state))
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
  const context = useContext(SidebarContext)
  if (context === undefined) {
    throw new Error("useSidebarContext must be used within SidebarProvider")
  }
  return context
}
