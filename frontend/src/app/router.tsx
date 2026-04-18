import { createBrowserRouter, createMemoryRouter, RouterProvider } from "react-router-dom"
import { routes } from "./routes"

// Keep the React Router transition opt-in enabled even though the current type
// definitions do not expose the flag yet.
const routerFuture = {
  v7_relativeSplatPath: true,
  ...({ v7_startTransition: true } as Record<string, boolean>),
}

const routerProviderFuture = {
  ...({ v7_startTransition: true } as Record<string, boolean>),
}

const router = createBrowserRouter(routes, {
  future: routerFuture,
})

export function AppRouter() {
  return <RouterProvider router={router} future={routerProviderFuture} />
}

export function createTestMemoryRouter(initialEntries: string[] = ["/"]) {
  return createMemoryRouter(routes, {
    initialEntries,
    future: routerFuture,
  })
}

export function TestAppRouter({ initialEntries = ["/"] }: { initialEntries?: string[] }) {
  const testRouter = createTestMemoryRouter(initialEntries)
  return <RouterProvider router={testRouter} future={routerProviderFuture} />
}
