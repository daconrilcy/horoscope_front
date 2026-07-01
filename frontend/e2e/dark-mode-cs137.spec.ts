// Verifie en navigateur que les routes CS-137 utilisent les surfaces dark effectives.
import { expect, test, type Page } from "@playwright/test"

const ACCESS_TOKEN =
  "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJkYXJrLW1vZGUtY3MxMzciLCJleHAiOjIwMDAwMDAwMDB9."

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
      {
        feature_code: "natal_chart",
        granted: true,
        reason_code: "included",
        access_mode: "unlimited",
        variant_code: "basic_short",
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

const NATAL_RUN_ID = "dark-natal"

const NATAL_JOB_RESPONSE = {
  run_id: NATAL_RUN_ID,
  status: "completed",
  service_code: "natal_basic",
  result: {
    reading: {
      status: "success",
      reading: {
        schema_version: "natal_reading_v1",
        reading_type: "natal",
        language: "fr",
        summary: {
          title: "Lecture dark natal",
          short_text: "Une lecture claire du theme en mode sombre.",
        },
        chapters: [
          {
            code: "identity",
            title: "Identité",
            summary_sentence: "Une présence stable et lisible.",
            body: "Votre thème natal met en avant une base personnelle structurée et facile à relire.",
            confidence: "high",
            astro_basis: ["Soleil en Bélier"],
          },
          {
            code: "emotions",
            title: "Émotions",
            summary_sentence: "Un climat intérieur nuancé.",
            body: "La lecture émotionnelle reste progressive et conserve des repères accessibles.",
          },
        ],
        calculation_reference: {
          version: "dark-test",
          zodiacal_reference_system: "tropical",
          coordinate_reference_system: "geocentric",
          house_system: "placidus",
          ephemeris_reference: "test-ephemeris",
        },
        legal: {
          disclaimer: "Lecture symbolique.",
        },
      },
    },
    calculation: {
      core_identity: {
        sun: {
          placement: {
            object: "Sun",
            sign: "Aries",
            house: { number: 1, theme: "Identité" },
          },
        },
        moon: {
          placement: {
            object: "Moon",
            sign: "Cancer",
            house: { number: 4, theme: "Intime" },
          },
        },
      },
      angles: {
        ascendant: { sign: "Leo", house: 1 },
      },
      dominant_themes: {
        houses: [{ number: 1, theme: "Identité", importance: "Forte" }],
      },
      dynamics: {
        major_aspects: [{ aspect: "Sun trine Moon", objects: ["Sun", "Moon"], orb_degrees: 1.2 }],
      },
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

  await page.route(`**/v1/astral/jobs/${NATAL_RUN_ID}`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ data: NATAL_JOB_RESPONSE }),
    })
  })

  await page.route(`**/v1/astral/jobs/${NATAL_RUN_ID}/events`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "text/event-stream",
      body: "",
    })
  })

  await page.addInitScript((token) => {
    window.localStorage.setItem("access_token_v2", token)
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
    await expect(page.locator(".summary-panel-card")).toBeVisible()
    await expect(page.locator(".shortcuts-section")).toBeVisible()
    await expect(page.locator(".shortcut-card")).toHaveCount(2)

    const pageTitleColor = await readColorChannels(page, ".summary-title", "color")
    expect(pageTitleColor.red).toBeGreaterThan(220)
    expect(pageTitleColor.green).toBeGreaterThan(210)
    expect(pageTitleColor.blue).toBeGreaterThan(220)

    const welcomeColor = await readColorChannels(page, ".summary-welcome", "color")
    expect(welcomeColor.red).toBeGreaterThan(190)
    expect(welcomeColor.green).toBeGreaterThan(180)
    expect(welcomeColor.blue).toBeGreaterThan(200)

    const summaryTextColor = await readColorChannels(page, ".summary-panel-card p", "color")
    expect(summaryTextColor.red).toBeGreaterThan(220)
    expect(summaryTextColor.green).toBeGreaterThan(210)
    expect(summaryTextColor.blue).toBeGreaterThan(220)

    const summaryCtaBackground = await readColorChannels(page, ".summary-panel-card", "backgroundColor")
    expect(summaryCtaBackground.alpha).toBeGreaterThanOrEqual(0.05)

    const summaryCtaColor = await readColorChannels(page, ".summary-panel-card__link", "color")
    expect(summaryCtaColor.red).toBeGreaterThan(220)
    expect(summaryCtaColor.green).toBeGreaterThan(210)
    expect(summaryCtaColor.blue).toBeGreaterThan(220)

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

    await page.locator(".summary-panel-card").click()
    await expect(page).toHaveURL(/\/dashboard\/horoscope$/)
  })

  test("applique les tokens dark effectifs sur /dashboard/horoscope", async ({ page }) => {
    await setupDarkSession(page)

    await page.goto("/dashboard/horoscope")
    await page.waitForLoadState("networkidle")

    await expect(page.locator("html")).toHaveClass(/dark/)
    await expect(page.locator(".daily-layout")).toBeVisible()
    await expect(page.getByRole("heading", { name: "Votre horoscope du jour" })).toBeVisible()

    const pageToken = await page.locator("#root").evaluate((element) =>
      window.getComputedStyle(element).getPropertyValue("--app-premium-page-layout-background").trim(),
    )
    expect(pageToken).not.toContain("#fffafc")

    const titleColor = await readColorChannels(page, ".daily-page-header__title", "color")
    expect(titleColor.red).toBeGreaterThan(220)
    expect(titleColor.green).toBeGreaterThan(210)
    expect(titleColor.blue).toBeGreaterThan(220)

    const layoutText = await readColorChannels(page, ".daily-layout p", "color")
    expect(layoutText.red).toBeGreaterThan(190)
    expect(layoutText.green).toBeGreaterThan(180)
    expect(layoutText.blue).toBeGreaterThan(200)
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

  test("applique les surfaces dark effectives sur /natal", async ({ page }) => {
    await setupDarkSession(page)

    await page.goto(`/natal?runId=${NATAL_RUN_ID}`)
    await page.waitForLoadState("networkidle")

    await expect(page.locator("html")).toHaveClass(/dark/)
    await expect(page.getByRole("heading", { name: "Thème natal", exact: true })).toBeVisible()
    await expect(page.locator(".natal-reading__chapter").first()).toBeVisible()
    await expect(page.locator(".natal-reading-facts").first()).toBeVisible()
    await expect(page.locator(".natal-reading-summary").first()).toBeVisible()

    const appBackgroundToken = await page.locator(".app-bg").evaluate((element) =>
      window.getComputedStyle(element).getPropertyValue("--premium-app-bg").trim(),
    )
    expect(appBackgroundToken).not.toContain("#fff")

    const headerBackground = await readColorChannels(page, ".app-header", "backgroundColor")
    expect(headerBackground.red).toBeLessThan(40)
    expect(headerBackground.green).toBeLessThan(50)
    expect(headerBackground.blue).toBeLessThan(80)

    const titleColor = await readColorChannels(page, ".natal-reading-hero h1", "color")
    expect(titleColor.red).toBeGreaterThan(220)
    expect(titleColor.green).toBeGreaterThan(210)
    expect(titleColor.blue).toBeGreaterThan(220)

    const chapterBackground = await readColorChannels(page, ".natal-reading__chapter", "backgroundColor")
    expect(chapterBackground.red).toBeLessThan(80)
    expect(chapterBackground.green).toBeLessThan(90)
    expect(chapterBackground.blue).toBeLessThan(120)
    expect(chapterBackground.alpha).toBeGreaterThanOrEqual(0.55)

    const summaryBackground = await readColorChannels(page, ".natal-reading-summary", "backgroundColor")
    expect(summaryBackground.red).toBeLessThan(80)
    expect(summaryBackground.green).toBeLessThan(90)
    expect(summaryBackground.blue).toBeLessThan(120)
    expect(summaryBackground.alpha).toBeGreaterThanOrEqual(0.55)

    const badgeBackground = await readColorChannels(page, ".natal-badge--basis", "backgroundColor")
    expect(badgeBackground.red).toBeLessThan(100)
    expect(badgeBackground.green).toBeLessThan(105)
    expect(badgeBackground.blue).toBeLessThan(135)

    const factsTextColor = await readColorChannels(page, ".natal-reading-facts__header h2", "color")
    expect(factsTextColor.red).toBeGreaterThan(220)
    expect(factsTextColor.green).toBeGreaterThan(210)
    expect(factsTextColor.blue).toBeGreaterThan(220)
  })
})
