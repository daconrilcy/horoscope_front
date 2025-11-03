import { http, HttpResponse } from 'msw';

const API_BASE_URL = 'http://localhost:8000';

export const handlers = [
  // POST /v1/paywall/decision
  http.post(`${API_BASE_URL}/v1/paywall/decision`, async ({ request }) => {
     
    const body = (await request.json()) as { feature?: string };

    if (!body.feature) {
      return HttpResponse.json(
        {
          message: 'Feature is required',
        },
        { status: 422 }
      );
    }

    // Simuler différentes décisions selon le feature
    const feature = body.feature;

    // Feature qui nécessite plan plus
    if (feature.includes('plus') && !feature.includes('pro')) {
      return HttpResponse.json({
        allowed: false,
        reason: 'plan',
        upgrade_url: 'https://example.com/upgrade',
      });
    }

    // Feature qui nécessite plan pro
    if (feature.includes('pro')) {
      return HttpResponse.json({
        allowed: false,
        reason: 'plan',
        upgrade_url: 'https://example.com/upgrade',
      });
    }

    // Feature rate limitée
    if (feature === 'rate_limited_feature') {
      return HttpResponse.json({
        allowed: false,
        reason: 'rate',
        retry_after: 300,
      });
    }

    // Par défaut, autorisé
    return HttpResponse.json({
      allowed: true,
    });
  }),
];
