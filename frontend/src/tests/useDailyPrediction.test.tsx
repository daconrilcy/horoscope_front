import { render } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { useDailyHistory, useDailyPrediction } from "../api/useDailyPrediction";
import { ANONYMOUS_SUBJECT } from "../utils/constants";

const useQueryMock = vi.fn();
const getSubjectFromAccessTokenMock = vi.fn();

vi.mock("@tanstack/react-query", async (importOriginal) => {
  const actual = await importOriginal<typeof import("@tanstack/react-query")>();
  return {
    ...actual,
    useQuery: (options: unknown) => useQueryMock(options),
  };
});

vi.mock("../utils/authToken", () => ({
  getSubjectFromAccessToken: (token: string | null) => getSubjectFromAccessTokenMock(token),
}));

function DailyPredictionProbe(props: { token: string | null; date?: string }) {
  useDailyPrediction(props.token, props.date);
  return null;
}

function DailyHistoryProbe(props: { token: string | null; from: string; to: string }) {
  useDailyHistory(props.token, props.from, props.to);
  return null;
}

describe("useDailyPrediction", () => {
  beforeEach(() => {
    useQueryMock.mockReset();
    getSubjectFromAccessTokenMock.mockReset();
    useQueryMock.mockReturnValue({});
  });

  afterEach(() => {
    vi.clearAllMocks();
  });

  it("scope le cache daily-prediction par utilisateur et date", () => {
    getSubjectFromAccessTokenMock.mockReturnValue("42");

    render(<DailyPredictionProbe token="token-a" date="2026-03-08" />);

    expect(useQueryMock).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ["daily-prediction", "42", "2026-03-08"],
        enabled: true,
      }),
    );
  });

  it("utilise le sujet anonyme quand le token est absent", () => {
    getSubjectFromAccessTokenMock.mockReturnValue(null);

    render(<DailyPredictionProbe token={null} />);

    expect(useQueryMock).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ["daily-prediction", ANONYMOUS_SUBJECT, "today"],
        enabled: false,
      }),
    );
  });

  it("desactive les retries et refetch automatiques pour la prediction quotidienne", () => {
    getSubjectFromAccessTokenMock.mockReturnValue("42");

    render(<DailyPredictionProbe token="token-a" date="2026-03-08" />);

    expect(useQueryMock).toHaveBeenCalledWith(
      expect.objectContaining({
        retry: false,
        refetchOnWindowFocus: false,
        refetchOnReconnect: false,
      }),
    );
  });

  it("scope aussi l'historique par utilisateur", () => {
    getSubjectFromAccessTokenMock.mockReturnValue("84");

    render(<DailyHistoryProbe token="token-b" from="2026-03-01" to="2026-03-08" />);

    expect(useQueryMock).toHaveBeenCalledWith(
      expect.objectContaining({
        queryKey: ["daily-history", "84", "2026-03-01", "2026-03-08"],
        enabled: true,
      }),
    );
  });
});
