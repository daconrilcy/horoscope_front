// Gardes statiques de frontiere pour frontend/src/api.
import { describe, expect, it } from "vitest"

import { listFiles, readFrontendFile } from "./design-system-policy"

function apiSourceFiles(): string[] {
  return [".ts", ".tsx"].flatMap((extension) => listFiles("api", extension))
}

describe("api-architecture", () => {
  it("garde les anciens modules racine adminPrompts et natalChart comme entrypoints publics uniquement", () => {
    const entrypoints = ["api/adminPrompts.ts", "api/natalChart.ts"]

    for (const entrypoint of entrypoints) {
      const executableLines = readFrontendFile(entrypoint)
        .split(/\r?\n/)
        .filter((line) => line.trim() && !line.trim().startsWith("//"))

      expect(executableLines).toEqual([expect.stringMatching(/^export \* from "\.\/.+"/)])
    }
  })

  it("interdit les imports du barrel public @api depuis le domaine API", () => {
    const offenders = apiSourceFiles().filter((file) =>
      /from\s+["']@api(?:\/[^"']*)?["']/.test(readFrontendFile(file)),
    )

    expect(offenders).toEqual([])
  })

  it("garde client.ts comme unique proprietaire du transport fetch sous api", () => {
    const offenders = apiSourceFiles().filter((file) => {
      if (file === "api/client.ts") {
        return false
      }
      return /\bfetch\s*\(/.test(readFrontendFile(file))
    })

    expect(offenders).toEqual([])
  })

  it("interdit a support.ts d'exposer ou importer la responsabilite ops persona", () => {
    const supportSource = readFrontendFile("api/support.ts")

    expect(supportSource).not.toContain("useOpsRollbackPersona")
    expect(supportSource).not.toContain("opsPersona")
  })

  it("garde les sous-domaines API migres sur le parser d'erreurs canonique", () => {
    const migratedOwners = [
      "api/admin-prompts/index.ts",
      "api/natal-chart/index.ts",
    ]
    const forbiddenLocalParserSymbols = [
      /\btype\s+ErrorEnvelope\b/,
      /\btype\s+ResponseEnvelope\b/,
      /\blet\s+payload\s*:/,
    ]

    const offenders = migratedOwners.flatMap((file) => {
      const source = readFrontendFile(file)
      return forbiddenLocalParserSymbols
        .filter((pattern) => pattern.test(source))
        .map((pattern) => `${file}:${pattern}`)
    })

    expect(offenders).toEqual([])
  })
})
