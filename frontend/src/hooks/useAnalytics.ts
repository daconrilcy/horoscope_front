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

const hasConsent = () => {
  if (ANALYTICS_CONFIG.provider === 'noop') return true
  if (ANALYTICS_CONFIG.provider === 'plausible') return true

  const consent = localStorage.getItem('cookie_consent')
  return consent === 'granted'
}

export const useAnalytics = () => {
  const track = useCallback((event: AnalyticsEvent, props: Record<string, any> = {}) => {
    if (!ANALYTICS_CONFIG.enabled) return

    if (ANALYTICS_CONFIG.provider === 'noop') {
      console.debug(`[Analytics NOOP] ${event}`, props)
      return
    }

    if (!hasConsent()) {
      console.warn(`[Analytics] Event ${event} suppressed: No consent`)
      return
    }

    if (ANALYTICS_CONFIG.provider === 'plausible') {
      const win = window as any
      if (typeof win.plausible === 'function') {
        win.plausible(event, { props })
      } else {
        console.warn('Plausible not loaded')
      }
    } else if (ANALYTICS_CONFIG.provider === 'matomo') {
      const win = window as any
      if (win._paq) {
        win._paq.push(['trackEvent', 'Funnel', event, JSON.stringify(props)])
      }
    }
  }, [])

  return { track }
}

/**
 * Utility to parse UTM parameters from URL
 */
export const getUtmParams = () => {
  const params = new URLSearchParams(window.location.search)
  return {
    utm_source: params.get('utm_source') || undefined,
    utm_medium: params.get('utm_medium') || undefined,
    utm_campaign: params.get('utm_campaign') || undefined,
    referrer: document.referrer || undefined
  }
}
