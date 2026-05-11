// Verifie en navigateur les invariants de conversion mobile de la landing CS-147.
import { expect, test, type Page } from "@playwright/test"

type RectMetrics = {
  y: number
  bottom: number
  height: number
}

type LandingMetrics = {
  cta: RectMetrics
  proof: RectMetrics
  device: RectMetrics
  socialProof: RectMetrics
  overflowX: number
}

async function collectLandingMetrics(page: Page): Promise<LandingMetrics> {
  return page.evaluate(() => {
    function measure(selector: string) {
      const element = document.querySelector(selector)

      if (!element) {
        throw new Error(`Missing landing selector: ${selector}`)
      }

      const rect = element.getBoundingClientRect()

      return {
        y: Math.round(rect.y),
        bottom: Math.round(rect.bottom),
        height: Math.round(rect.height),
      }
    }

    return {
      cta: measure(".hero-ctas"),
      proof: measure(".hero-proof-strip"),
      device: measure(".hero-device"),
      socialProof: measure("#social-proof"),
      overflowX: Math.max(0, document.documentElement.scrollWidth - window.innerWidth),
    }
  })
}

test.describe("CS-147 landing conversion", () => {
  test("affiche CTA, preuve compacte et debut du mock produit sur mobile", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 })

    await page.goto("/")
    await page.waitForLoadState("networkidle")

    await expect(page.locator(".hero-proof-strip")).toBeVisible()
    const metrics = await collectLandingMetrics(page)

    expect(metrics.cta.bottom).toBeLessThanOrEqual(844)
    expect(metrics.proof.bottom).toBeLessThanOrEqual(844)
    expect(metrics.device.y).toBeLessThan(844)
    expect(metrics.overflowX).toBe(0)
  })

  test("conserve un signal de section suivante au premier viewport desktop", async ({ page }) => {
    await page.setViewportSize({ width: 1440, height: 1000 })

    await page.goto("/")
    await page.waitForLoadState("networkidle")

    await expect(page.locator(".hero-proof-strip")).toBeHidden()
    const metrics = await collectLandingMetrics(page)

    expect(metrics.socialProof.y).toBeLessThan(1000)
    expect(metrics.overflowX).toBe(0)
  })
})
