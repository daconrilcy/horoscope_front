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

function frontendSourceFiles(): string[] {
  return [".ts", ".tsx"].flatMap((extension) => listFiles("", extension))
}

function pathPrefix(parts: string[]): string {
  return parts.join("/")
}

function isActiveModuleUnderPrefix(file: string, prefixParts: string[]): boolean {
  const prefix = pathPrefix(prefixParts)
  return file === `${prefix}.ts` || file === `${prefix}.tsx` || file.startsWith(`${prefix}/`)
}

function extractModuleSpecifiers(source: string): string[] {
  return [
    ...source.matchAll(/\b(?:import|export)\s+(?:type\s+)?(?:[^"']*?\s+from\s+)?["']([^"']+)["']/g),
    ...source.matchAll(/\bimport\(\s*["']([^"']+)["']\s*\)/g),
  ].map((match) => match[1].replace(/\\/g, "/"))
}

function modulePathVariants(parts: string[]): Set<string> {
  const legacyPath = pathPrefix(parts)
  return new Set([legacyPath, `${legacyPath}/index`])
}

function isForbiddenNatalInterpretationSpecifier(specifier: string): boolean {
  const oldComponentVariants = modulePathVariants(["components", "NatalInterpretation"])
  const oldSelectorVariants = modulePathVariants([
    "components",
    "natal-interpretation",
    "NatalInterpretationPersonaSelector",
  ])
  const forbiddenVariants = [...oldComponentVariants, ...oldSelectorVariants]

  return forbiddenVariants.some(
    (variant) =>
      specifier === `@/${variant}` ||
      specifier === `@${variant}` ||
      specifier.endsWith(`/${variant}`) ||
      specifier.endsWith(`/${variant}.ts`) ||
      specifier.endsWith(`/${variant}.tsx`),
  )
}

function componentOwnerModule(parts: string[]): string {
  return ["components", ...parts].join("/")
}

const FORBIDDEN_COMPONENT_OWNER_MODULES = [
  componentOwnerModule(["AdminGuard"]),
  componentOwnerModule(["B2BReconciliationPanel"]),
  componentOwnerModule(["EnterpriseCredentialsPanel"]),
  componentOwnerModule(["SupportOpsPanel"]),
  componentOwnerModule(["dashboard", "useDashboardAstroSummary"]),
  componentOwnerModule(["dashboard", "DashboardHoroscopeSummaryCardContainer"]),
  componentOwnerModule(["settings", "DeleteAccountModal"]),
  componentOwnerModule(["layout", "BottomNav"]),
  componentOwnerModule(["layout", "Header"]),
  componentOwnerModule(["layout", "Sidebar"]),
]

function isForbiddenComponentOwnerSpecifier(specifier: string): boolean {
  return FORBIDDEN_COMPONENT_OWNER_MODULES.some(
    (modulePath) =>
      specifier === `@/${modulePath}` ||
      specifier === `@${modulePath}` ||
      specifier.endsWith(`/${modulePath}`) ||
      specifier.endsWith(`/${modulePath}.ts`) ||
      specifier.endsWith(`/${modulePath}.tsx`),
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

  it("bloque le retour des anciens owners API composants CS-120", () => {
    const existingLegacyFiles = componentSourceFiles().filter((file) =>
      FORBIDDEN_COMPONENT_OWNER_MODULES.some(
        (modulePath) => file === `${modulePath}.ts` || file === `${modulePath}.tsx`,
      ),
    )
    const legacyImports = frontendSourceFiles()
      .map((file) => ({
        file,
        forbiddenSpecifiers: extractModuleSpecifiers(readFrontendFile(file)).filter(
          isForbiddenComponentOwnerSpecifier,
        ),
      }))
      .filter(({ forbiddenSpecifiers }) => forbiddenSpecifiers.length > 0)
    const staleAllowlistEntries = COMPONENT_API_IMPORT_EXCEPTIONS.filter((entry) =>
      FORBIDDEN_COMPONENT_OWNER_MODULES.some(
        (modulePath) => entry.file === `${modulePath}.ts` || entry.file === `${modulePath}.tsx`,
      ),
    )

    expect(existingLegacyFiles).toEqual([])
    expect(legacyImports).toEqual([])
    expect(staleAllowlistEntries).toEqual([])
  })

  it("bloque le retour des anciens containers auth sous components", () => {
    const forbiddenAllowlistEntries = new Set(
      ["SignInForm.tsx", "SignUpForm.tsx"].map((fileName) => ["components", fileName].join("/")),
    )
    const staleAuthEntries = COMPONENT_API_IMPORT_EXCEPTIONS.filter((entry) =>
      forbiddenAllowlistEntries.has(entry.file),
    )
    const legacyAuthImports = frontendSourceFiles().filter((file) => {
      const source = readFrontendFile(file)
      return /from\s+["']\.\.\/components\/Sign(?:In|Up)Form["']/.test(source)
    })

    expect(staleAuthEntries).toEqual([])
    expect(legacyAuthImports).toEqual([])
    expect(readFrontendFile("pages/LoginPage.tsx")).toContain('from "../features/auth/SignInForm"')
  })

  it("garde NatalInterpretation sous feature natal-chart et les enfants presentational sans API", () => {
    const legacyNatalFiles = componentSourceFiles().filter(
      (file) =>
        isActiveModuleUnderPrefix(file, ["components", "NatalInterpretation"]) ||
        isActiveModuleUnderPrefix(file, [
          "components",
          "natal-interpretation",
          "NatalInterpretationPersonaSelector",
        ]),
    )
    const legacyNatalImports = frontendSourceFiles()
      .map((file) => ({
        file,
        forbiddenSpecifiers: extractModuleSpecifiers(readFrontendFile(file)).filter(
          isForbiddenNatalInterpretationSpecifier,
        ),
      }))
      .filter(({ forbiddenSpecifiers }) => forbiddenSpecifiers.length > 0)
    const staleNatalAllowlistEntries = COMPONENT_API_IMPORT_EXCEPTIONS.filter((entry) =>
      isActiveModuleUnderPrefix(entry.file, ["components", "NatalInterpretation"]) ||
      isActiveModuleUnderPrefix(entry.file, [
        "components",
        "natal-interpretation",
        "NatalInterpretationPersonaSelector",
      ]),
    )

    expect(readFrontendFile("features/natal-chart/NatalInterpretation.tsx")).toContain("useNatalInterpretation")
    expect(readFrontendFile("features/natal-chart/NatalInterpretation.tsx")).toContain(
      'from "../../components/natal-interpretation/NatalInterpretationContent"',
    )
    expect(legacyNatalFiles).toEqual([])
    expect(legacyNatalImports).toEqual([])
    expect(staleNatalAllowlistEntries).toEqual([])

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
