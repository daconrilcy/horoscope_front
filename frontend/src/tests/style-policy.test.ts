// Tests de politique garantissant que les gardes statiques couvrent aussi SCSS.
import { describe, expect, it } from "vitest"

import { listStyleFiles, readFrontendStyleFile } from "./design-system-policy"

describe("style policy", () => {
  it("inclut les feuilles SCSS dans les surfaces de style analysees", () => {
    expect(listStyleFiles()).toContain("components/ui/Badge/Badge.scss")
  })

  it("compile les feuilles SCSS avant analyse statique", () => {
    const badgeCss = readFrontendStyleFile("components/ui/Badge/Badge.scss")

    expect(badgeCss).toContain(".badge--color-primary")
    expect(badgeCss).toContain("background: var(--color-primary)")
  })
})
