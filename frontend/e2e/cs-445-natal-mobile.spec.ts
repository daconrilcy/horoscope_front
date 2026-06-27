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
          body:
            "Le deuxième chapitre reste ouvert pour donner immédiatement de la matière. Il doit se lire avec un interligne confortable et des boutons faciles à toucher.",
          confidence: "high",
          astro_basis: ["Mercure en Lion", "Maison VI - Routines / hygiène de vie"],
        },
        {
          code: "relationships",
          title: "Relations",
          body: "Ce chapitre secondaire reste replié jusqu'à l'action explicite de l'utilisateur.",
          confidence: "low",
          astro_basis: ["Vénus carré Saturne", "Maison VII - Relations et engagements durables"],
        },
      ],
      legal: {
        disclaimer: "Lecture symbolique et non médicale.",
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

test("garde /natal lisible et non masque a 360, 390 et 430 px", async ({ page }) => {
  mkdirSync(EVIDENCE_DIR, { recursive: true })
  await setupNatalFixture(page)

  await page.goto(`/natal?runId=${ASTRAL_RUN_ID}`)
  await expect(page.getByRole("heading", { name: "Lecture mobile Astral" })).toBeVisible()

  for (const viewport of MOBILE_VIEWPORTS) {
    await page.setViewportSize(viewport)
    await expectNoHorizontalOverflow(page)

    const progressList = page.locator(".natal-reading__progress ol").first()
    const progressStyles = await progressList.evaluate((element) => {
      const styles = window.getComputedStyle(element)
      return {
        display: styles.display,
        overflowX: styles.overflowX,
        scrollSnapType: styles.scrollSnapType,
      }
    })
    expect(progressStyles.display).toBe("flex")
    expect(progressStyles.overflowX).toBe("auto")
    expect(progressStyles.scrollSnapType).toContain("x")

    const progressLink = page.locator(".natal-reading__progress-link").first()
    await expectTouchTarget(progressLink)
    await expect(progressLink.locator(".natal-reading__progress-label--short")).toHaveText("Identité")
    await expect(page.locator(".natal-reading__progress-label--short").nth(1)).toHaveText("Émotions")
    await expect(page.locator(".natal-reading__progress-label--short").nth(2)).toHaveText("Relations")
    const progressLinkBox = await progressLink.boundingBox()
    expect(progressLinkBox?.width ?? 0).toBeLessThanOrEqual(190)

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
