import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { App } from './App';

describe('App', () => {
  it('should render the app', () => {
    render(<App />);
    // Vérifier que la page d'accueil est rendue avec son titre
    expect(
      screen.getByText('Horoscope & Conseils Personnalisés')
    ).toBeInTheDocument();
    expect(
      screen.getByText(
        /Découvrez votre horoscope personnalisé et recevez des conseils adaptés à votre profil astrologique/i
      )
    ).toBeInTheDocument();
  });
});
