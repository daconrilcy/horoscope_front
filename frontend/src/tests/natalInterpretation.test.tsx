import type { ComponentProps } from "react";
import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, cleanup, waitFor, within } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { NatalInterpretationSection } from "../components/NatalInterpretation";
import { 
  useNatalInterpretation, 
  useNatalInterpretationsList, 
  useNatalPdfTemplates,
  useNatalInterpretationById,
  deleteNatalInterpretation,
  downloadNatalInterpretationPdf,
  previewNatalInterpretationPdf,
} from "../api/natalChart";
import { useAstrologers } from "../api/astrologers";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Mock hooks
vi.mock("../api/natalChart", async () => {
  const actual = await vi.importActual("../api/natalChart");
  return {
    ...actual,
    useNatalInterpretation: vi.fn(),
    useNatalInterpretationsList: vi.fn(),
    useNatalPdfTemplates: vi.fn(),
    useNatalInterpretationById: vi.fn(),
    deleteNatalInterpretation: vi.fn(),
    downloadNatalInterpretationPdf: vi.fn(),
    previewNatalInterpretationPdf: vi.fn(),
  };
});

vi.mock("../api/astrologers", async () => {
  const actual = await vi.importActual("../api/astrologers");
  return {
    ...actual,
    useAstrologers: vi.fn(),
  };
});

// Mock authToken
vi.mock("../utils/authToken", () => ({
  useAccessTokenSnapshot: () => "mock-token",
  getSubjectFromAccessToken: () => "mock-subject",
}));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const mockInterpretationData = {
  chart_id: "chart-123",
  use_case: "natal_interpretation_short",
  interpretation: {
    title: "Votre Thème Test",
    summary: "Résumé test de votre personnalité.",
    highlights: ["Point 1", "Point 2"],
    sections: [
      { key: "overall", heading: "Vue d'ensemble", content: "Contenu global." }
    ],
    advice: ["Conseil 1"],
    evidence: ["SUN_LEO"],
    disclaimers: ["Note test"]
  },
  meta: {
    id: 101,
    level: "short",
    use_case: "natal_interpretation_short",
    persona_id: null,
    persona_name: null,
    prompt_version_id: "v1",
    validation_status: "valid",
    repair_attempted: false,
    fallback_triggered: false,
    was_fallback: false,
    latency_ms: 1200,
    request_id: "req-123",
    persisted_at: "2026-03-04T10:00:00Z"
  },
  degraded_mode: null
};

const mockHistory = {
  items: [
    {
      id: 101,
      chart_id: "chart-123",
      level: "short",
      persona_id: null,
      persona_name: null,
      created_at: "2026-03-04T10:00:00Z",
      use_case: "natal_interpretation_short"
    },
    {
      id: 102,
      chart_id: "chart-123",
      level: "complete",
      persona_id: "1",
      persona_name: "Luna Céleste",
      created_at: "2026-03-04T11:00:00Z",
      use_case: "natal_interpretation"
    }
  ],
  total: 2,
  limit: 20,
  offset: 0
};

const mockAstrologers = [
  { id: "1", name: "Luna Céleste", first_name: "Luna", last_name: "Céleste", provider_type: "ai", specialties: ["Relations"], bio_short: "Bio Luna" }
];

describe("NatalInterpretationSection", () => {
  beforeEach(() => {
    cleanup();
    vi.clearAllMocks();
    queryClient.clear();
    
    // Default mocks
    (useNatalInterpretation as any).mockReturnValue({ isLoading: false, data: mockInterpretationData });
    (useNatalInterpretationsList as any).mockReturnValue({ isLoading: false, data: mockHistory });
    (useNatalPdfTemplates as any).mockReturnValue({
      isLoading: false,
      data: { items: [{ key: "default_natal", name: "Par défaut", description: null, locale: "fr", is_default: true }] },
    });
    (useNatalInterpretationById as any).mockReturnValue({ isLoading: false, data: null });
    (useAstrologers as any).mockReturnValue({ isLoading: false, data: mockAstrologers });
  });

  const renderSection = (props: Partial<ComponentProps<typeof NatalInterpretationSection>> = {}) => {
    return render(
      <MemoryRouter initialEntries={["/natal"]}>
        <Routes>
          <Route
            path="/natal"
            element={
              <QueryClientProvider client={queryClient}>
                <NatalInterpretationSection chartLoaded={true} chartId="chart-123" lang="fr" {...props} />
              </QueryClientProvider>
            }
          />
          <Route path="/settings/subscription" element={<div>Subscription page</div>} />
        </Routes>
      </MemoryRouter>
    );
  };

  it("affiche l'historique des versions", () => {
    renderSection();
    // The button shows the current version label instead of the title when a version is selected
    expect(screen.getByText(/Standard/i)).toBeInTheDocument();
  });

  it("masque le bloc des autres interprétations quand une seule version existe", () => {
    (useNatalInterpretationsList as any).mockReturnValue({
      isLoading: false,
      data: {
        items: [mockHistory.items[0]],
        total: 1,
        limit: 20,
        offset: 0,
      },
    });

    renderSection();

    expect(
      screen.queryByText(/Autres interprétations du thème disponibles/i),
    ).not.toBeInTheDocument();
  });

  it("permet de sélectionner une version de l'historique", async () => {
    const mockIdQuery = vi.fn().mockReturnValue({
      isLoading: false,
      data: { ...mockInterpretationData, meta: { ...mockInterpretationData.meta, id: 102, persona_name: "Luna Céleste" } }
    });
    (useNatalInterpretationById as any).mockImplementation(mockIdQuery);

    renderSection();
    
    // Ouvrir le sélecteur (cliquer sur le bouton qui affiche la version actuelle)
    fireEvent.click(screen.getByText(/Standard/i));
    
    // Cliquer sur la version de Luna
    fireEvent.click(screen.getByText(/Luna Céleste/i));

    expect(useNatalInterpretationById).toHaveBeenCalledWith(expect.objectContaining({
      interpretationId: 102
    }));
  });

  it("affiche la modal de confirmation avant suppression", async () => {
    renderSection();
    
    // Ouvrir le sélecteur
    fireEvent.click(screen.getByText(/Standard/i));
    
    // Cliquer sur le bouton supprimer de la première version (Standard)
    const deleteButtons = screen.getAllByTitle(/Supprimer/i);
    fireEvent.click(deleteButtons[0]);

    expect(screen.getByText(/Supprimer cette version/i)).toBeInTheDocument();
    expect(screen.getByText(/définitivement supprimée/i)).toBeInTheDocument();
  });

  it("appelle l'API de suppression et rafraîchit la liste", async () => {
    const mockRefetch = vi.fn().mockResolvedValue({ data: { items: [mockHistory.items[1]] } });
    (useNatalInterpretationsList as any).mockReturnValue({ 
      isLoading: false, 
      data: mockHistory,
      refetch: mockRefetch
    });
    (deleteNatalInterpretation as any).mockResolvedValue(undefined);

    renderSection();
    
    fireEvent.click(screen.getByText(/Standard/i));
    const deleteButtons = screen.getAllByTitle(/Supprimer/i);
    fireEvent.click(deleteButtons[0]);
    
    // Select the button in the modal.
    const modal = screen.getByRole("dialog");
    const modalDeleteButton = within(modal).getByRole("button", { name: /^Supprimer$/i });
    fireEvent.click(modalDeleteButton);

    await waitFor(() => {
      expect(deleteNatalInterpretation).toHaveBeenCalledWith("mock-token", 101);
      expect(mockRefetch).toHaveBeenCalled();
    });
  });

  it("déclenche le téléchargement PDF", async () => {
    (downloadNatalInterpretationPdf as any).mockResolvedValue(undefined);

    renderSection();

    fireEvent.click(screen.getByRole("button", { name: /Actions PDF/i }));
    fireEvent.click(screen.getByRole("button", { name: /Télécharger PDF/i }));

    expect(downloadNatalInterpretationPdf).toHaveBeenCalledWith(
      "mock-token", 
      101, 
      "default_natal", 
      "fr"
    );
  });

  it("déclenche l'aperçu PDF", async () => {
    (previewNatalInterpretationPdf as any).mockResolvedValue(undefined);

    renderSection();

    fireEvent.click(screen.getByRole("button", { name: /Actions PDF/i }));
    fireEvent.click(screen.getByRole("button", { name: /Aperçu PDF/i }));

    expect(previewNatalInterpretationPdf).toHaveBeenCalledWith(
      "mock-token",
      101,
      "default_natal",
      "fr",
    );
  });

  it("ouvre le sélecteur d'astrologues au clic sur l'action autre astrologue quand short+complete existent", async () => {
    (useNatalInterpretationById as any).mockReturnValue({
      isLoading: false,
      data: {
        ...mockInterpretationData,
        meta: {
          ...mockInterpretationData.meta,
          id: 102,
          level: "complete",
          use_case: "natal_interpretation",
          persona_id: "1",
          persona_name: "Luna Céleste",
        },
      },
    });

    renderSection({
      longFeatureAccess: {
        feature_code: "natal_chart_long",
        granted: true,
        reason_code: "granted",
        access_mode: "quota",
        variant_code: "multi_astrologer",
        usage_states: [{ exhausted: false, remaining: 3 }],
      } as any,
    });

    fireEvent.click(screen.getByRole("button", { name: /Choisir un autre astrologue/i }));

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText(/Choisissez votre astrologue/i)).toBeInTheDocument();
  });

  it("n'affiche pas le CTA autre astrologue en Basic quand seul un free_short existe", () => {
    (useNatalInterpretationsList as any).mockReturnValue({
      isLoading: false,
      data: {
        items: [
          {
            id: 202,
            chart_id: "chart-123",
            level: "complete",
            persona_id: null,
            persona_name: null,
            created_at: "2026-03-04T10:00:00Z",
            use_case: "natal_long_free",
          },
        ],
        total: 1,
        limit: 20,
        offset: 0,
      },
      refetch: vi.fn(),
    });

    renderSection({
      longFeatureAccess: {
        feature_code: "natal_chart_long",
        granted: true,
        reason_code: "granted",
        access_mode: "quota",
        variant_code: "single_astrologer",
        usage_states: [{ exhausted: false, remaining: 1 }],
      } as any,
    });

    expect(
      screen.getByRole("button", { name: /Obtenir le thème natal complet/i }),
    ).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /Choisir un autre astrologue/i }),
    ).not.toBeInTheDocument();
  });

  it("n'affiche le CTA autre astrologue qu'en Premium avec une vraie interprétation complète", () => {
    (useNatalInterpretationById as any).mockReturnValue({
      isLoading: false,
      data: {
        ...mockInterpretationData,
        meta: {
          ...mockInterpretationData.meta,
          id: 102,
          level: "complete",
          use_case: "natal_interpretation",
          persona_id: "1",
          persona_name: "Luna Céleste",
        },
      },
    });

    renderSection({
      longFeatureAccess: {
        feature_code: "natal_chart_long",
        granted: true,
        reason_code: "granted",
        access_mode: "quota",
        variant_code: "multi_astrologer",
        usage_states: [{ exhausted: false, remaining: 3 }],
      } as any,
    });

    expect(
      screen.getAllByRole("button", { name: /Choisir un autre astrologue/i }).length,
    ).toBeGreaterThan(0);
  });

  it("redirige vers l'abonnement quand le quota Basic complet est déjà consommé", () => {
    renderSection({
      longFeatureAccess: {
        feature_code: "natal_chart_long",
        granted: true,
        reason_code: "quota_exhausted",
        access_mode: "quota",
        variant_code: "single_astrologer",
        usage_states: [{ exhausted: true, remaining: 0 }],
      },
    });

    const actionButton = screen.getByRole("button", { name: /Passer à Premium pour plus d'interprétations/i });

    fireEvent.click(actionButton);

    expect(screen.getByText(/Subscription page/i)).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("n'arme pas une requête complete sans persona quand on demande le thème complet", async () => {
    (useNatalInterpretationsList as any).mockReturnValue({
      isLoading: false,
      data: {
        items: [mockHistory.items[0]],
        total: 1,
        limit: 20,
        offset: 0,
      },
    });

    renderSection();

    fireEvent.click(screen.getByRole("button", { name: /Obtenir le thème natal complet/i }));

    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(useNatalInterpretation).toHaveBeenLastCalledWith(
      expect.objectContaining({
        useCaseLevel: "short",
      }),
    );
  });

  it("autorise le flux free_short complet sans persona quand le thème free est verrouillé", () => {
    render(
      <MemoryRouter initialEntries={["/natal"]}>
        <Routes>
          <Route
            path="/natal"
            element={
              <QueryClientProvider client={queryClient}>
                <NatalInterpretationSection
                  chartLoaded={true}
                  chartId="chart-123"
                  lang="fr"
                  isLockedFree={true}
                />
              </QueryClientProvider>
            }
          />
          <Route path="/settings/subscription" element={<div>Subscription page</div>} />
        </Routes>
      </MemoryRouter>,
    );

    expect(useNatalInterpretation).toHaveBeenCalledWith(
      expect.objectContaining({
        useCaseLevel: "complete",
        personaId: null,
        allowCompleteWithoutPersona: true,
      }),
    );
  });

  it("affiche par défaut la dernière interprétation complète en premium", () => {
    renderSection({
      longFeatureAccess: {
        feature_code: "natal_chart_long",
        granted: true,
        reason_code: "granted",
        access_mode: "quota",
        variant_code: "multi_astrologer",
        usage_states: [{ exhausted: false, remaining: 3 }],
      } as any,
    });

    expect(useNatalInterpretationById).toHaveBeenCalledWith(
      expect.objectContaining({
        interpretationId: 102,
        enabled: true,
      }),
    );
  });

  it("affiche par défaut la dernière interprétation complète en free", () => {
    renderSection({
      isLockedFree: true,
      longFeatureAccess: {
        feature_code: "natal_chart_long",
        granted: true,
        reason_code: "granted",
        access_mode: "quota",
        variant_code: "free_short",
        usage_states: [],
      } as any,
    });

    expect(useNatalInterpretationById).toHaveBeenCalledWith(
      expect.objectContaining({
        interpretationId: 102,
        enabled: true,
      }),
    );
  });

  it("redirige vers l'abonnement Basic au clic sur le CTA free verrouillé", () => {
    (useNatalInterpretationById as any).mockReturnValue({
      isLoading: false,
      data: {
        ...mockInterpretationData,
        meta: {
          ...mockInterpretationData.meta,
          id: 102,
          level: "complete",
          persona_name: "Luna Céleste",
        },
      },
    });

    render(
      <MemoryRouter initialEntries={["/natal"]}>
        <Routes>
          <Route
            path="/natal"
            element={
              <QueryClientProvider client={queryClient}>
                <NatalInterpretationSection
                  chartLoaded={true}
                  chartId="chart-123"
                  lang="fr"
                  isLockedFree={true}
                />
              </QueryClientProvider>
            }
          />
          <Route path="/settings/subscription" element={<div>Subscription page</div>} />
        </Routes>
      </MemoryRouter>,
    );

    fireEvent.click(screen.getByRole("button", { name: /Passer à Basic pour le thème complet/i }));

    expect(screen.getByText(/Subscription page/i)).toBeInTheDocument();
    expect(useNatalInterpretation).toHaveBeenLastCalledWith(
      expect.objectContaining({
        useCaseLevel: "complete",
        personaId: null,
        allowCompleteWithoutPersona: true,
      }),
    );
  });

  it("regénère un short Basic quand l'utilisateur vient d'un free_short", async () => {
    (useNatalInterpretationsList as any).mockReturnValue({
      isLoading: false,
      data: {
        items: [
          {
            id: 202,
            chart_id: "chart-123",
            level: "complete",
            persona_id: null,
            persona_name: null,
            created_at: "2026-03-04T10:00:00Z",
            use_case: "natal_long_free",
          },
        ],
        total: 1,
        limit: 20,
        offset: 0,
      },
      refetch: vi.fn(),
    });

    renderSection({
      longFeatureAccess: {
        feature_code: "natal_chart_long",
        granted: true,
        reason_code: "granted",
        access_mode: "quota",
        variant_code: "single_astrologer",
        usage_states: [{ exhausted: false, remaining: 1 }],
      } as any,
    });

    await waitFor(() => {
      expect(useNatalInterpretation).toHaveBeenLastCalledWith(
        expect.objectContaining({
          useCaseLevel: "short",
          personaId: null,
          forceRefresh: true,
        }),
      );
    });
  });

  it("rafraîchit l'historique quand une nouvelle interprétation persistée n'est pas encore dans la liste", async () => {
    const refetch = vi.fn().mockResolvedValue({ data: mockHistory });
    (useNatalInterpretationsList as any).mockReturnValue({
      isLoading: false,
      data: {
        items: [mockHistory.items[0]],
        total: 1,
        limit: 20,
        offset: 0,
      },
      refetch,
    });
    (useNatalInterpretation as any).mockReturnValue({
      isLoading: false,
      data: {
        ...mockInterpretationData,
        meta: {
          ...mockInterpretationData.meta,
          id: 202,
          level: "complete",
          persona_id: "1",
          persona_name: "Luna Céleste",
          persisted_at: "2026-03-04T11:00:00Z",
        },
      },
    });

    renderSection();

    await waitFor(() => {
      expect(refetch).toHaveBeenCalled();
    });
  });

  it("affiche le skeleton pendant le chargement", () => {
    (useNatalInterpretation as any).mockReturnValue({
      isLoading: true,
      data: null,
    });

    renderSection();
    expect(screen.getByText(/analyse votre thème/i)).toBeInTheDocument();
  });

  it("affiche le contenu une fois chargé", () => {
    renderSection();
    expect(screen.getByText("Votre Thème Test")).toBeInTheDocument();
    expect(screen.getByText("Résumé test de votre personnalité.")).toBeInTheDocument();
  });

  it("affiche systématiquement les mentions légales applicatives", () => {
    renderSection();

    expect(screen.getByText(/Mentions légales/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Cette interprétation astrologique est un contenu de réflexion personnelle/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Ce contenu ne constitue pas un conseil médical, psychologique, juridique, fiscal ou financier/i),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Aucune garantie de résultat n'est fournie/i),
    ).toBeInTheDocument();
  });

  it("n'utilise plus les mentions légales provenant du payload LLM", () => {
    (useNatalInterpretation as any).mockReturnValue({
      isLoading: false,
      data: {
        ...mockInterpretationData,
        disclaimers: ["Disclaimer API spécifique"],
        interpretation: {
          ...mockInterpretationData.interpretation,
          disclaimers: ["Disclaimer LLM spécifique"],
        },
      },
    });

    renderSection();

    expect(screen.queryByText(/Disclaimer API spécifique/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Disclaimer LLM spécifique/i)).not.toBeInTheDocument();
    expect(screen.getByText(/Mentions légales/i)).toBeInTheDocument();
  });

  it("gère l'erreur d'interprétation", () => {
    (useNatalInterpretation as any).mockReturnValue({
      isLoading: false,
      error: new Error("Failed"),
      refetch: vi.fn(),
    });

    renderSection();
    expect(screen.getByText(/n'est pas disponible pour le moment/i)).toBeInTheDocument();
  });
});
