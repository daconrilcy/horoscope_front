// Verifie en navigateur que les routes CS-137 utilisent les surfaces dark effectives.
import { expect, test, type Page } from "@playwright/test"

const ACCESS_TOKEN =
  "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJkYXJrLW1vZGUtY3MxMzcifQ."

const PROFILE_ID = "luna-dark"

const AUTH_ME_RESPONSE = {
  data: {
    id: 137,
    role: "user",
    email: "playwright-dark@example.com",
    created_at: "2026-05-10T00:00:00Z",
  },
}

const ENTITLEMENTS_RESPONSE = {
  data: {
    plan_code: "premium",
    billing_status: "active",
    features: [
      {
        feature_code: "thematic_consultation",
        granted: true,
        reason_code: "included",
        access_mode: "unlimited",
        variant_code: null,
        usage_states: [],
      },
    ],
    upgrade_hints: [],
  },
}

const CATALOGUE_RESPONSE = {
  items: [
    {
      key: "career",
      icon_ref: "✨",
      title: "Orientation professionnelle",
      subtitle: "Clarifiez votre prochaine etape.",
      description: "Lecture thematique.",
      metadata_config: { tags: ["travail", "cycle"] },
      sort_order: 1,
    },
  ],
  meta: { request_id: "dark-cs137", total: 1 },
}

const USER_SETTINGS_RESPONSE = {
  data: {
    default_astrologer_id: null,
  },
}

const DAILY_PREDICTION_RESPONSE = {
  data: {
    sign: "aries",
    date: "2026-05-10",
    summary: "Une journee propice a clarifier vos priorites.",
    love: "Dialogue simple.",
    work: "Priorite aux actions utiles.",
    energy: "Rythme stable.",
    mood: "Confiant.",
    score: 78,
  },
}

const BIRTH_PROFILE_RESPONSE = {
  data: {
    birth_date: "1990-01-15",
    birth_time: "10:30",
    birth_place: "Paris, France",
    birth_timezone: "Europe/Paris",
    astro_profile: {
      sun_sign_code: "aries",
      ascendant_sign_code: "leo",
      missing_birth_time: false,
    },
  },
}

const PROFILE_RESPONSE = {
  data: {
    id: PROFILE_ID,
    name: "Luna Celeste",
    first_name: "Luna",
    last_name: "Caron",
    provider_type: "ia",
    avatar_url: null,
    specialties: ["Theme natal", "Transits", "Relations"],
    style: "Pedagogique",
    bio_short: "Astrologue generaliste.",
    bio_full: "Luna propose une astrologie claire et orientee vers la comprehension des cycles.",
    gender: "female",
    age: 36,
    location: "Paris",
    quote: "Je vous aide a relire votre theme avec douceur.",
    mission_statement: "Comprendre avant d'agir.",
    ideal_for: "Ideal pour debutants",
    metrics: {
      total_experience_years: 5,
      experience_years: 7,
      consultations_count: 2400,
      average_rating: 4.8,
    },
    specialties_details: [
      { title: "Theme natal", description: "Lecture simple et progressive." },
      { title: "Transits", description: "Comprendre les cycles actuels." },
    ],
    professional_background: ["5 ans accompagnement", "7 ans astrologue"],
    key_skills: [],
    behavioral_style: [],
    reviews: [],
    review_summary: {
      average_rating: 4.8,
      review_count: 0,
    },
    action_state: {
      has_chat: false,
      has_natal_interpretation: false,
    },
  },
}

/** Installe une session authentifiee en theme dark sans dependance backend. */
async function setupDarkSession(page: Page) {
  await page.route("**/v1/auth/me*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(AUTH_ME_RESPONSE),
    })
  })

  await page.route("**/v1/entitlements/me*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(ENTITLEMENTS_RESPONSE),
    })
  })

  await page.route("**/v1/consultations/catalogue*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(CATALOGUE_RESPONSE),
    })
  })

  await page.route("**/v1/users/me/settings*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(USER_SETTINGS_RESPONSE),
    })
  })

  await page.route("**/v1/predictions/daily*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(DAILY_PREDICTION_RESPONSE),
    })
  })

  await page.route("**/v1/birth-profiles/me*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(BIRTH_PROFILE_RESPONSE),
    })
  })

  await page.route("**/v1/users/me/birth-data*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(BIRTH_PROFILE_RESPONSE),
    })
  })

  await page.route(`**/v1/astrologers/${PROFILE_ID}*`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(PROFILE_RESPONSE),
    })
  })

  await page.addInitScript((token) => {
    window.localStorage.setItem("access_token", token)
    window.localStorage.setItem("theme", "dark")
    window.localStorage.setItem("lang", "fr")
  }, ACCESS_TOKEN)
}

/** Retourne les composantes numeriques d'une couleur CSS calculee. */
async function readColorChannels(page: Page, selector: string, property: "color" | "backgroundColor") {
  const value = await page.locator(selector).first().evaluate((element, cssProperty) => {
    return window.getComputedStyle(element)[cssProperty]
  }, property)
  const channels = value.match(/\d+(?:\.\d+)?/g)?.map(Number) ?? []
  return {
    value,
    red: channels[0] ?? 0,
    green: channels[1] ?? 0,
    blue: channels[2] ?? 0,
    alpha: channels[3] ?? 1,
  }
}

test.describe("CS-137 dark mode runtime surfaces", () => {
  test("applique les surfaces dark effectives a toute la page dashboard", async ({ page }) => {
    await setupDarkSession(page)

    await page.goto("/dashboard")
    await page.waitForLoadState("networkidle")

    await expect(page.locator("html")).toHaveClass(/dark/)
    await expect(page.locator(".summary-title")).toBeVisible()
    await expect(page.locator(".summary-panel-card-wrapper")).toBeVisible()
    await expect(page.locator(".shortcuts-section")).toBeVisible()
    await expect(page.locator(".shortcut-card")).toHaveCount(3)

    const pageTitleColor = await readColorChannels(page, ".summary-title", "color")
    expect(pageTitleColor.red).toBeGreaterThan(220)
    expect(pageTitleColor.green).toBeGreaterThan(210)
    expect(pageTitleColor.blue).toBeGreaterThan(220)

    const welcomeColor = await readColorChannels(page, ".summary-welcome", "color")
    expect(welcomeColor.red).toBeGreaterThan(190)
    expect(welcomeColor.green).toBeGreaterThan(180)
    expect(welcomeColor.blue).toBeGreaterThan(200)

    const summaryTextColor = await readColorChannels(page, ".summary-panel-card__text", "color")
    expect(summaryTextColor.red).toBeGreaterThan(220)
    expect(summaryTextColor.green).toBeGreaterThan(210)
    expect(summaryTextColor.blue).toBeGreaterThan(220)

    const summaryCtaBackground = await readColorChannels(page, ".summary-panel-card__cta", "backgroundColor")
    expect(summaryCtaBackground.alpha).toBeGreaterThanOrEqual(0.6)

    const summaryCtaColor = await readColorChannels(page, ".summary-panel-card__cta", "color")
    expect(summaryCtaColor.red).toBeGreaterThan(220)
    expect(summaryCtaColor.green).toBeGreaterThan(210)
    expect(summaryCtaColor.blue).toBeGreaterThan(220)

    const pillBackground = await readColorChannels(page, ".default_card_pill", "backgroundColor")
    expect(pillBackground.alpha).toBeGreaterThanOrEqual(0.5)

    const cardBackground = await readColorChannels(page, ".shortcut-card", "backgroundColor")
    expect(cardBackground.alpha).toBeLessThanOrEqual(0.12)

    const titleColor = await readColorChannels(page, ".shortcut-card__title", "color")
    expect(titleColor.red).toBeGreaterThan(220)
    expect(titleColor.green).toBeGreaterThan(210)
    expect(titleColor.blue).toBeGreaterThan(220)

    const subtitleBackground = await readColorChannels(page, ".shortcut-card__subtitle", "backgroundColor")
    expect(subtitleBackground.alpha).toBeLessThanOrEqual(0.12)

    const subtitleColor = await readColorChannels(page, ".shortcut-card__subtitle", "color")
    expect(subtitleColor.red).toBeGreaterThan(190)
    expect(subtitleColor.green).toBeGreaterThan(180)
    expect(subtitleColor.blue).toBeGreaterThan(200)

    await page.locator(".summary-panel-card-wrapper").click()
    await expect(page).toHaveURL(/\/dashboard\/horoscope$/)
  })

  test("applique les tokens dark effectifs sur /consultations", async ({ page }) => {
    await setupDarkSession(page)

    await page.goto("/consultations")
    await page.waitForLoadState("networkidle")

    await expect(page.locator("html")).toHaveClass(/dark/)
    await expect(page.locator(".activity-card-premium").first()).toBeVisible()

    const pageToken = await page.locator("#root").evaluate((element) =>
      window.getComputedStyle(element).getPropertyValue("--app-premium-page-layout-background").trim(),
    )
    expect(pageToken).not.toContain("#fffafc")

    const titleColor = await readColorChannels(page, ".premium-hero-title", "color")
    expect(titleColor.red).toBeGreaterThan(220)
    expect(titleColor.green).toBeGreaterThan(210)
    expect(titleColor.blue).toBeGreaterThan(220)

    const cardBackground = await readColorChannels(page, ".activity-card-premium", "backgroundColor")
    expect(cardBackground.alpha).toBeLessThanOrEqual(0.12)
  })

  test("applique les surfaces dark effectives sur /astrologers/:id", async ({ page }) => {
    await setupDarkSession(page)

    await page.goto(`/astrologers/${PROFILE_ID}`)
    await page.waitForLoadState("networkidle")

    await expect(page.locator("html")).toHaveClass(/dark/)
    await expect(page.locator(".profile-hero-cta")).toBeVisible()

    const cardToken = await page.locator(".astrologer-profile-container").evaluate((element) =>
      window.getComputedStyle(element).getPropertyValue("--profile-card-surface").trim(),
    )
    expect(cardToken).not.toContain("255, 255, 255, 0.62")

    const nameColor = await readColorChannels(page, ".profile-full-name", "color")
    expect(nameColor.red).toBeGreaterThan(220)
    expect(nameColor.green).toBeGreaterThan(210)
    expect(nameColor.blue).toBeGreaterThan(220)

    const metricsBackground = await readColorChannels(page, ".profile-metrics-bar", "backgroundColor")
    expect(metricsBackground.alpha).toBeLessThanOrEqual(0.12)
  })
})
