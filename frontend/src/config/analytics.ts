// Configuration frontend de l'integration analytics cible et de son defaut local.
export type AnalyticsProvider = 'plausible' | 'noop'

export interface AnalyticsConfig {
  provider: AnalyticsProvider
  enabled: boolean
  domain?: string
  apiHost?: string
}

const requestedProvider = import.meta.env.VITE_ANALYTICS_PROVIDER
const analyticsDomain = import.meta.env.VITE_ANALYTICS_DOMAIN
const configuredProvider: AnalyticsProvider = requestedProvider === 'plausible' ? 'plausible' : 'noop'

export const ANALYTICS_CONFIG: AnalyticsConfig = {
  provider: configuredProvider,
  enabled:
    configuredProvider === 'plausible'
      ? import.meta.env.VITE_ANALYTICS_ENABLED === 'true' && Boolean(analyticsDomain)
      : true,
  domain: analyticsDomain,
  apiHost: import.meta.env.VITE_ANALYTICS_API_HOST || 'https://plausible.io',
}
