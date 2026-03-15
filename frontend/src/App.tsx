import "./App.css"
import { AppRouter } from "./app/router"
import { AppProviders } from "./state/providers"

function App() {
  return (
    <AppProviders>
      <AppRouter />
    </AppProviders>
  )
}

export default App
