import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, getDailyHistory, getDailyPrediction } from "../api/dailyPrediction";

describe("dailyPrediction api", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("appelle l'endpoint daily avec la date en query string", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          meta: {},
          summary: {},
          categories: [],
          timeline: [],
          turning_points: [],
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    await getDailyPrediction("token-1", "2026-03-08");

    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe("http://localhost:8001/v1/predictions/daily?date=2026-03-08");
    expect((init.headers as Record<string, string>).Authorization).toBe("Bearer token-1");
  });

  it("mappe le format FastAPI 422 vers ApiError", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(JSON.stringify({ detail: [{ msg: "Champ requis" }] }), {
          status: 422,
          headers: { "Content-Type": "application/json" },
        }),
      ),
    );

    await expect(getDailyPrediction("token-1")).rejects.toMatchObject({
      code: "unprocessable_entity",
      status: 422,
      message: "Champ requis",
    });
  });

  it("mappe le format detail { code, message } des endpoints prediction", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            detail: {
              code: "timezone_missing",
              message: "Timezone missing",
            },
          }),
          {
            status: 422,
            headers: { "Content-Type": "application/json" },
          },
        ),
      ),
    );

    await expect(getDailyPrediction("token-1")).rejects.toMatchObject({
      code: "timezone_missing",
      status: 422,
      message: "Timezone missing",
    });
  });

  it("propage request_id et code sur les erreurs API standard", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            error: {
              code: "range_too_large",
              message: "too large",
              request_id: "rid-history-1",
            },
          }),
          { status: 400, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    try {
      await getDailyHistory("token-2", "2026-01-01", "2026-04-30");
    } catch (error) {
      expect(error).toBeInstanceOf(ApiError);
      expect(error).toMatchObject({
        code: "range_too_large",
        status: 400,
        requestId: "rid-history-1",
      });
    }
  });
});
