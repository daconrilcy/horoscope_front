import "@testing-library/jest-dom/vitest"
import { cleanup } from "@testing-library/react"
import { afterEach, beforeEach, vi } from "vitest"

// Default language for all tests to French to maintain backward compatibility
// with existing tests that expect French strings.
beforeEach(() => {
  if (typeof navigator !== "undefined") {
    vi.stubGlobal("navigator", {
      ...navigator,
      language: "fr-FR",
    })
  }
})

afterEach(() => {
  cleanup()
})

// Mock IntersectionObserver
class MockIntersectionObserver {
  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()
}

vi.stubGlobal('IntersectionObserver', MockIntersectionObserver)
