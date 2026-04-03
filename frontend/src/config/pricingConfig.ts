/**
 * Canoncial Plan Codes for the platform.
 */
export type PlanCode = 'free' | 'trial' | 'basic' | 'premium'

export interface PlanFeature {
  id: 'natal' | 'horoscope' | 'chat' | 'consultation' | 'predictions' | 'support'
  enabled: boolean
  quota?: string
}

export interface PlanPricing {
  planCode: PlanCode
  monthlyPriceCents: number | null
  currency: string
  isRecommended: boolean
  isAvailable: boolean
  features: PlanFeature[]
}

/**
 * Pricing configuration for the public landing page.
 * Synchronized with the backend canonical catalog and Stripe.
 */
export const PRICING_CONFIG: Record<string, PlanPricing> = {
  free: {
    planCode: 'free',
    monthlyPriceCents: 0,
    currency: 'EUR',
    isRecommended: false,
    isAvailable: true,
    features: [
      { id: 'natal', enabled: true },
      { id: 'horoscope', enabled: true },
      { id: 'chat', enabled: true, quota: '1/week' },
      { id: 'consultation', enabled: false },
      { id: 'predictions', enabled: false },
      { id: 'support', enabled: false },
    ],
  },
  basic: {
    planCode: 'basic',
    monthlyPriceCents: 900,
    currency: 'EUR',
    isRecommended: true,
    isAvailable: true,
    features: [
      { id: 'natal', enabled: true },
      { id: 'horoscope', enabled: true },
      { id: 'chat', enabled: true },
      { id: 'consultation', enabled: true },
      { id: 'predictions', enabled: true },
      { id: 'support', enabled: false },
    ],
  },
  premium: {
    planCode: 'premium',
    monthlyPriceCents: 2900,
    currency: 'EUR',
    isRecommended: false,
    isAvailable: true,
    features: [
      { id: 'natal', enabled: true },
      { id: 'horoscope', enabled: true },
      { id: 'chat', enabled: true },
      { id: 'consultation', enabled: true },
      { id: 'predictions', enabled: true },
      { id: 'support', enabled: true },
    ],
  },
}

/**
 * Helper to get active plans for display.
 */
export const getActivePlans = (): PlanPricing[] => {
  return Object.values(PRICING_CONFIG).filter(plan => plan.isAvailable)
}

/**
 * Formats the price for display.
 */
export const formatPrice = (priceCents: number | null, currency: string, lang: string = 'fr'): string => {
  if (priceCents === null) return '--'
  if (priceCents === 0) return '0'
  
  const amount = priceCents / 100
  return new Intl.NumberFormat(lang === 'en' ? 'en-US' : lang === 'es' ? 'es-ES' : 'fr-FR', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(amount)
}
