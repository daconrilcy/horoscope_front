// Valide le rendu mobile effectif du dashboard avec les contrats UI actuels.
import { expect, test, type Page } from "@playwright/test"
import { mkdirSync } from "node:fs"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"

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

const SHOULD_CAPTURE_DOD = process.env.CAPTURE_DOD === "1"
const SPEC_DIR = dirname(fileURLToPath(import.meta.url))
const MOBILE_VIEWPORT = { width: 390, height: 844 }

const DAILY_PREDICTION_BODY = JSON.stringify({
  meta: {
    date_local: "2026-03-12",
    timezone: "Europe/Paris",
    computed_at: "2026-03-12T06:00:00Z",
    reference_version: "e2e",
    ruleset_version: "e2e",
    was_reused: false,
    house_system_effective: null,
    is_provisional_calibration: false,
    calibration_label: null,
  },
  summary: {
    overall_tone: "open",
    top_categories: ["love"],
    bottom_categories: [],
    best_window: null,
    main_turning_point: null,
  },
  day_climate: {
    label: "Climat favorable",
    tone: "open",
    intensity: 7,
    stability: 6,
    summary: "Une excellente journée vous attend avec de belles opportunités.",
    top_domains: ["love"],
    watchout: null,
    best_window_ref: null,
  },
  categories: [
    { code: "love", note_20: 18, raw_score: 0.9, power: 0.7, volatility: 0.2, rank: 1, summary: "Relationnel fluide." },
    { code: "work", note_20: 14, raw_score: 0.7, power: 0.5, volatility: 0.3, rank: 2, summary: "Travail stable." },
  ],
  timeline: [],
  turning_points: [],
  has_llm_narrative: true,
})

const BIRTH_PROFILE_BODY = JSON.stringify({
  data: {
    astro_profile: {
      sun_sign_code: "Aries",
    },
    geolocation_consent: true,
  },
})

async function captureDodScreenshot(page: Page, fileName: string) {
  if (!SHOULD_CAPTURE_DOD) {
    return
  }
  const targetPath = resolve(SPEC_DIR, "../../artifacts/dashboard-17-15", fileName)
  mkdirSync(dirname(targetPath), { recursive: true })
  await page.screenshot({ path: targetPath, fullPage: true })
}

async function setupDashboardSession(page: Page, theme: "light" | "dark") {
  await page.route("**/v1/auth/me*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(AUTH_ME_RESPONSE),
    })
  })

  await page.route("**/v1/predictions/daily**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: DAILY_PREDICTION_BODY,
    })
  })

  await page.route("**/v1/birth-profiles/me**", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: BIRTH_PROFILE_BODY,
    })
  })

  await page.addInitScript(
    ({ token, selectedTheme }) => {
      window.localStorage.setItem("access_token", token)
      window.localStorage.setItem("theme", selectedTheme)
      window.localStorage.setItem("lang", "fr")
    },
    { token: ACCESS_TOKEN, selectedTheme: theme },
  )
}

test.describe("Dashboard visual AC4/AC5", () => {
  test("keeps shortcut cards responsive at 390px and renders the astro canvas", async ({ page }) => {
    const pageErrors: string[] = []
    page.on("pageerror", (error) => pageErrors.push(error.message))
    await page.setViewportSize(MOBILE_VIEWPORT)

    await setupDashboardSession(page, "light")

    await page.goto("/dashboard")
    await page.waitForLoadState("networkidle")
    expect(pageErrors).toEqual([])
    await expect(page).toHaveURL(/\/dashboard$/)

    await expect(page.getByText("Une excellente journée vous attend avec de belles opportunités.")).toBeVisible()

    const grid = page.locator(".shortcuts-grid")
    await expect(grid).toBeVisible()
    const cards = page.locator(".shortcut-card")
    await expect(cards).toHaveCount(3)
    await cards.first().scrollIntoViewIfNeeded()
    const positions = await cards.evaluateAll((elements) =>
      elements.map((element) => {
        const rect = element.getBoundingClientRect()
        return { x: rect.x, y: rect.y }
      }),
    )
    expect(Math.abs(positions[0].y - positions[1].y)).toBeLessThan(2)
    expect(positions[0].x).toBeLessThan(positions[1].x)
    expect(positions[2].y).toBeGreaterThan(positions[0].y)

    await expect(page.locator("html")).not.toHaveClass(/dark/)
    const canvas = page.locator(".summary-panel-card-bg .astro-mood-background__canvas")
    await expect(canvas).toBeVisible()
    const canvasSize = await canvas.evaluate((element) => {
      const rect = element.getBoundingClientRect()
      return { width: rect.width, height: rect.height }
    })
    expect(canvasSize.width).toBeGreaterThan(0)
    expect(canvasSize.height).toBeGreaterThan(0)
    await captureDodScreenshot(page, "dashboard-light.png")
  })

  test("renders the astro canvas in dark mode", async ({ page }) => {
    await setupDashboardSession(page, "dark")

    await page.goto("/dashboard")
    await page.waitForLoadState("networkidle")

    await expect(page.locator("html")).toHaveClass(/dark/)
    await expect(page.getByText("Une excellente journée vous attend avec de belles opportunités.")).toBeVisible()
    const canvas = page.locator(".summary-panel-card-bg .astro-mood-background__canvas")
    await expect(canvas).toBeVisible()
    const canvasSize = await canvas.evaluate((element) => {
      const rect = element.getBoundingClientRect()
      return { width: rect.width, height: rect.height }
    })
    expect(canvasSize.width).toBeGreaterThan(0)
    expect(canvasSize.height).toBeGreaterThan(0)
    await captureDodScreenshot(page, "dashboard-dark.png")
  })
})
