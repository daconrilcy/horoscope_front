import { test, expect } from '@playwright/test';

// E2E: Dev Terminal declined card while using a PIN-required amount
test.describe('Dev Terminal (declined PIN scenario)', () => {
  test('offline PIN amount with declined card results in failed payment', async ({
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
    await page.route('**/v1/terminal/process', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'requires_payment_method',
          payment_intent_id: 'pi',
          error_code: 'card_declined',
          error_message: 'Your card was declined.',
        }),
      })
    );

    await page.goto(`${baseURL}/dev/terminal`);

    await expect(
      page.getByRole('heading', { name: /Stripe Terminal Simulator/i })
    ).toBeVisible();
    await page.getByRole('button', { name: /connecter terminal/i }).click();
    await expect(page.getByText(/État: connected/i)).toBeVisible();

    // Sélectionner la carte avant de créer le PaymentIntent
    await page.selectOption('#terminal-card-select', '4000000000000002');

    await page.getByRole('button', { name: /créer paymentintent/i }).click();
    await expect(page.getByText(/État: intent_created/i)).toBeVisible();

    await page.getByRole('button', { name: /traiter paiement/i }).click();
    await expect(page.getByText(/État: failed/i)).toBeVisible();
    await expect(
      page.getByText(/Your card was declined/i).first()
    ).toBeVisible();
  });
});
