import { cleanup, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it } from "vitest"
import { AdminPermissionsProvider, useAdminPermissions } from "../state/AdminPermissionsContext"

function PermissionCheck({ domain }: { domain: any }) {
  const { canEdit, canExport } = useAdminPermissions()
  return (
    <div>
      <div data-testid="can-edit">{canEdit(domain) ? "YES" : "NO"}</div>
      <div data-testid="can-export">{canExport ? "YES" : "NO"}</div>
    </div>
  )
}

afterEach(() => {
  cleanup()
})

describe("AdminPermissionsContext", () => {
  it("provides default full access for admin", () => {
    render(
      <AdminPermissionsProvider>
        <PermissionCheck domain="entitlements" />
      </AdminPermissionsProvider>
    )
    
    expect(screen.getByTestId("can-edit")).toHaveTextContent("YES")
    expect(screen.getByTestId("can-export")).toHaveTextContent("YES")
  })

  it("respects overrides", () => {
    render(
      <AdminPermissionsProvider overrides={{ canEdit: () => false, canExport: false }}>
        <PermissionCheck domain="entitlements" />
      </AdminPermissionsProvider>
    )
    
    expect(screen.getByTestId("can-edit")).toHaveTextContent("NO")
    expect(screen.getByTestId("can-export")).toHaveTextContent("NO")
  })
})
