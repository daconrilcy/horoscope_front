// Configure Vite pour l'application React et son environnement de test.
import { defineConfig } from "vitest/config"
import react from "@vitejs/plugin-react"
import path from "node:path"

export default defineConfig({
  plugins: [react()],
  server: {
    host: "127.0.0.1",
    port: 5173,
    strictPort: true,
    allowedHosts: ["student-swapping-idealness.ngrok-free.dev"],
  },
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
    exclude: ["**/node_modules/**", "**/dist/**", "**/e2e/**"],
    reporters: ["default", "json"],
    outputFile: {
      json: "./logs/vite/vitest-report.json",
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (!id.includes("node_modules")) {
            return undefined
          }

          if (id.includes("@xyflow/react")) {
            return "vendor-flow"
          }

          if (id.includes("react-dom") || id.includes("react/")) {
            return "vendor-react"
          }

          if (id.includes("react-router-dom") || id.includes("@remix-run")) {
            return "vendor-router"
          }

          if (id.includes("@tanstack/react-query")) {
            return "vendor-query"
          }

          if (
            id.includes("react-hook-form") ||
            id.includes("@hookform/resolvers") ||
            id.includes("zod")
          ) {
            return "vendor-forms"
          }

          return undefined
        },
      },
    },
  },
})
