import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Loader } from './Loader';

describe('Loader', () => {
  it('devrait afficher un spinner par défaut', () => {
    render(<Loader />);

    const loader = screen.getByRole('status');
    expect(loader).toBeInTheDocument();
    expect(loader).toHaveAttribute('aria-busy', 'true');
    expect(loader).toHaveAttribute('aria-label', 'Chargement');
  });

  it('devrait afficher un spinner avec taille sm', () => {
    const { container } = render(<Loader variant="spinner" size="sm" />);

    const loader = container.querySelector('[role="status"]');
    expect(loader).toBeInTheDocument();
    expect(loader).toHaveStyle({ width: '16px', height: '16px' });
  });

  it('devrait afficher un spinner avec taille md', () => {
    const { container } = render(<Loader variant="spinner" size="md" />);

    const loader = container.querySelector('[role="status"]');
    expect(loader).toHaveStyle({ width: '24px', height: '24px' });
  });

  it('devrait afficher un spinner avec taille lg', () => {
    const { container } = render(<Loader variant="spinner" size="lg" />);

    const loader = container.querySelector('[role="status"]');
    expect(loader).toHaveStyle({ width: '32px', height: '32px' });
  });

  it('devrait afficher un skeleton', () => {
    const { container } = render(<Loader variant="skeleton" size="md" />);

    const loader = container.querySelector('[role="status"]');
    expect(loader).toBeInTheDocument();
    expect(loader).toHaveStyle({ height: '24px' });
  });

  it('devrait être inline si inline=true', () => {
    const { container } = render(<Loader inline={true} />);

    const loader = container.querySelector('[role="status"]');
    expect(loader).toHaveStyle({ display: 'inline-block' });
  });

  it('devrait être block si inline=false', () => {
    const { container } = render(<Loader inline={false} />);

    const loader = container.querySelector('[role="status"]');
    expect(loader).toHaveStyle({ display: 'block' });
  });
});
