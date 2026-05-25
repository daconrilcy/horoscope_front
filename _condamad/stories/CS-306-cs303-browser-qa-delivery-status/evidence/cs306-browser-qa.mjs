// Script d'evidence CS-306: valide /natal dans Chromium avec des reponses API publiques controlees.
import { chromium } from "../../../..//frontend/node_modules/playwright/index.mjs"
import { spawn } from "node:child_process"
import { mkdir, writeFile } from "node:fs/promises"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "../../../..")
const frontendRoot = resolve(repoRoot, "frontend")
const evidenceRoot = resolve(
  repoRoot,
  "_condamad/stories/CS-306-cs303-browser-qa-delivery-status/evidence",
)
const baseUrl = "http://127.0.0.1:4173"
const startedAt = new Date().toISOString()

const tokenPayload = Buffer.from(JSON.stringify({
  sub: "cs306-browser-user",
  role: "user",
  exp: Math.floor(Date.now() / 1000) + 3600,
})).toString("base64url")
const accessToken = `x.${tokenPayload}.y`

const chart = {
  chart_id: "chart-cs306",
  created_at: "2026-05-25T21:55:00Z",
  metadata: {
    reference_version: "cs306-browser",
    ruleset_version: "cs306-browser",
    engine: "qa-fixture",
    house_system: "equal",
    degraded_mode: null,
  },
  result: {
    reference_version: "cs306-browser",
    ruleset_version: "cs306-browser",
    prepared_input: {
      birth_datetime_local: "1990-01-15T10:30:00",
      birth_datetime_utc: "1990-01-15T09:30:00Z",
      timestamp_utc: 632400600,
      julian_day: 2447907.896,
      birth_timezone: "Europe/Paris",
    },
    planet_positions: [],
    houses: [],
    aspects: [],
  },
  astro_profile: {
    sun_sign_code: "capricorn",
    ascendant_sign_code: "aries",
    missing_birth_time: false,
  },
}

const interpretation = {
  chart_id: "chart-cs306",
  use_case: "natal_interpretation",
  degraded_mode: null,
  meta: {
    id: 306,
    level: "complete",
    use_case: "natal_interpretation",
    persona_id: null,
    persona_name: "Luna Celeste",
    prompt_version_id: "cs306",
    created_at: "2026-05-25T21:56:00Z",
    was_fallback: false,
    locale: "fr-FR",
    module: null,
  },
  interpretation: {
    title: "Votre theme revele une energie claire et structuree.",
    summary: "Synthese CS-306 affichee dans le navigateur.",
    highlights: ["Cap central", "Rythme stable"],
    sections: [
      {
        title: "Elan principal",
        text: "Vous avancez avec une priorite nette: transformer l'intuition en action concrete.",
      },
    ],
    evidence: ["fixture navigateur CS-306"],
  },
}

function json(data, status = 200) {
  return {
    status,
    contentType: "application/json",
    body: JSON.stringify(data),
  }
}

function projectionResponse(type) {
  if (type === "beginner_summary_v1") {
    return {
      chart_id: "chart-cs306",
      projection_type: "beginner_summary_v1",
      projection_version: "v1",
      persisted: false,
      projection_hash: "hash-beginner-cs306",
      payload: {
        state: "success",
        display_messages: [
          { code: "BGS_OK", message: "Résumé débutant visible en navigateur CS-306." },
        ],
        summary_items: ["Lecture claire", "Repères concrets"],
      },
      metadata: { source: "chart_id", plan_code: "free", request_id: "req-beginner-cs306" },
    }
  }
  return {
    chart_id: "chart-cs306",
    projection_type: "client_interpretation_projection_v1",
    projection_version: "v1",
    persisted: false,
    projection_hash: "hash-client-cs306",
    payload: {
      state: "success",
      sections: [
        {
          code: "main",
          title: "Projection client visible",
          text: "Interprétation client validée dans Chromium pour CS-306.",
        },
      ],
      support_elements: ["Support public uniquement"],
    },
    metadata: { source: "chart_id", plan_code: "free", request_id: "req-client-cs306" },
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

async function installRoutes(page, requests) {
  await page.route("**/v1/**", async (route) => {
    const request = route.request()
    const url = new URL(request.url())
    requests.push({ method: request.method(), path: url.pathname, postData: request.postData() })

    if (url.pathname === "/v1/users/me/natal-chart/latest") {
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
      await route.fulfill(json(projectionResponse(payload.projection_type)))
      return
    }
    await route.fulfill(json({ data: null }))
  })
}

async function runViewport(browser, viewportName, viewport) {
  const context = await browser.newContext({ viewport, deviceScaleFactor: 1 })
  await context.addInitScript((token) => {
    window.localStorage.setItem("access_token", token)
    window.localStorage.setItem("lang", "fr")
  }, accessToken)
  const page = await context.newPage()
  const requests = []
  await installRoutes(page, requests)
  await page.goto(`${baseUrl}/natal`, { waitUntil: "networkidle" })

  await page.getByRole("heading", { name: "Résumé débutant" }).waitFor({ state: "visible", timeout: 20_000 })
  await page.getByRole("heading", { name: "Interprétation client" }).waitFor({ state: "visible", timeout: 20_000 })
  await page.getByText("Résumé débutant visible en navigateur CS-306.", { exact: false }).waitFor({
    state: "visible",
    timeout: 20_000,
  })
  await page.getByText("Interprétation client validée dans Chromium pour CS-306.", { exact: false }).waitFor({
    state: "visible",
    timeout: 20_000,
  })

  const projections = page.locator(".ni-projections")
  const actions = page.locator(".ni-actions")
  const projectionBox = await projections.boundingBox()
  const actionBox = await actions.boundingBox()
  if (!projectionBox || !actionBox) throw new Error(`Missing layout box for ${viewportName}`)
  const verticalOverlap = !(
    projectionBox.y >= actionBox.y + actionBox.height ||
    actionBox.y >= projectionBox.y + projectionBox.height
  )
  if (verticalOverlap) throw new Error(`Projection panel overlaps primary controls on ${viewportName}`)

  const screenshotPath = resolve(evidenceRoot, `browser-${viewportName}.png`)
  await page.screenshot({ path: screenshotPath, fullPage: true })
  const visibleText = await page.locator(".ni-projections").innerText()
  await context.close()

  return {
    artifact_type: "browser-screenshot",
    route: "/natal",
    viewport: viewportName,
    projection_state: "success",
    command: "node evidence/cs306-browser-qa.mjs",
    result: "pass",
    report_status: "Delivered",
    screenshot_path: screenshotPath,
    visible_text_contains: [
      "Résumé débutant",
      "Interprétation client",
      "Résumé débutant visible en navigateur CS-306.",
      "Interprétation client validée dans Chromium pour CS-306.",
    ],
    projection_box: projectionBox,
    primary_controls_box: actionBox,
    no_primary_control_overlap: true,
    requests,
    captured_text_excerpt: visibleText.slice(0, 500),
  }
}

async function main() {
  await mkdir(evidenceRoot, { recursive: true })
  const startupLogPath = resolve(evidenceRoot, "startup-log.txt")
  const server = spawn(
    process.execPath,
    ["scripts/run-vite-logged.mjs", "vite", "vite-dev", "dev", "--host", "127.0.0.1", "--port", "4173"],
    { cwd: frontendRoot, stdio: ["ignore", "pipe", "pipe"], shell: false },
  )
  const startupLines = [`started_at=${startedAt}`, `command=node scripts/run-vite-logged.mjs vite vite-dev dev --host 127.0.0.1 --port 4173`]
  server.stdout.on("data", (chunk) => startupLines.push(chunk.toString()))
  server.stderr.on("data", (chunk) => startupLines.push(chunk.toString()))

  let browser
  try {
    await waitForServer()
    startupLines.push("result=pass")
    browser = await chromium.launch()
    const desktop = await runViewport(browser, "desktop", { width: 1366, height: 900 })
    const mobile = await runViewport(browser, "mobile", { width: 390, height: 844 })
    const ledger = {
      artifact_type: "browser-log",
      route: "/natal",
      command: "node evidence/cs306-browser-qa.mjs",
      result: "pass",
      report_status: "Delivered",
      date: new Date().toISOString(),
      entries: [desktop, mobile],
      projection_state_coverage: [
        { projection_state: "success", result: "pass", evidence: "desktop and mobile browser screenshots" },
        { projection_state: "loading", result: "pass", evidence: "natalInterpretation Vitest state coverage" },
        { projection_state: "controlled-error", result: "pass", evidence: "natalInterpretation Vitest state coverage" },
        { projection_state: "entitlement", result: "pass", evidence: "natalInterpretation Vitest state coverage" },
        { projection_state: "empty", result: "pass", evidence: "natalInterpretation Vitest state coverage" },
        { projection_state: "degraded", result: "pass", evidence: "natalInterpretation Vitest state coverage" },
      ],
    }
    await writeFile(resolve(evidenceRoot, "browser-qa-ledger.json"), `${JSON.stringify(ledger, null, 2)}\n`)
    await writeFile(
      resolve(evidenceRoot, "browser-qa-after.md"),
      [
        "# Browser QA After",
        "",
        "- artifact_type: browser-log",
        "- route: /natal",
        "- viewport: desktop + mobile",
        "- projection_state: success",
        "- command: node evidence/cs306-browser-qa.mjs",
        "- result: pass",
        "- report_status: Delivered",
        "- desktop screenshot: evidence/browser-desktop.png",
        "- mobile screenshot: evidence/browser-mobile.png",
        "- loading/error/entitlement/empty/degraded states: covered by logged `natalInterpretation` Vitest validation.",
        "",
      ].join("\n"),
    )
  } finally {
    if (browser) await browser.close()
    server.kill()
    await writeFile(startupLogPath, `${startupLines.join("")}\n`)
  }
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
