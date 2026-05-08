// Gardes statiques de frontiere pour frontend/src/components.
import { describe, expect, it } from "vitest"

import { listFiles, readFrontendFile } from "./design-system-policy"
import {
  COMPONENT_API_IMPORT_EXCEPTIONS,
  COMPONENT_TS_NOCHECK_EXCEPTIONS,
  type ComponentArchitectureException,
} from "./component-architecture-allowlist"

function exactFiles(entries: ComponentArchitectureException[]): Set<string> {
  for (const entry of entries) {
    expect(entry.file).not.toContain("*")
    expect(entry.owner.trim()).not.toBe("")
    expect(entry.reason.trim()).not.toBe("")
    expect(entry.exitCondition.trim()).not.toBe("")
  }
  return new Set(entries.map((entry) => entry.file))
}

function componentSourceFiles(): string[] {
  return [".ts", ".tsx"].flatMap((extension) => listFiles("components", extension))
}

function hasApiOrFeatureOwnership(source: string): boolean {
  return (
    /from\s+["'](?:@api(?:\/[^"']*)?|\.\.?\/.*api(?:\/[^"']*)?|\.\.?\/.*features(?:\/[^"']*)?)["']/.test(source) ||
    /\b(?:apiFetch|fetch)\s*\(|\baxios\./.test(source)
  )
}

describe("component-architecture guards", () => {
  it("bloque les imports API/feature et appels HTTP non classes dans components", () => {
    const allowed = exactFiles(COMPONENT_API_IMPORT_EXCEPTIONS)
    const violations = componentSourceFiles().filter(
      (file) => hasApiOrFeatureOwnership(readFrontendFile(file)) && !allowed.has(file),
    )
    const staleEntries = COMPONENT_API_IMPORT_EXCEPTIONS.filter(
      (entry) => !hasApiOrFeatureOwnership(readFrontendFile(entry.file)),
    )

    expect(violations).toEqual([])
    expect(staleEntries).toEqual([])
  })

  it("bloque les suppressions TypeScript non classees dans components", () => {
    const allowed = exactFiles(COMPONENT_TS_NOCHECK_EXCEPTIONS)
    const violations = componentSourceFiles().filter(
      (file) => readFrontendFile(file).includes("@ts-nocheck") && !allowed.has(file),
    )
    const staleEntries = COMPONENT_TS_NOCHECK_EXCEPTIONS.filter(
      (entry) => !readFrontendFile(entry.file).includes("@ts-nocheck"),
    )

    expect(violations).toEqual([])
    expect(staleEntries).toEqual([])
  })

  it("garde NatalInterpretation comme container et les enfants presentational sans API", () => {
    expect(readFrontendFile("components/NatalInterpretation.tsx")).toContain("useNatalInterpretation")

    const presentationalFiles = [
      "components/natal-interpretation/NatalInterpretationContent.tsx",
      "components/natal-interpretation/NatalInterpretationEvidence.tsx",
      "components/natal-interpretation/NatalInterpretationMenus.tsx",
    ]

    for (const file of presentationalFiles) {
      expect(hasApiOrFeatureOwnership(readFrontendFile(file))).toBe(false)
    }
  })
})
