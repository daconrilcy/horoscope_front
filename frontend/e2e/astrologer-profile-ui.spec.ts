// Verifie le rendu navigateur critique du profil astrologue.
import { expect, test, type Page } from "@playwright/test"

const ACCESS_TOKEN =
  "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJwcm9maWxlLXVpLXVzZXIifQ."

const PROFILE_ID = "luna-ui"

const AUTH_ME_RESPONSE = {
  data: {
    id: 129,
    role: "user",
    email: "playwright-profile@example.com",
    created_at: "2026-05-10T00:00:00Z",
  },
}

const USER_SETTINGS_RESPONSE = {
  data: {
    default_astrologer_id: null,
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
    bio_full:
      "Luna propose une astrologie claire, progressive et orientee vers la comprehension des cycles personnels.",
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

/** Prepare les reponses API necessaires au profil sans dependance backend. */
async function setupProfileSession(page: Page) {
  await page.route("**/v1/auth/me*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(AUTH_ME_RESPONSE),
    })
  })

  await page.route("**/v1/users/me/settings*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(USER_SETTINGS_RESPONSE),
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
    window.localStorage.setItem("lang", "fr")
  }, ACCESS_TOKEN)
}

/** Verifie que le document ne deborde pas horizontalement au viewport courant. */
async function expectNoHorizontalOverflow(page: Page) {
  const dimensions = await page.evaluate(() => ({
    scrollWidth: document.documentElement.scrollWidth,
    clientWidth: document.documentElement.clientWidth,
  }))

  expect(dimensions.scrollWidth).toBeLessThanOrEqual(dimensions.clientWidth)
}

test.describe("Astrologer profile UI", () => {
  test("keeps desktop and mobile profile without horizontal overflow and exposes hero CTA", async ({ page }) => {
    await setupProfileSession(page)

    await page.setViewportSize({ width: 1280, height: 900 })
    await page.goto(`/astrologers/${PROFILE_ID}`)
    await page.waitForLoadState("networkidle")

    await expect(page.locator(".profile-hero-cta")).toBeVisible()
    await expect(page.locator(".profile-reviews-summary--empty")).toContainText("Nouvel astrologue")
    await expectNoHorizontalOverflow(page)

    await page.setViewportSize({ width: 390, height: 844 })
    await expect(page.locator(".profile-hero-cta")).toBeVisible()
    await expect(page.locator(".profile-hero-cta")).toBeInViewport()
    await expectNoHorizontalOverflow(page)
  })
})
