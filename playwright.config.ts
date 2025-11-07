import { defineConfig, devices } from '@playwright/test';

/**
 * Configuration Playwright pour tests E2E locaux
 * Base URL: frontend Vite (http://localhost:5173)
 * Backend: http://localhost:8000 (doit être démarré séparément)
 */
export default defineConfig({
  testDir: './e2e',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'html',
  use: {
    baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:5173',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Lancer automatiquement un build + preview Vite pour les tests E2E
  // Utilise un serveur plus stable que le mode dev, et active le flag Terminal
  webServer: {
    command: 'npm run e2e:web',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 180000,
    env: {
      // Assure que le build inclut la page /dev/terminal même hors DEV
      VITE_DEV_TERMINAL: 'true',
    },
  },
});
