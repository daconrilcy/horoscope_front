import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { App } from './App';

describe('App', () => {
  it('should render the app', () => {
    render(<App />);
    // Vérifier que la page d'accueil est rendue avec son titre
    expect(screen.getByText('Bienvenue sur Horoscope')).toBeInTheDocument();
    expect(
      screen.getByText('Découvrez votre horoscope personnalisé')
    ).toBeInTheDocument();
  });
});
