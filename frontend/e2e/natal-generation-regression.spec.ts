// Verifie le flux navigateur natal critique sans appel backend ni provider reel.
import { expect, test, type Page } from "@playwright/test"

const ACCESS_TOKEN =
  "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiIzODEiLCJyb2xlIjoidXNlciJ9."

const LABELS = {
  birthDate: /Date de naissance|Date of birth/i,
  birthTime: /Heure de naissance|Time of birth/i,
  birthCity: /Ville de naissance|City of birth/i,
  birthCountry: /Pays de naissance|Country of birth/i,
  unknownTime: /Heure inconnue|Unknown time/i,
  save: /Enregistrer|Save/i,
  saved: /Profil natal sauvegardé|Natal profile saved/i,
  generate: /Générer mon thème astral|Generate my natal chart/i,
}

const AUTH_ME_RESPONSE = {
  data: {
    id: 381,
    role: "user",
    email: "playwright-natal@example.test",
    created_at: "2026-05-29T00:00:00Z",
  },
}

const EMPTY_BIRTH_PROFILE = {
  data: {
    birth_date: "",
    birth_time: null,
    birth_place: "",
    birth_place_text: "",
    birth_timezone: "Europe/Paris",
    birth_city: null,
    birth_country: null,
  },
  meta: { request_id: "birth-empty" },
}

const SAVED_BIRTH_PROFILE = {
  data: {
    birth_date: "1973-04-24",
    birth_time: "11:00",
    birth_place: "Paris, France",
    birth_place_text: "Paris, France",
    birth_timezone: "Europe/Paris",
    birth_city: "Paris",
    birth_country: "France",
    birth_lat: 48.8566,
    birth_lon: 2.3522,
  },
  meta: { request_id: "birth-saved" },
}

const GENERATED_NATAL_CHART = {
  data: {
    chart_id: "chart-cs-381-paris-1973",
    metadata: {
      reference_version: "1.0.0",
      ruleset_version: "1.0.0",
      house_system: "placidus",
      engine: "simplified",
      degraded_mode: null,
    },
    result: {
      prepared_input: {
        birth_datetime_local: "1973-04-24T11:00:00",
        birth_timezone: "Europe/Paris",
      },
      planet_positions: [{ planet: "Soleil", planet_code: "sun", sign: "Taureau", sign_code: "taurus" }],
      houses: [{ number: 1, cusp_longitude: 120 }],
      aspects: [],
      traditional_conditions: {
        sun: {
          planet_code: "sun",
          hayz: { planet_code: "sun", is_hayz: true },
          rejoicing: { planet_code: "sun", is_rejoicing: false },
        },
      },
    },
  },
  meta: { request_id: "natal-generated" },
}

/** Installe les routes API mockees pour isoler le flux navigateur natal. */
async function setupNatalSession(page: Page) {
  await page.route("**/v1/auth/me*", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(AUTH_ME_RESPONSE) })
  })
  await page.route("**/v1/users/me/settings*", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ data: {} }) })
  })
  await page.route("**/v1/users/me/birth-data*", async (route) => {
    if (route.request().method() === "PUT") {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(SAVED_BIRTH_PROFILE) })
      return
    }
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(EMPTY_BIRTH_PROFILE) })
  })
  await page.route("**/v1/geocoding/search*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          results: [
            {
              display_name: "Paris, France",
              city: "Paris",
              country: "France",
              lat: 48.8566,
              lon: 2.3522,
              timezone_iana: "Europe/Paris",
            },
          ],
          count: 1,
        },
      }),
    })
  })
  await page.route("**/v1/geocoding/resolve*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          id: 19730424,
          provider: "nominatim",
          provider_place_id: 19730424,
          display_name: "Paris, France",
          latitude: 48.8566,
          longitude: 2.3522,
        },
      }),
    })
  })
  await page.route("**/v1/users/me/natal-chart", async (route) => {
    expect(route.request().method()).toBe("POST")
    expect(route.request().postDataJSON()).toEqual({ accurate: true })
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(GENERATED_NATAL_CHART) })
  })
  await page.route("**/v1/users/me/natal-chart/latest*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: { ...GENERATED_NATAL_CHART.data, created_at: "2026-05-29T10:00:00Z" },
        meta: { request_id: "natal-latest" },
      }),
    })
  })
  await page.addInitScript((token) => {
    window.localStorage.setItem("access_token", token)
    window.localStorage.setItem("lang", "fr")
  }, ACCESS_TOKEN)
}

test.describe("Natal generation regression", () => {
  test("creates a natal chart after saving known Paris birth data", async ({ page }) => {
    await setupNatalSession(page)
    const reactConsoleErrors: string[] = []
    page.on("console", (message) => {
      if (message.type() === "error" && message.text().includes("NatalExpertPanel")) {
        reactConsoleErrors.push(message.text())
      }
    })

    const postNatalChart = page.waitForResponse(
      (response) =>
        response.url().includes("/v1/users/me/natal-chart") &&
        !response.url().includes("/latest") &&
        response.request().method() === "POST",
    )

    await page.goto("/profile")
    await page.getByLabel(LABELS.birthDate).fill("1973-04-24")
    await page.getByLabel(LABELS.unknownTime).uncheck()
    await page.getByLabel(LABELS.birthTime).fill("11:00")
    await page.getByLabel(LABELS.birthCity).fill("Paris")
    await page.getByLabel(LABELS.birthCountry).fill("France")
    await page.getByRole("button", { name: LABELS.save }).click()
    await expect(page.getByText(LABELS.saved)).toBeVisible()

    await page.getByRole("button", { name: LABELS.generate }).click()
    const response = await postNatalChart
    const body = await response.json()

    expect(response.status()).toBe(200)
    expect(body.data.chart_id).toBe("chart-cs-381-paris-1973")
    expect(body.data.result.prepared_input.birth_datetime_local).toBe("1973-04-24T11:00:00")
    expect(body.data.result.traditional_conditions.sun.hayz.is_hayz).toBe(true)
    expect(reactConsoleErrors).toEqual([])
  })
})
