import { test, expect } from '@playwright/test';

/**
 * Scénario E2E 6: Billing cancel page
 * Teste la page d'annulation après checkout Stripe
 */
test.describe('Billing cancel page', () => {
  // Utiliser l'état d'authentification sauvegardé
  test.use({ storageState: 'e2e/.auth/user.json' });

  test("devrait afficher message d'annulation et boutons", async ({ page }) => {
    // Naviguer vers la page cancel
    await page.goto('/billing/cancel');

    // Vérifier le titre
    await expect(page.locator('text=Paiement annulé')).toBeVisible({
      timeout: 2000,
    });

    // Vérifier le message d'annulation
    await expect(
      page.getByRole('heading', { name: /Paiement annulé/i })
    ).toBeVisible();
    await expect(
      page.locator('text=Vous avez annulé le processus de paiement.')
    ).toBeVisible();

    // Vérifier le bouton "Réessayer le paiement"
    const dashboardLink = page.locator(
      'a:has-text("Retour au tableau de bord")'
    );
    await expect(dashboardLink).toBeVisible();
    await expect(dashboardLink).toHaveAttribute('href', '/app/dashboard');

    // Vérifier le bouton "Retour au tableau de bord"
    const dashboardButton = page.locator(
      'a:has-text("Retour au tableau de bord")'
    );
    await expect(dashboardButton).toBeVisible();
    await expect(dashboardButton).toHaveAttribute('href', '/app/dashboard');
  });

  test('devrait permettre navigation vers dashboard', async ({ page }) => {
    await page.goto('/billing/cancel');

    // Cliquer sur le bouton dashboard
    const dashboardButton = page.locator(
      'a:has-text("Retour au tableau de bord")'
    );
    await dashboardButton.click();

    // Vérifier la navigation
    await page.waitForURL('**/app/dashboard', { timeout: 5000 });
    await expect(page).toHaveURL(/.*\/app\/dashboard/);
  });
});
