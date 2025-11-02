import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/**
 * Composant pour restaurer la position de scroll en haut à chaque changement de route
 * Alternative à ScrollRestoration de React Router (plus simple)
 */
export function ScrollRestoration(): null {
  const { pathname } = useLocation();

  useEffect(() => {
    // Remonter en haut de la page à chaque changement de route
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

