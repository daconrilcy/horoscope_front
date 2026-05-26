// Configuration frontend de l'integration analytics cible et de son defaut local.
export type AnalyticsProvider = 'plausible' | 'matomo' | 'noop'

export interface AnalyticsConfig {
  provider: AnalyticsProvider
  enabled: boolean
  domain?: string
  apiHost?: string
}

const configuredProvider = import.meta.env.VITE_ANALYTICS_PROVIDER as AnalyticsProvider | undefined
const analyticsDomain = import.meta.env.VITE_ANALYTICS_DOMAIN

export const ANALYTICS_CONFIG: AnalyticsConfig = {
  provider: configuredProvider || 'noop',
  enabled:
    configuredProvider === 'plausible'
      ? import.meta.env.VITE_ANALYTICS_ENABLED === 'true' && Boolean(analyticsDomain)
      : configuredProvider === 'noop' || !configuredProvider,
  domain: analyticsDomain,
  apiHost: import.meta.env.VITE_ANALYTICS_API_HOST || 'https://plausible.io',
}
