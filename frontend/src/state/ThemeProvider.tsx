import { createContext, useContext, useState, useEffect, useCallback } from "react"
import type { ReactNode } from "react"

/** Available theme options */
export type Theme = "light" | "dark"

/** Context value provided by ThemeProvider */
export interface ThemeContextValue {
  theme: Theme
  toggleTheme: () => void
}

const ThemeContext = createContext<ThemeContextValue | undefined>(undefined)

/** Media query for detecting system dark mode preference */
export const THEME_MEDIA_QUERY = "(prefers-color-scheme: dark)"

/** Type guard to validate theme values from external sources */
function isValidTheme(value: unknown): value is Theme {
  return value === "light" || value === "dark"
}

/** Retrieves stored theme from localStorage, returns null if invalid or unavailable */
function getStoredTheme(): Theme | null {
  if (typeof window === "undefined") {
    return null
  }
  const stored = localStorage.getItem("theme")
  if (isValidTheme(stored)) {
    return stored
  }
  return null
}

/** Detects system theme preference via matchMedia, defaults to "light" if unavailable */
function getSystemTheme(): Theme {
  if (typeof window === "undefined" || typeof window.matchMedia !== "function") {
    return "light"
  }
  return window.matchMedia(THEME_MEDIA_QUERY).matches ? "dark" : "light"
}

/** Determines initial theme: localStorage > system preference > "light" fallback */
function getInitialTheme(): Theme {
  return getStoredTheme() ?? getSystemTheme()
}

/**
 * Provides theme context to the application.
 * Handles theme persistence in localStorage and responds to system preference changes.
 * @param children - React children to wrap with theme context
 */
export function ThemeProvider({ children }: { children: ReactNode }) {
  const [theme, setTheme] = useState<Theme>(getInitialTheme)
  const [hasExplicitChoice, setHasExplicitChoice] = useState<boolean>(() => getStoredTheme() !== null)

  useEffect(() => {
    document.documentElement.classList.toggle("dark", theme === "dark")
    if (hasExplicitChoice) {
      localStorage.setItem("theme", theme)
    }
  }, [theme, hasExplicitChoice])

  useEffect(() => {
    if (hasExplicitChoice || typeof window.matchMedia !== "function") {
      return
    }
    const mediaQuery = window.matchMedia(THEME_MEDIA_QUERY)
    const handleChange = (e: MediaQueryListEvent) => {
      setTheme(e.matches ? "dark" : "light")
    }
    mediaQuery.addEventListener("change", handleChange)
    return () => mediaQuery.removeEventListener("change", handleChange)
  }, [hasExplicitChoice])

  const toggleTheme = useCallback(() => {
    setHasExplicitChoice(true)
    setTheme((t) => (t === "dark" ? "light" : "dark"))
  }, [])

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  )
}

/**
 * Hook to access the current theme and toggle function.
 * Must be used within a ThemeProvider.
 * @throws Error if used outside of ThemeProvider
 */
export function useTheme(): ThemeContextValue {
  const context = useContext(ThemeContext)
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider")
  }
  return context
}

/**
 * Safe version of useTheme that returns undefined instead of throwing
 * when used outside of ThemeProvider. Useful for components that may
 * render both inside and outside the provider.
 */
export function useThemeSafe(): ThemeContextValue | undefined {
  return useContext(ThemeContext)
}
