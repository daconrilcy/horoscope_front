import { describe, it, expect, beforeEach, afterEach, vi } from "vitest"
import { render, screen, fireEvent, act, cleanup } from "@testing-library/react"
import { ThemeProvider, useTheme, useThemeSafe, THEME_MEDIA_QUERY, type ThemeContextValue, type Theme } from "../state/ThemeProvider"

function TestComponent() {
  const { theme, toggleTheme } = useTheme()
  return (
    <div>
      <span data-testid="theme">{theme}</span>
      <button onClick={toggleTheme}>Toggle</button>
    </div>
  )
}

function SafeTestComponent() {
  const ctx = useThemeSafe()
  return <span data-testid="safe-theme">{ctx?.theme ?? "no-context"}</span>
}

describe("ThemeProvider", () => {
  beforeEach(() => {
    localStorage.clear()
    document.documentElement.classList.remove("dark")
  })

  afterEach(() => {
    cleanup()
  })

  describe("AC5: Toggle dark mode fonctionnel", () => {
    it("defaults to light when no stored preference", () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )
      expect(screen.getByTestId("theme")).toHaveTextContent("light")
    })

    it("does not persist theme to localStorage without explicit user choice", () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      expect(screen.getByTestId("theme")).toHaveTextContent("light")
      expect(localStorage.getItem("theme")).toBeNull()
    })

    it("toggles theme and applies dark class to documentElement", () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      expect(screen.getByTestId("theme")).toHaveTextContent("light")
      expect(document.documentElement.classList.contains("dark")).toBe(false)

      act(() => {
        fireEvent.click(screen.getByRole("button", { name: "Toggle" }))
      })

      expect(screen.getByTestId("theme")).toHaveTextContent("dark")
      expect(document.documentElement.classList.contains("dark")).toBe(true)
    })

    it("persists theme choice in localStorage", () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      act(() => {
        fireEvent.click(screen.getByRole("button", { name: "Toggle" }))
      })

      expect(localStorage.getItem("theme")).toBe("dark")
    })

    it("restores theme from localStorage on mount", () => {
      localStorage.setItem("theme", "dark")

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      expect(screen.getByTestId("theme")).toHaveTextContent("dark")
      expect(document.documentElement.classList.contains("dark")).toBe(true)
    })

    it("toggles back to light", () => {
      localStorage.setItem("theme", "dark")

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      act(() => {
        fireEvent.click(screen.getByRole("button", { name: "Toggle" }))
      })

      expect(screen.getByTestId("theme")).toHaveTextContent("light")
      expect(document.documentElement.classList.contains("dark")).toBe(false)
      expect(localStorage.getItem("theme")).toBe("light")
    })
  })

  describe("useTheme hook", () => {
    it("throws error when used outside ThemeProvider", () => {
      const consoleError = vi.spyOn(console, "error").mockImplementation(() => {})

      expect(() => render(<TestComponent />)).toThrow(
        "useTheme must be used within a ThemeProvider"
      )

      consoleError.mockRestore()
    })
  })

  describe("useThemeSafe hook", () => {
    it("returns undefined when used outside ThemeProvider", () => {
      render(<SafeTestComponent />)
      expect(screen.getByTestId("safe-theme")).toHaveTextContent("no-context")
    })

    it("returns context when used inside ThemeProvider", () => {
      render(
        <ThemeProvider>
          <SafeTestComponent />
        </ThemeProvider>
      )
      expect(screen.getByTestId("safe-theme")).toHaveTextContent("light")
    })
  })

  describe("ThemeContextValue interface", () => {
    it("exports ThemeContextValue for external typing", () => {
      const mockContext: ThemeContextValue = {
        theme: "dark",
        toggleTheme: () => {},
      }
      expect(mockContext.theme).toBe("dark")
      expect(typeof mockContext.toggleTheme).toBe("function")
    })
  })

  describe("Theme type", () => {
    it("exports Theme type for external typing", () => {
      const lightTheme: Theme = "light"
      const darkTheme: Theme = "dark"
      expect(lightTheme).toBe("light")
      expect(darkTheme).toBe("dark")
    })
  })

  describe("Theme initialization priority", () => {
    it("prioritizes localStorage over system preference", () => {
      localStorage.setItem("theme", "light")

      const mockMatchMedia = vi.fn((query: string) => ({
        matches: query.includes("dark") ? true : false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      }))
      vi.stubGlobal("matchMedia", mockMatchMedia)

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      expect(screen.getByTestId("theme")).toHaveTextContent("light")

      vi.unstubAllGlobals()
    })

    it("falls back to system preference when no localStorage", () => {
      const mockMatchMedia = vi.fn((query: string) => ({
        matches: query.includes("dark") ? true : false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: vi.fn(),
        dispatchEvent: vi.fn(),
      }))
      vi.stubGlobal("matchMedia", mockMatchMedia)

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      expect(screen.getByTestId("theme")).toHaveTextContent("dark")

      vi.unstubAllGlobals()
    })
  })

  describe("Invalid localStorage handling", () => {
    it("ignores invalid theme value in localStorage and defaults to light", () => {
      localStorage.setItem("theme", "invalid")

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      expect(screen.getByTestId("theme")).toHaveTextContent("light")
    })

    it("ignores uppercase theme value in localStorage", () => {
      localStorage.setItem("theme", "DARK")

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      expect(screen.getByTestId("theme")).toHaveTextContent("light")
    })

    it("ignores empty string in localStorage", () => {
      localStorage.setItem("theme", "")

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      expect(screen.getByTestId("theme")).toHaveTextContent("light")
    })
  })

  describe("System theme detection", () => {
    let mediaQueryListeners: Array<(e: MediaQueryListEvent) => void> = []
    let mockMatchesDark = false

    beforeEach(() => {
      mediaQueryListeners = []
      mockMatchesDark = false

      const mockMatchMedia = vi.fn((query: string) => ({
        matches: query.includes("dark") ? mockMatchesDark : false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn((_event: string, listener: (e: MediaQueryListEvent) => void) => {
          mediaQueryListeners.push(listener)
        }),
        removeEventListener: vi.fn((_event: string, listener: (e: MediaQueryListEvent) => void) => {
          mediaQueryListeners = mediaQueryListeners.filter((l) => l !== listener)
        }),
        dispatchEvent: vi.fn(),
      }))

      vi.stubGlobal("matchMedia", mockMatchMedia)
    })

    afterEach(() => {
      vi.unstubAllGlobals()
    })

    it("responds to system theme changes when no explicit choice made", () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      expect(screen.getByTestId("theme")).toHaveTextContent("light")

      act(() => {
        mediaQueryListeners.forEach((listener) => {
          listener({ matches: true } as MediaQueryListEvent)
        })
      })

      expect(screen.getByTestId("theme")).toHaveTextContent("dark")
    })

    it("ignores system theme changes after explicit toggle", () => {
      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      act(() => {
        fireEvent.click(screen.getByRole("button", { name: "Toggle" }))
      })

      expect(screen.getByTestId("theme")).toHaveTextContent("dark")

      act(() => {
        mediaQueryListeners.forEach((listener) => {
          listener({ matches: false } as MediaQueryListEvent)
        })
      })

      expect(screen.getByTestId("theme")).toHaveTextContent("dark")
    })

    it("ignores system theme changes when localStorage has explicit choice", () => {
      localStorage.setItem("theme", "light")

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      act(() => {
        mediaQueryListeners.forEach((listener) => {
          listener({ matches: true } as MediaQueryListEvent)
        })
      })

      expect(screen.getByTestId("theme")).toHaveTextContent("light")
    })

    it("exports THEME_MEDIA_QUERY constant for consistency", () => {
      expect(THEME_MEDIA_QUERY).toBe("(prefers-color-scheme: dark)")
    })

    it("removes event listener on unmount", () => {
      const removeEventListenerMock = vi.fn()
      const mockMatchMedia = vi.fn((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: vi.fn(),
        removeEventListener: removeEventListenerMock,
        dispatchEvent: vi.fn(),
      }))

      vi.stubGlobal("matchMedia", mockMatchMedia)

      const { unmount } = render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      unmount()

      expect(removeEventListenerMock).toHaveBeenCalledWith("change", expect.any(Function))
    })

    it("removes event listener when user makes explicit choice", () => {
      const removeEventListenerMock = vi.fn()
      const addEventListenerMock = vi.fn()
      const mockMatchMedia = vi.fn((query: string) => ({
        matches: false,
        media: query,
        onchange: null,
        addListener: vi.fn(),
        removeListener: vi.fn(),
        addEventListener: addEventListenerMock,
        removeEventListener: removeEventListenerMock,
        dispatchEvent: vi.fn(),
      }))

      vi.stubGlobal("matchMedia", mockMatchMedia)

      render(
        <ThemeProvider>
          <TestComponent />
        </ThemeProvider>
      )

      expect(addEventListenerMock).toHaveBeenCalledWith("change", expect.any(Function))

      act(() => {
        fireEvent.click(screen.getByRole("button", { name: "Toggle" }))
      })

      expect(removeEventListenerMock).toHaveBeenCalledWith("change", expect.any(Function))
    })
  })
})
