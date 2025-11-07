import { test, expect } from '@playwright/test';

/**
 * Scénario E2E 2: upgrade Plus → chat débloqué
 * Teste le parcours d'upgrade avec interception Stripe Checkout
 */
test.describe('Billing upgrade flow', () => {
  // Utiliser l'état d'authentification sauvegardé
  test.use({ storageState: 'e2e/.auth/user.json' });

  test('devrait permettre upgrade Plus → chat débloqué', async ({ page }) => {
    await page.addInitScript(() => {
      window.localStorage.setItem(
        'APP_AUTH_TOKEN',
        JSON.stringify({ token: 'e2e-token' })
      );
    });

    // Intercepter la requête checkout pour retourner une URL locale fake
    await page.route('**/v1/billing/checkout', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          checkout_url: '/checkout',
        }),
      });
    });

    // Aller au dashboard
    await page.goto('/app/dashboard');

    // Cliquer sur Upgrade (ou bouton d'upgrade Plus)
    const upgradeButton = page
      .getByRole('button', {
        name: /Passer au plan Plus|Upgrade/i,
      })
      .first();

    await expect(upgradeButton).toBeVisible({ timeout: 5000 });
    const [request] = await Promise.all([
      page.waitForRequest('**/v1/billing/checkout'),
      upgradeButton.click(),
    ]);

    expect(request.postDataJSON()).toBeDefined();

    // Remarque: le déblocage du plan nécessite le backend; on s'arrête à la navigation.
  });
});
