import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Card } from './Card';

describe('Card', () => {
  it('renders correctly with children', () => {
    render(<Card>Hello Card</Card>);
    expect(screen.getByText('Hello Card')).toBeInTheDocument();
  });

  it('renders as different HTML elements', () => {
    const { container } = render(<Card as="article">Article Content</Card>);
    expect(container.querySelector('article')).toBeInTheDocument();
  });

  it('applies variant classes', () => {
    const { container: glass } = render(<Card variant="glass">Glass</Card>);
    expect(glass.firstChild).toHaveClass('card--glass');
    expect(glass.firstChild).toHaveClass('glass-card');

    const { container: solid } = render(<Card variant="solid">Solid</Card>);
    expect(solid.firstChild).toHaveClass('card--solid');

    const { container: elevated } = render(<Card variant="elevated">Elevated</Card>);
    expect(elevated.firstChild).toHaveClass('card--elevated');
  });

  it('renders sub-components correctly', () => {
    render(
      <Card>
        <Card.Header>Header Content</Card.Header>
        <Card.Body>Body Content</Card.Body>
        <Card.Footer>Footer Content</Card.Footer>
      </Card>
    );

    expect(screen.getByText('Header Content')).toHaveClass('card__header');
    expect(screen.getByText('Body Content')).toHaveClass('card__body');
    expect(screen.getByText('Footer Content')).toHaveClass('card__footer');
  });

  it('applies clickable class when clickable is true', () => {
    const { container } = render(<Card clickable>Clickable Card</Card>);
    expect(container.firstChild).toHaveClass('card--clickable');
  });

  it('applies correct padding classes', () => {
    const { container } = render(<Card padding="lg">Large Padding</Card>);
    expect(container.firstChild).toHaveClass('card--padding-lg');
  });
});
