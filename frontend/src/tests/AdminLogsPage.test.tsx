import { afterEach, describe, expect, it, vi } from "vitest"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { cleanup, render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"

import { AdminLogsPage } from "../pages/admin/AdminLogsPage"
import { clearAccessToken, setAccessToken } from "../utils/authToken"

function makeJsonResponse(payload: unknown, status = 200) {
  return new Response(JSON.stringify(payload), {
    status,
    headers: { "Content-Type": "application/json" },
  })
}

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
    },
  })

  return render(
    <QueryClientProvider client={queryClient}>
      <AdminLogsPage />
    </QueryClientProvider>,
  )
}

describe("AdminLogsPage", () => {
  afterEach(() => {
    cleanup()
    clearAccessToken()
    vi.unstubAllGlobals()
  })

  it("uses audit logs with filters, detail modal and csv export", async () => {
    setAccessToken("x.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0=.y")

    const createObjectUrlMock = vi.fn(() => "blob:admin-audit")
    const revokeObjectUrlMock = vi.fn()
    Object.defineProperty(window.URL, "createObjectURL", {
      value: createObjectUrlMock,
      configurable: true,
    })
    Object.defineProperty(window.URL, "revokeObjectURL", {
      value: revokeObjectUrlMock,
      configurable: true,
    })

    const auditRows = [
      {
        id: 1,
        timestamp: "2026-04-06T09:00:00Z",
        actor_email_masked: "adm***@example.com",
        actor_role: "admin",
        action: "user_suspended",
        target_type: "user",
        target_id_masked: "***4",
        status: "success",
        details: { reason: "fraud" },
      },
      {
        id: 2,
        timestamp: "2026-04-06T08:00:00Z",
        actor_email_masked: "ops***@example.com",
        actor_role: "admin",
        action: "feature_flag_toggled",
        target_type: "system",
        target_id_masked: "ff-paywall",
        status: "success",
        details: { flag: "paywall_copy" },
      },
    ]

    const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input)

      if (url.endsWith("/v1/admin/logs/quota-alerts")) {
        return makeJsonResponse({ data: [] })
      }

      if (url.startsWith("/v1/admin/audit?") || url.endsWith("/v1/admin/audit")) {
        const requestUrl = new URL(url, "http://localhost")
        const actor = requestUrl.searchParams.get("actor")
        const action = requestUrl.searchParams.get("action")
        const period = requestUrl.searchParams.get("period")

        let filteredRows = [...auditRows]
        if (actor) {
          filteredRows = filteredRows.filter(
            (row) => row.actor_email_masked.includes(actor) || row.actor_role.includes(actor),
          )
        }
        if (action) {
          filteredRows = filteredRows.filter((row) => row.action === action)
        }
        if (period && period !== "all") {
          filteredRows = filteredRows.filter((row) => row.id === 1)
        }

        return makeJsonResponse({
          data: filteredRows,
          total: filteredRows.length,
          page: 1,
          per_page: 50,
        })
      }

      if (url.endsWith("/v1/admin/audit/export") && init?.method === "POST") {
        return new Response("id,timestamp\r\n1,2026-04-06T09:00:00Z\r\n", {
          status: 200,
          headers: {
            "Content-Type": "text/csv",
            "Content-Disposition": "attachment; filename=audit_log_all_20260406T090000Z.csv",
          },
        })
      }

      return makeJsonResponse({ error: { code: "not_found", message: "not found" } }, 404)
    })

    vi.stubGlobal("fetch", fetchMock)

    renderPage()

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Observabilité Technique" })).toBeInTheDocument()
    })

    expect(screen.getByRole("button", { name: "Journal d'audit" })).toBeInTheDocument()
    expect(await screen.findByText("adm***@example.com")).toBeInTheDocument()
    expect(screen.getByText("***4")).toBeInTheDocument()

    await userEvent.type(screen.getByLabelText("Acteur"), "adm")
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/v1/admin/audit?actor=adm&period=30d"),
        expect.any(Object),
      )
    })

    await userEvent.selectOptions(screen.getByLabelText("Action"), "user_suspended")
    await userEvent.selectOptions(screen.getByLabelText("Période"), "all")

    await waitFor(() => {
      expect(
        fetchMock.mock.calls.some(([url]) =>
          String(url).includes("/v1/admin/audit?actor=adm&action=user_suspended"),
        ),
      ).toBe(true)
    })

    await userEvent.click(screen.getByRole("button", { name: "Voir détail" }))

    await waitFor(() => {
      expect(
        screen.getByRole("dialog", { name: "Détail de l'événement d'audit" }),
      ).toBeInTheDocument()
    })

    expect(screen.getByText(/"reason": "fraud"/)).toBeInTheDocument()

    await userEvent.click(screen.getByRole("button", { name: "Fermer" }))
    await userEvent.click(screen.getByRole("button", { name: "Exporter CSV" }))

    await waitFor(() => {
      expect(screen.getByText(/Export CSV généré/)).toBeInTheDocument()
    })

    expect(createObjectUrlMock).toHaveBeenCalled()
    expect(revokeObjectUrlMock).toHaveBeenCalledWith("blob:admin-audit")
  })
})
