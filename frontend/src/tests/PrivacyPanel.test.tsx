import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { PrivacyPanel } from "../components/PrivacyPanel"

const mockUseExportStatus = vi.fn()
const mockUseDeleteStatus = vi.fn()
const mockUseRequestExport = vi.fn()
const mockUseRequestDelete = vi.fn()

vi.mock("../api/privacy", () => ({
  PrivacyApiError: class extends Error {},
  useExportStatus: () => mockUseExportStatus(),
  useDeleteStatus: () => mockUseDeleteStatus(),
  useRequestExport: () => mockUseRequestExport(),
  useRequestDelete: () => mockUseRequestDelete(),
}))

afterEach(() => {
  cleanup()
  vi.restoreAllMocks()
  mockUseExportStatus.mockReset()
  mockUseDeleteStatus.mockReset()
  mockUseRequestExport.mockReset()
  mockUseRequestDelete.mockReset()
})

describe("PrivacyPanel", () => {
  it("triggers export request and refreshes export status", async () => {
    const refetchExport = vi.fn()
    const mutateAsyncExport = vi.fn().mockResolvedValue({ status: "completed" })

    mockUseExportStatus.mockReturnValue({
      isLoading: false,
      data: null,
      error: null,
      refetch: refetchExport,
    })
    mockUseDeleteStatus.mockReturnValue({
      isLoading: false,
      data: null,
      error: null,
      refetch: vi.fn(),
    })
    mockUseRequestExport.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: mutateAsyncExport,
    })
    mockUseRequestDelete.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })

    render(<PrivacyPanel />)
    fireEvent.click(screen.getByRole("button", { name: "Demander un export" }))

    await waitFor(() => expect(mutateAsyncExport).toHaveBeenCalled())
    expect(refetchExport).toHaveBeenCalled()
  })

  it("renders statuses and triggers delete request", async () => {
    const refetchDelete = vi.fn()
    const mutateAsyncDelete = vi.fn().mockResolvedValue({ status: "completed" })

    mockUseExportStatus.mockReturnValue({
      isLoading: false,
      data: { status: "completed" },
      error: null,
      refetch: vi.fn(),
    })
    mockUseDeleteStatus.mockReturnValue({
      isLoading: false,
      data: { status: "completed" },
      error: null,
      refetch: refetchDelete,
    })
    mockUseRequestExport.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseRequestDelete.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: mutateAsyncDelete,
    })
    vi.spyOn(window, "confirm").mockReturnValue(true)

    render(<PrivacyPanel />)
    expect(screen.getByText("Statut export: completed")).toBeInTheDocument()
    expect(screen.getByText("Statut suppression: completed")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "Supprimer mes donnees" }))
    await waitFor(() => expect(mutateAsyncDelete).toHaveBeenCalled())
    expect(refetchDelete).toHaveBeenCalled()
  })

  it("shows empty states and does not delete when confirmation is canceled", async () => {
    const mutateAsyncDelete = vi.fn()
    const confirmSpy = vi.spyOn(window, "confirm").mockReturnValue(false)

    mockUseExportStatus.mockReturnValue({
      isLoading: false,
      data: null,
      error: null,
      refetch: vi.fn(),
    })
    mockUseDeleteStatus.mockReturnValue({
      isLoading: false,
      data: null,
      error: null,
      refetch: vi.fn(),
    })
    mockUseRequestExport.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: vi.fn(),
    })
    mockUseRequestDelete.mockReturnValue({
      isPending: false,
      error: null,
      mutateAsync: mutateAsyncDelete,
    })

    render(<PrivacyPanel />)
    expect(screen.getByText("Aucune demande d export pour le moment.")).toBeInTheDocument()
    expect(screen.getByText("Aucune demande de suppression pour le moment.")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "Supprimer mes donnees" }))

    await waitFor(() => expect(confirmSpy).toHaveBeenCalled())
    expect(mutateAsyncDelete).not.toHaveBeenCalled()
  })
})
