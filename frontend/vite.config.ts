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
    exclude: ["**/node_modules/**", "**/dist/**", "**/e2e/**"],
  },
})
