import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { SupportOpsPanel } from "../components/SupportOpsPanel"

const mockUseOpsSearchUser = vi.fn()
const mockUseOpsRollbackPersona = vi.fn()

vi.mock("@api", () => ({
  useOpsSearchUser: (...args: unknown[]) => mockUseOpsSearchUser(...args),
  useOpsRollbackPersona: () => mockUseOpsRollbackPersona(),
}))

afterEach(() => {
  cleanup()
  mockUseOpsSearchUser.mockReset()
  mockUseOpsRollbackPersona.mockReset()
})

describe("SupportOpsPanel", () => {
  it("renders and supports search and rollback", async () => {
    const refetch = vi.fn()
    const rollbackMutate = vi.fn()
    mockUseOpsSearchUser.mockReturnValue({
      isPending: false,
      error: null,
      data: {
        privacy_requests: [
          { request_id: 1, type: "export", status: "completed", created_at: "2026-03-01T00:00:00Z" }
        ],
        audit_log: [
          { event_id: 100, action: "auth_login", timestamp: "2026-03-01T10:00:00Z" }
        ]
      },
      refetch,
    })
    mockUseOpsRollbackPersona.mockReturnValue({
      isPending: false,
      mutate: rollbackMutate,
    })

    render(<SupportOpsPanel />)
    expect(screen.getByText("Support et opérations")).toBeInTheDocument()
    
    expect(screen.getByText(/Demandes RGPD: 1/i)).toBeInTheDocument()
    expect(screen.getByText(/export - completed/i)).toBeInTheDocument()
    expect(screen.getByText(/auth_login/i)).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: /Search/i }))
    expect(refetch).toHaveBeenCalled()

    fireEvent.click(screen.getByRole("button", { name: /Global System Rollback/i }))
    expect(rollbackMutate).toHaveBeenCalled()
  })
})
