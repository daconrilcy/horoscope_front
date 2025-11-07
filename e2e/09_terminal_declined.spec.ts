import { test, expect } from '@playwright/test';

// E2E: Dev Terminal declined card scenario
test.describe('Dev Terminal (declined)', () => {
  test('shows failed state on declined card', async ({ page, baseURL }) => {
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
          status: 'requires_payment_method',
          payment_intent_id: 'pi_test_123',
          error_code: 'card_declined',
          error_message: 'Your card was declined.',
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
    await expect(page.getByText(/État: failed/i)).toBeVisible();
    // Scope message to main content to avoid strict mode violation with toast
    await expect(
      page.getByRole('main').getByText(/Your card was declined/i)
    ).toBeVisible();
  });
});
