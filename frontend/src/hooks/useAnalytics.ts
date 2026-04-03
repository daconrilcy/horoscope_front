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

/**
 * Basic consent check. 
 * In a real app, this would check a cookie or global state from a Consent Banner.
 */
const hasConsent = () => {
  // AC1: Privacy-first - if provider is noop, we always "have consent" for logging
  if (ANALYTICS_CONFIG.provider === 'noop') return true
  
  // For Plausible/Matomo, check if user has accepted cookies/tracking
  // This is a placeholder for the actual consent management logic
  const consent = localStorage.getItem('cookie_consent')
  return consent === 'granted' || ANALYTICS_CONFIG.provider === 'plausible' // Plausible often runs without consent if configured cookie-less
}

export const useAnalytics = () => {
  const track = useCallback((event: AnalyticsEvent, props: Record<string, any> = {}) => {
    if (!ANALYTICS_CONFIG.enabled) return

    if (ANALYTICS_CONFIG.provider === 'noop') {
      console.debug(`[Analytics NOOP] ${event}`, props)
      return
    }

    // AC1.1: No events without consent
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
