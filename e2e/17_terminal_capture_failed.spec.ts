import { test, expect } from '@playwright/test';

// E2E: Dev Terminal capture failure (process => requires_action, then capture => failed)
test.describe('Dev Terminal (capture failure)', () => {
  test('goes to failed when capture fails', async ({ page, baseURL }) => {
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
          status: 'requires_action',
          payment_intent_id: 'pi',
        }),
      })
    );
    await page.route('**/v1/terminal/capture', (route) =>
      route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ status: 'failed', payment_intent_id: 'pi' }),
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
    await expect(page.getByText(/État: processing/i)).toBeVisible();

    await page.getByRole('button', { name: /capturer/i }).click();
    await expect(page.getByText(/État: failed/i)).toBeVisible();
  });
});
