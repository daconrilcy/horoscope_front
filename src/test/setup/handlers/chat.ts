import { http, HttpResponse } from 'msw';

const API_BASE_URL = 'http://localhost:8000';

export const handlers = [
  // POST /v1/chat/advise
  http.post(`${API_BASE_URL}/v1/chat/advise`, async ({ request }) => {
     
    const body = (await request.json()) as {
      chart_id?: string;
      question?: string;
    };

    // Validation
    if (!body.chart_id || !body.question) {
      return HttpResponse.json(
        {
          message: 'Validation failed',
          details: {
            chart_id: body.chart_id ? [] : ['Chart ID is required'],
            question: body.question ? [] : ['Question is required'],
          },
        },
        { status: 422 }
      );
    }

    // Simuler 402 si plan insuffisant
    if (body.chart_id === 'plan-required') {
      return HttpResponse.json(
        {
          message: 'Plan insuffisant',
          code: 'plan_required',
        },
        { status: 402 }
      );
    }

    // Simuler 429 si rate limit
    if (body.chart_id === 'rate-limited') {
      return HttpResponse.json(
        {
          message: 'Rate limit exceeded',
          code: 'rate_limit',
        },
        { status: 429 }
      );
    }

    // Succès
    return HttpResponse.json({
      answer: `Réponse à la question: ${body.question}`,
      generated_at: new Date().toISOString(),
      request_id: 'req-' + Date.now(),
    });
  }),
];
