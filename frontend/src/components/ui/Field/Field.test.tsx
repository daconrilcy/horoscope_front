import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { Field } from './Field';

describe('Field', () => {
  it('renders input with label and links them via id', () => {
    render(<Field label="Email" placeholder="Enter email" />);
    
    const label = screen.getByText('Email');
    const input = screen.getByPlaceholderText('Enter email');
    
    expect(label).toHaveAttribute('for', input.id);
    expect(input).toHaveAttribute('id');
  });

  it('renders error message and sets aria-invalid', () => {
    render(<Field label="Email" error="Invalid email" />);
    
    const error = screen.getByText('Invalid email');
    const input = screen.getByLabelText('Email');
    
    expect(error).toBeInTheDocument();
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveAttribute('aria-describedby', expect.stringContaining(error.id));
  });

  it('renders hint when no error is present', () => {
    render(<Field label="Email" hint="Use your work email" />);
    
    const hint = screen.getByText('Use your work email');
    const input = screen.getByLabelText('Email');
    
    expect(hint).toBeInTheDocument();
    expect(input).toHaveAttribute('aria-describedby', expect.stringContaining(hint.id));
  });

  it('does not render hint when error is present', () => {
    render(<Field label="Email" hint="Hint text" error="Error text" />);
    
    expect(screen.getByText('Error text')).toBeInTheDocument();
    expect(screen.queryByText('Hint text')).not.toBeInTheDocument();
  });

  it('toggles password visibility', () => {
    render(<Field label="Password" type="password" />);
    
    const input = screen.getByLabelText('Password') as HTMLInputElement;
    const toggle = screen.getByLabelText(/afficher le mot de passe/i);
    
    expect(input.type).toBe('password');
    
    fireEvent.click(toggle);
    expect(input.type).toBe('text');
    expect(screen.getByLabelText(/masquer le mot de passe/i)).toBeInTheDocument();
    
    fireEvent.click(screen.getByLabelText(/masquer le mot de passe/i));
    expect(input.type).toBe('password');
  });

  it('renders left and right icons', () => {
    render(
      <Field 
        label="Search" 
        leftIcon={<span data-testid="left-icon" />} 
        rightIcon={<span data-testid="right-icon" />} 
      />
    );
    
    expect(screen.getByTestId('left-icon')).toBeInTheDocument();
    expect(screen.getByTestId('right-icon')).toBeInTheDocument();
  });

  it('handles disabled state', () => {
    render(<Field label="Disabled Field" disabled />);
    
    const input = screen.getByLabelText('Disabled Field');
    expect(input).toBeDisabled();
    expect(input).toHaveClass('field__input--disabled');
  });
});
