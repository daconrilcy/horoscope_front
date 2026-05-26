// Hook applicatif centralisant l'emission analytics et la redaction des payloads publics.
import { useCallback } from 'react'
import { ANALYTICS_CONFIG } from '../config/analytics'

export type AnalyticsEvent = 
  | 'landing_view' 
  | 'hero_cta_click' 
  | 'secondary_cta_click' 
  | 'pricing_view' 
  | 'pricing_plan_select' 
  | 'register_view' 
  | 'register_start' 
  | 'register_success' 
  | 'register_error'
  | 'natal_projection_request_started'
  | 'natal_projection_success'
  | 'natal_projection_api_error'
  | 'natal_projection_entitlement_denied'
  | 'natal_projection_empty'
  | 'natal_projection_degraded'
  | 'natal_projection_retry'

export const SENSITIVE_ANALYTICS_FIELD_NAMES = [
  'birth_date',
  'birth_time',
  'birth_place',
  'latitude',
  'longitude',
  'provider_response',
  'raw_runtime',
  'replay_snapshot',
  'prompt',
  'api_key',
  'password',
] as const

type AnalyticsProps = Record<string, unknown>

type AnalyticsWindow = Window & {
  plausible?: (event: AnalyticsEvent, options: { props: AnalyticsProps }) => void
}

const sensitiveAnalyticsFields = new Set<string>(SENSITIVE_ANALYTICS_FIELD_NAMES)

/** Retire les champs sensibles avant tout envoi vers un fournisseur analytics. */
export function sanitizeAnalyticsProps(props: AnalyticsProps): AnalyticsProps {
  return Object.fromEntries(
    Object.entries(props).filter(([key]) => !sensitiveAnalyticsFields.has(key)),
  )
}

/** Fournit l'API de tracking commune afin d'eviter les appels fournisseur directs. */
export const useAnalytics = () => {
  const track = useCallback((event: AnalyticsEvent, props: AnalyticsProps = {}) => {
    if (!ANALYTICS_CONFIG.enabled) return
    const safeProps = sanitizeAnalyticsProps(props)

    if (ANALYTICS_CONFIG.provider === 'noop') {
      console.debug(`[Analytics NOOP] ${event}`, safeProps)
      return
    }

    if (ANALYTICS_CONFIG.provider === 'plausible') {
      const win = window as AnalyticsWindow
      if (typeof win.plausible === 'function') {
        win.plausible(event, { props: safeProps })
      } else {
        console.warn('Plausible not loaded')
      }
    }
  }, [])

  return { track }
}

/** Extrait les parametres UTM publics depuis l'URL courante. */
export const getUtmParams = () => {
  const params = new URLSearchParams(window.location.search)
  return {
    utm_source: params.get('utm_source') || undefined,
    utm_medium: params.get('utm_medium') || undefined,
    utm_campaign: params.get('utm_campaign') || undefined,
    referrer: document.referrer || undefined
  }
}
