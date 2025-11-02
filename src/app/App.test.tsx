import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { App } from './App';

describe('App', () => {
  it('should render the app', () => {
    render(
      <MemoryRouter>
        <App />
      </MemoryRouter>
    );
    expect(screen.getByText(/Horoscope/i)).toBeInTheDocument();
    expect(screen.getByText(/Page d'accueil/i)).toBeInTheDocument();
  });
});

