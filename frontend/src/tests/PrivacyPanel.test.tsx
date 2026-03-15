import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react"
import { afterEach, describe, expect, it, vi } from "vitest"

import { PrivacyPanel } from "../components/PrivacyPanel"

const mockUseExportStatus = vi.fn()
const mockUseDeleteStatus = vi.fn()
const mockUseRequestExport = vi.fn()
const mockUseRequestDelete = vi.fn()

vi.mock("@api", () => ({
  PrivacyApiError: class extends Error {},
  useExportStatus: () => mockUseExportStatus(),
  useDeleteStatus: () => mockUseDeleteStatus(),
  useRequestExport: () => mockUseRequestExport(),
  useRequestDelete: () => mockUseRequestDelete(),
}))

afterEach(() => {
  cleanup()
  mockUseExportStatus.mockReset()
  mockUseDeleteStatus.mockReset()
  mockUseRequestExport.mockReset()
  mockUseRequestDelete.mockReset()
})

describe("PrivacyPanel", () => {
  it("triggers export request and refreshes export status", async () => {
    const mutateAsyncExport = vi.fn().mockResolvedValue({ status: "requested" })
    mockUseExportStatus.mockReturnValue({ data: null, isPending: false, refetch: vi.fn() })
    mockUseDeleteStatus.mockReturnValue({ data: null, isPending: false, refetch: vi.fn() })
    mockUseRequestExport.mockReturnValue({ mutate: mutateAsyncExport, isPending: false, error: null })
    mockUseRequestDelete.mockReturnValue({ mutate: vi.fn(), isPending: false, error: null })

    render(<PrivacyPanel />)
    fireEvent.click(screen.getByRole("button", { name: "Demander un export" }))

    await waitFor(() => expect(mutateAsyncExport).toHaveBeenCalled())
  })

  it("renders statuses and triggers delete request", async () => {
    const mutateAsyncDelete = vi.fn().mockResolvedValue({ status: "requested" })
    mockUseExportStatus.mockReturnValue({ 
      data: { status: "completed" }, 
      isPending: false, 
      refetch: vi.fn() 
    })
    mockUseDeleteStatus.mockReturnValue({ 
      data: { status: "completed" }, 
      isPending: false, 
      refetch: vi.fn() 
    })
    mockUseRequestExport.mockReturnValue({ mutate: vi.fn(), isPending: false, error: null })
    mockUseRequestDelete.mockReturnValue({ mutate: mutateAsyncDelete, isPending: false, error: null })

    render(<PrivacyPanel />)
    
    expect(screen.getByText("Statut export: completed")).toBeInTheDocument()
    expect(screen.getByText("Statut suppression: completed")).toBeInTheDocument()

    fireEvent.click(screen.getByRole("button", { name: "Supprimer mes données" }))
    await waitFor(() => expect(mutateAsyncDelete).toHaveBeenCalled())
  })
})
