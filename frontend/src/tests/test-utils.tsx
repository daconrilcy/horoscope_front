import type { ReactNode } from "react"
import { MemoryRouter } from "react-router-dom"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { render, type RenderOptions } from "@testing-library/react"

type WrapperProps = {
  children: ReactNode
}

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
        <MemoryRouter
          initialEntries={initialEntries}
          future={{ v7_startTransition: true, v7_relativeSplatPath: true }}
        >
          {children}
        </MemoryRouter>
      </QueryClientProvider>
    )
  }
}

/**
 * Custom render helper for tests involving routing.
 * story 52.1 fix: Force French as default for tests using this utility
 * to maintain backward compatibility with tests expecting French strings.
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
