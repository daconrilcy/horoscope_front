// Configure les tests navigateur et centralise leurs artefacts dans le dossier autorise.
import { defineConfig } from "@playwright/test"
import { resolve } from "node:path"
import { fileURLToPath } from "node:url"

const playwrightPort = process.env.PLAYWRIGHT_PORT ?? "4173"
const playwrightBaseUrl = `http://127.0.0.1:${playwrightPort}`
const skipWebServer = process.env.PLAYWRIGHT_SKIP_WEBSERVER === "1"
const repositoryRoot = fileURLToPath(new URL("../", import.meta.url))

export default defineConfig({
  testDir: "./e2e",
  outputDir: resolve(repositoryRoot, "output", "playwright", "test-results"),
  fullyParallel: false,
  retries: 0,
  use: {
    baseURL: playwrightBaseUrl,
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },
  webServer: skipWebServer
    ? undefined
    : {
        command:
          `node ./scripts/run-vite-logged.mjs vite vite-dev dev ` +
          `--host 127.0.0.1 --port ${playwrightPort} --strictPort`,
        url: playwrightBaseUrl,
        reuseExistingServer: false,
        timeout: 120_000,
      },
  projects: [
    {
      name: "chromium-mobile",
      use: {
        browserName: "chromium",
        viewport: { width: 390, height: 844 },
      },
    },
  ],
})
