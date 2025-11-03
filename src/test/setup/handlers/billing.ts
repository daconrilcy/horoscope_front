import { http, HttpResponse } from 'msw';

const API_BASE_URL = 'http://localhost:8000';

export const handlers = [
  // POST /v1/billing/checkout
  http.post(`${API_BASE_URL}/v1/billing/checkout`, async ({ request }) => {
    // eslint-disable-next-line @typescript-eslint/no-unsafe-assignment, @typescript-eslint/no-unsafe-member-access
    const body = (await request.json()) as { plan?: string };
    const idempotencyKey = request.headers.get('Idempotency-Key');

    // Vérifier idempotency key
    if (!idempotencyKey) {
      return HttpResponse.json(
        {
          message: 'Idempotency-Key header is required',
        },
        { status: 400 }
      );
    }

    if (!body.plan || !['plus', 'pro'].includes(body.plan)) {
      return HttpResponse.json(
        {
          message: 'Invalid plan',
          details: {
            plan: ['Plan must be plus or pro'],
          },
        },
        { status: 422 }
      );
    }

    // Succès
    return HttpResponse.json({
      checkout_url: 'https://checkout.stripe.com/pay/test',
    });
  }),

  // POST /v1/billing/portal
  http.post(`${API_BASE_URL}/v1/billing/portal`, () => {
    // Succès
    return HttpResponse.json({
      portal_url: 'https://billing.stripe.com/p/test',
    });
  }),
];
