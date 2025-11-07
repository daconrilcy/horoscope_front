import { test, expect } from '@playwright/test';

// E2E: Dev Terminal signature required (1.03€ -> 103) treated as success after process
test.describe('Dev Terminal (signature amount 1.03€)', () => {
  test('process returns succeeded and shows captured', async ({
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
        body: JSON.stringify({ status: 'succeeded', payment_intent_id: 'pi' }),
      })
    );

    await page.goto(`${baseURL}/dev/terminal`);

    await expect(
      page.getByRole('heading', { name: /Stripe Terminal Simulator/i })
    ).toBeVisible();
    await page.getByRole('button', { name: /connecter terminal/i }).click();
    await expect(page.getByText(/État: connected/i)).toBeVisible();

    await page.getByRole('button', { name: /créer paymentintent/i }).click();
    await expect(page.getByText(/État: intent_created/i)).toBeVisible();

    await page.getByRole('button', { name: /traiter paiement/i }).click();
    await expect(page.getByText(/État: captured/i)).toBeVisible();
  });
});
