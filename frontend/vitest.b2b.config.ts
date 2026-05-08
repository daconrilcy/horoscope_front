// Configure la suite Vitest B2B et centralise ses rapports dans les logs frontend.
import { defineConfig } from "vitest/config"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  test: {
    environment: "jsdom",
    setupFiles: "./src/tests/setup.ts",
    include: [
      "src/tests/B2B*.test.tsx",
      "src/tests/b2b*Api.test.ts",
      "src/tests/EnterpriseCredentialsPanel.test.tsx",
      "src/tests/enterpriseCredentialsApi.test.ts",
    ],
    reporters: ["default", "json"],
    outputFile: {
      json: "./logs/vite/vitest-b2b-report.json",
    },
    coverage: {
      provider: "v8",
      reportsDirectory: "./logs/vite/coverage-b2b",
      reporter: ["text", "text-summary"],
      include: [
        "src/api/b2bAstrology.ts",
        "src/api/b2bUsage.ts",
        "src/api/b2bEditorial.ts",
        "src/api/b2bBilling.ts",
        "src/api/enterpriseCredentials.ts",
        "src/components/B2BAstrologyPanel.tsx",
        "src/components/B2BUsagePanel.tsx",
        "src/components/B2BEditorialPanel.tsx",
        "src/components/B2BBillingPanel.tsx",
        "src/components/EnterpriseCredentialsPanel.tsx",
      ],
      thresholds: {
        lines: 80,
        functions: 80,
        statements: 80,
        branches: 70,
      },
    },
  },
})
