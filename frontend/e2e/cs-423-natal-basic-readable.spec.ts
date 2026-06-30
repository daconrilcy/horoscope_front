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
  "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJkYWNvbnJpbGN5QGhvdG1haWwuY29tIiwicm9sZSI6InVzZXIiLCJleHAiOjQxMDI0NDQ4MDB9."
const ASTRAL_RUN_ID = "run-cs-423-readable-basic"

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
            "Votre manière d'avancer cherche des équilibres clairs et une expression personnelle apaisée. Cette nuance reste volontairement sobre pour vérifier le corps de texte mobile.",
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
      core_identity: {
        sun: {
          placement: {
            object: "Sun",
            sign: "Libra",
            house: { number: 7, theme: "Relations" },
            longitude_deg: 202.2,
          },
        },
        moon: {
          placement: {
            object: "Moon",
            sign: "Taurus",
            house: { number: 2, theme: "Ressources" },
            longitude_deg: 44.8,
          },
        },
      },
      angles: {
        ascendant: { sign: "Cancer", house: 1 },
      },
      planet_positions: [
        { planet: "Soleil", planet_code: "sun", sign: "Balance", sign_code: "libra" },
        { planet: "Lune", planet_code: "moon", sign: "Taureau", sign_code: "taurus" },
      ],
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
          result: {
            metadata: {
              product_code: "natal_full_basic",
              tier: "basic",
              variant: "full",
            },
            quality: {
              reading_completeness: "completed",
            },
            calculation: LATEST_CHART.data.result,
            ...BASIC_PAYLOAD,
          },
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

test("capture les preuves desktop et mobile d'une lecture Basic V2 lisible", async ({ page }) => {
  mkdirSync(EVIDENCE_DIR, { recursive: true })
  await setupBasicNatalFixture(page)

  await page.setViewportSize({ width: 1440, height: 1200 })
  await page.goto(`/natal?runId=${ASTRAL_RUN_ID}`)
  await expect(page.getByRole("heading", { name: "Thème natal", exact: true })).toBeVisible()
  await expect(page.getByText("Essentielle").first()).toBeVisible()
  await expect(page.getByText(/Introduction lisible/i).first()).toBeVisible()
  await expect(page.getByText(/Conclusion:/i).first()).toBeVisible()
  const firstChapterToggle = page.locator(".natal-reading__chapter-toggle").first()
  const firstChapterBody = page.locator(".natal-reading__chapter-body").first()
  await expect(firstChapterBody).toBeVisible()
  await firstChapterToggle.click()
  await expect(firstChapterToggle).toHaveAttribute("aria-expanded", "false")
  await expect(firstChapterToggle).toHaveText("Lire la suite")
  await expect(firstChapterBody).not.toBeVisible()
  await firstChapterToggle.click()
  await expect(firstChapterToggle).toHaveAttribute("aria-expanded", "true")
  await expect(firstChapterToggle).toHaveText("Réduire")
  await expect(firstChapterBody).toBeVisible()

  const desktopTypography = await page
    .locator(".natal-reading__chapter-body p")
    .first()
    .evaluate((bodyText) => {
      const chapter = bodyText.closest(".natal-reading__chapter")
      const excerptText = chapter?.querySelector(".natal-reading__chapter-excerpt-text")
      if (!excerptText || !bodyText) {
        throw new Error("Lecture natale incomplete pour la comparaison typographique")
      }
      const excerptStyles = window.getComputedStyle(excerptText)
      const bodyStyles = window.getComputedStyle(bodyText)
      return {
        bodyFontFamily: bodyStyles.fontFamily,
        bodyFontSize: bodyStyles.fontSize,
        bodyFontWeight: bodyStyles.fontWeight,
        bodyLineHeight: Number.parseFloat(bodyStyles.lineHeight),
        excerptFontFamily: excerptStyles.fontFamily,
        excerptFontSize: excerptStyles.fontSize,
        excerptFontWeight: excerptStyles.fontWeight,
        excerptLineHeight: Number.parseFloat(excerptStyles.lineHeight),
      }
    })
  expect(desktopTypography.excerptFontFamily).toBe(desktopTypography.bodyFontFamily)
  expect(desktopTypography.excerptFontSize).toBe(desktopTypography.bodyFontSize)
  expect(desktopTypography.excerptFontWeight).toBe(desktopTypography.bodyFontWeight)
  expect(desktopTypography.excerptLineHeight).toBe(desktopTypography.bodyLineHeight)

  const desktopSurfaceWidths = await page.evaluate(() => {
    const metrics = document.querySelector(".natal-reading-metrics")
    const chapter = document.querySelector(".natal-reading__chapter")
    const contentCard = document.querySelector(".natal-card")
    const guide = document.querySelector(".natal-chart-guide")
    if (!metrics || !chapter || !contentCard || !guide) {
      throw new Error("Cadres natals introuvables pour la comparaison de largeur")
    }
    return {
      chapterWidth: chapter.getBoundingClientRect().width,
      cardWidth: contentCard.getBoundingClientRect().width,
      guideWidth: guide.getBoundingClientRect().width,
      metricsWidth: metrics.getBoundingClientRect().width,
    }
  })
  expect(Math.abs(desktopSurfaceWidths.metricsWidth - desktopSurfaceWidths.chapterWidth)).toBeLessThanOrEqual(1)
  expect(Math.abs(desktopSurfaceWidths.guideWidth - desktopSurfaceWidths.chapterWidth)).toBeLessThanOrEqual(1)
  expect(desktopSurfaceWidths.cardWidth).toBeGreaterThanOrEqual(desktopSurfaceWidths.metricsWidth)

  const summaryPosition = await page
    .locator(".natal-reading-summary")
    .first()
    .evaluate((element) => window.getComputedStyle(element).position)
  expect(summaryPosition).toBe("sticky")
  const progressBar = page.locator(".natal-reading-summary__bar").first()
  expect(await progressBar.evaluate((element) => (element as HTMLProgressElement).value)).toBe(0)
  await page.locator(".natal-reading-summary__button").nth(2).click()
  await expect
    .poll(() => progressBar.evaluate((element) => (element as HTMLProgressElement).value))
    .toBeGreaterThan(0)
  await page.locator(".natal-reading-summary__button").last().click()
  await expect
    .poll(() => progressBar.evaluate((element) => (element as HTMLProgressElement).value))
    .toBe(100)

  const guideToggle = page.locator(".natal-chart-guide__toggle").first()
  await expect(guideToggle).toHaveAttribute("aria-expanded", "false")
  await expect(guideToggle).toHaveText("Lire le guide")
  await guideToggle.click()
  await expect(guideToggle).toHaveAttribute("aria-expanded", "true")
  await expect(guideToggle).toHaveText("Réduire le guide")
  await expect(page.getByText(/Ton thème natal est une représentation géométrique/i)).toBeVisible()
  await guideToggle.click()
  await expect(guideToggle).toHaveAttribute("aria-expanded", "false")
  await expect(guideToggle).toHaveText("Lire le guide")
  await expect(page.getByText(/Ton thème natal est une représentation géométrique/i)).not.toBeVisible()

  const publicBody = (await page.locator(".natal-reading").innerText()).trim()
  expect(publicBody).not.toMatch(
    /cette lecture s'appuie uniquement|Ce repere retient|avec une confiance editoriale controlee|Luminaire: moon|Position planetaire:|north node|south node|visibility_expression|audit_input|condition_axis:|interpretive_signal_ids/i,
  )
  expect(publicBody).not.toMatch(/\b(moon|sun|saturn|north node|south node|Synthese|theme|themes|repere|planetaire|a integrer)\b/i)
  expect(page.getByText(/Lecture complète à régénérer/i)).toHaveCount(0)

  writeFileSync(resolve(EVIDENCE_DIR, "basic-readable-api-after.json"), JSON.stringify(BASIC_PAYLOAD, null, 2), "utf8")
  writeFileSync(resolve(EVIDENCE_DIR, "basic-readable-dom-text-after.txt"), `${publicBody}\n`, "utf8")
  await page.screenshot({ path: resolve(EVIDENCE_DIR, "basic-readable-desktop-after.png"), fullPage: true })

  await page.setViewportSize({ width: 390, height: 844 })
  const mobileMetaToggle = page.locator(".natal-reading__meta-toggle").first()
  await expect(mobileMetaToggle).toHaveAttribute("aria-expanded", "false")
  await mobileMetaToggle.click()
  await expect(mobileMetaToggle).toHaveAttribute("aria-expanded", "true")
  await expect(mobileMetaToggle).toHaveText("Masquer les repères")
  const mobileChapterText = page.locator(".natal-reading__chapter-body p").first()
  const mobileChapterTitle = page.locator(".natal-reading__chapter-head h3").first()
  const mobileChapterExcerpt = page.locator(".natal-reading__chapter-excerpt").first()
  const mobileChapterMeta = page.locator(".natal-reading__chapter-meta").first()
  const mobileBasisList = page.locator(".natal-reading__basis ul").first()
  const mobileBasisChip = page.locator(".natal-badge--basis").first()
  const mobileMetrics = page.locator(".natal-reading-metrics").first()
  const mobileMetricCards = page.locator(".natal-reading-metrics__item")
  const mobilePageMain = page.locator(".page-layout.natal-page-container .page-layout__main").first()
  const mobileGuideToggle = page.locator(".natal-chart-guide__toggle").first()
  const mobileStyles = await mobileChapterText.evaluate((element) => {
    const styles = window.getComputedStyle(element)
    return {
      fontSize: Number.parseFloat(styles.fontSize),
      lineHeight: Number.parseFloat(styles.lineHeight),
    }
  })
  const excerptStyles = await mobileChapterExcerpt.evaluate((element) => {
    const styles = window.getComputedStyle(element)
    return {
      fontSize: Number.parseFloat(styles.fontSize),
      fontWeight: Number.parseFloat(styles.fontWeight),
      lineHeight: Number.parseFloat(styles.lineHeight),
    }
  })
  const titleStyles = await mobileChapterTitle.evaluate((element) => {
    const styles = window.getComputedStyle(element)
    return {
      fontSize: Number.parseFloat(styles.fontSize),
    }
  })
  const basisChipStyles = await mobileBasisChip.evaluate((element) => {
    const styles = window.getComputedStyle(element)
    return {
      fontSize: Number.parseFloat(styles.fontSize),
      height: Number.parseFloat(styles.height),
      paddingLeft: Number.parseFloat(styles.paddingLeft),
      textOverflow: styles.textOverflow,
      whiteSpace: styles.whiteSpace,
    }
  })
  const basisListStyles = await mobileBasisList.evaluate((element) => {
    const styles = window.getComputedStyle(element)
    return {
      flexWrap: styles.flexWrap,
      overflowX: styles.overflowX,
    }
  })
  const guideToggleHeight = await mobileGuideToggle.evaluate((element) => element.getBoundingClientRect().height)
  const metaDisplay = await mobileChapterMeta.evaluate((element) => window.getComputedStyle(element).display)
  const metricsColumns = await mobileMetrics.evaluate((element) => window.getComputedStyle(element).gridTemplateColumns)
  const bottomPadding = await mobilePageMain.evaluate((element) =>
    Number.parseFloat(window.getComputedStyle(element).paddingBottom),
  )

  expect(mobileStyles.fontSize).toBeGreaterThanOrEqual(12)
  expect(mobileStyles.lineHeight).toBeGreaterThanOrEqual(18)
  expect(excerptStyles.fontSize).toBeLessThan(titleStyles.fontSize)
  expect(excerptStyles.fontWeight).toBeLessThanOrEqual(500)
  expect(excerptStyles.lineHeight).toBeGreaterThanOrEqual(18)
  expect(metaDisplay).toBe("grid")
  expect(basisChipStyles.fontSize).toBeGreaterThanOrEqual(10)
  expect(basisChipStyles.height).toBeGreaterThanOrEqual(24)
  expect(basisChipStyles.paddingLeft).toBeGreaterThanOrEqual(6)
  expect(basisChipStyles.textOverflow).toBe("clip")
  expect(basisChipStyles.whiteSpace).toBe("normal")
  expect(basisListStyles.flexWrap).toBe("wrap")
  expect(basisListStyles.overflowX).toBe("visible")
  await expect(mobileMetricCards).toHaveCount(4)
  expect(metricsColumns.trim().split(/\s+/)).toHaveLength(1)
  expect(guideToggleHeight).toBeGreaterThanOrEqual(44)
  expect(bottomPadding).toBeGreaterThanOrEqual(140)
  await page.screenshot({ path: resolve(EVIDENCE_DIR, "basic-readable-mobile-after.png"), fullPage: true })
})
