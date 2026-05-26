// Script d'audit UX read-only pour valider /natal avec des donnees API controlees.
import { chromium } from "../../../../frontend/node_modules/playwright/index.mjs"
import { spawn } from "node:child_process"
import { mkdir, writeFile } from "node:fs/promises"
import { createServer } from "node:net"
import { dirname, resolve } from "node:path"
import { fileURLToPath } from "node:url"

const auditRoot = dirname(fileURLToPath(import.meta.url))
const repoRoot = resolve(auditRoot, "../../../..")
const frontendRoot = resolve(repoRoot, "frontend")
const screenshotRoot = resolve(auditRoot, "screenshots")
const startedAt = new Date().toISOString()
let baseUrl

const tokenPayload = Buffer.from(JSON.stringify({
  sub: "cs307-audit-user",
  role: "user",
  exp: Math.floor(Date.now() / 1000) + 3600,
})).toString("base64url")
const accessToken = `x.${tokenPayload}.y`

const chart = {
  chart_id: "chart-cs307-audit",
  created_at: "2026-05-26T06:22:00Z",
  metadata: {
    reference_version: "cs307-audit",
    ruleset_version: "cs307-audit",
    engine: "audit-fixture",
    house_system: "equal",
    degraded_mode: null,
  },
  result: {
    reference_version: "cs307-audit",
    ruleset_version: "cs307-audit",
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
  chart_id: "chart-cs307-audit",
  use_case: "natal_interpretation",
  degraded_mode: null,
  meta: {
    id: 307,
    level: "complete",
    use_case: "natal_interpretation",
    persona_id: null,
    persona_name: "Luna Celeste",
    prompt_version_id: "cs307",
    persisted_at: "2026-05-26T06:22:00Z",
    validation_status: "valid",
    repair_attempted: false,
    fallback_triggered: false,
    was_fallback: false,
    latency_ms: 1200,
  },
  interpretation: {
    title: "Votre theme revele une energie claire et structuree.",
    summary: "Synthese CS-307 affichee dans le navigateur.",
    highlights: ["Cap central", "Rythme stable"],
    sections: [
      {
        key: "overall",
        heading: "Elan principal",
        content: "Vous avancez avec une priorite nette: transformer l'intuition en action concrete.",
      },
    ],
    advice: ["Conserver un rythme lisible."],
    evidence: ["fixture navigateur CS-307"],
  },
}

function json(data, status = 200) {
  return { status, contentType: "application/json", body: JSON.stringify(data) }
}

function projectionResponse(type) {
  if (type === "beginner_summary_v1") {
    return {
      chart_id: "chart-cs307-audit",
      projection_type: "beginner_summary_v1",
      projection_version: "v1",
      persisted: false,
      projection_hash: "hash-beginner-cs307",
      payload: {
        state: "success",
        display_messages: [
          { code: "BGS_OK", message: "Résumé débutant visible en audit CS-307." },
        ],
        summary_items: ["Lecture claire", "Repères concrets"],
      },
      metadata: { source: "chart_id", plan_code: "free", request_id: "req-beginner-cs307" },
    }
  }
  return {
    chart_id: "chart-cs307-audit",
    projection_type: "client_interpretation_projection_v1",
    projection_version: "v1",
    persisted: false,
    projection_hash: "hash-client-cs307",
    payload: {
      state: "success",
      sections: [
        {
          code: "main",
          title: "Projection client visible",
          text: "Interprétation client validée dans Chromium pour l'audit CS-307.",
        },
      ],
      support_elements: ["Support public uniquement"],
    },
    metadata: { source: "chart_id", plan_code: "free", request_id: "req-client-cs307" },
  }
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
  if (!address || typeof address === "string") throw new Error("Unable to reserve a local port")
  return address.port
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

    if (url.pathname === "/v1/users/me/natal-chart/latest") return route.fulfill(json({ data: chart }))
    if (url.pathname === "/v1/natal/interpretation") return route.fulfill(json({ data: interpretation }))
    if (url.pathname === "/v1/natal/interpretations") {
      return route.fulfill(json({ data: { items: [], total: 0, limit: 20, offset: 0 } }))
    }
    if (url.pathname === "/v1/natal/pdf-templates") return route.fulfill(json({ data: { items: [] } }))
    if (url.pathname === "/v1/entitlements/me") {
      return route.fulfill(json({
        data: {
          plan_code: "premium",
          billing_status: "active",
          features: [{
            feature_code: "natal_chart_long",
            granted: true,
            reason_code: "plan_allows",
            access_mode: "included",
            variant_code: "multi_astrologer",
            usage_states: [],
          }],
          upgrade_hints: [],
        },
      }))
    }
    if (url.pathname === "/v1/astrology/projections") {
      const payload = JSON.parse(request.postData() ?? "{}")
      return route.fulfill(json(projectionResponse(payload.projection_type)))
    }
    return route.fulfill(json({ data: null }))
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
  await page.getByText("Résumé débutant visible en audit CS-307.", { exact: false }).waitFor({ state: "visible" })
  await page.getByText("Interprétation client validée dans Chromium pour l'audit CS-307.", { exact: false }).waitFor({
    state: "visible",
  })
  await page.getByText("Mentions légales", { exact: false }).waitFor({ state: "visible" })

  const projections = page.locator(".ni-projections")
  const actions = page.locator(".ni-actions")
  const disclaimer = page.locator(".ni-disclaimer-footer")
  const projectionBox = await projections.boundingBox()
  const actionBox = await actions.boundingBox()
  const disclaimerBox = await disclaimer.boundingBox()
  if (!projectionBox || !actionBox || !disclaimerBox) throw new Error(`Missing layout box for ${viewportName}`)
  const overlapsControls = !(
    projectionBox.y >= actionBox.y + actionBox.height ||
    actionBox.y >= projectionBox.y + projectionBox.height
  )
  const overlapsDisclaimer = !(
    disclaimerBox.y >= projectionBox.y + projectionBox.height ||
    projectionBox.y >= disclaimerBox.y + disclaimerBox.height
  )
  if (overlapsControls) throw new Error(`Projection panel overlaps primary controls on ${viewportName}`)
  if (overlapsDisclaimer) throw new Error(`Projection panel overlaps disclaimer on ${viewportName}`)

  const screenshotPath = resolve(screenshotRoot, `${viewportName}.png`)
  await page.screenshot({ path: screenshotPath, fullPage: true })
  const projectionText = await projections.innerText()
  await context.close()
  return {
    route: "/natal",
    viewport: viewportName,
    state: "success",
    result: "pass",
    screenshot_path: screenshotPath,
    visible_text_contains: [
      "Résumé débutant",
      "Interprétation client",
      "Résumé débutant visible en audit CS-307.",
      "Interprétation client validée dans Chromium pour l'audit CS-307.",
      "Mentions légales",
    ],
    projection_box: projectionBox,
    primary_controls_box: actionBox,
    disclaimer_box: disclaimerBox,
    no_primary_control_overlap: true,
    no_disclaimer_overlap: true,
    requests,
    captured_text_excerpt: projectionText.slice(0, 500),
  }
}

async function main() {
  await mkdir(screenshotRoot, { recursive: true })
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
    const entries = [
      await runViewport(browser, "desktop-1366x900", { width: 1366, height: 900 }),
      await runViewport(browser, "tablet-768x1024", { width: 768, height: 1024 }),
      await runViewport(browser, "mobile-390x844", { width: 390, height: 844 }),
    ]
    await writeFile(resolve(auditRoot, "browser-qa-ledger.json"), `${JSON.stringify({
      audit_date: new Date().toISOString(),
      route: "/natal",
      command: "node _condamad/audits/frontend-ux-natal-projections/2026-05-26-0622/browser-qa.mjs",
      result: "pass",
      entries,
    }, null, 2)}\n`)
  } finally {
    if (browser) await browser.close()
    server.kill()
    await writeFile(resolve(auditRoot, "startup-log.txt"), `${startupLines.join("\n")}\n`)
  }
}

main().catch((error) => {
  console.error(error)
  process.exit(1)
})
