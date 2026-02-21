import { describe, expect, it, vi } from "vitest"
import { render, screen } from "@testing-library/react"

import App from "../App"
import { AppProviders } from "../state/providers"

describe("App", () => {
  it("renders natal chart page shell", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 404,
        json: async () => ({ error: { code: "natal_chart_not_found", message: "not found" } }),
      }),
    )

    render(
      <AppProviders>
        <App />
      </AppProviders>,
    )

    expect(await screen.findByRole("heading", { name: "Theme natal" })).toBeInTheDocument()
  })
})
