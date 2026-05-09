// Configure la suite Vitest B2B et centralise ses rapports dans les logs frontend.
import { defineConfig } from "vitest/config"
import react from "@vitejs/plugin-react"
import path from "node:path"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@ui": path.resolve(__dirname, "./src/components/ui"),
      "@components": path.resolve(__dirname, "./src/components"),
      "@api": path.resolve(__dirname, "./src/api"),
      "@hooks": path.resolve(__dirname, "./src/hooks"),
      "@i18n": path.resolve(__dirname, "./src/i18n"),
      "@styles": path.resolve(__dirname, "./src/styles"),
      "@state": path.resolve(__dirname, "./src/state"),
      "@pages": path.resolve(__dirname, "./src/pages"),
      "@layouts": path.resolve(__dirname, "./src/layouts"),
      "@utils": path.resolve(__dirname, "./src/utils"),
      "@app-types": path.resolve(__dirname, "./src/types"),
    },
  },
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
        "src/features/enterprise/EnterpriseCredentialsPanel.tsx",
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
