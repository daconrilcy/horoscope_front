import { test, expect } from '@playwright/test';

// E2E: Dev Terminal insufficient funds (2.01€ -> 201)
test.describe('Dev Terminal (insufficient funds)', () => {
  test('shows failed state on insufficient funds', async ({
    page,
    baseURL,
  }) => {
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
          error_code: 'insufficient_funds',
          error_message: 'Insufficient funds',
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
    await expect(page.getByText(/Insufficient funds/i).first()).toBeVisible();
  });
});
