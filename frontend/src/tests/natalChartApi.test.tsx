import { render } from "@testing-library/react"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"

import { ApiError, generateNatalChart, useLatestNatalChart } from "../api/natalChart"
import { getBirthData, type BirthProfileData } from "../api/birthProfile"
import { ANONYMOUS_SUBJECT } from "../utils/constants"

const useQueryMock = vi.fn()
const useAccessTokenSnapshotMock = vi.fn()
const getSubjectFromAccessTokenMock = vi.fn()

vi.mock("@tanstack/react-query", () => ({
  useQuery: (options: unknown) => useQueryMock(options),
}))

vi.mock("../utils/authToken", () => ({
  useAccessTokenSnapshot: () => useAccessTokenSnapshotMock(),
  getSubjectFromAccessToken: (token: string | null) => getSubjectFromAccessTokenMock(token),
}))

function HookProbe() {
  useLatestNatalChart()
  return null
}

describe("generateNatalChart", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("sends Content-Type: application/json header", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ data: { chart_id: "c1", result: {}, metadata: {}, created_at: "" } }),
    })
    vi.stubGlobal("fetch", fetchMock)

    await generateNatalChart("test-token").catch(() => {})

    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit]
    expect((init.headers as Record<string, string>)["Content-Type"]).toBe("application/json")
    expect((init.headers as Record<string, string>)["Authorization"]).toBe("Bearer test-token")
    expect(init.body).toBe('{"accurate":false}')
  })

  it("parses FastAPI native 422 format {detail: [...]} as unprocessable_entity", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        json: async () => ({ detail: [{ loc: ["body"], msg: "Field required", type: "missing" }] }),
      }),
    )

    await expect(generateNatalChart("test-token")).rejects.toMatchObject({
      code: "unprocessable_entity",
      status: 422,
      message: "Field required",
    })
  })

  it("parses standard API error format {error: {...}} correctly", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        json: async () => ({ error: { code: "unprocessable_entity", message: "Données invalides" } }),
      }),
    )

    await expect(generateNatalChart("test-token")).rejects.toMatchObject({
      code: "unprocessable_entity",
      status: 422,
      message: "Données invalides",
    })
  })

  it("falls back to unknown_error when response body is unparseable", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 500,
        json: async () => { throw new Error("not JSON") },
      }),
    )

    await expect(generateNatalChart("test-token")).rejects.toMatchObject({
      code: "unknown_error",
      status: 500,
    })
  })
})

describe("astro_profile nullable consumption", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("parses LatestNatalChart with astro_profile null fields without crash (AC5)", async () => {
    const chartWithNullAstroProfile = {
      chart_id: "c1",
      result: {
        reference_version: "1.0",
        ruleset_version: "1.0",
        prepared_input: {
          birth_datetime_local: "1990-01-15T12:00:00",
          birth_datetime_utc: "1990-01-15T12:00:00Z",
          timestamp_utc: 632491200,
          julian_day: 2447907.0,
          birth_timezone: "UTC",
        },
        planet_positions: [],
        houses: [],
        aspects: [],
      },
      metadata: { reference_version: "1.0", ruleset_version: "1.0", house_system: "equal" },
      created_at: "2026-01-01T00:00:00Z",
      astro_profile: {
        sun_sign_code: null,
        ascendant_sign_code: null,
        missing_birth_time: true,
      },
    }
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ data: chartWithNullAstroProfile }),
      }),
    )

    const result = await generateNatalChart("test-token")
    expect(result.metadata.house_system).toBe("equal")
    expect(result.astro_profile?.sun_sign_code).toBeNull()
    expect(result.astro_profile?.ascendant_sign_code).toBeNull()
    expect(result.astro_profile?.missing_birth_time).toBe(true)
  })

  it("parses LatestNatalChart without astro_profile field (absent = undefined, no crash)", async () => {
    const chartWithoutAstroProfile = {
      chart_id: "c2",
      result: {
        reference_version: "1.0",
        ruleset_version: "1.0",
        prepared_input: {
          birth_datetime_local: "1990-01-15T12:00:00",
          birth_datetime_utc: "1990-01-15T12:00:00Z",
          timestamp_utc: 632491200,
          julian_day: 2447907.0,
          birth_timezone: "UTC",
        },
        planet_positions: [],
        houses: [],
        aspects: [],
      },
      metadata: { reference_version: "1.0", ruleset_version: "1.0", house_system: "equal" },
      created_at: "2026-01-01T00:00:00Z",
    }
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ data: chartWithoutAstroProfile }),
      }),
    )

    const result = await generateNatalChart("test-token")
    expect(result.astro_profile).toBeUndefined()
    // Optional chaining safe access — no crash
    expect(result.astro_profile?.sun_sign_code).toBeUndefined()
    expect(result.astro_profile?.missing_birth_time).toBeUndefined()
  })

  it("parses BirthProfileData with astro_profile including null signs (AC4)", async () => {
    // Compile-time contract check for the payload shape consumed by getBirthData.
    const profileWithAstroProfile: BirthProfileData = {
      birth_date: "1990-01-15",
      birth_time: null,
      birth_place: "Paris, France",
      birth_timezone: "Europe/Paris",
      astro_profile: {
        sun_sign_code: "CAPRICORN",
        ascendant_sign_code: null,
        missing_birth_time: true,
      },
    }
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ data: profileWithAstroProfile }),
      }),
    )

    const result = await getBirthData("test-token")
    expect(result).not.toBeNull()

    const astroProfile = result?.astro_profile
    expect(astroProfile).toBeDefined()
    if (!astroProfile) throw new Error("astro_profile should be defined in this fixture")
    expect(astroProfile.sun_sign_code).toBe("CAPRICORN")
    expect(astroProfile.ascendant_sign_code).toBeNull()
    expect(astroProfile.missing_birth_time).toBe(true)
  })
})

describe("planet position retrograde contract compatibility", () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it("keeps optional retrograde fields when backend sends them", async () => {
    const chartWithRetrograde = {
      chart_id: "c-retro",
      result: {
        reference_version: "1.0",
        ruleset_version: "1.0",
        prepared_input: {
          birth_datetime_local: "1990-01-15T12:00:00",
          birth_datetime_utc: "1990-01-15T12:00:00Z",
          timestamp_utc: 632491200,
          julian_day: 2447907.0,
          birth_timezone: "UTC",
        },
        planet_positions: [
          {
            planet_code: "MERCURY",
            longitude: 100.5,
            sign_code: "CANCER",
            house_number: 4,
            is_retrograde: true,
            speed_longitude: -0.75,
          },
        ],
        houses: [],
        aspects: [],
      },
      metadata: { reference_version: "1.0", ruleset_version: "1.0" },
      created_at: "2026-01-01T00:00:00Z",
    }

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ data: chartWithRetrograde }),
      }),
    )

    const result = await generateNatalChart("test-token")
    expect(result.result.planet_positions[0]?.is_retrograde).toBe(true)
    expect(result.result.planet_positions[0]?.speed_longitude).toBe(-0.75)
  })

  it("remains compatible with legacy planet positions that omit retrograde fields", async () => {
    const legacyChart = {
      chart_id: "c-legacy",
      result: {
        reference_version: "1.0",
        ruleset_version: "1.0",
        prepared_input: {
          birth_datetime_local: "1990-01-15T12:00:00",
          birth_datetime_utc: "1990-01-15T12:00:00Z",
          timestamp_utc: 632491200,
          julian_day: 2447907.0,
          birth_timezone: "UTC",
        },
        planet_positions: [
          {
            planet_code: "SUN",
            longitude: 15.0,
            sign_code: "ARIES",
            house_number: 1,
          },
        ],
        houses: [],
        aspects: [],
      },
      metadata: { reference_version: "1.0", ruleset_version: "1.0" },
      created_at: "2026-01-01T00:00:00Z",
    }

    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ data: legacyChart }),
      }),
    )

    const result = await generateNatalChart("test-token")
    expect(result.result.planet_positions[0]?.is_retrograde).toBeUndefined()
    expect(result.result.planet_positions[0]?.speed_longitude).toBeUndefined()
  })
})

describe("useLatestNatalChart", () => {
  beforeEach(() => {
    useQueryMock.mockReset()
    useAccessTokenSnapshotMock.mockReset()
    getSubjectFromAccessTokenMock.mockReset()
  })

  it("uses user-scoped query key when token exists", () => {
    useAccessTokenSnapshotMock.mockReturnValue("token-a")
    getSubjectFromAccessTokenMock.mockReturnValue("42")
    useQueryMock.mockReturnValue({})

    render(<HookProbe />)

    expect(useQueryMock).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ["latest-natal-chart", "42"],
        enabled: true,
        retryOnMount: false,
        refetchOnWindowFocus: false,
        refetchOnReconnect: false,
      }),
    )
  })

  it("disables query when token is absent", () => {
    useAccessTokenSnapshotMock.mockReturnValue(null)
    getSubjectFromAccessTokenMock.mockReturnValue(null)
    useQueryMock.mockReturnValue({})

    render(<HookProbe />)

    expect(useQueryMock).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ["latest-natal-chart", ANONYMOUS_SUBJECT],
        enabled: false,
      }),
    )
  })

  it("does not retry on client errors (4xx) for latest natal chart", () => {
    useAccessTokenSnapshotMock.mockReturnValue("token-a")
    getSubjectFromAccessTokenMock.mockReturnValue("42")
    useQueryMock.mockReturnValue({})

    render(<HookProbe />)

    const options = useQueryMock.mock.calls[0]?.[0] as {
      retry?: (failureCount: number, error: unknown) => boolean
    }
    expect(options.retry).toBeTypeOf("function")
    const shouldRetry404 = options.retry?.(1, new ApiError("natal_chart_not_found", "not found", 404))
    expect(shouldRetry404).toBe(false)
  })
})
