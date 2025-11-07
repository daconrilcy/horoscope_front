import { test, expect } from '@playwright/test';

// E2E: Dev Terminal refund after capture
test.describe('Dev Terminal (refund)', () => {
  test('captures then refunds successfully', async ({ page, baseURL }) => {
    await page.route('**/v1/terminal/connect', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ connection_token: 'tok_test_123' }),
      });
    });

    await page.route('**/v1/terminal/payment-intent', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          client_secret: 'pi_secret_123',
          payment_intent_id: 'pi_test_123',
        }),
      });
    });

    await page.route('**/v1/terminal/process', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          status: 'succeeded',
          payment_intent_id: 'pi_test_123',
        }),
      });
    });

    await page.route('**/v1/terminal/refund', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({
          refund_id: 're_test_123',
          amount: 100,
          status: 'succeeded',
        }),
      });
    });

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

    await page.getByRole('button', { name: /rembourser/i }).click();
    await expect(page.getByText(/État: refunded/i)).toBeVisible();
  });
});
