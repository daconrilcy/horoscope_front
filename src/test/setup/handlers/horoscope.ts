import { http, HttpResponse } from 'msw';

const API_BASE_URL = 'http://localhost:8000';

export const handlers = [
  // POST /v1/horoscope/natal
  http.post(`${API_BASE_URL}/v1/horoscope/natal`, async ({ request }) => {
    const body = (await request.json()) as {
      date?: string;
      time?: string;
      latitude?: number;
      longitude?: number;
      timezone?: string;
      name?: string;
    };

    // Validation
    if (
      !body.date ||
      !body.time ||
      body.latitude === undefined ||
      body.longitude === undefined ||
      !body.timezone
    ) {
      return HttpResponse.json(
        {
          message: 'Validation failed',
          details: {
            date: body.date ? [] : ['Date is required'],
            time: body.time ? [] : ['Time is required'],
            latitude:
              body.latitude !== undefined ? [] : ['Latitude is required'],
            longitude:
              body.longitude !== undefined ? [] : ['Longitude is required'],
            timezone: body.timezone ? [] : ['Timezone is required'],
          },
        },
        { status: 422 }
      );
    }

    // Succès
    const chartId = 'chart-' + Date.now();
    return HttpResponse.json({
      chart_id: chartId,
      created_at: new Date().toISOString(),
    });
  }),

  // GET /v1/horoscope/today/:chartId
  // eslint-disable-next-line @typescript-eslint/require-await
  http.get(
    `${API_BASE_URL}/v1/horoscope/today/:chartId`,
    async ({ params }) => {
      const chartId = params.chartId as string;

      if (!chartId || chartId === 'not-found') {
        return HttpResponse.json(
          {
            message: 'Chart not found',
          },
          { status: 404 }
        );
      }

      // Succès
      return HttpResponse.json({
        content: `Horoscope today for chart ${chartId}`,
        generated_at: new Date().toISOString(),
      });
    }
  ),

  // GET /v1/horoscope/today/premium/:chartId
  // eslint-disable-next-line @typescript-eslint/require-await
  http.get(
    `${API_BASE_URL}/v1/horoscope/today/premium/:chartId`,
    async ({ params }) => {
      const chartId = params.chartId as string;

      if (!chartId || chartId === 'not-found') {
        return HttpResponse.json(
          {
            message: 'Chart not found',
          },
          { status: 404 }
        );
      }

      // Simuler 402 si plan insuffisant
      if (chartId === 'plan-required') {
        return HttpResponse.json(
          {
            message: 'Plan insuffisant',
            code: 'plan_required',
          },
          { status: 402 }
        );
      }

      // Succès
      return HttpResponse.json({
        content: `Premium horoscope today for chart ${chartId}`,
        premium_insights: 'Premium insights here',
        generated_at: new Date().toISOString(),
      });
    }
  ),

  // GET /v1/horoscope/pdf/natal/:chartId
  http.get(
    `${API_BASE_URL}/v1/horoscope/pdf/natal/:chartId`,
    async ({ params }) => {
      const chartId = params.chartId as string;

      if (!chartId || chartId === 'not-found') {
        return HttpResponse.json(
          {
            message: 'Chart not found',
          },
          { status: 404 }
        );
      }

      // Créer un blob PDF simulé
      const pdfContent =
        '%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\nxref\n0 1\ntrailer\n<<\n/Size 1\n/Root 1 0 R\n>>\nstartxref\n9\n%%EOF';
      const blob = new Blob([pdfContent], { type: 'application/pdf' });
      const arrayBuffer = await blob.arrayBuffer();

      // eslint-disable-next-line @typescript-eslint/no-unsafe-return, @typescript-eslint/no-unsafe-call
      return HttpResponse.body(arrayBuffer, {
        headers: {
          'Content-Type': 'application/pdf',
          'Content-Disposition': `attachment; filename="natal-${chartId}.pdf"`,
        },
      });
    }
  ),
];
