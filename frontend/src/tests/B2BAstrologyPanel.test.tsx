import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { B2BAstrologyPanel } from "../components/B2BAstrologyPanel"

const mockUseB2BWeeklyBySign = vi.fn()

vi.mock("../api/b2bAstrology", () => ({
  B2BAstrologyApiError: class extends Error {
    code: string
    status: number
    details: Record<string, string>
    requestId: string | null

    constructor(
      code: string,
      message: string,
      status: number,
      details: Record<string, string> = {},
      requestId: string | null = null,
    ) {
      super(message)
      this.code = code
      this.status = status
      this.details = details
      this.requestId = requestId
    }
  },
  useB2BWeeklyBySign: () => mockUseB2BWeeklyBySign(),
}))

afterEach(() => {
  cleanup()
  mockUseB2BWeeklyBySign.mockReset()
})

describe("B2BAstrologyPanel", () => {
  it("submits api key and renders data", async () => {
    const mutate = vi.fn()
    mockUseB2BWeeklyBySign.mockReturnValue({
      isPending: false,
      isSuccess: true,
      error: null,
      mutate,
      data: {
        api_version: "v1",
        reference_version: "2026.01",
        generated_at: "2026-02-20T00:00:00Z",
        items: [{ sign_code: "aries", sign_name: "Aries", weekly_summary: "Momentum stable." }],
      },
    })

    render(<B2BAstrologyPanel />)
    fireEvent.change(screen.getByLabelText("Cle API B2B"), { target: { value: "b2b_demo_secret" } })
    fireEvent.click(screen.getByRole("button", { name: "Recuperer weekly-by-sign" }))

    await waitFor(() => expect(mutate).toHaveBeenCalledWith("b2b_demo_secret"))
    expect(screen.getByText(/Version API: v1/)).toBeInTheDocument()
    expect(screen.getByText(/Aries/)).toBeInTheDocument()
  })

  it("renders loading, error and empty states", () => {
    mockUseB2BWeeklyBySign.mockReturnValueOnce({
      isPending: true,
      isSuccess: false,
      error: null,
      mutate: vi.fn(),
      data: undefined,
    })
    const { rerender } = render(<B2BAstrologyPanel />)
    expect(screen.getByText("Chargement weekly-by-sign...")).toBeInTheDocument()

    mockUseB2BWeeklyBySign.mockReturnValueOnce({
      isPending: false,
      isSuccess: false,
      error: {
        code: "invalid_api_key",
        message: "invalid api key",
        requestId: "rid-b2b-err",
      },
      mutate: vi.fn(),
      data: undefined,
    })
    rerender(<B2BAstrologyPanel />)
    expect(screen.getByText(/Erreur API B2B:/)).toBeInTheDocument()
    expect(screen.getByText(/request_id=rid-b2b-err/)).toBeInTheDocument()

    mockUseB2BWeeklyBySign.mockReturnValueOnce({
      isPending: false,
      isSuccess: true,
      error: null,
      mutate: vi.fn(),
      data: {
        api_version: "v1",
        reference_version: "2026.01",
        generated_at: "2026-02-20T00:00:00Z",
        items: [],
      },
    })
    rerender(<B2BAstrologyPanel />)
    expect(screen.getByText("Aucun contenu astrologique disponible pour cette periode.")).toBeInTheDocument()
  })
})
