import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { EmptyState } from './EmptyState';

describe('EmptyState', () => {
  it('renders title and description', () => {
    render(<EmptyState title="No data" description="Try again later" />);
    expect(screen.getByText('No data')).toBeInTheDocument();
    expect(screen.getByText('Try again later')).toBeInTheDocument();
  });

  it('renders action when provided', () => {
    render(
      <EmptyState 
        title="Empty" 
        action={<button>Retry</button>} 
      />
    );
    expect(screen.getByRole('button', { name: /retry/i })).toBeInTheDocument();
  });

  it('renders icon when provided', () => {
    render(
      <EmptyState 
        title="Empty" 
        icon={<span data-testid="test-icon" />} 
      />
    );
    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
  });
});
