import { afterEach, describe, expect, it, vi } from "vitest"

import {
  downloadAdminConsumptionCsv,
  getAdminConsumption,
  toUtcIsoFromDateTimeInput,
} from "../api/adminPrompts"

describe("adminPrompts consommation time params", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("convertit une valeur datetime-local vers UTC ISO", () => {
    const localValue = "2026-04-22T10:00"
    const converted = toUtcIsoFromDateTimeInput(localValue)
    const expected = new Date(2026, 3, 22, 10, 0, 0, 0).toISOString()
    expect(converted).toBe(expected)
  })

  it("normalise from_utc/to_utc en UTC pour getAdminConsumption", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          data: [],
          meta: {
            view: "feature",
            granularity: "day",
            count: 0,
            page: 1,
            page_size: 20,
            sort_by: "period_start_utc",
            sort_order: "desc",
            timezone: "UTC",
            default_granularity_behavior: "aggregated_by_selected_period",
          },
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    )
    vi.stubGlobal("fetch", fetchMock)

    await getAdminConsumption({
      view: "feature",
      granularity: "day",
      fromUtc: "2026-04-22T10:00",
      toUtc: "2026-04-22T11:00",
    })

    const calledUrl = String(fetchMock.mock.calls[0]?.[0] ?? "")
    const parsed = new URL(calledUrl)
    expect(parsed.searchParams.get("from_utc")).toBe(
      new Date(2026, 3, 22, 10, 0, 0, 0).toISOString(),
    )
    expect(parsed.searchParams.get("to_utc")).toBe(
      new Date(2026, 3, 22, 11, 0, 0, 0).toISOString(),
    )
  })

  it("normalise aussi les bornes UTC pour l'export CSV", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response("period_start_utc\n", { status: 200, headers: { "Content-Type": "text/csv" } }),
    )
    vi.stubGlobal("fetch", fetchMock)

    await downloadAdminConsumptionCsv({
      view: "user",
      granularity: "month",
      fromUtc: "2026-04-01T00:00",
      toUtc: "2026-05-01T00:00",
    })

    const calledUrl = String(fetchMock.mock.calls[0]?.[0] ?? "")
    const parsed = new URL(calledUrl)
    expect(parsed.searchParams.get("from_utc")).toBe(
      new Date(2026, 3, 1, 0, 0, 0, 0).toISOString(),
    )
    expect(parsed.searchParams.get("to_utc")).toBe(
      new Date(2026, 4, 1, 0, 0, 0, 0).toISOString(),
    )
  })
})

