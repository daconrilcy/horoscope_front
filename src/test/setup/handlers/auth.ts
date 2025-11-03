import { http, HttpResponse } from 'msw';

const API_BASE_URL = 'http://localhost:8000';

export const handlers = [
  // POST /v1/auth/signup
  http.post(`${API_BASE_URL}/v1/auth/signup`, async ({ request }) => {
     
    const body = (await request.json()) as {
      email?: string;
      password?: string;
    };

    // Validation simple côté handler
    if (!body.email || !body.password) {
      return HttpResponse.json(
        {
          message: 'Validation failed',
          details: {
            email: body.email ? [] : ['Email is required'],
            password: body.password ? [] : ['Password is required'],
          },
        },
        { status: 422 }
      );
    }

    // Email déjà utilisé (simulation)
    if (body.email === 'exists@example.com') {
      return HttpResponse.json(
        {
          message: 'Email already exists',
          details: {
            email: ['Email already exists'],
          },
        },
        { status: 422 }
      );
    }

    // Succès
    return HttpResponse.json({
      token: 'valid-token-1234567890',
      user: {
        id: '123e4567-e89b-12d3-a456-426614174000',
        email: body.email.toLowerCase().trim(),
      },
    });
  }),

  // POST /v1/auth/login
  http.post(`${API_BASE_URL}/v1/auth/login`, async ({ request }) => {
    const body = (await request.json()) as {
      email?: string;
      password?: string;
    };

    // Credentials invalides
    if (body.email !== 'test@example.com' || body.password !== 'password123') {
      return HttpResponse.json(
        {
          message: 'Invalid credentials',
          code: 'invalid_credentials',
        },
        { status: 401 }
      );
    }

    // Succès
    return HttpResponse.json({
      token: 'valid-token-1234567890',
      user: {
        id: '123e4567-e89b-12d3-a456-426614174000',
        email: body.email.toLowerCase().trim(),
      },
    });
  }),

  // POST /v1/auth/reset/request
  http.post(`${API_BASE_URL}/v1/auth/reset/request`, async ({ request }) => {
    const body = (await request.json()) as { email?: string };

    if (!body.email) {
      return HttpResponse.json(
        {
          message: 'Validation failed',
          details: {
            email: ['Email is required'],
          },
        },
        { status: 422 }
      );
    }

    // Succès (toujours retourner succès pour éviter email enumeration)
    return HttpResponse.json({
      message: 'If an account exists, a reset email has been sent',
    });
  }),

  // POST /v1/auth/reset/confirm
  http.post(`${API_BASE_URL}/v1/auth/reset/confirm`, async ({ request }) => {
    const body = (await request.json()) as {
      token?: string;
      password?: string;
    };

    if (!body.token || !body.password) {
      return HttpResponse.json(
        {
          message: 'Validation failed',
          details: {
            token: body.token ? [] : ['Token is required'],
            password: body.password ? [] : ['Password is required'],
          },
        },
        { status: 422 }
      );
    }

    // Token invalide
    if (body.token === 'invalid-token') {
      return HttpResponse.json(
        {
          message: 'Invalid or expired token',
          code: 'invalid_token',
        },
        { status: 400 }
      );
    }

    // Succès
    return HttpResponse.json({
      message: 'Password reset successfully',
    });
  }),
];
