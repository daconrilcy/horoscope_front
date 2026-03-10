import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { createMemoryRouter, RouterProvider } from "react-router-dom";

import { routes } from "../app/routes";
import { ThemeProvider } from "../state/ThemeProvider";
import { setAccessToken } from "../utils/authToken";

const authMeOk = {
  data: {
    id: 42,
    role: "user",
    email: "celeste@example.com",
    created_at: "2026-03-08T08:30:00Z",
  },
};

const predictionOk = {
  meta: {
    date_local: "2026-03-08",
    timezone: "Europe/Paris",
    computed_at: "2026-03-08T06:00:00Z",
    reference_version: "2026.03",
    ruleset_version: "1.0.0",
    was_reused: false,
    house_system_effective: "placidus",
  },
  summary: {
    overall_tone: "open",
    overall_summary: "Journee favorable pour prendre contact et structurer vos priorites.",
    top_categories: ["love", "career"],
    bottom_categories: ["energy", "social_network"],
    best_window: {
      start_local: "2026-03-08T08:00:00+01:00",
      end_local: "2026-03-08T09:30:00+01:00",
      dominant_category: "career",
    },
    main_turning_point: {
      occurred_at_local: "2026-03-08T11:15:00+01:00",
      severity: 2.5,
      summary: "Accalmie passagere avant un nouveau pic d'energie.",
    },
  },
  categories: [
    {
      code: "love",
      note_20: 13.6,
      raw_score: 0.64,
      power: 1.2,
      volatility: 0.4,
      rank: 1,
      summary: "Les echanges sont fluides.",
    },
    {
      code: "career",
      note_20: 7.2,
      raw_score: 0.12,
      power: 0.8,
      volatility: 0.7,
      rank: 2,
      summary: "Gardez une marge de manoeuvre.",
    },
  ],
  timeline: [
    {
      start_local: "2026-03-08T08:00:00+01:00",
      end_local: "2026-03-08T09:30:00+01:00",
      tone_code: "open",
      dominant_categories: ["love", "career"],
      summary: "Bon moment pour lancer une conversation importante.",
      turning_point: false,
    },
    {
      start_local: "2026-03-08T11:15:00+01:00",
      end_local: "2026-03-08T12:00:00+01:00",
      tone_code: "careful",
      dominant_categories: ["energy"],
      summary: "Le rythme change brusquement.",
      turning_point: true,
    },
  ],
  turning_points: [
    {
      occurred_at_local: "2026-03-08T11:15:00+01:00",
      severity: 2.5,
      summary: "Un signal demande de lever le pied.",
      drivers: [{ label: "Mars carre Lune" }],
    },
  ],
};

const predictionWithDecisionWindows = {
  meta: {
    date_local: "2026-03-08",
    timezone: "Europe/Paris",
    computed_at: "2026-03-08T06:00:00Z",
    reference_version: "2026.03",
    ruleset_version: "2.0.0",
    was_reused: false,
    house_system_effective: "placidus",
  },
  summary: {
    overall_tone: "positive",
    overall_summary: "Journée avec des créneaux décisionnels bien définis.",
    top_categories: ["love", "work"],
    bottom_categories: ["energy"],
    best_window: null,
    main_turning_point: null,
  },
  categories: [
    { code: "love", note_20: 14, raw_score: 0.7, power: 1.1, volatility: 0.3, rank: 1, summary: null },
  ],
  timeline: [
    {
      start_local: "2026-03-08T09:00:00+01:00",
      end_local: "2026-03-08T11:00:00+01:00",
      tone_code: "positive",
      dominant_categories: ["love"],
      summary: null,
      turning_point: false,
    },
  ],
  turning_points: [
    {
      occurred_at_local: "2026-03-08T14:00:00+01:00",
      severity: "0.6",
      summary: "high_priority_event",
      drivers: [{ event_type: "aspect_enter_orb", body: "Mars", target: "Jupiter" }],
    },
  ],
  decision_windows: [
    {
      start_local: "2026-03-08T09:00:00+01:00",
      end_local: "2026-03-08T11:00:00+01:00",
      window_type: "favorable",
      score: 0.82,
      confidence: 0.9,
      dominant_categories: ["love"],
    },
    {
      start_local: "2026-03-08T14:00:00+01:00",
      end_local: "2026-03-08T15:30:00+01:00",
      window_type: "prudence",
      score: 0.55,
      confidence: 0.75,
      dominant_categories: ["work"],
    },
    {
      start_local: "2026-03-08T17:00:00+01:00",
      end_local: "2026-03-08T18:30:00+01:00",
      window_type: "pivot",
      score: 0.65,
      confidence: 0.8,
      dominant_categories: ["love", "work"],
    },
  ],
};

const predictionTechnical = {
  meta: {
    date_local: "2026-03-08",
    timezone: "Europe/Paris",
    computed_at: "2026-03-08T20:22:30Z",
    reference_version: "2.0.0",
    ruleset_version: "2.0.0",
    was_reused: false,
    house_system_effective: "placidus",
    is_provisional_calibration: true,
    calibration_label: "provisional",
  },
  summary: {
    overall_tone: "neutral",
    overall_summary:
      "Votre journée du 2026-03-08 s'annonce équilibrée. Vos points forts : Énergie & Vitalité, Humeur & Climat intérieur, Santé & Hygiène de vie.",
    calibration_note:
      "Les scores sont calculés sans données historiques : ils reflètent des tendances relatives à la journée, pas des statistiques absolues.",
    top_categories: ["energy", "mood", "health"],
    bottom_categories: ["energy", "mood"],
    best_window: {
      start_local: "2026-03-08T00:00:00+01:00",
      end_local: "2026-03-08T01:00:00+01:00",
      dominant_category: "career",
    },
    main_turning_point: {
      occurred_at_local: "2026-03-08T07:30:00",
      severity: 0.8,
      summary: "delta_note",
    },
  },
  categories: [
    {
      code: "energy",
      note_20: 10,
      raw_score: 0,
      power: 0,
      volatility: 0,
      rank: 1,
      summary: "Énergie & Vitalité : Votre score est de 10/20 (climat neutre).",
    },
    {
      code: "mood",
      note_20: 10,
      raw_score: 0,
      power: 0,
      volatility: 0,
      rank: 2,
      summary: "Humeur & Climat intérieur : Votre score est de 10/20 (climat neutre).",
    },
    {
      code: "health",
      note_20: 10,
      raw_score: 0,
      power: 0,
      volatility: 0,
      rank: 3,
      summary: "Santé & Hygiène de vie : Votre score est de 10/20 (climat neutre).",
    },
  ],
  timeline: [
    {
      start_local: "2026-03-08T00:00:00+01:00",
      end_local: "2026-03-08T01:00:00+01:00",
      tone_code: "neutral",
      dominant_categories: ["career", "communication", "energy"],
      summary: null,
      turning_point: false,
    },
    {
      start_local: "2026-03-08T01:00:00+01:00",
      end_local: "2026-03-08T02:00:00+01:00",
      tone_code: "neutral",
      dominant_categories: ["career", "communication", "energy"],
      summary: null,
      turning_point: false,
    },
    {
      start_local: "2026-03-08T02:00:00+01:00",
      end_local: "2026-03-08T03:00:00+01:00",
      tone_code: "neutral",
      dominant_categories: ["career", "communication", "energy"],
      summary: null,
      turning_point: false,
    },
    {
      start_local: "2026-03-08T07:00:00+01:00",
      end_local: "2026-03-08T07:30:00+01:00",
      tone_code: "neutral",
      dominant_categories: ["career", "communication", "energy"],
      summary: null,
      turning_point: true,
    },
  ],
  turning_points: [
    {
      occurred_at_local: "2026-03-08T07:30:00+01:00",
      severity: 0.8,
      summary: "delta_note",
      drivers: [
        {
          event_type: "exact",
          body: "Venus",
          target: "Pluto",
          aspect: "opposition",
        },
      ],
    },
  ],
};

const predictionNeutralTimelineWithLateWindows = {
  meta: {
    date_local: "2026-03-10",
    timezone: "Europe/Paris",
    computed_at: "2026-03-10T04:48:58.981478",
    reference_version: "2.0.0",
    ruleset_version: "2.0.0",
    was_reused: false,
    house_system_effective: "placidus",
    is_provisional_calibration: true,
    calibration_label: "provisional",
  },
  summary: {
    overall_tone: "positive",
    overall_summary: "Votre journée du 2026-03-10 s'annonce très porteuse.",
    calibration_note: "Les scores sont calculés sans données historiques : ils reflètent des tendances relatives à la journée, pas des statistiques absolues.",
    top_categories: ["social_network", "pleasure_creativity", "energy"],
    bottom_categories: ["money", "work"],
    best_window: {
      start_local: "2026-03-10T21:30:00+01:00",
      end_local: "2026-03-10T22:15:00+01:00",
      dominant_category: "pleasure_creativity",
    },
    main_turning_point: {
      occurred_at_local: "2026-03-10T02:30:00",
      severity: 1.0,
      summary: "À 02:30, un basculement critique : plusieurs domaines.",
    },
  },
  categories: [
    { code: "social_network", note_20: 20, raw_score: 0.1, power: 0.1, volatility: 0.1, rank: 1, is_provisional: true, summary: null },
    { code: "pleasure_creativity", note_20: 19, raw_score: 0.09, power: 0.09, volatility: 0.09, rank: 2, is_provisional: true, summary: null },
  ],
  timeline: [
    {
      start_local: "2026-03-10T00:00:00",
      end_local: "2026-03-10T21:30:00",
      tone_code: "neutral",
      dominant_categories: ["career", "communication", "energy"],
      summary: "Entre 00:00 et 21:30, tonalité équilibrée — Carrière, Communication, Énergie & Vitalité.",
      turning_point: true,
    },
    {
      start_local: "2026-03-10T21:30:00",
      end_local: "2026-03-10T23:15:00",
      tone_code: "positive",
      dominant_categories: ["pleasure_creativity", "social_network", "career"],
      summary: "Entre 21:30 et 23:15, tonalité très porteuse — Plaisir & Créativité, Vie sociale & Réseau, Carrière.",
      turning_point: true,
    },
    {
      start_local: "2026-03-10T23:15:00",
      end_local: "2026-03-11T00:00:00",
      tone_code: "neutral",
      dominant_categories: ["career", "communication", "energy"],
      summary: "Entre 23:15 et 00:00, tonalité équilibrée — Carrière, Communication, Énergie & Vitalité.",
      turning_point: true,
    },
  ],
  turning_points: [
    {
      occurred_at_local: "2026-03-10T02:30:00",
      severity: "1.0",
      summary: "À 02:30, un basculement critique : plusieurs domaines.",
      drivers: [],
    },
    {
      occurred_at_local: "2026-03-10T21:30:00",
      severity: "0.8",
      summary: "À 21:30, un basculement critique : Communication, Énergie & Vitalité, Plaisir & Créativité, Vie sociale & Réseau.",
      drivers: [],
    },
  ],
  decision_windows: [
    {
      start_local: "2026-03-10T02:00:00+01:00",
      end_local: "2026-03-10T06:00:00+01:00",
      window_type: "pivot",
      score: 10,
      confidence: 1,
      dominant_categories: ["career", "communication"],
    },
    {
      start_local: "2026-03-10T21:30:00+01:00",
      end_local: "2026-03-10T22:15:00+01:00",
      window_type: "favorable",
      score: 19.5,
      confidence: 0.99,
      dominant_categories: ["pleasure_creativity", "social_network"],
    },
    {
      start_local: "2026-03-10T22:15:00+01:00",
      end_local: "2026-03-10T23:15:00+01:00",
      window_type: "favorable",
      score: 19.5,
      confidence: 0.99,
      dominant_categories: ["pleasure_creativity", "social_network"],
    },
  ],
};

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json" },
  });
}

function installFetchMock(options?: {
  authMe?: Response | Promise<Response>;
  prediction?: Response | Promise<Response>;
}) {
  const authMe = options?.authMe ?? jsonResponse(authMeOk);
  const prediction = options?.prediction ?? jsonResponse(predictionOk);

  vi.stubGlobal(
    "fetch",
    vi.fn((input: RequestInfo | URL) => {
      const url = String(input);
      if (url.endsWith("/v1/auth/me")) {
        return Promise.resolve(authMe);
      }
      if (url.includes("/v1/predictions/daily")) {
        return Promise.resolve(prediction);
      }
      return Promise.resolve(jsonResponse({ error: { code: "not_found", message: "not found" } }, 404));
    }),
  );
}

function setupToken(sub = "42") {
  const payload = btoa(JSON.stringify({ sub, role: "user" }));
  setAccessToken(`x.${payload}.y`);
}

function renderDashboard(initialEntries: string[] = ["/dashboard"]) {
  const router = createMemoryRouter(routes, {
    initialEntries,
    future: { v7_relativeSplatPath: true },
  });
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: Infinity } },
  });

  return {
    router,
    ...render(
      <ThemeProvider>
        <QueryClientProvider client={queryClient}>
          <RouterProvider router={router} future={{ v7_startTransition: true }} />
        </QueryClientProvider>
      </ThemeProvider>,
    ),
  };
}

describe("TodayPage", () => {
  beforeEach(() => {
    localStorage.setItem("lang", "fr");
    setupToken();
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
    localStorage.clear();
  });

  it("affiche la prediction API, les categories dynamiques et les heures en HH:mm", async () => {
    installFetchMock();

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/Journee favorable pour prendre contact/i)).toBeInTheDocument();
    });

    expect(screen.getByRole("heading", { level: 1, name: "Horoscope" })).toBeInTheDocument();
    expect(screen.getByText("11:00 – 11:30")).toBeInTheDocument();
    expect(screen.getByText("Moments clés du jour")).toBeInTheDocument();
    expect(screen.getByText("Agenda du jour")).toBeInTheDocument();
    expect(screen.getAllByText("Bascule").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Impacts :").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Carrière").length).toBeGreaterThan(0);
    expect(screen.getByText("13.6")).toBeInTheDocument();
    expect(screen.getByText("7.2")).toBeInTheDocument();
    expect(screen.getByText("Chat astrologue")).toBeInTheDocument();
    expect(screen.getByText("Tirage du jour")).toBeInTheDocument();
  });

  it("affiche un etat de chargement explicite pendant la recuperation de la prediction", async () => {
    installFetchMock({
      prediction: new Promise<Response>(() => undefined),
    });

    renderDashboard();

    expect(screen.getByText("Chargement de votre ciel du jour...")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /Chargement du profil/i })).toBeInTheDocument();
  });

  it("affiche un message d'erreur explicite et permet de relancer", async () => {
    let shouldFail = true;
    vi.stubGlobal(
      "fetch",
      vi.fn((input: RequestInfo | URL) => {
        const url = String(input);
        if (url.endsWith("/v1/auth/me")) {
          return Promise.resolve(jsonResponse(authMeOk));
        }
        if (url.includes("/v1/predictions/daily")) {
          if (shouldFail) {
            return Promise.resolve(
              jsonResponse(
                { error: { code: "daily_prediction_unavailable", message: "prediction indisponible" } },
                503,
              ),
            );
          }
          return Promise.resolve(jsonResponse(predictionOk));
        }
        return Promise.resolve(jsonResponse({ error: { code: "not_found", message: "not found" } }, 404));
      }),
    );

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText("Impossible de charger votre horoscope.")).toBeInTheDocument();
    });

    shouldFail = false;
    await userEvent.click(screen.getByRole("button", { name: "Réessayer" }));

    await waitFor(() => {
      expect(screen.getByText(/Journee favorable pour prendre contact/i)).toBeInTheDocument();
    });
  });

  it("n'explose pas sur une reponse vide et affiche l'etat empty", async () => {
    installFetchMock({
      prediction: jsonResponse(null),
    });

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText("Aucune prédiction disponible.")).toBeInTheDocument();
    });
  });

  it("affiche l'etat empty quand l'API renvoie une erreur de setup 422", async () => {
    installFetchMock({
      prediction: jsonResponse(
        {
          detail: {
            code: "profile_missing",
            message: "Profil de naissance introuvable",
          },
        },
        422,
      ),
    });

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText("Aucune prédiction disponible.")).toBeInTheDocument();
    });
  });

  it("bascule les libelles de prediction en anglais quand la langue active est en", async () => {
    localStorage.setItem("lang", "en");
    installFetchMock();

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/Journee favorable pour prendre contact/i)).toBeInTheDocument();
    });

    expect(screen.getByText("Best window")).toBeInTheDocument();
    expect(screen.getByText("Key moments today")).toBeInTheDocument();
    expect(screen.getByText("Dominant : Career")).toBeInTheDocument();
  });

  it("humanise les payloads techniques et compacte la timeline repetitive", async () => {
    installFetchMock({
      prediction: jsonResponse(predictionTechnical),
    });

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/Votre journée du 2026-03-08 s'annonce équilibrée/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Les scores sont calculés sans données historiques/i)).toBeInTheDocument();
    expect(screen.queryByText("delta_note")).not.toBeInTheDocument();
    expect(screen.getAllByText("Pas d'aspect majeur").length).toBeGreaterThan(0);
    expect(screen.queryByText("Énergie & Vitalité : Votre score est de 10/20 (climat neutre).")).not.toBeInTheDocument();
  });

  it("affiche l'agenda du jour et les moments clés quand ils sont présents", async () => {
    installFetchMock({
      prediction: jsonResponse(predictionWithDecisionWindows),
    });

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/Journée avec des créneaux décisionnels bien définis/i)).toBeInTheDocument();
    });

    expect(screen.getByText("Agenda du jour")).toBeInTheDocument();
    expect(screen.getByText("Moments clés du jour")).toBeInTheDocument();
    expect(screen.getAllByTestId("agenda-slot")).toHaveLength(12);
    expect(screen.getAllByTestId("agenda-slot-pivot").length).toBeGreaterThan(0);

    const morningSlot = screen
      .getAllByTestId("agenda-slot")
      .find((element) => element.getAttribute("data-slot-label") === "08:00");
    expect(morningSlot).toBeDefined();
    expect(within(morningSlot!).getByText("Amour & Relations")).toBeInTheDocument();

    const pivotSlot = screen
      .getAllByTestId("agenda-slot")
      .find((element) => element.getAttribute("data-slot-label") === "14:00");
    expect(pivotSlot).toBeDefined();
    expect(within(pivotSlot!).getByTestId("agenda-slot-pivot")).toBeInTheDocument();

    expect(screen.getAllByText(/aspects majeurs/i).length).toBeGreaterThan(0);
  });

  it("localise le libellé d'impacts en anglais", async () => {
    localStorage.setItem("lang", "en");
    installFetchMock();

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/Journee favorable pour prendre contact/i)).toBeInTheDocument();
    });

    expect(screen.getAllByText("Impacts:").length).toBeGreaterThan(0);
    expect(screen.queryByText("Impacts :")).not.toBeInTheDocument();
  });

  it("n'affiche pas de fausses recommandations d'agenda sur des créneaux uniquement neutres", async () => {
    installFetchMock({
      prediction: jsonResponse(predictionNeutralTimelineWithLateWindows),
    });

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText("Votre journée du 2026-03-10 s'annonce très porteuse.")).toBeInTheDocument();
    });

    const midnightSlot = screen
      .getAllByTestId("agenda-slot")
      .find((element) => element.getAttribute("data-slot-label") === "00:00");
    expect(midnightSlot).toBeDefined();
    expect(within(midnightSlot!).queryByText("Carrière")).not.toBeInTheDocument();
    expect(within(midnightSlot!).queryByText("Communication")).not.toBeInTheDocument();

    const eveningSlot = screen
      .getAllByTestId("agenda-slot")
      .find((element) => element.getAttribute("data-slot-label") === "20:00");
    expect(eveningSlot).toBeDefined();
    expect(within(eveningSlot!).getByText("Plaisir & Créativité")).toBeInTheDocument();
    expect(within(midnightSlot!).getByText("Pas d'aspect majeur")).toBeInTheDocument();
  });

  it("n'expose pas de codes techniques backend dans l'interface", async () => {
    installFetchMock({
      prediction: jsonResponse(predictionWithDecisionWindows),
    });

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/Journée avec des créneaux décisionnels bien définis/i)).toBeInTheDocument();
    });

    expect(screen.queryByText("aspect_enter_orb")).not.toBeInTheDocument();
    expect(screen.queryByText("high_priority_event")).not.toBeInTheDocument();
    expect(screen.queryByText("Entrée en orbe d'aspect")).not.toBeInTheDocument();
  });

  it("ne rend plus la chronologie du jour devenue redondante", async () => {
    installFetchMock();

    renderDashboard();

    await waitFor(() => {
      expect(screen.getByText(/Journee favorable pour prendre contact/i)).toBeInTheDocument();
    });

    expect(screen.queryByText("Chronologie du jour")).not.toBeInTheDocument();
  });
});
