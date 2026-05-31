// Verifie /natal en navigateur avec une lecture Basic V2 fixturee pour l'evidence CS-423.
import { expect, test, type Page } from "@playwright/test"
import { mkdirSync, writeFileSync } from "node:fs"
import { resolve } from "node:path"

const EVIDENCE_DIR = resolve(
  process.cwd(),
  "..",
  "_condamad",
  "stories",
  "CS-423-qa-live-lecture-basic-natal-lisible",
  "evidence",
)

const ACCESS_TOKEN =
  "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJkYWNvbnJpbGN5QGhvdG1haWwuY29tIiwicm9sZSI6InVzZXIifQ."

const BASIC_PAYLOAD = {
  chart_id: "chart-cs-423-readable-basic",
  use_case: "natal_interpretation",
  degraded_mode: null,
  narrative_natal_reading_v1: null,
  meta: {
    id: 423,
    level: "complete",
    use_case: "natal_interpretation",
    persona_id: null,
    persona_name: null,
    prompt_version_id: "basic-natal-draft-prompt-v1",
    validation_status: "valid",
    repair_attempted: false,
    fallback_triggered: false,
    was_fallback: false,
    latency_ms: 20,
    request_id: "req-cs-423-browser",
    persisted_at: "2026-06-01T08:00:00Z",
    schema_version: "basic_natal_interpretation_v2",
  },
  interpretation: {
    title: "Ancien titre non public",
    summary: "Ancien résumé non public.",
    sections: [],
    highlights: [],
    advice: [],
    evidence: [],
  },
  basic_natal_interpretation_v2: {
    locale: "fr-FR",
    level: "basic",
    engine_version: "basic-natal-reading-v1",
    schema_version: "basic_natal_interpretation_v2",
    taxonomy_version: "basic-natal-theme-taxonomy-v1",
    salience_version: "basic-natal-salience-v1",
    prompt_version: "basic-natal-draft-prompt-v1",
    validator_version: "basic-natal-validator-v1",
    interpretation: {
      title: "Lecture Basic publique",
      introduction:
        "Introduction lisible: cette lecture synthétise les appuis majeurs du thème sans jargon technique.",
      themes: [
        {
          title: "Identité relationnelle",
          narrative:
            "Votre manière d'avancer cherche des équilibres clairs et une expression personnelle apaisée.",
          public_evidence: [],
        },
        {
          title: "Ressources émotionnelles",
          narrative:
            "Votre sensibilité gagne en stabilité quand les repères sont simples, concrets et réguliers.",
          public_evidence: [],
        },
        {
          title: "Chemin d'évolution",
          narrative:
            "Votre progression devient plus fluide lorsque vous reliez vos choix quotidiens à une intention durable.",
          public_evidence: [],
        },
      ],
      conclusion:
        "Conclusion: la lecture met en avant des pistes compréhensibles, non prédictives et directement lisibles.",
      public_evidence: [
        { label: "Soleil en Balance", meaning: "Expression personnelle orientée vers l'équilibre." },
        { label: "Lune en Taureau", meaning: "Besoin émotionnel de stabilité et de rythme." },
      ],
    },
    public_evidence: [
      { label: "Soleil en Balance", meaning: "Expression personnelle orientée vers l'équilibre." },
      { label: "Lune en Taureau", meaning: "Besoin émotionnel de stabilité et de rythme." },
    ],
    limitations: ["Lecture symbolique, non scientifique et non prédictive."],
    disclaimers: ["Contenu de réflexion personnelle, sans promesse de résultat."],
  },
}

const LATEST_CHART = {
  data: {
    chart_id: "chart-cs-423-readable-basic",
    created_at: "2026-06-01T08:00:00Z",
    metadata: {
      reference_version: "1.0.0",
      ruleset_version: "1.0.0",
      house_system: "placidus",
      engine: "fixture",
      degraded_mode: null,
    },
    result: {
      prepared_input: {
        birth_datetime_local: "1990-06-15T14:30:00",
        birth_timezone: "Europe/Paris",
      },
      planet_positions: [{ planet: "Soleil", planet_code: "sun", sign: "Balance", sign_code: "libra" }],
      houses: [],
      aspects: [],
    },
  },
  meta: { request_id: "latest-cs-423" },
}

async function setupBasicNatalFixture(page: Page) {
  await page.route("**/v1/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          id: 423,
          role: "user",
          email: "daconrilcy@hotmail.com",
          created_at: "2026-06-01T00:00:00Z",
        },
      }),
    })
  })
  await page.route("**/v1/entitlements/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          plan_code: "basic",
          billing_status: "active",
          features: [
            {
              feature_code: "natal_chart_long",
              granted: true,
              reason_code: "granted",
              access_mode: "quota",
              variant_code: "single_astrologer",
              usage_states: [],
            },
          ],
          upgrade_hints: [],
        },
      }),
    })
  })
  await page.route("**/v1/users/me/natal-chart/latest*", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(LATEST_CHART) })
  })
  await page.route("**/v1/natal/interpretations?*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          items: [
            {
              id: 423,
              chart_id: "chart-cs-423-readable-basic",
              level: "complete",
              persona_id: null,
              persona_name: null,
              module: null,
              created_at: "2026-06-01T08:00:00Z",
              use_case: "natal_interpretation",
              prompt_version_id: "basic-natal-draft-prompt-v1",
              was_fallback: false,
            },
          ],
          total: 1,
          limit: 20,
          offset: 0,
        },
      }),
    })
  })
  await page.route("**/v1/natal/interpretations/423*", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ data: BASIC_PAYLOAD }),
    })
  })
  await page.route("**/v1/b2c/astrology/projections*", async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ data: [] }) })
  })
  await page.addInitScript((token) => {
    window.localStorage.setItem("access_token", token)
    window.localStorage.setItem("lang", "fr")
  }, ACCESS_TOKEN)
}

test("capture les preuves desktop et mobile d'une lecture Basic V2 lisible", async ({ page }) => {
  mkdirSync(EVIDENCE_DIR, { recursive: true })
  await setupBasicNatalFixture(page)

  await page.setViewportSize({ width: 1440, height: 1200 })
  await page.goto("/natal")
  await expect(page.getByRole("heading", { name: "Lecture Basic publique" })).toBeVisible()
  await expect(page.getByText(/Introduction lisible/i)).toBeVisible()
  await expect(page.getByText(/Conclusion:/i)).toBeVisible()

  const publicBody = (await page.locator(".ni-content").innerText()).trim()
  expect(publicBody).not.toMatch(
    /cette lecture s'appuie uniquement|Ce repere retient|avec une confiance editoriale controlee|Luminaire: moon|Position planetaire:|north node|south node|visibility_expression|audit_input|condition_axis:|interpretive_signal_ids/i,
  )
  expect(publicBody).not.toMatch(/\b(moon|sun|saturn|north node|south node|Synthese|theme|themes|repere|planetaire|a integrer)\b/i)
  expect(publicBody.match(/Ce que j’ai utilisé pour écrire cette interprétation/g) ?? []).toHaveLength(1)
  expect(publicBody.match(/Mentions légales/g) ?? []).toHaveLength(1)
  expect(page.getByText(/Lecture complète à régénérer/i)).toHaveCount(0)

  writeFileSync(resolve(EVIDENCE_DIR, "basic-readable-api-after.json"), JSON.stringify(BASIC_PAYLOAD, null, 2), "utf8")
  writeFileSync(resolve(EVIDENCE_DIR, "basic-readable-dom-text-after.txt"), `${publicBody}\n`, "utf8")
  await page.screenshot({ path: resolve(EVIDENCE_DIR, "basic-readable-desktop-after.png"), fullPage: true })

  await page.setViewportSize({ width: 390, height: 844 })
  await page.screenshot({ path: resolve(EVIDENCE_DIR, "basic-readable-mobile-after.png"), fullPage: true })
})
