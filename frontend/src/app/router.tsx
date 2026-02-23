import { createBrowserRouter, createMemoryRouter, RouterProvider } from "react-router-dom"
import { routes } from "./routes"

const router = createBrowserRouter(routes, {
  future: {
    v7_relativeSplatPath: true,
  },
})

export function AppRouter() {
  return <RouterProvider router={router} future={{ v7_startTransition: true }} />
}

export function TestAppRouter({ initialEntries = ["/"] }: { initialEntries?: string[] }) {
  const testRouter = createMemoryRouter(routes, {
    initialEntries,
    future: {
      v7_relativeSplatPath: true,
    },
  })
  return <RouterProvider router={testRouter} future={{ v7_startTransition: true }} />
}
