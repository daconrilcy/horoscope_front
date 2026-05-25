// Configure l'environnement Vitest partage par les tests React.
import "@testing-library/jest-dom/vitest"
import { cleanup } from "@testing-library/react"
import { afterEach, beforeEach, vi } from "vitest"

const originalConsoleDebug = console.debug.bind(console)
const originalConsoleError = console.error.bind(console)
const originalStderrWrite = process.stderr.write.bind(process.stderr)

function createCanvasRenderingContextMock() {
  return {
    beginPath: vi.fn(),
    arc: vi.fn(),
    clearRect: vi.fn(),
    closePath: vi.fn(),
    createLinearGradient: vi.fn(() => ({
      addColorStop: vi.fn(),
    })),
    createRadialGradient: vi.fn(() => ({
      addColorStop: vi.fn(),
    })),
    drawImage: vi.fn(),
    fill: vi.fn(),
    fillRect: vi.fn(),
    fillText: vi.fn(),
    getImageData: vi.fn(() => ({ data: new Uint8ClampedArray() })),
    lineTo: vi.fn(),
    measureText: vi.fn(() => ({ width: 0 })),
    moveTo: vi.fn(),
    putImageData: vi.fn(),
    restore: vi.fn(),
    rotate: vi.fn(),
    save: vi.fn(),
    scale: vi.fn(),
    setTransform: vi.fn(),
    stroke: vi.fn(),
    translate: vi.fn(),
  }
}

function isKnownJsdomNavigationMessage(args: unknown[]): boolean {
  return args.some(
    (arg) =>
      (arg instanceof Error &&
        arg.message.includes("Not implemented: navigation to another Document")) ||
      (typeof arg === "string" &&
        arg.includes("Not implemented: navigation to another Document")),
  )
}

function isAnalyticsDebugMessage(args: unknown[]): boolean {
  return typeof args[0] === "string" && (
    args[0].startsWith("[Analytics NOOP]") ||
    args[0].startsWith("[analytics]")
  )
}

class MockIntersectionObserver {
  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()
}

class MockResizeObserver {
  observe = vi.fn()
  unobserve = vi.fn()
  disconnect = vi.fn()
}

function installBrowserApiMocks() {
  // JSDOM ne fournit pas Canvas; ce mock global evite le bruit des composants decoratifs.
  Object.defineProperty(HTMLCanvasElement.prototype, "getContext", {
    configurable: true,
    writable: true,
    value: vi.fn(() => createCanvasRenderingContextMock()),
  })

  // Les tests ne doivent pas ouvrir de nouvel onglet reel.
  vi.stubGlobal("open", vi.fn())
  vi.stubGlobal("IntersectionObserver", MockIntersectionObserver)
  vi.stubGlobal("ResizeObserver", MockResizeObserver)
  vi.stubGlobal(
    "matchMedia",
    vi.fn().mockImplementation((query: string) => ({
      matches: false,
      media: query,
      onchange: null,
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      addListener: vi.fn(),
      removeListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  )
}

console.debug = vi.fn((...args: unknown[]) => {
  if (isAnalyticsDebugMessage(args)) {
    return
  }

  originalConsoleDebug(...args)
})

console.error = vi.fn((...args: unknown[]) => {
  if (isKnownJsdomNavigationMessage(args)) {
    return
  }

  originalConsoleError(...args)
})

process.stderr.write = ((chunk: string | Uint8Array, ...args: unknown[]) => {
  const message = typeof chunk === "string" ? chunk : new TextDecoder().decode(chunk)
  if (message.includes("Not implemented: navigation to another Document")) {
    return true
  }

  return originalStderrWrite(chunk as string, ...(args as []))
}) as typeof process.stderr.write

// Default language for all tests to French so existing string assertions stay stable.
beforeEach(() => {
  installBrowserApiMocks()
  localStorage.removeItem("lang")

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
