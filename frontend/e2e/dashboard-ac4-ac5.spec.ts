import { expect, test } from "@playwright/test"

const AUTH_ME_RESPONSE = {
  data: {
    id: 42,
    role: "user",
    email: "playwright@example.com",
    created_at: "2026-02-24T00:00:00Z",
  },
}

const ACCESS_TOKEN =
  "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJwbGF5d3JpZ2h0LXVzZXIifQ."

test.describe("Dashboard visual AC4/AC5", () => {
  test("keeps 3 mini cards columns at 390px and shows light constellation color", async ({ page }) => {
    const pageErrors: string[] = []
    page.on("pageerror", (error) => pageErrors.push(error.message))

    await page.route("**/v1/auth/me*", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(AUTH_ME_RESPONSE),
      })
    })

    await page.addInitScript(({ token }) => {
      window.localStorage.setItem("access_token", token)
      window.localStorage.setItem("theme", "light")
      window.localStorage.setItem("lang", "fr")
    }, { token: ACCESS_TOKEN })

    await page.goto("/dashboard")
    await page.waitForLoadState("networkidle")
    expect(pageErrors).toEqual([])
    await expect(page).toHaveURL(/\/dashboard$/)

    const grid = page.locator(".mini-cards-grid")
    await expect(grid).toBeVisible()
    const cards = page.locator(".mini-card")
    await expect(cards).toHaveCount(3)
    await cards.first().scrollIntoViewIfNeeded()
    const positions = await cards.evaluateAll((elements) =>
      elements.map((element) => {
        const rect = element.getBoundingClientRect()
        return { x: rect.x, y: rect.y }
      }),
    )
    expect(Math.abs(positions[0].y - positions[1].y)).toBeLessThan(2)
    expect(Math.abs(positions[1].y - positions[2].y)).toBeLessThan(2)
    expect(positions[0].x).toBeLessThan(positions[1].x)
    expect(positions[1].x).toBeLessThan(positions[2].x)

    await expect(page.locator("html")).not.toHaveClass(/dark/)
    const constellation = page.locator(".hero-card__constellation-svg")
    await expect(constellation).toBeVisible()
    const computedColor = await constellation.evaluate((element) => window.getComputedStyle(element).color)
    const channels = computedColor.match(/\d+(?:\.\d+)?/g)?.slice(0, 3).map(Number) ?? []
    expect(channels.length).toBe(3)
    const [r, g, b] = channels
    expect(b).toBeGreaterThan(r)
    expect(b).toBeGreaterThan(g)
  })

  test("shows white constellation in dark mode", async ({ page }) => {
    await page.route("**/v1/auth/me*", async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(AUTH_ME_RESPONSE),
      })
    })

    await page.addInitScript(({ token }) => {
      window.localStorage.setItem("access_token", token)
      window.localStorage.setItem("theme", "dark")
      window.localStorage.setItem("lang", "fr")
    }, { token: ACCESS_TOKEN })

    await page.goto("/dashboard")
    await page.waitForLoadState("networkidle")

    await expect(page.locator("html")).toHaveClass(/dark/)
    const constellation = page.locator(".hero-card__constellation-svg")
    await expect(constellation).toBeVisible()
    const computedColor = await constellation.evaluate((element) => window.getComputedStyle(element).color)
    
    // In dark mode it should be #ffffff or rgba(255, 255, 255, ...)
    const channels = computedColor.match(/\d+/g)?.slice(0, 3).map(Number) ?? []
    expect(channels).toEqual([255, 255, 255])
  })
})
