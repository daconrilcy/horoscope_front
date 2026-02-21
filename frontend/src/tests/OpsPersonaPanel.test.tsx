import { cleanup, fireEvent, render, screen } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { OpsPersonaPanel } from "../components/OpsPersonaPanel"

const mockUseActivePersonaConfig = vi.fn()
const mockUseUpdatePersonaConfig = vi.fn()
const mockUseRollbackPersonaConfig = vi.fn()

vi.mock("../api/opsPersona", () => ({
  OpsPersonaApiError: class extends Error {},
  useActivePersonaConfig: () => mockUseActivePersonaConfig(),
  useUpdatePersonaConfig: () => mockUseUpdatePersonaConfig(),
  useRollbackPersonaConfig: () => mockUseRollbackPersonaConfig(),
}))

afterEach(() => {
  cleanup()
  mockUseActivePersonaConfig.mockReset()
  mockUseUpdatePersonaConfig.mockReset()
  mockUseRollbackPersonaConfig.mockReset()
})

describe("OpsPersonaPanel", () => {
  it("renders and submits update + rollback", () => {
    const mutateUpdate = vi.fn()
    const mutateRollback = vi.fn()
    mockUseActivePersonaConfig.mockReturnValue({
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
    mockUseUpdatePersonaConfig.mockReturnValue({
      isPending: false,
      isSuccess: false,
      error: null,
      mutate: mutateUpdate,
    })
    mockUseRollbackPersonaConfig.mockReturnValue({
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
    fireEvent.click(screen.getByRole("button", { name: "Activer configuration persona" }))

    expect(mutateUpdate).toHaveBeenCalledWith({
      tone: "empathetic",
      prudence_level: "standard",
      scope_policy: "balanced",
      response_style: "detailed",
    })

    fireEvent.click(screen.getByRole("button", { name: "Rollback persona" }))
    expect(mutateRollback).toHaveBeenCalled()
  })
})
