import { chromium, request } from '@playwright/test';
import { randomUUID } from 'node:crypto';
import { mkdirSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

export default async function globalSetup(): Promise<void> {
  const frontendBase = process.env.E2E_BASE_URL ?? 'http://localhost:5173';
  const apiBase = process.env.API_BASE_URL ?? 'http://localhost:8000';

  const authDir = resolve('e2e/.auth');
  const storageStatePath = resolve(authDir, 'user.json');
  if (!existsSync(authDir)) {
    mkdirSync(authDir, { recursive: true });
  }

  const email = `e2e-${Date.now()}@example.com`;
  const password = 'Password123!';

  const api = await request.newContext({ baseURL: apiBase, timeout: 15000 });

  // Signup (ignore 409 if already exists)
  const signupRes = await api.post('/v1/auth/signup', {
    data: { email, password, entitlements: [] },
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': randomUUID(),
    },
  });
  if (!(signupRes.ok() || signupRes.status() === 409)) {
    const body = await signupRes.text();
    throw new Error(`Signup failed: ${signupRes.status()} ${body}`);
  }

  // Login
  const loginRes = await api.post('/v1/auth/login', {
    data: { email, password },
    headers: {
      'Content-Type': 'application/json',
      'Idempotency-Key': randomUUID(),
    },
  });
  if (!loginRes.ok()) {
    const body = await loginRes.text();
    throw new Error(`Login failed: ${loginRes.status()} ${body}`);
  }
  const loginJson = (await loginRes.json()) as { access_token: string };
  const token = loginJson.access_token;

  // Seed storage state with localStorage token for the frontend
  const browser = await chromium.launch();
  const context = await browser.newContext({ baseURL: frontendBase });
  const page = await context.newPage();
  await page.goto('/');
  await page.evaluate(([t]) => {
    try {
      localStorage.setItem('APP_AUTH_TOKEN', JSON.stringify({ token: t }));
    } catch {}
  }, [token]);
  await context.storageState({ path: storageStatePath });
  await browser.close();
  await api.dispose();
}
