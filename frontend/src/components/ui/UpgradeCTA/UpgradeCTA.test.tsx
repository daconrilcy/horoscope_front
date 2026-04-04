import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { UpgradeCTA } from './UpgradeCTA'
import { createWrapper } from '../../../tests/test-utils'
import type { UpgradeHint } from '../../../api/billing'

// Mock the entitlement snapshot hook
vi.mock('../../../hooks/useEntitlementSnapshot', () => ({
  useUpgradeHint: vi.fn(),
}))

// Mock useAstrologyLabels
vi.mock('../../../i18n/astrology', () => ({
  useAstrologyLabels: vi.fn(() => ({ lang: 'fr' })),
}))

import { useUpgradeHint } from '../../../hooks/useEntitlementSnapshot'

const mockUseUpgradeHint = vi.mocked(useUpgradeHint)

const fakeHint: UpgradeHint = {
  feature_code: 'horoscope_daily',
  current_plan_code: 'free',
  target_plan_code: 'basic',
  benefit_key: 'upgrade.horoscope_daily.full_access',
  cta_variant: 'inline',
  priority: 1,
}

describe('UpgradeCTA', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders null when no hint exists for the feature (AC4)', () => {
    mockUseUpgradeHint.mockReturnValue(undefined)
    const { container } = render(<UpgradeCTA featureCode="horoscope_daily" />, {
      wrapper: createWrapper(),
    })
    expect(container).toBeEmptyDOMElement()
  })

  it('renders a link with translated label when hint exists (AC2)', () => {
    mockUseUpgradeHint.mockReturnValue(fakeHint)
    render(<UpgradeCTA featureCode="horoscope_daily" />, {
      wrapper: createWrapper(),
    })
    const link = screen.getByRole('link')
    expect(link).toBeInTheDocument()
    expect(link).toHaveTextContent("Accéder à l'horoscope complet")
  })

  it('renders link pointing to /subscription-guide (AC2)', () => {
    mockUseUpgradeHint.mockReturnValue(fakeHint)
    render(<UpgradeCTA featureCode="horoscope_daily" />, {
      wrapper: createWrapper(),
    })
    const link = screen.getByRole('link')
    expect(link).toHaveAttribute('href', '/subscription-guide')
  })

  it('applies button variant class by default (AC2)', () => {
    mockUseUpgradeHint.mockReturnValue(fakeHint)
    render(<UpgradeCTA featureCode="horoscope_daily" />, {
      wrapper: createWrapper(),
    })
    const link = screen.getByRole('link')
    expect(link).toHaveClass('upgrade-cta--button')
  })

  it('applies link variant class when specified', () => {
    mockUseUpgradeHint.mockReturnValue(fakeHint)
    render(<UpgradeCTA featureCode="horoscope_daily" variant="link" />, {
      wrapper: createWrapper(),
    })
    const link = screen.getByRole('link')
    expect(link).toHaveClass('upgrade-cta--link')
  })

  it('renders null for unknown feature code (AC4)', () => {
    mockUseUpgradeHint.mockReturnValue(undefined)
    const { container } = render(<UpgradeCTA featureCode="unknown_feature" />, {
      wrapper: createWrapper(),
    })
    expect(container).toBeEmptyDOMElement()
  })
})
