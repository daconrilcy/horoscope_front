import { API_BASE_URL, apiFetch, ApiError } from "./client";
import type { DailyPredictionResponse, DailyHistoryResponse } from "@app-types/dailyPrediction";

type ErrorEnvelope = {
  error: {
    code: string;
    message: string;
    request_id?: string;
  };
};

type FastApiDetailEnvelope = {
  detail?: unknown;
};

function toApiErrorPayload(raw: Record<string, unknown>): ErrorEnvelope | null {
  if (raw?.error && typeof raw.error === "object") {
    return raw as unknown as ErrorEnvelope;
  }

  const detail = (raw as FastApiDetailEnvelope).detail;
  if (detail && typeof detail === "object" && !Array.isArray(detail)) {
    const detailRecord = detail as Record<string, unknown>;
    if (typeof detailRecord.code === "string" && typeof detailRecord.message === "string") {
      return {
        error: {
          code: detailRecord.code,
          message: detailRecord.message,
        },
      };
    }
  }

  if (typeof detail === "string") {
    return {
      error: {
        code: "request_failed",
        message: detail,
      },
    };
  }

  if (Array.isArray(detail)) {
    const firstDetail = detail[0] as { msg?: string } | undefined;
    return {
      error: {
        code: "unprocessable_entity",
        message: firstDetail?.msg || "Données invalides",
      },
    };
  }

  return null;
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let payload: ErrorEnvelope | null = null;
    try {
      const raw = (await response.json()) as Record<string, unknown>;
      payload = toApiErrorPayload(raw);
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
