import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles/theme.css'
import './App.css'
import './index.css'
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
