import { render } from "@testing-library/react"
import { beforeEach, describe, expect, it, vi } from "vitest"

import { useLatestNatalChart } from "../api/natalChart"

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
        queryKey: ["latest-natal-chart", "anonymous"],
        enabled: false,
      }),
    )
  })
})
