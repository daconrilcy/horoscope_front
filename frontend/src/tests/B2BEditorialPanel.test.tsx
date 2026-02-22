import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { B2BEditorialPanel } from "../components/B2BEditorialPanel"

const mockUseB2BEditorialConfig = vi.fn()
const mockUseUpdateB2BEditorialConfig = vi.fn()

vi.mock("../api/b2bEditorial", () => ({
  B2BEditorialApiError: class extends Error {
    code: string
    status: number
    details: Record<string, unknown>
    requestId: string | null

    constructor(
      code: string,
      message: string,
      status: number,
      details: Record<string, unknown> = {},
      requestId: string | null = null,
    ) {
      super(message)
      this.code = code
      this.status = status
      this.details = details
      this.requestId = requestId
    }
  },
  useB2BEditorialConfig: () => mockUseB2BEditorialConfig(),
  useUpdateB2BEditorialConfig: () => mockUseUpdateB2BEditorialConfig(),
}))

afterEach(() => {
  cleanup()
  mockUseB2BEditorialConfig.mockReset()
  mockUseUpdateB2BEditorialConfig.mockReset()
})

describe("B2BEditorialPanel", () => {
  it("loads and updates editorial config", async () => {
    const loadMutateAsync = vi.fn().mockResolvedValue({
      config_id: 1,
      account_id: 2,
      version_number: 1,
      is_active: true,
      tone: "neutral",
      length_style: "medium",
      output_format: "paragraph",
      preferred_terms: ["focus"],
      avoided_terms: ["drama"],
      created_by_credential_id: 5,
      created_at: "2026-02-20T00:00:00Z",
      updated_at: "2026-02-20T00:00:00Z",
    })
    const updateMutateAsync = vi.fn().mockResolvedValue({
      config_id: 2,
      account_id: 2,
      version_number: 2,
      is_active: true,
      tone: "friendly",
      length_style: "short",
      output_format: "bullet",
      preferred_terms: ["focus", "clarté"],
      avoided_terms: ["drama"],
      created_by_credential_id: 5,
      created_at: "2026-02-20T00:00:00Z",
      updated_at: "2026-02-20T00:00:00Z",
    })

    mockUseB2BEditorialConfig.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: loadMutateAsync,
    })
    mockUseUpdateB2BEditorialConfig.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: updateMutateAsync,
    })

    render(<B2BEditorialPanel />)
    fireEvent.change(screen.getByLabelText("Clé API B2B"), { target: { value: "b2b_editorial_secret" } })
    fireEvent.click(screen.getByRole("button", { name: "Charger la configuration" }))
    await waitFor(() => expect(loadMutateAsync).toHaveBeenCalledWith("b2b_editorial_secret"))

    fireEvent.change(screen.getByLabelText("Ton"), { target: { value: "friendly" } })
    fireEvent.change(screen.getByLabelText("Longueur"), { target: { value: "short" } })
    fireEvent.change(screen.getByLabelText("Format"), { target: { value: "bullet" } })
    fireEvent.change(screen.getByLabelText("Mots à privilégier (séparés par des virgules)"), {
      target: { value: "focus, clarté" },
    })
    fireEvent.click(screen.getByRole("button", { name: "Enregistrer la configuration" }))

    await waitFor(() =>
      expect(updateMutateAsync).toHaveBeenCalledWith({
        apiKey: "b2b_editorial_secret",
        payload: {
          tone: "friendly",
          length_style: "short",
          output_format: "bullet",
          preferred_terms: ["focus", "clarté"],
          avoided_terms: ["drama"],
        },
      }),
    )
    expect(screen.getByText("Version active: 2 (active)")).toBeInTheDocument()
  })

  it("renders loading, error and empty states", () => {
    mockUseB2BEditorialConfig.mockReturnValueOnce({
      isPending: true,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseUpdateB2BEditorialConfig.mockReturnValueOnce({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    const { rerender } = render(<B2BEditorialPanel />)
    expect(screen.getByText("Chargement configuration éditoriale...")).toBeInTheDocument()

    mockUseB2BEditorialConfig.mockReturnValueOnce({
      isPending: false,
      error: {
        code: "invalid_api_key",
        message: "invalid api key",
        requestId: "rid-editorial-read",
        details: { retry_after: "3" },
      },
      mutateAsync: vi.fn(),
    })
    mockUseUpdateB2BEditorialConfig.mockReturnValueOnce({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    rerender(<B2BEditorialPanel />)
    expect(screen.getByText(/Erreur lecture éditoriale:/)).toBeInTheDocument()
    expect(screen.getByText(/\[details=retry_after=3\]/)).toBeInTheDocument()
    expect(screen.queryByText("Aucune configuration chargée.")).not.toBeInTheDocument()
  })
})
