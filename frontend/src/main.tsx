import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/design-tokens.css'
import './styles/utilities.css'
import './styles/glass.css'
import './index.css'
import './styles/theme.css'
import './App.css'
import './styles/premium-theme.css'
import './styles/backgrounds.css'
import { AppProviders } from './state/providers.tsx'
import { AppRouter } from './app/router.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AppProviders>
      <AppRouter />
    </AppProviders>
  </StrictMode>,
)
