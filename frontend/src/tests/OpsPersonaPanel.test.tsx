import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { OpsPersonaPanel } from "../components/OpsPersonaPanel"

const mockUseOpsPersonaConfig = vi.fn()
const mockUseUpdateOpsPersonaConfig = vi.fn()
const mockUseRollbackOpsPersonaConfig = vi.fn()

vi.mock("@api", () => ({
  useOpsPersonaConfig: () => mockUseOpsPersonaConfig(),
  useUpdateOpsPersonaConfig: () => mockUseUpdateOpsPersonaConfig(),
  useRollbackOpsPersonaConfig: () => mockUseRollbackOpsPersonaConfig(),
}))

afterEach(() => {
  cleanup()
  mockUseOpsPersonaConfig.mockReset()
  mockUseUpdateOpsPersonaConfig.mockReset()
  mockUseRollbackOpsPersonaConfig.mockReset()
})

describe("OpsPersonaPanel", () => {
  it("renders and submits update + rollback", () => {
    const mutateUpdate = vi.fn()
    const mutateRollback = vi.fn()
    mockUseOpsPersonaConfig.mockReturnValue({
      isPending: false,
      error: null,
      data: {
        version: 2,
        tone: "direct",
        prudence_level: "high",
        scope_policy: "strict",
        response_style: "concise",
      },
    })
    mockUseUpdateOpsPersonaConfig.mockReturnValue({
      isPending: false,
      isSuccess: false,
      error: null,
      mutate: mutateUpdate,
    })
    mockUseRollbackOpsPersonaConfig.mockReturnValue({
      isPending: false,
      isSuccess: false,
      error: null,
      mutate: mutateRollback,
    })

    render(<OpsPersonaPanel />)
    fireEvent.change(screen.getByLabelText("Tone"), { target: { value: "empathetic" } })
    fireEvent.change(screen.getByLabelText("Prudence"), { target: { value: "standard" } })
    fireEvent.change(screen.getByLabelText("Scope"), { target: { value: "balanced" } })
    fireEvent.change(screen.getByLabelText("Style"), { target: { value: "detailed" } })
    
    // The button text is now "Configuration persona mise à jour." after my i18n update?
    // Wait, I used t.successUpdate for the update button in component.
    fireEvent.click(screen.getByRole("button", { name: "Configuration persona mise à jour." }))

    expect(mutateUpdate).toHaveBeenCalledWith({
      tone: "empathetic",
      prudence_level: "standard",
      scope_policy: "balanced",
      response_style: "detailed",
    })

    fireEvent.click(screen.getByRole("button", { name: "Rollback persona effectué." }))
    expect(mutateRollback).toHaveBeenCalled()
  })
})
