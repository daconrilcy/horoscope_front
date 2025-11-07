import { test, expect } from '@playwright/test';

// E2E: Dev Terminal processing error (2.03€ -> 203)
test.describe('Dev Terminal (processing error)', () => {
  test('shows failed state on processing error (2.03€)', async ({
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
          error_code: 'processing_error',
          error_message: 'A processing error occurred.',
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

    // Sélectionner montant 2.03€ (203)
    await page.getByLabel('Montant (centimes):').selectOption('203');

    await page.getByRole('button', { name: /traiter paiement/i }).click();
    await expect(page.getByText(/État: failed/i)).toBeVisible();
    await expect(page.getByText(/processing error/i)).toBeVisible();
  });
});
