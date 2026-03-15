import { afterEach, describe, expect, it, vi } from "vitest"
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"

import { EnterpriseCredentialsPanel } from "../components/EnterpriseCredentialsPanel"

const mockUseB2BCredentials = vi.fn()
const mockUseGenerateB2BCredential = vi.fn()
const mockUseRotateB2BCredential = vi.fn()

vi.mock("../api/enterpriseCredentials", () => ({
  useB2BCredentials: () => mockUseB2BCredentials(),
  useGenerateB2BCredential: () => mockUseGenerateB2BCredential(),
  useRotateB2BCredential: () => mockUseRotateB2BCredential(),
}))

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

function renderWithQuery(ui: React.ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      {ui}
    </QueryClientProvider>
  )
}

describe("EnterpriseCredentialsPanel", () => {
  it("renders panel and supports generate + rotate", async () => {
    const generateMutate = vi.fn()
    const rotateMutate = vi.fn()

    mockUseB2BCredentials.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        company_name: "AstroCorp",
        status: "active",
        credentials: [
          {
            credential_id: 9,
            key_prefix: "b2b_abcd",
            is_active: true,
            created_at: "2026-02-20T00:00:00Z",
            scope: "full"
          },
        ],
      },
    })

    mockUseGenerateB2BCredential.mockReturnValue({
      isPending: false,
      error: null,
      mutate: generateMutate,
    })
    mockUseRotateB2BCredential.mockReturnValue({
      isPending: false,
      error: null,
      mutate: rotateMutate,
    })

    renderWithQuery(<EnterpriseCredentialsPanel />)
    
    expect(screen.getByText("API Entreprise")).toBeInTheDocument()
    
    await waitFor(() => {
      expect(screen.getByText(/Compte: AstroCorp/i)).toBeInTheDocument()
      expect(screen.getByText(/Clé: b2b_abcd/i)).toBeInTheDocument()
    })

    fireEvent.click(screen.getByRole("button", { name: /Générer une clé API/i }))
    expect(generateMutate).toHaveBeenCalled()

    fireEvent.click(screen.getByRole("button", { name: /Régénérer la clé active/i }))
    expect(rotateMutate).toHaveBeenCalled()
  })
})
