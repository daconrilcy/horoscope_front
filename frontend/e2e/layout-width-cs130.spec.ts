// Verifie en navigateur que la largeur centrale non-admin reste portee par le layout.
import { expect, test, type Page } from "@playwright/test"

const ACCESS_TOKEN =
  "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJsYXlvdXQtd2lkdGgtdXNlciJ9."

const AUTH_ME_RESPONSE = {
  data: {
    id: 130,
    role: "user",
    email: "playwright-layout@example.com",
    created_at: "2026-05-10T00:00:00Z",
  },
}

const ASTROLOGERS_RESPONSE = {
  data: [
    {
      id: "layout-luna",
      name: "Luna Celeste",
      first_name: "Luna",
      last_name: "Caron",
      provider_type: "ia",
      avatar_url: null,
      specialties: ["Theme natal", "Transits", "Relations"],
      style: "Pedagogique",
      bio_short: "Astrologue generaliste orientee cycles personnels.",
    },
    {
      id: "layout-orion",
      name: "Orion Vega",
      first_name: "Orion",
      last_name: "Vega",
      provider_type: "ia",
      avatar_url: null,
      specialties: ["Carriere", "Timing", "Guidance"],
      style: "Direct",
      bio_short: "Astrologue specialise dans les questions de decision.",
    },
  ],
}

/** Prepare une session applicative sans dependance au backend local. */
async function setupLayoutSession(page: Page) {
  await page.route("**/v1/auth/me*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(AUTH_ME_RESPONSE),
    })
  })

  await page.route("**/v1/astrologers", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ASTROLOGERS_RESPONSE),
    })
  })

  await page.addInitScript((token) => {
    window.localStorage.setItem("access_token", token)
    window.localStorage.setItem("lang", "fr")
  }, ACCESS_TOKEN)
}

test.describe("CS-130 layout width", () => {
  test("keeps astrologers page width owned by PageLayout instead of a page cap", async ({ page }) => {
    await setupLayoutSession(page)
    await page.setViewportSize({ width: 1280, height: 900 })

    await page.goto("/astrologers")
    await page.waitForLoadState("networkidle")

    const layout = page.locator(".page-layout.people-page")
    await expect(layout).toBeVisible()
    await expect(page.locator(".person-card")).toHaveCount(2)

    const layoutMetrics = await layout.evaluate((element) => {
      const rect = element.getBoundingClientRect()
      const styles = window.getComputedStyle(element)

      return {
        maxWidth: styles.maxWidth,
        width: rect.width,
      }
    })

    expect(layoutMetrics.maxWidth).not.toBe("600px")
    expect(layoutMetrics.width).toBeGreaterThan(700)
  })
})
