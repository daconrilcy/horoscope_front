// Verifie la lisibilite mobile de /natal avec une lecture Astral longue et des reperes longs.
import { expect, test, type Locator, type Page } from "@playwright/test"
import { mkdirSync } from "node:fs"
import { resolve } from "node:path"

const EVIDENCE_DIR = resolve(
  process.cwd(),
  "..",
  "_condamad",
  "stories",
  "CS-445-optimiser-page-natal-mobile",
  "evidence",
)

const ACCESS_TOKEN =
  "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJkYWNvbnJpbGN5QGhvdG1haWwuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjQxMDI0NDQ4MDB9."
const ASTRAL_RUN_ID = "run-cs-445-natal-mobile"

const MOBILE_VIEWPORTS = [
  { width: 360, height: 780 },
  { width: 390, height: 844 },
  { width: 430, height: 932 },
] as const

const ASTRAL_RESULT = {
  metadata: {
    product_code: "natal_full_basic",
    tier: "basic",
    variant: "full",
  },
  quality: {
    reading_completeness: "completed",
  },
  calculation: {
    core_identity: {
      sun: {
        placement: {
          object: "Sun",
          sign: "Cancer",
          house: { number: 6, theme: "Routines / hygiène de vie" },
          longitude_deg: 94.12,
        },
      },
      moon: {
        placement: {
          object: "Moon",
          sign: "Libra",
          house: { number: 2, theme: "Ressources" },
          longitude_deg: 185.4,
        },
      },
    },
    angles: {
      ascendant: { sign: "Virgo", house: 1 },
    },
    dominant_themes: {
      houses: [{ number: 6, theme: "Routines / hygiène de vie", importance: "Très haute" }],
    },
    placements: {
      supporting: [
        {
          object: "Mercury",
          sign: "Leo",
          house: { number: 6, theme: "Routines / hygiène de vie" },
          longitude_deg: 121.8,
        },
      ],
    },
    dynamics: {
      major_aspects: [
        {
          aspect: "Venus square Saturn",
          objects: ["Venus", "Saturn"],
          orb_degrees: 1.2,
          quality: "Tension constructive",
        },
      ],
    },
  },
  reading: {
    status: "success",
    reading: {
      schema_version: "natal_reading_v1",
      reading_type: "natal",
      language: "fr",
      summary: {
        title: "Lecture mobile Astral",
        short_text:
          "Une synthèse mobile volontairement concise pour garder le portrait utile sans retarder la lecture.",
      },
      chapters: [
        {
          code: "identity",
          title: "Identité",
          summary_sentence: "Une orientation personnelle claire structure la lecture.",
          body:
            "Votre lecture commence par une orientation personnelle claire. Elle met en avant une manière d'avancer qui cherche des repères concrets sans écraser les nuances du thème.\n\nLa suite du chapitre reste lisible sur mobile, sans colonne latérale ni zone de texte enfermée dans un petit scroll interne.",
          confidence: "medium",
          astro_basis: [
            "Soleil en Cancer",
            "Maison VI - Routines / hygiène de vie",
            "Ascendant en Vierge avec une formulation volontairement longue",
          ],
        },
        {
          code: "daily-life",
          title: "Rythme quotidien",
          summary_sentence: "Le rythme quotidien donne immédiatement de la matière lisible.",
          body:
            "Le deuxième chapitre reste ouvert pour donner immédiatement de la matière. Il doit se lire avec un interligne confortable et des boutons faciles à toucher.",
          confidence: "high",
          astro_basis: ["Mercure en Lion", "Maison VI - Routines / hygiène de vie"],
        },
        {
          code: "relationships",
          title: "Relations",
          summary_sentence: "Les relations restent disponibles après une action explicite.",
          body: "Ce chapitre secondaire reste replié jusqu'à l'action explicite de l'utilisateur.",
          confidence: "low",
          astro_basis: ["Vénus carré Saturne", "Maison VII - Relations et engagements durables"],
        },
      ],
      evidence_summary: {
        language: "fr",
        score_scale_version: "score-scale-v1",
        dominant_houses: [
          {
            house_label: "Maison VI - Routines / hygiène de vie",
            theme_label: "Routines / hygiène de vie",
            score: 0.82,
            strength_label: "Très haute",
            evidence: [
              { label: "Soleil en maison VI" },
              { label: "Mercure en maison VI" },
            ],
          },
        ],
        sensitive_positions: [
          {
            object_label: "Mercure",
            sign_label: "Lion",
            house_label: "Maison VI - Routines / hygiène de vie",
          },
        ],
        major_aspects: [
          {
            label: "Vénus carré Saturne",
            source_object_label: "Vénus",
            target_object_label: "Saturne",
            aspect_label: "Carré",
            quality_label: "Tension constructive",
            phase_label: "Appliquant",
            orb_degrees: 1.2,
          },
        ],
      },
      legal: {
        disclaimer: "Lecture symbolique et non médicale.",
      },
      calculation_reference: {
        zodiacal_reference_system: "tropical",
        coordinate_reference_system: "geocentric",
        house_system: "placidus",
        ephemeris_reference: "Swiss Ephemeris 2.10",
        precision: "arc-second",
      },
    },
  },
  explanations: {
    status: "complete",
    language_code: "fr",
    items: [
      {
        title: "Maison VI - Routines / hygiène de vie",
        explanation:
          "Ce repère explique pourquoi les routines reviennent dans la lecture. Il doit rester consultable sans casser la lecture principale.",
      },
    ],
  },
}

async function setupNatalFixture(page: Page) {
  await page.route("**/v1/auth/me", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          id: 445,
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
              feature_code: "horoscope_daily",
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

  await page.route("**/v1/users/me/birth-data", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          birth_date: "1990-01-15",
          birth_time: "10:30",
          birth_place: "Paris, France",
          birth_timezone: "Europe/Paris",
          birth_city: "Paris",
          birth_country: "France",
          birth_lat: 48.8566,
          birth_lon: 2.3522,
          geolocation_consent: false,
        },
        meta: { request_id: "birth-data-cs-445" },
      }),
    })
  })

  await page.route(`**/v1/astral/jobs/${ASTRAL_RUN_ID}`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        data: {
          run_id: ASTRAL_RUN_ID,
          status: "completed",
          service_code: "natal_basic",
          result: ASTRAL_RESULT,
        },
      }),
    })
  })

  await page.route(`**/v1/astral/jobs/${ASTRAL_RUN_ID}/events`, async (route) => {
    await route.fulfill({ status: 204, body: "" })
  })

  await page.addInitScript((token) => {
    window.localStorage.setItem("access_token_v2", token)
    window.localStorage.setItem("lang", "fr")
  }, ACCESS_TOKEN)
}

async function expectNoHorizontalOverflow(page: Page) {
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - window.innerWidth)
  expect(overflow).toBeLessThanOrEqual(1)
}

async function expectTouchTarget(locator: Locator) {
  const box = await locator.boundingBox()
  expect(box?.height ?? 0).toBeGreaterThanOrEqual(44)
}

async function expectCompactSummaryTarget(locator: Locator) {
  const box = await locator.boundingBox()
  expect(box?.height ?? 0).toBeGreaterThanOrEqual(36)
}

test("garde /natal lisible et non masque a 360, 390 et 430 px", async ({ page }) => {
  mkdirSync(EVIDENCE_DIR, { recursive: true })
  await setupNatalFixture(page)

  await page.goto(`/natal?runId=${ASTRAL_RUN_ID}`)
  await expect(page.getByRole("heading", { name: "Thème natal", exact: true })).toBeVisible()

  for (const viewport of MOBILE_VIEWPORTS) {
    await page.setViewportSize(viewport)
    await page.evaluate(() => window.scrollTo(0, 0))
    await expectNoHorizontalOverflow(page)
    await expect(page.getByRole("heading", { name: "Base du calcul natal" })).toBeVisible()
    await expect(page.getByRole("region", { name: "Repères principaux" })).toContainText("Soleil")
    await expect(page.getByRole("region", { name: "Système et méthodes de calcul" })).toContainText("Paris")
    await expect(page.getByRole("button", { name: "Afficher la base" })).toHaveCount(0)
    const explanationsSection = page.getByRole("region", { name: "Repères astrologiques" })
    const explanationExcerpt = explanationsSection.getByText(/Ce repère explique pourquoi les routines/i)
    const explanationToggle = explanationsSection
      .locator(".natal-reading__chapter--excerpt-toggle .natal-reading__chapter-toggle")
      .first()
    await expect(explanationExcerpt).not.toBeVisible()
    await explanationToggle.click()
    await expect(explanationToggle).toHaveAttribute("aria-expanded", "true")
    await expect(explanationExcerpt).toBeVisible()
    await explanationToggle.click()
    await expect(explanationToggle).toHaveAttribute("aria-expanded", "false")
    await expect(explanationExcerpt).not.toBeVisible()

    const progressList = page.locator(".natal-reading-summary__list").first()
    const progressStyles = await progressList.evaluate((element) => {
      const styles = window.getComputedStyle(element)
      return {
        display: styles.display,
        gridTemplateColumns: styles.gridTemplateColumns,
        overflowX: styles.overflowX,
      }
    })
    expect(progressStyles.display).toBe("grid")
    expect(progressStyles.gridTemplateColumns.trim().split(/\s+/)).toHaveLength(2)
    expect(progressStyles.overflowX).toBe("visible")

    const progressLink = page.locator(".natal-reading-summary__button").first()
    await expectCompactSummaryTarget(progressLink)
    await expect(progressLink.locator(".natal-reading-summary__title")).toHaveText("Identité")
    await expect(page.locator(".natal-reading-summary__title").nth(1)).toHaveText("Émotions")
    await expect(page.locator(".natal-reading-summary__title").nth(2)).toHaveText("Relations")
    const progressLinkOverflow = await page.locator(".natal-reading-summary__item").evaluateAll((items) =>
      items.map((item) => {
        const link = item.querySelector(".natal-reading-summary__button")
        const itemBox = item.getBoundingClientRect()
        const linkBox = link?.getBoundingClientRect()
        return {
          itemWidth: itemBox.width,
          linkWidth: linkBox?.width ?? 0,
          overflow: (linkBox?.width ?? 0) - itemBox.width,
        }
      }),
    )
    expect(progressLinkOverflow.every(({ overflow }) => overflow <= 1)).toBe(true)
    const firstViewportLayout = await page.evaluate(() => {
      const summary = document.querySelector(".natal-reading-summary")?.getBoundingClientRect()
      const hero = document.querySelector(".natal-reading-hero")?.getBoundingClientRect()
      const metrics = document.querySelector(".natal-reading-metrics")?.getBoundingClientRect()
      return {
        heroTop: hero?.top ?? 0,
        metricsTop: metrics?.top ?? 0,
        summaryHeight: summary?.height ?? 0,
      }
    })
    if (viewport.width <= 390) {
      expect(firstViewportLayout.summaryHeight).toBeLessThanOrEqual(400)
      expect(firstViewportLayout.heroTop).toBeLessThanOrEqual(460)
      expect(firstViewportLayout.metricsTop).toBeLessThanOrEqual(720)
    }
    if (viewport.width <= 360) {
      const headerLayout = await page.evaluate(() => {
        const header = document.querySelector(".app-header")?.getBoundingClientRect()
        const title = document.querySelector(".app-header-title")?.getBoundingClientRect()
        const actions = document.querySelector(".app-header-actions")?.getBoundingClientRect()
        return {
          actionsRight: actions?.right ?? 0,
          actionsStart: actions?.left ?? 0,
          headerRight: header?.right ?? 0,
          titleEnd: title?.right ?? 0,
        }
      })
      expect(headerLayout.titleEnd).toBeLessThanOrEqual(headerLayout.actionsStart)
      expect(headerLayout.actionsRight).toBeLessThanOrEqual(headerLayout.headerRight)
    }
    const measuredPanelBackgrounds = await page.evaluate(() => {
      const selectors = [".natal-reading-summary", ".natal-reading-metrics", ".bottom-nav"]
      return selectors.map((selector) => {
        const element = document.querySelector(selector)
        return {
          backgroundColor: element ? window.getComputedStyle(element).backgroundColor : "",
          selector,
        }
      })
    })
    const transparentPanels = measuredPanelBackgrounds.filter(
      ({ backgroundColor }) =>
        backgroundColor === "" || backgroundColor === "transparent" || backgroundColor === "rgba(0, 0, 0, 0)",
    )
    expect(transparentPanels, JSON.stringify(measuredPanelBackgrounds)).toEqual([])

    const metaToggle = page.locator(".natal-reading__meta-toggle").first()
    await expectTouchTarget(metaToggle)
    await expect(metaToggle).toHaveAttribute("aria-expanded", "false")
    await metaToggle.click()
    await expect(metaToggle).toHaveAttribute("aria-expanded", "true")
    await expect(metaToggle).toHaveText("Masquer les repères")

    const longBasis = page.getByText("Maison VI - Routines / hygiène de vie").first()
    await expect(longBasis).toBeVisible()
    const longBasisStyles = await longBasis.evaluate((element) => {
      const styles = window.getComputedStyle(element)
      return {
        fontSize: Number.parseFloat(styles.fontSize),
        whiteSpace: styles.whiteSpace,
        overflowX: styles.overflowX,
      }
    })
    expect(longBasisStyles.fontSize).toBeGreaterThanOrEqual(10)
    expect(longBasisStyles.whiteSpace).not.toBe("nowrap")
    expect(longBasisStyles.overflowX).not.toBe("auto")

    const firstChapter = page.locator(".natal-reading__chapter").first()
    const chapterColumns = await firstChapter.evaluate((element) => window.getComputedStyle(element).gridTemplateColumns)
    expect(chapterColumns.trim().split(/\s+/)).toHaveLength(1)

    const chapterBodyStyles = await page.locator(".natal-reading__chapter-body").first().evaluate((element) => {
      const styles = window.getComputedStyle(element)
      return {
        overflowY: styles.overflowY,
        fontSize: Number.parseFloat(window.getComputedStyle(element.querySelector("p") ?? element).fontSize),
        lineHeight: Number.parseFloat(window.getComputedStyle(element.querySelector("p") ?? element).lineHeight),
      }
    })
    expect(chapterBodyStyles.overflowY).not.toBe("auto")
    expect(chapterBodyStyles.fontSize).toBeGreaterThanOrEqual(12)
    expect(chapterBodyStyles.lineHeight).toBeGreaterThanOrEqual(18)

    const metaTop = await page.locator(".natal-reading__chapter-meta").first().evaluate((element) => {
      const metaBox = element.getBoundingClientRect()
      const mainBox = element.parentElement?.querySelector(".natal-reading__chapter-main")?.getBoundingClientRect()
      return { metaTop: metaBox.top, mainBottom: mainBox?.bottom ?? 0 }
    })
    expect(metaTop.metaTop).toBeGreaterThanOrEqual(metaTop.mainBottom - 1)

    await metaToggle.click()
    await expect(metaToggle).toHaveAttribute("aria-expanded", "false")

    const reduceButton = page.locator(".natal-reading__chapter-toggle").first()
    await expectTouchTarget(reduceButton)
    await expectTouchTarget(page.getByRole("button", { name: "Lire la suite" }).first())
    await reduceButton.click()
    await expect(reduceButton).toHaveAttribute("aria-expanded", "false")
    await expect(page.locator(".natal-reading__chapter-body").first()).not.toBeVisible()
    await reduceButton.click()
    await expect(reduceButton).toHaveAttribute("aria-expanded", "true")
    await expect(page.locator(".natal-reading__chapter-body").first()).toBeVisible()

    const guideToggle = page.locator(".natal-chart-guide__toggle").first()
    await expectTouchTarget(guideToggle)
    await guideToggle.click()
    await expect(guideToggle).toHaveAttribute("aria-expanded", "true")
    await expect(page.locator(".natal-chart-guide__content").first()).toBeVisible()
    await guideToggle.click()
    await expect(guideToggle).toHaveAttribute("aria-expanded", "false")
    await expect(page.locator(".natal-chart-guide__content").first()).not.toBeVisible()

    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight))
    await expectNoHorizontalOverflow(page)
    const bottomGap = await page.evaluate(() => {
      const guide = document.querySelector(".natal-chart-guide")
      const nav = document.querySelector(".bottom-nav")
      const guideBox = guide?.getBoundingClientRect()
      const navBox = nav?.getBoundingClientRect()
      if (!guideBox || !navBox) return 0
      return navBox.top - guideBox.bottom
    })
    expect(bottomGap).toBeGreaterThanOrEqual(8)

    await page.screenshot({
      path: resolve(EVIDENCE_DIR, `natal-mobile-${viewport.width}.png`),
      fullPage: true,
    })
  }
})
