import { test, expect } from '@playwright/test';

// E2E: Dev Terminal simulator happy path (connect -> create -> process success)
// Requires the frontend dev server (Vite) running at baseURL and DEV mode

test.describe('Dev Terminal (happy path)', () => {
  test('renders console and processes a successful payment', async ({
    page,
    baseURL,
  }) => {
    // Network mocks for Terminal endpoints
    await page.route('**/v1/terminal/connect', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify({ connection_token: 'tok_test_123' }),
      });
    });

    await page.route('**/v1/terminal/payment-intent', async (route) => {
      // Optionally assert payload shape
      // const body = JSON.parse(route.request().postData() || '{}');
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

    // Go to the dev terminal route
    await page.goto(`${baseURL}/dev/terminal`);

    // Page title-ish content should be visible
    await expect(
      page.getByRole('heading', { name: /Stripe Terminal Simulator/i })
    ).toBeVisible();

    // Connect terminal
    await page.getByRole('button', { name: /connecter terminal/i }).click();
    await expect(page.getByText(/État: connected/i)).toBeVisible();

    // Create PaymentIntent
    await page.getByRole('button', { name: /créer paymentintent/i }).click();
    await expect(page.getByText(/État: intent_created/i)).toBeVisible();

    // Process (should go to captured on success)
    await page.getByRole('button', { name: /traiter paiement/i }).click();
    await expect(page.getByText(/État: captured/i)).toBeVisible();
  });
});
