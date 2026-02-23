import { afterEach, describe, expect, it, vi } from "vitest"
import { getUserTimezone, TIMEZONES } from "../data/timezones"

afterEach(() => {
  vi.restoreAllMocks()
})

describe("getUserTimezone", () => {
  it("returns detected timezone when it exists in TIMEZONES list", () => {
    vi.spyOn(Intl, "DateTimeFormat").mockReturnValue({
      resolvedOptions: () => ({ timeZone: "Europe/Paris" }),
    } as Intl.DateTimeFormat)

    expect(getUserTimezone()).toBe("Europe/Paris")
  })

  it("returns UTC when detected timezone is not in TIMEZONES list", () => {
    vi.spyOn(Intl, "DateTimeFormat").mockReturnValue({
      resolvedOptions: () => ({ timeZone: "Unknown/Fake_Timezone" }),
    } as Intl.DateTimeFormat)

    expect(getUserTimezone()).toBe("UTC")
  })

  it("returns UTC when Intl.DateTimeFormat throws an error", () => {
    vi.spyOn(Intl, "DateTimeFormat").mockImplementation(() => {
      throw new Error("Not supported")
    })

    expect(getUserTimezone()).toBe("UTC")
  })

  it("returns UTC when resolvedOptions returns undefined timeZone", () => {
    vi.spyOn(Intl, "DateTimeFormat").mockReturnValue({
      resolvedOptions: () => ({ timeZone: undefined }),
    } as unknown as Intl.DateTimeFormat)

    expect(getUserTimezone()).toBe("UTC")
  })

  it("returns UTC when resolvedOptions returns empty string", () => {
    vi.spyOn(Intl, "DateTimeFormat").mockReturnValue({
      resolvedOptions: () => ({ timeZone: "" }),
    } as unknown as Intl.DateTimeFormat)

    expect(getUserTimezone()).toBe("UTC")
  })

  it("returns UTC for obsolete/legacy timezone identifiers not in IANA list", () => {
    // Some browsers may return legacy timezone IDs like "US/Eastern" instead of "America/New_York"
    vi.spyOn(Intl, "DateTimeFormat").mockReturnValue({
      resolvedOptions: () => ({ timeZone: "US/Eastern" }),
    } as Intl.DateTimeFormat)

    expect(getUserTimezone()).toBe("UTC")
  })
})

describe("TIMEZONES list", () => {
  it("contains common IANA timezones", () => {
    expect(TIMEZONES).toContain("UTC")
    expect(TIMEZONES).toContain("Europe/Paris")
    expect(TIMEZONES).toContain("America/New_York")
    expect(TIMEZONES).toContain("Asia/Tokyo")
  })

  it("contains timezones with multiple segments (e.g., Argentina)", () => {
    expect(TIMEZONES).toContain("America/Argentina/Buenos_Aires")
  })

  it("has no duplicates", () => {
    const uniqueTimezones = new Set(TIMEZONES)
    expect(uniqueTimezones.size).toBe(TIMEZONES.length)
  })
})
