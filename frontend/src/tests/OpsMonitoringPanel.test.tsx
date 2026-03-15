import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { OpsMonitoringPanel } from "../components/OpsMonitoringPanel"

const mockUseOpsMonitoring = vi.fn()
const mockUseRollbackOpsPersonaConfig = vi.fn()

vi.mock("@api", () => ({
  useOpsMonitoring: (...args: unknown[]) => mockUseOpsMonitoring(...args),
  useRollbackOpsPersonaConfig: () => mockUseRollbackOpsPersonaConfig(),
}))

afterEach(() => {
  cleanup()
  mockUseOpsMonitoring.mockReset()
  mockUseRollbackOpsPersonaConfig.mockReset()
})

describe("OpsMonitoringPanel", () => {
  it("renders kpis and triggers rollback", () => {
    const rollbackMutate = vi.fn()
    mockUseOpsMonitoring.mockReturnValue({
      isPending: false,
      isFetching: false,
      error: null,
      data: {
        window: "24h",
        aggregation_scope: "instance_local",
        messages_total: 100,
        quality_score_avg: 0.85,
        p95_latency_ms: 420,
      },
    })
    mockUseRollbackOpsPersonaConfig.mockReturnValue({
      isPending: false,
      isSuccess: false,
      error: null,
      mutate: rollbackMutate,
    })

    render(<OpsMonitoringPanel />)

    expect(screen.getByText("Portée agrégation: instance_local")).toBeInTheDocument()
    expect(screen.getByText("Messages total: 100")).toBeInTheDocument()
    expect(screen.getByText("Quality avg: 85.0%")).toBeInTheDocument()
    expect(screen.getByText("Latence p95: 420ms")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: /Emergency Rollback Persona/i }))
    expect(rollbackMutate).toHaveBeenCalled()
  })

  it("shows loading, error and empty states", () => {
    mockUseRollbackOpsPersonaConfig.mockReturnValue({
      isPending: false,
      isSuccess: false,
      error: null,
      mutate: vi.fn(),
    })

    mockUseOpsMonitoring.mockReturnValueOnce({
      isPending: true,
      isFetching: true,
      error: null,
      data: null,
    })
    const { rerender } = render(<OpsMonitoringPanel />)
    expect(screen.getByText("Loading...")).toBeInTheDocument()

    mockUseOpsMonitoring.mockReturnValueOnce({
      isPending: false,
      isFetching: false,
      error: new Error("network down"),
      data: null,
    })
    rerender(<OpsMonitoringPanel />)
    expect(screen.getByText("Erreur monitoring: network down")).toBeInTheDocument()

    mockUseOpsMonitoring.mockReturnValueOnce({
      isPending: false,
      isFetching: false,
      error: null,
      data: null,
      isSuccess: true,
    })
    rerender(<OpsMonitoringPanel />)
    expect(screen.getByText("Aucune donnée conversationnelle sur cette fenêtre.")).toBeInTheDocument()
  })
})
