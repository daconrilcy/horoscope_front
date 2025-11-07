import { test, expect } from '@playwright/test';

// E2E: Dev Terminal success amount 1.05€ (105) — 3D Secure simulated success
test.describe('Dev Terminal (success 1.05€ - 3DS)', () => {
  test('process succeeds and shows captured (105 / 3DS)', async ({
    page,
    baseURL,
  }) => {
    await page.route('**/v1/terminal/connect', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ connection_token: 'tok' }),
      })
    );
    await page.route('**/v1/terminal/payment-intent', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ client_secret: 'sec', payment_intent_id: 'pi' }),
      })
    );
    // Simuler un succès (côté UI, aucun challenge 3DS n'est réellement présenté)
    await page.route('**/v1/terminal/process', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'succeeded', payment_intent_id: 'pi' }),
      })
    );

    await page.goto(`${baseURL}/dev/terminal`);

    await expect(
      page.getByRole('heading', { name: /Stripe Terminal Simulator/i })
    ).toBeVisible();
    await page.getByRole('button', { name: /connecter terminal/i }).click();
    await expect(page.getByText(/État: connected/i)).toBeVisible();

    // Sélectionner montant 1.05€ (105) avant de créer l'intent
    await page.getByLabel('Montant (centimes):').selectOption('105');

    await page.getByRole('button', { name: /créer paymentintent/i }).click();
    await expect(page.getByText(/État: intent_created/i)).toBeVisible();

    await page.getByRole('button', { name: /traiter paiement/i }).click();
    await expect(page.getByText(/État: captured/i)).toBeVisible();
  });
});
