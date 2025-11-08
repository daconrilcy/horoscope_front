import { act } from '@testing-library/react';

/**
 * Helper pour encapsuler les interactions utilisateur dans un bloc React `act`.
 * Garantit que toutes les mises à jour d'état liées à l'action sont flushées avant les assertions.
 */
export async function actUser(
  action: () => Promise<void> | void
): Promise<void> {
  await act(async () => {
    await action();
  });
}
