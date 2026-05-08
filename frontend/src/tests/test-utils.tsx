import type { ReactNode } from "react"
import { MemoryRouter } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, type RenderOptions } from "@testing-library/react"

type WrapperProps = {
  children: ReactNode
}

export const routerFutureFlags = {
  v7_startTransition: true,
  v7_relativeSplatPath: true,
} as const

export const routerProviderFutureFlags = {
  v7_startTransition: true,
} as const

function createTestQueryClient() {
  return new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        staleTime: Infinity,
      },
    },
  })
}

export function createWrapper(initialEntries: string[] = ["/"]) {
  const queryClient = createTestQueryClient()
  return function Wrapper({ children }: WrapperProps) {
    return (
      <QueryClientProvider client={queryClient}>
        <MemoryRouter initialEntries={initialEntries} future={routerFutureFlags}>
          {children}
        </MemoryRouter>
      </QueryClientProvider>
    )
  }
}

/**
 * Custom render helper for tests involving routing.
 * story 52.1 fix: Force French as default for tests using this utility
 * so tests expecting French strings stay stable.
 */
export function renderWithRouter(
  ui: React.ReactElement,
  options?: Omit<RenderOptions, "wrapper"> & { initialEntries?: string[] }
) {
  const { initialEntries = ["/"], ...renderOptions } = options ?? {}
  
  if (typeof localStorage !== "undefined") {
    localStorage.setItem("lang", "fr")
  }

  return render(ui, {
    wrapper: createWrapper(initialEntries),
    ...renderOptions,
  })
}
