import React from 'react'
import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { LockedSection } from './LockedSection'

describe('LockedSection', () => {
  it('renders children inside blurred content area (AC1)', () => {
    render(
      <LockedSection>
        <p>Secret content</p>
      </LockedSection>
    )
    // Content is in DOM (not removed), aria-hidden for accessibility
    const content = document.querySelector('.locked-section__content')
    expect(content).toBeInTheDocument()
    expect(content).toHaveAttribute('aria-hidden', 'true')
    expect(content).toHaveTextContent('Secret content')
  })

  it('renders lock icon in overlay (AC1)', () => {
    render(<LockedSection><p>text</p></LockedSection>)
    const overlay = document.querySelector('.locked-section__overlay')
    expect(overlay).toBeInTheDocument()
  })

  it('renders label when provided (AC3)', () => {
    render(
      <LockedSection label="Disponible avec Basic">
        <p>text</p>
      </LockedSection>
    )
    expect(screen.getByText('Disponible avec Basic')).toBeInTheDocument()
  })

  it('does not render label when not provided (AC3)', () => {
    render(<LockedSection><p>text</p></LockedSection>)
    expect(document.querySelector('.locked-section__label')).not.toBeInTheDocument()
  })

  it('renders CTA slot when provided (AC3)', () => {
    render(
      <LockedSection cta={<button>Upgrade</button>}>
        <p>text</p>
      </LockedSection>
    )
    expect(screen.getByRole('button', { name: 'Upgrade' })).toBeInTheDocument()
  })

  it('renders without CTA when not provided (AC3)', () => {
    const { container } = render(<LockedSection><p>text</p></LockedSection>)
    // The cta container div is still rendered but empty
    const ctaContainer = container.querySelector('.locked-section__cta-container')
    expect(ctaContainer).toBeInTheDocument()
    expect(ctaContainer).toBeEmptyDOMElement()
  })
})
