import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { SupportOpsPanel } from "../components/SupportOpsPanel"

const mockUseSupportContext = vi.fn()
const mockUseSupportIncidents = vi.fn()
const mockUseCreateSupportIncident = vi.fn()
const mockUseUpdateSupportIncident = vi.fn()

vi.mock("../api/support", () => ({
  SupportApiError: class extends Error {},
  useSupportContext: (...args: unknown[]) => mockUseSupportContext(...args),
  useSupportIncidents: (...args: unknown[]) => mockUseSupportIncidents(...args),
  useCreateSupportIncident: () => mockUseCreateSupportIncident(),
  useUpdateSupportIncident: () => mockUseUpdateSupportIncident(),
}))

afterEach(() => {
  cleanup()
  mockUseSupportContext.mockReset()
  mockUseSupportIncidents.mockReset()
  mockUseCreateSupportIncident.mockReset()
  mockUseUpdateSupportIncident.mockReset()
})

describe("SupportOpsPanel", () => {
  it("renders and supports create/update incident", async () => {
    const createMutate = vi.fn().mockResolvedValue({
      incident_id: 12,
      status: "open",
    })
    const updateMutate = vi.fn().mockResolvedValue({
      incident_id: 12,
      status: "in_progress",
    })
    const refetchContext = vi.fn()
    const refetchIncidents = vi.fn()
    mockUseSupportContext.mockReturnValue({
      isLoading: false,
      error: null,
      data: {
        user: { user_id: 9, email: "customer@example.com", role: "user", created_at: "" },
        subscription: { status: "active", plan: { display_name: "Basic", code: "basic-entry", monthly_price_cents: 500, currency: "EUR", daily_message_limit: 5, is_active: true }, failure_reason: null, updated_at: null },
        privacy_requests: [{ request_id: 1, request_kind: "export", status: "completed", requested_at: "", completed_at: "", error_reason: null }],
        incidents: [],
        audit_events: [
          {
            event_id: 100,
            action: "support_incident_create",
            status: "success",
            target_type: "incident",
            target_id: "12",
            created_at: "",
          },
        ],
      },
      refetch: refetchContext,
    })
    mockUseSupportIncidents.mockReturnValue({
      isLoading: false,
      error: null,
      data: {
        incidents: [
          {
            incident_id: 12,
            user_id: 9,
            created_by_user_id: 2,
            assigned_to_user_id: null,
            category: "account",
            title: "Ticket",
            description: "Desc",
            status: "open",
            priority: "medium",
            resolved_at: null,
            created_at: "",
            updated_at: "",
          },
        ],
        total: 1,
        limit: 50,
        offset: 0,
      },
      refetch: refetchIncidents,
    })
    mockUseCreateSupportIncident.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: createMutate,
    })
    mockUseUpdateSupportIncident.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: updateMutate,
    })

    render(<SupportOpsPanel />)
    expect(screen.getByText("Support et operations")).toBeInTheDocument()
    expect(screen.getByText("RGPD #1 · export · completed")).toBeInTheDocument()
    expect(screen.getByText("Audit #100 · support_incident_create · success")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "Creer incident" }))
    expect(createMutate).toHaveBeenCalled()

    fireEvent.click(screen.getByRole("button", { name: "Passer en cours" }))
    expect(updateMutate).toHaveBeenCalledWith({
      incidentId: 12,
      payload: { status: "in_progress" },
    })
  })
})
