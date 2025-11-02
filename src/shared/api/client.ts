import { env } from '@/shared/config/env';

/**
 * Client HTTP de base
 * TODO: Implémenter la gestion des tokens, interceptors, etc.
 */
export class ApiClient {
  private baseUrl: string;

  constructor() {
    this.baseUrl = env.VITE_API_BASE_URL;
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json() as Promise<T>;
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json() as Promise<T>;
  }
}

export const apiClient = new ApiClient();

