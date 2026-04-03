export type AnalyticsProvider = 'plausible' | 'matomo' | 'noop'

export interface AnalyticsConfig {
  provider: AnalyticsProvider
  enabled: boolean
  domain?: string
  apiHost?: string
}

export const ANALYTICS_CONFIG: AnalyticsConfig = {
  provider: (import.meta.env.VITE_ANALYTICS_PROVIDER as AnalyticsProvider) || 'noop',
  enabled: import.meta.env.VITE_ANALYTICS_ENABLED === 'true' || import.meta.env.VITE_ANALYTICS_PROVIDER === 'noop' || !import.meta.env.VITE_ANALYTICS_PROVIDER,
  domain: import.meta.env.VITE_ANALYTICS_DOMAIN,
  apiHost: import.meta.env.VITE_ANALYTICS_API_HOST || 'https://plausible.io',
}
