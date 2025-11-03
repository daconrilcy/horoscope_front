import { test, expect } from '@playwright/test';

/**
 * Scénario E2E 2: upgrade Plus → chat débloqué
 * Teste le parcours d'upgrade avec interception Stripe Checkout
 */
test.describe('Billing upgrade flow', () => {
  // Utiliser l'état d'authentification sauvegardé
  test.use({ storageState: 'e2e/.auth/user.json' });

  test('devrait permettre upgrade Plus → chat débloqué', async ({ page }) => {
    // Intercepter la requête checkout pour retourner une URL locale fake
    await page.route('**/v1/billing/checkout', (route) => {
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          checkout_url: '/__fake_stripe_success',
        }),
      });
    });

    // Aller au dashboard
    await page.goto('/app/dashboard');

    // Cliquer sur Upgrade (ou bouton d'upgrade Plus)
    const upgradeButton = page
      .locator('button:has-text("Upgrade")')
      .or(page.locator('button:has-text("Plus")'))
      .or(page.locator('[data-testid="upgrade-button"]'));

    await expect(upgradeButton).toBeVisible({ timeout: 5000 });
    await upgradeButton.click();

    // Attendre navigation vers la page fake Stripe success
    await page.waitForURL('**/__fake_stripe_success', { timeout: 10000 });

    // Attendre redirection vers dashboard après succès
    await page.waitForURL('**/app/dashboard', { timeout: 10000 });

    // Vérifier que le plan est maintenant Plus (via PlanBanner ou QuotaBadge)
    await expect(
      page
        .locator('text=Plus')
        .or(page.locator('[data-testid="plan-banner"]:has-text("Plus")'))
    ).toBeVisible({ timeout: 5000 });

    // Vérifier que Chat est accessible (pas de PaywallGate visible)
    await page.goto('/app/chat');
    await expect(
      page
        .locator('text=Chat')
        .or(page.locator('[data-testid="chat-container"]'))
    ).toBeVisible({ timeout: 5000 });

    // Vérifier que PaywallGate ne bloque pas (pas de message "plan insuffisant")
    await expect(
      page.locator('text=plan insuffisant').or(page.locator('text=Plan insuffisant'))
    ).not.toBeVisible();
  });
});

