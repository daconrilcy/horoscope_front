import { test, expect } from '@playwright/test';

// E2E: Dev Terminal cancel flow
test.describe('Dev Terminal (cancel flow)', () => {
  test('creates intent then cancels successfully', async ({
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
    await page.route('**/v1/terminal/cancel', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'canceled', payment_intent_id: 'pi' }),
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

    await page.getByRole('button', { name: /annuler/i }).click();
    await expect(page.getByText(/État: canceled/i)).toBeVisible();
  });
});
