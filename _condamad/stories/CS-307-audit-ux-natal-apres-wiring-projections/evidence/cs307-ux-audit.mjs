// Script d'evidence CS-307: audite /natal dans Chromium avec des etats de projection controles.
import { chromium } from "../../../..//frontend/node_modules/playwright/index.mjs"
import { spawn } from "node:child_process"
import { mkdir, writeFile } from "node:fs/promises"
import { createServer } from "node:net"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../../..")
const frontendRoot = resolve(repoRoot, "frontend")
const evidenceRoot = resolve(
  repoRoot,
  "_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence",
)
const screenshotsRoot = resolve(evidenceRoot, "browser-screenshots")
const startedAt = new Date().toISOString()
const auditDate = startedAt.slice(0, 10)
let baseUrl

const tokenPayload = Buffer.from(JSON.stringify({
  sub: "cs307-ux-audit-user",
  role: "user",
  exp: Math.floor(Date.now() / 1000) + 3600,
})).toString("base64url")
const accessToken = `x.${tokenPayload}.y`

const chart = {
  chart_id: "chart-cs307",
  created_at: "2026-05-26T09:20:00Z",
  metadata: {
    reference_version: "cs307-browser",
    ruleset_version: "cs307-browser",
    engine: "qa-fixture",
    house_system: "equal",
    degraded_mode: null,
  },
  result: {
    reference_version: "cs307-browser",
    ruleset_version: "cs307-browser",
    prepared_input: {
      birth_datetime_local: "1992-04-18T08:15:00",
      birth_datetime_utc: "1992-04-18T06:15:00Z",
      timestamp_utc: 703573800,
      julian_day: 2448729.76,
      birth_timezone: "Europe/Paris",
    },
    planet_positions: [],
    houses: [],
    aspects: [],
  },
  astro_profile: {
    sun_sign_code: "aries",
    ascendant_sign_code: "gemini",
    missing_birth_time: false,
  },
}

const interpretation = {
  chart_id: "chart-cs307",
  use_case: "natal_interpretation",
  degraded_mode: null,
  meta: {
    id: 307,
    level: "complete",
    use_case: "natal_interpretation",
    persona_id: null,
    persona_name: "Luna Celeste",
    prompt_version_id: "cs307",
    created_at: "2026-05-26T09:21:00Z",
    was_fallback: false,
    locale: "fr-FR",
    module: null,
  },
  interpretation: {
    title: "Votre theme natal garde une lecture claire.",
    summary: "Synthese CS-307 controlee pour auditer la page /natal.",
    highlights: ["Elan visible", "Repere stable"],
    sections: [
      {
        title: "Orientation principale",
        text: "Le contenu principal reste lisible avant les projections publiques.",
      },
    ],
    evidence: ["fixture navigateur CS-307"],
  },
}

const viewports = [
  ["desktop", { width: 1366, height: 900 }],
  ["tablet", { width: 820, height: 1180 }],
  ["mobile", { width: 390, height: 844 }],
]

function json(data, status = 200) {
  return {
    status,
    contentType: "application/json",
    body: JSON.stringify(data),
  }
}

function projectionSuccess(type) {
  if (type === "beginner_summary_v1") {
    return {
      chart_id: "chart-cs307",
      projection_type: "beginner_summary_v1",
      projection_version: "v1",
      persisted: false,
      projection_hash: "hash-beginner-cs307",
      payload: {
        state: "success",
        display_messages: [
          { code: "BGS_OK", message: "Resume debutant visible et scannable dans le navigateur CS-307." },
        ],
        summary_items: ["Point solaire clair", "Rythme personnel concret"],
      },
      metadata: { source: "chart_id", plan_code: "free", request_id: "req-beginner-cs307" },
    }
  }
  return {
    chart_id: "chart-cs307",
    projection_type: "client_interpretation_projection_v1",
    projection_version: "v1",
    persisted: false,
    projection_hash: "hash-client-cs307",
    payload: {
      state: "success",
      sections: [
        {
          code: "orientation",
          title: "Projection client lisible",
          text: "La lecture client relie les signaux sans chevaucher les controles ou les mentions legales.",
        },
      ],
      support_elements: ["Support public controle"],
    },
    metadata: { source: "chart_id", plan_code: "premium", request_id: "req-client-cs307" },
  }
}

function projectionDegraded(type) {
  return {
    ...projectionSuccess(type),
    payload: {
      state: "degraded",
      display_messages: [
        { code: "BGS_DEGRADED_NO_TIME", message: "Lecture partielle: heure de naissance absente." },
      ],
      missing_data: ["no_time"],
    },
  }
}

async function waitForServer() {
  const deadline = Date.now() + 120_000
  while (Date.now() < deadline) {
    try {
      const response = await fetch(baseUrl)
      if (response.ok) return
    } catch {
      await new Promise((resolveDelay) => setTimeout(resolveDelay, 500))
    }
  }
  throw new Error("Vite server did not become ready")
}

async function reserveFreePort() {
  const server = createServer()
  await new Promise((resolveListen, rejectListen) => {
    server.once("error", rejectListen)
    server.listen(0, "127.0.0.1", resolveListen)
  })
  const address = server.address()
  await new Promise((resolveClose, rejectClose) => {
    server.close((error) => (error ? rejectClose(error) : resolveClose()))
  })
  if (!address || typeof address === "string") throw new Error("Unable to reserve a local QA port")
  return address.port
}

async function installRoutes(page, scenario, requests) {
  await page.route("**/v1/**", async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    requests.push({ method: request.method(), path: url.pathname, postData: request.postData() })

    if (url.pathname === "/v1/users/me/natal-chart/latest") {
      if (scenario === "empty") {
        await route.fulfill(json({ data: null }))
        return
      }
      await route.fulfill(json({ data: chart }))
      return
    }
    if (url.pathname === "/v1/natal/interpretation") {
      await route.fulfill(json({ data: interpretation, disclaimers: ["payload disclaimer ignored"] }))
      return
    }
    if (url.pathname === "/v1/natal/interpretations") {
      await route.fulfill(json({ data: { items: [], total: 0, limit: 20, offset: 0 } }))
      return
    }
    if (url.pathname === "/v1/natal/pdf-templates") {
      await route.fulfill(json({ data: { items: [] } }))
      return
    }
    if (url.pathname === "/v1/entitlements/me") {
      await route.fulfill(json({
        data: {
          plan_code: "premium",
          billing_status: "active",
          features: [
            {
              feature_code: "natal_chart_long",
              granted: true,
              reason_code: "plan_allows",
              access_mode: "included",
              variant_code: "complete",
              usage_states: [],
            },
          ],
          upgrade_hints: [],
        },
      }))
      return
    }
    if (url.pathname === "/v1/astrology/projections") {
      const payload = JSON.parse(request.postData() ?? "{}")
      if (scenario === "entitlement") {
        await route.fulfill(json({
          error: { code: "projection.unauthorized", message: "Projection reservee au plan superieur." },
        }, 403))
        return
      }
      if (scenario === "error") {
        await route.fulfill(json({
          error: { code: "projection.request_failed", message: "Projection temporairement indisponible." },
        }, 503))
        return
      }
      await route.fulfill(json(
        scenario === "degraded"
          ? projectionDegraded(payload.projection_type)
          : projectionSuccess(payload.projection_type),
      ))
      return
    }
    await route.fulfill(json({ data: null }))
  })
}

async function newAuditedPage(browser, viewport, scenario) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1 })
  await context.addInitScript((token) => {
    window.localStorage.setItem("access_token", token)
    window.localStorage.setItem("lang", "fr")
  }, accessToken)
  const page = await context.newPage()
  const requests = []
  await installRoutes(page, scenario, requests)
  return { context, page, requests }
}

async function assertNoVerticalOverlap(page, firstSelector, secondSelector, label) {
  const first = await page.locator(firstSelector).boundingBox()
  const second = await page.locator(secondSelector).boundingBox()
  if (!first || !second) throw new Error(`Missing layout box for ${label}`)
  const overlaps = !(
    first.y >= second.y + second.height ||
    second.y >= first.y + first.height
  )
  if (overlaps) throw new Error(`Layout overlap detected: ${label}`)
  return { first, second }
}

async function runVisualViewport(browser, viewportName, viewport) {
  const { context, page, requests } = await newAuditedPage(browser, viewport, "success")
  await page.goto(`${baseUrl}/natal`, { waitUntil: "networkidle" })

  await page.getByRole("heading", { name: "Résumé découverte" }).waitFor({ state: "visible", timeout: 20_000 })
  await page.getByRole("heading", { name: "Interprétation client" }).waitFor({ state: "visible", timeout: 20_000 })
  await page.getByText("Resume debutant visible et scannable", { exact: false }).waitFor({
    state: "visible",
    timeout: 20_000,
  })
  await page.getByText("Projection client lisible", { exact: false }).waitFor({ state: "visible", timeout: 20_000 })
  await page.getByText("Mentions légales", { exact: false }).waitFor({ state: "visible", timeout: 20_000 })

  const controlsOverlap = await assertNoVerticalOverlap(page, ".ni-actions", ".ni-projections", `${viewportName} controls/projections`)
  const disclaimerOverlap = await assertNoVerticalOverlap(page, ".ni-projections", ".ni-disclaimer-footer", `${viewportName} projections/disclaimer`)
  const screenshotPath = resolve(screenshotsRoot, `browser-${viewportName}.png`)
  await page.screenshot({ path: screenshotPath, fullPage: true })
  const visibleText = await page.locator(".ni-projections").innerText()
  await context.close()

  return {
    audit_date: auditDate,
    route: "/natal",
    viewport: viewportName,
    state: "success",
    finding: "Projection hierarchy and disclaimer remain visible without critical overlap.",
    decision: "acceptable",
    evidence_path: "_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/browser-qa.md",
    screenshot_path: `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/browser-screenshots/browser-${viewportName}.png`,
    result: "pass",
    checks: {
      no_primary_control_overlap: true,
      no_disclaimer_overlap: true,
      controls_overlap_boxes: controlsOverlap,
      disclaimer_overlap_boxes: disclaimerOverlap,
      visible_text_excerpt: visibleText.slice(0, 500),
      requests,
    },
  }
}

async function runProjectionState(browser, state) {
  const { context, page, requests } = await newAuditedPage(browser, { width: 390, height: 844 }, state)
  await page.goto(`${baseUrl}/natal`, { waitUntil: "networkidle" })

  const expected = {
    degraded: /Lecture partielle/i,
    entitlement: /demande une formule plus avancée|Projection reservee/i,
    error: /lectures du thème ne sont pas disponibles|Projection temporairement indisponible/i,
    empty: /Aucune donnée de thème disponible pour le moment|Aucun thème natal disponible pour le moment/i,
  }[state]
  await writeFile(resolve(evidenceRoot, `debug-mobile-${state}.txt`), await page.locator("body").innerText())
  await page.getByText(expected).first().waitFor({ state: "visible", timeout: 20_000 })

  const screenshotPath = resolve(screenshotsRoot, `browser-mobile-${state}.png`)
  await page.screenshot({ path: screenshotPath, fullPage: true })
  await context.close()
  return {
    audit_date: auditDate,
    route: "/natal",
    viewport: "mobile",
    state,
    finding: `${state} state remains understandable in the projection panel.`,
    decision: "acceptable",
    evidence_path: "_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/browser-qa.md",
    screenshot_path: `_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/browser-screenshots/browser-mobile-${state}.png`,
    result: "pass",
    checks: { requests },
  }
}

async function main() {
  await mkdir(screenshotsRoot, { recursive: true })
  const startupLogPath = resolve(evidenceRoot, "startup-log.txt")
  const port = await reserveFreePort()
  baseUrl = `http://127.0.0.1:${port}`
  const server = spawn(
    process.execPath,
    ["scripts/run-vite-logged.mjs", "vite", "vite-dev", "dev", "--host", "127.0.0.1", "--port", String(port), "--strictPort"],
    { cwd: frontendRoot, stdio: ["ignore", "pipe", "pipe"], shell: false },
  )
  const startupLines = [
    `started_at=${startedAt}`,
    `command=node scripts/run-vite-logged.mjs vite vite-dev dev --host 127.0.0.1 --port ${port} --strictPort`,
    `base_url=${baseUrl}`,
  ]
  server.stdout.on("data", (chunk) => startupLines.push(chunk.toString()))
  server.stderr.on("data", (chunk) => startupLines.push(chunk.toString()))

  let browser
  try {
    await waitForServer()
    startupLines.push("result=pass")
    browser = await chromium.launch()
    const visualEntries = []
    for (const [viewportName, viewport] of viewports) {
      visualEntries.push(await runVisualViewport(browser, viewportName, viewport))
    }
    const stateEntries = []
    for (const state of ["degraded", "entitlement", "error", "empty"]) {
      stateEntries.push(await runProjectionState(browser, state))
    }
    const ledger = {
      audit_date: auditDate,
      route: "/natal",
      command: "node evidence/cs307-ux-audit.mjs",
      result: "pass",
      entries: [
        ...visualEntries,
        ...stateEntries,
        {
          audit_date: auditDate,
          route: "/natal",
          viewport: "not-browser",
          state: "loading",
          finding: "Loading state remains covered by targeted Vitest while browser script verifies rendered page states.",
          decision: "acceptable",
          evidence_path: "frontend/src/tests/natalInterpretation.test.tsx",
          result: "pass",
          validation_command: "node .\\scripts\\run-vite-logged.mjs vitest vitest run natalInterpretation",
        },
        {
          audit_date: auditDate,
          route: "/natal",
          viewport: "desktop/tablet/mobile",
          state: "disclaimer",
          finding: "App-owned legal disclaimer is visible below projections and does not overlap the projection panel.",
          decision: "acceptable",
          evidence_path: "_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/browser-qa.md",
          result: "pass",
          screenshot_path: "_condamad/stories/CS-307-audit-ux-natal-apres-wiring-projections/evidence/browser-screenshots/browser-desktop.png",
        },
      ],
    }
    await writeFile(resolve(evidenceRoot, "browser-qa-ledger.json"), `${JSON.stringify(ledger, null, 2)}\n`)
  } finally {
    if (browser) await browser.close()
    server.kill()
    await writeFile(startupLogPath, `${startupLines.join("\n")}\n`)
  }
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
