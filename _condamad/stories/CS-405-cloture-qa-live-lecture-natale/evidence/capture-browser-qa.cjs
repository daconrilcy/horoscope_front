// Script de preuve QA navigateur pour capturer /natal avec la session locale authentifiee.
const fs = require("node:fs/promises");
const path = require("node:path");
const { chromium } = require("../../../../frontend/node_modules/playwright");

const repoRoot = path.resolve(__dirname, "../../../..");
const evidenceDir = __dirname;
const outputDir = path.join(repoRoot, "output", "playwright");
const frontUrl = "http://127.0.0.1:5173";

async function readToken() {
  const loginPath = path.join(evidenceDir, "auth-login-response.json");
  const login = JSON.parse(await fs.readFile(loginPath, "utf8"));
  return login.data.tokens.access_token;
}

async function captureProfile(browser, token, profile, viewport) {
  const context = await browser.newContext({
    viewport: { width: viewport.width, height: viewport.height },
  });
  const page = await context.newPage();
  await page.goto(`${frontUrl}/login`, { waitUntil: "domcontentloaded" });
  await page.evaluate(
    ({ accessToken }) => {
      localStorage.setItem("access_token", accessToken);
      localStorage.setItem("lang", "fr");
    },
    { accessToken: token },
  );
  await page.goto(`${frontUrl}/natal`, { waitUntil: "networkidle", timeout: 30000 });
  await page.waitForTimeout(2500);

  const screenshot = path.join(outputDir, `cs-400-${profile}-${viewport.name}.png`);
  await page.screenshot({ path: screenshot, fullPage: true });
  const bodyText = await page.locator("body").innerText({ timeout: 10000 });
  const accordionCount = await page.locator(".natal-narrative-reading__toggle").count();
  const forbiddenPattern =
    /chart_json|natal_data|evidence_refs|audit_input|interpretive_signal_ids|technical_scores|condition_axis|projection_version/i;

  await context.close();
  return {
    profile,
    viewport: viewport.name,
    screenshot: path.relative(repoRoot, screenshot).replaceAll("\\", "/"),
    accordionCount,
    forbiddenPublicMarkerFound: forbiddenPattern.test(bodyText),
    bodyExcerpt: bodyText.slice(0, 1800),
  };
}

async function main() {
  await fs.mkdir(outputDir, { recursive: true });
  const token = await readToken();
  const browser = await chromium.launch({ headless: true });
  const viewports = [
    { name: "desktop", width: 1440, height: 1100 },
    { name: "mobile", width: 390, height: 844 },
  ];
  const results = [];
  for (const viewport of viewports) {
    results.push(await captureProfile(browser, token, "basic", viewport));
  }
  await browser.close();
  await fs.writeFile(
    path.join(evidenceDir, "browser-qa-basic.json"),
    `${JSON.stringify(results, null, 2)}\n`,
  );
  console.log(JSON.stringify(results, null, 2));
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
