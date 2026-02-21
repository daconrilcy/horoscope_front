import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { OpsMonitoringPanel } from "../components/OpsMonitoringPanel"

const mockUseConversationKpis = vi.fn()
const mockUseRollbackPersonaConfig = vi.fn()

vi.mock("../api/opsMonitoring", () => ({
  OpsMonitoringApiError: class extends Error {},
  useConversationKpis: (...args: unknown[]) => mockUseConversationKpis(...args),
}))

vi.mock("../api/opsPersona", () => ({
  useRollbackPersonaConfig: () => mockUseRollbackPersonaConfig(),
}))

afterEach(() => {
  cleanup()
  mockUseConversationKpis.mockReset()
  mockUseRollbackPersonaConfig.mockReset()
})

describe("OpsMonitoringPanel", () => {
  it("renders kpis and triggers rollback", () => {
    const refetch = vi.fn()
    const rollbackMutate = vi.fn()
    mockUseConversationKpis.mockReturnValue({
      isPending: false,
      isFetching: false,
      error: null,
      data: {
        window: "24h",
        aggregation_scope: "instance_local",
        messages_total: 100,
        out_of_scope_count: 8,
        out_of_scope_rate: 0.08,
        llm_error_count: 3,
        llm_error_rate: 0.03,
        p95_latency_ms: 420,
      },
      refetch,
    })
    mockUseRollbackPersonaConfig.mockReturnValue({
      isPending: false,
      isSuccess: false,
      error: null,
      mutate: rollbackMutate,
    })

    render(<OpsMonitoringPanel />)

    expect(screen.getByText("Portee aggregation: instance_local")).toBeInTheDocument()
    expect(screen.getByText("Messages total: 100")).toBeInTheDocument()
    expect(screen.getByText("Hors-scope: 8 (8.0%)")).toBeInTheDocument()
    expect(screen.getByText("Erreurs LLM: 3 (3.0%)")).toBeInTheDocument()
    expect(screen.getByText("Latence p95: 420 ms")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "Rafraichir KPI" }))
    expect(refetch).toHaveBeenCalled()

    fireEvent.click(screen.getByRole("button", { name: "Rollback configuration persona" }))
    expect(rollbackMutate).toHaveBeenCalled()
  })

  it("shows loading, error and empty states", () => {
    mockUseRollbackPersonaConfig.mockReturnValue({
      isPending: false,
      isSuccess: false,
      error: null,
      mutate: vi.fn(),
    })

    mockUseConversationKpis.mockReturnValueOnce({
      isPending: true,
      isFetching: true,
      error: null,
      data: null,
      refetch: vi.fn(),
    })
    const { rerender } = render(<OpsMonitoringPanel />)
    expect(screen.getByText("Chargement KPI monitoring...")).toBeInTheDocument()

    mockUseConversationKpis.mockReturnValueOnce({
      isPending: false,
      isFetching: false,
      error: new Error("network down"),
      data: null,
      refetch: vi.fn(),
    })
    rerender(<OpsMonitoringPanel />)
    expect(screen.getByText("Erreur monitoring: network down")).toBeInTheDocument()

    mockUseConversationKpis.mockReturnValueOnce({
      isPending: false,
      isFetching: false,
      error: null,
      data: {
        window: "24h",
        aggregation_scope: "instance_local",
        messages_total: 0,
        out_of_scope_count: 0,
        out_of_scope_rate: 0,
        llm_error_count: 0,
        llm_error_rate: 0,
        p95_latency_ms: 0,
      },
      refetch: vi.fn(),
    })
    rerender(<OpsMonitoringPanel />)
    expect(screen.getByText("Aucune donnee conversationnelle sur cette fenetre.")).toBeInTheDocument()
  })
})
