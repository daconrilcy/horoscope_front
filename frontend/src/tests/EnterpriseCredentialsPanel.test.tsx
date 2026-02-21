import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { EnterpriseCredentialsPanel } from "../components/EnterpriseCredentialsPanel"

const mockUseEnterpriseCredentials = vi.fn()
const mockUseGenerateEnterpriseCredential = vi.fn()
const mockUseRotateEnterpriseCredential = vi.fn()

vi.mock("../api/enterpriseCredentials", () => ({
  EnterpriseCredentialsApiError: class extends Error {},
  useEnterpriseCredentials: (...args: unknown[]) => mockUseEnterpriseCredentials(...args),
  useGenerateEnterpriseCredential: () => mockUseGenerateEnterpriseCredential(),
  useRotateEnterpriseCredential: () => mockUseRotateEnterpriseCredential(),
}))

afterEach(() => {
  cleanup()
  mockUseEnterpriseCredentials.mockReset()
  mockUseGenerateEnterpriseCredential.mockReset()
  mockUseRotateEnterpriseCredential.mockReset()
})

describe("EnterpriseCredentialsPanel", () => {
  it("renders panel and supports generate + rotate", async () => {
    const refetch = vi.fn()
    const generateMutate = vi.fn().mockResolvedValue({ api_key: "b2b_secret_generated" })
    const rotateMutate = vi.fn().mockResolvedValue({ api_key: "b2b_secret_rotated" })

    mockUseEnterpriseCredentials.mockReturnValue({
      isPending: false,
      error: null,
      data: {
        account_id: 1,
        company_name: "Acme Media",
        status: "active",
        has_active_credential: true,
        credentials: [{ credential_id: 9, key_prefix: "b2b_abcd", status: "active" }],
      },
      refetch,
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

    render(<EnterpriseCredentialsPanel />)
    expect(screen.getByText("Credentials API entreprise")).toBeInTheDocument()
    expect(screen.getByText("Credential #9 · b2b_abcd · active")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "Generer une cle API" }))
    await waitFor(() => expect(generateMutate).toHaveBeenCalled())

    fireEvent.click(screen.getByRole("button", { name: "Regenerer la cle active" }))
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
      isPending: true,
      error: null,
      data: null,
      refetch: vi.fn(),
    })
    const { rerender } = render(<EnterpriseCredentialsPanel />)
    expect(screen.getByText("Chargement credentials...")).toBeInTheDocument()

    mockUseEnterpriseCredentials.mockReturnValueOnce({
      isPending: false,
      error: new Error("service down"),
      data: null,
      refetch: vi.fn(),
    })
    rerender(<EnterpriseCredentialsPanel />)
    expect(screen.getByText("Erreur credentials: service down")).toBeInTheDocument()

    mockUseEnterpriseCredentials.mockReturnValueOnce({
      isPending: false,
      error: null,
      data: {
        account_id: 1,
        company_name: "Acme Media",
        status: "active",
        has_active_credential: false,
        credentials: [],
      },
      refetch: vi.fn(),
    })
    rerender(<EnterpriseCredentialsPanel />)
    expect(screen.getByText("Aucun credential configure pour ce compte.")).toBeInTheDocument()
  })
})
