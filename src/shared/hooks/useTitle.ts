import { useEffect } from 'react';

/**
 * Hook pour mettre à jour document.title
 * @param title - Le titre à afficher dans l'onglet du navigateur
 */
export function useTitle(title: string): void {
  useEffect(() => {
    document.title = title;
  }, [title]);
}
