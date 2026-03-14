import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Badge, IconBadge, BADGE_COLORS } from './Badge';
import { Mail } from 'lucide-react';

describe('Badge', () => {
  it('renders correctly with children', () => {
    render(<Badge>12</Badge>);
    expect(screen.getByText('12')).toBeInTheDocument();
  });

  it('applies correct size classes', () => {
    const { container: sm } = render(<Badge size="sm">SM</Badge>);
    expect(sm.firstChild).toHaveClass('badge--sm');

    const { container: lg } = render(<Badge size="lg">LG</Badge>);
    expect(lg.firstChild).toHaveClass('badge--lg');
  });

  it('applies custom background color', () => {
    const { container } = render(<Badge color="red">Red</Badge>);
    const el = container.firstChild as HTMLElement;
    expect(el.style.background).toBe('red');
  });

  it('uses BADGE_COLORS correctly', () => {
    const { container } = render(<Badge color={BADGE_COLORS.amour}>Amour</Badge>);
    const el = container.firstChild as HTMLElement;
    expect(el.style.background).toContain('var(--color-badge-amour)');
  });
});

describe('IconBadge', () => {
  it('renders the icon', () => {
    render(<IconBadge icon={<Mail data-testid="mail-icon" />} />);
    expect(screen.getByTestId('mail-icon')).toBeInTheDocument();
  });

  it('is hidden from screen readers by default (decorative)', () => {
    const { container } = render(<IconBadge icon={<Mail />} />);
    expect(container.firstChild).toHaveAttribute('aria-hidden', 'true');
  });
});
