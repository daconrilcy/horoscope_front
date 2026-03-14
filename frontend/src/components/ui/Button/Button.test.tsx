import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('renders primary button by default', () => {
    render(<Button>Click me</Button>);
    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('btn--primary');
    expect(button).not.toHaveAttribute('disabled');
  });

  describe('variants', () => {
    const variants = ['primary', 'secondary', 'ghost', 'danger'] as const;
    
    variants.forEach((variant) => {
      it(`renders ${variant} variant correctly`, () => {
        render(<Button variant={variant}>{variant}</Button>);
        const button = screen.getByRole('button', { name: new RegExp(variant, 'i') });
        expect(button).toHaveClass(`btn--${variant}`);
      });
    });
  });

  describe('sizes', () => {
    const sizes = ['sm', 'md', 'lg'] as const;
    
    sizes.forEach((size) => {
      it(`renders ${size} size correctly`, () => {
        render(<Button size={size}>{size}</Button>);
        const button = screen.getByRole('button', { name: new RegExp(size, 'i') });
        expect(button).toHaveClass(`btn--${size}`);
      });
    });
  });

  describe('states', () => {
    it('handles disabled state', () => {
      const handleClick = vi.fn();
      render(
        <Button disabled onClick={handleClick}>
          Disabled
        </Button>
      );
      
      const button = screen.getByRole('button', { name: /disabled/i });
      expect(button).toBeDisabled();
      expect(button).toHaveAttribute('aria-disabled', 'true');
      
      fireEvent.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });

    it('handles loading state', () => {
      const handleClick = vi.fn();
      const { container } = render(
        <Button loading onClick={handleClick}>
          Loading
        </Button>
      );
      
      const button = screen.getByRole('button', { name: /loading/i });
      expect(button).toBeDisabled(); // implicitly disabled when loading
      expect(button).toHaveAttribute('aria-busy', 'true');
      expect(button).toHaveClass('btn--loading');
      
      // Spinner should be in the document
      const spinner = container.querySelector('.btn__spinner');
      expect(spinner).toBeInTheDocument();
      
      fireEvent.click(button);
      expect(handleClick).not.toHaveBeenCalled();
    });
  });

  describe('icons', () => {
    it('renders left icon', () => {
      const { container } = render(
        <Button leftIcon={<svg data-testid="left-icon" />}>With Left Icon</Button>
      );
      expect(screen.getByTestId('left-icon')).toBeInTheDocument();
      expect(container.querySelector('.btn__icon--left')).toBeInTheDocument();
    });

    it('renders right icon', () => {
      const { container } = render(
        <Button rightIcon={<svg data-testid="right-icon" />}>With Right Icon</Button>
      );
      expect(screen.getByTestId('right-icon')).toBeInTheDocument();
      expect(container.querySelector('.btn__icon--right')).toBeInTheDocument();
    });

    it('does not render icons when loading', () => {
      const { container } = render(
        <Button 
          loading 
          leftIcon={<svg data-testid="left-icon" />}
          rightIcon={<svg data-testid="right-icon" />}
        >
          Loading
        </Button>
      );
      expect(screen.queryByTestId('left-icon')).not.toBeInTheDocument();
      expect(screen.queryByTestId('right-icon')).not.toBeInTheDocument();
      expect(container.querySelector('.btn__spinner')).toBeInTheDocument();
    });
  });

  describe('props passthrough', () => {
    it('passes fullWidth and custom className', () => {
      render(
        <Button fullWidth className="custom-class">
          Full Width
        </Button>
      );
      const button = screen.getByRole('button', { name: /full width/i });
      expect(button).toHaveClass('btn--full-width');
      expect(button).toHaveClass('custom-class');
    });

    it('defaults to type="button"', () => {
      render(<Button>Default Type</Button>);
      const button = screen.getByRole('button', { name: /default type/i });
      expect(button).toHaveAttribute('type', 'button');
    });

    it('allows overriding type="submit"', () => {
      render(<Button type="submit">Submit</Button>);
      const button = screen.getByRole('button', { name: /submit/i });
      expect(button).toHaveAttribute('type', 'submit');
    });
  });
});
