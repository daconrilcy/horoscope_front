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
    // Vérifier que window.scrollTo existe (peut être absent dans certains environnements de test)
    if (
      typeof window !== 'undefined' &&
      typeof window.scrollTo === 'function'
    ) {
      window.scrollTo(0, 0);
    }
  }, [pathname]);

  return null;
}
