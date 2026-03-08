import { API_BASE_URL, apiFetch } from "./client";
import type { DailyPredictionResponse, DailyHistoryResponse } from "../types/dailyPrediction";

type ErrorEnvelope = {
  error: {
    code: string;
    message: string;
    request_id?: string;
  };
};

export class ApiError extends Error {
  readonly code: string;
  readonly status: number;
  readonly requestId?: string;

  constructor(code: string, message: string, status: number, requestId?: string) {
    super(message);
    this.code = code;
    this.status = status;
    this.requestId = requestId;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let payload: ErrorEnvelope | null = null;
    try {
      const raw = (await response.json()) as Record<string, unknown>;
      if (raw?.error) {
        payload = raw as unknown as ErrorEnvelope;
      } else if (Array.isArray(raw?.detail)) {
        const firstDetail = (raw.detail as Array<{ msg?: string }>)[0];
        payload = {
          error: {
            code: "unprocessable_entity",
            message: firstDetail?.msg || "Données invalides",
          },
        };
      }
    } catch {
      payload = null;
    }
    throw new ApiError(
      payload?.error?.code ?? "unknown_error",
      payload?.error?.message ?? `Request failed with status ${response.status}`,
      response.status,
      payload?.error?.request_id
    );
  }

  const payload = (await response.json()) as T;
  return payload;
}

export async function getDailyPrediction(
  token: string,
  date?: string
): Promise<DailyPredictionResponse> {
  const url = new URL(`${API_BASE_URL}/v1/predictions/daily`);
  if (date) url.searchParams.set("date", date);

  const response = await apiFetch(url.toString(), {
    headers: { Authorization: `Bearer ${token}` },
  });

  return handleResponse<DailyPredictionResponse>(response);
}

export async function getDailyHistory(
  token: string,
  from: string,
  to: string
): Promise<DailyHistoryResponse> {
  const url = new URL(`${API_BASE_URL}/v1/predictions/daily/history`);
  url.searchParams.set("from_date", from);
  url.searchParams.set("to_date", to);

  const response = await apiFetch(url.toString(), {
    headers: { Authorization: `Bearer ${token}` },
  });

  return handleResponse<DailyHistoryResponse>(response);
}
