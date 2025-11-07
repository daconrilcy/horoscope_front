import { test, expect } from '@playwright/test';

// E2E: Dev Terminal PIN flows (offline/online) - simulate processing then capture
test.describe('Dev Terminal (PIN flows)', () => {
  test('offline PIN amount leads to processing then capture', async ({
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
          status: 'requires_action',
          payment_intent_id: 'pi',
        }),
      })
    );
    await page.route('**/v1/terminal/capture', (route) =>
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
    await expect(page.getByText(/état: connected/i)).toBeVisible();

    await page.getByRole('button', { name: /créer paymentintent/i }).click();
    await expect(page.getByText(/état: intent_created/i)).toBeVisible();

    await page.getByRole('button', { name: /traiter paiement/i }).click();
    await expect(page.getByText(/état: processing/i)).toBeVisible();

    await page.getByRole('button', { name: /capturer/i }).click();
    await expect(page.getByText(/état: captured/i)).toBeVisible();
  });

  test('online PIN amount leads to processing then capture', async ({
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
          status: 'requires_action',
          payment_intent_id: 'pi',
        }),
      })
    );
    await page.route('**/v1/terminal/capture', (route) =>
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
    await expect(page.getByText(/état: connected/i)).toBeVisible();

    await page.getByRole('button', { name: /créer paymentintent/i }).click();
    await expect(page.getByText(/état: intent_created/i)).toBeVisible();

    await page.getByRole('button', { name: /traiter paiement/i }).click();
    await expect(page.getByText(/état: processing/i)).toBeVisible();

    await page.getByRole('button', { name: /capturer/i }).click();
    await expect(page.getByText(/état: captured/i)).toBeVisible();
  });
});
