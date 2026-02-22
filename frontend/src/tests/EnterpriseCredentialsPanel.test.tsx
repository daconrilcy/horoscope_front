import { afterEach, describe, expect, it, vi } from "vitest"
import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"

import { EnterpriseCredentialsPanel } from "../components/EnterpriseCredentialsPanel"
import * as api from "../api/enterpriseCredentials"
import { AppProviders } from "../state/providers"

vi.mock("../api/enterpriseCredentials", async () => {
  const actual = await vi.importActual("../api/enterpriseCredentials")
  return {
    ...actual,
    useEnterpriseCredentials: vi.fn(),
    useGenerateEnterpriseCredential: vi.fn(),
    useRotateEnterpriseCredential: vi.fn(),
  }
})

const mockUseEnterpriseCredentials = api.useEnterpriseCredentials as any
const mockUseGenerateEnterpriseCredential = api.useGenerateEnterpriseCredential as any
const mockUseRotateEnterpriseCredential = api.useRotateEnterpriseCredential as any

afterEach(() => {
  cleanup()
  vi.clearAllMocks()
})

describe("EnterpriseCredentialsPanel", () => {
  it("renders panel and supports generate + rotate", async () => {
    const generateMutate = vi.fn().mockResolvedValue({ api_key: "b2b_secret_generated" })
    const rotateMutate = vi.fn().mockResolvedValue({ api_key: "b2b_secret_rotated" })

    mockUseEnterpriseCredentials.mockReturnValue({
      isLoading: false,
      isError: false,
      data: {
        company_name: "AstroCorp",
        status: "active",
        credentials: [
          {
            credential_id: 9,
            key_prefix: "b2b_abcd",
            status: "active",
            created_at: "2026-02-20T00:00:00Z",
          },
        ],
      },
      refetch: vi.fn(),
    })

    mockUseGenerateEnterpriseCredential.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: generateMutate,
    })
    mockUseRotateEnterpriseCredential.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: rotateMutate,
    })

    render(
      <AppProviders>
        <EnterpriseCredentialsPanel />
      </AppProviders>
    )
    expect(screen.getByText("API Entreprise")).toBeInTheDocument()
    expect(screen.getByText("Compte: AstroCorp")).toBeInTheDocument()
    expect(screen.getByText("Clé: b2b_abcd***")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "Générer une clé API" }))
    await waitFor(() => expect(generateMutate).toHaveBeenCalled())

    fireEvent.click(screen.getByRole("button", { name: "Régénérer la clé active" }))
    await waitFor(() => expect(rotateMutate).toHaveBeenCalled())
  })

  it("shows loading, error and empty states", () => {
    mockUseGenerateEnterpriseCredential.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseRotateEnterpriseCredential.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    mockUseEnterpriseCredentials.mockReturnValueOnce({
      isLoading: true,
      isError: false,
      data: null,
      refetch: vi.fn(),
    })

    const { rerender } = render(
      <AppProviders>
        <EnterpriseCredentialsPanel />
      </AppProviders>
    )
    expect(screen.getByText("Chargement des credentials...")).toBeInTheDocument()

    mockUseEnterpriseCredentials.mockReturnValueOnce({
      isLoading: false,
      isError: true,
      data: null,
      refetch: vi.fn(),
    })

    rerender(
      <AppProviders>
        <EnterpriseCredentialsPanel />
      </AppProviders>
    )
    expect(screen.getByText("Impossible de charger les credentials.")).toBeInTheDocument()
  })
})
