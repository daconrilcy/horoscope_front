import React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Skeleton, SkeletonGroup } from './Skeleton';

describe('Skeleton', () => {
  it('renders with default variant', () => {
    const { container } = render(<Skeleton />);
    expect(container.firstChild).toHaveClass('skeleton--text');
  });

  it('renders different variants', () => {
    const { container: rect } = render(<Skeleton variant="rect" />);
    expect(rect.firstChild).toHaveClass('skeleton--rect');

    const { container: circle } = render(<Skeleton variant="circle" />);
    expect(circle.firstChild).toHaveClass('skeleton--circle');
  });

  it('applies custom dimensions', () => {
    const { container } = render(<Skeleton width="100px" height="50px" />);
    const el = container.firstChild as HTMLElement;
    expect(el.style.width).toBe('100px');
    expect(el.style.height).toBe('50px');
  });

  it('is hidden from screen readers', () => {
    const { container } = render(<Skeleton />);
    expect(container.firstChild).toHaveAttribute('aria-hidden', 'true');
  });
});

describe('SkeletonGroup', () => {
  it('renders correct number of items', () => {
    const { container } = render(<SkeletonGroup count={5} />);
    expect(container.querySelectorAll('.skeleton')).toHaveLength(5);
  });
});
