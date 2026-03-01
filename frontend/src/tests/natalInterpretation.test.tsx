import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, cleanup } from "@testing-library/react";
import { NatalInterpretationSection } from "../components/NatalInterpretation";
import { useNatalInterpretation } from "../api/natalChart";
import { useAstrologers } from "../api/astrologers";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Mock hooks
vi.mock("../api/natalChart", async () => {
  const actual = await vi.importActual("../api/natalChart");
  return {
    ...actual,
    useNatalInterpretation: vi.fn(),
  };
});

vi.mock("../api/astrologers", async () => {
  const actual = await vi.importActual("../api/astrologers");
  return {
    ...actual,
    useAstrologers: vi.fn(),
  };
});

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
    request_id: "req-123"
  },
  degraded_mode: null
};

const mockAstrologers = [
  { id: "1", name: "Luna Céleste", specialties: ["Relations"], bio_short: "Bio Luna" }
];

describe("NatalInterpretationSection", () => {
  beforeEach(() => {
    cleanup();
    vi.clearAllMocks();
    queryClient.clear();
  });

  const renderSection = () => {
    return render(
      <QueryClientProvider client={queryClient}>
        <NatalInterpretationSection chartLoaded={true} lang="fr" />
      </QueryClientProvider>
    );
  };

  it("affiche le skeleton pendant le chargement", () => {
    (useNatalInterpretation as any).mockReturnValue({
      isLoading: true,
      data: null,
    });

    renderSection();
    expect(screen.getByText(/analyse votre thème/i)).toBeInTheDocument();
  });

  it("affiche le contenu une fois chargé", () => {
    (useNatalInterpretation as any).mockReturnValue({
      isLoading: false,
      data: mockInterpretationData,
    });

    renderSection();
    expect(screen.getByText("Votre Thème Test")).toBeInTheDocument();
    expect(screen.getByText("Résumé test de votre personnalité.")).toBeInTheDocument();
    expect(screen.getByText("Point 1")).toBeInTheDocument();
  });

  it("gère l'erreur d'interprétation", () => {
    (useNatalInterpretation as any).mockReturnValue({
      isLoading: false,
      error: new Error("Failed"),
      refetch: vi.fn(),
    });

    renderSection();
    expect(screen.getByText(/n'est pas disponible pour le moment/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /réessayer/i })).toBeInTheDocument();
  });

  it("affiche le bloc upsell en mode short", () => {
    (useNatalInterpretation as any).mockReturnValue({
      isLoading: false,
      data: mockInterpretationData,
    });

    renderSection();
    expect(screen.getByText(/Interprétation complète/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /choisir mon astrologue/i })).toBeInTheDocument();
  });

  it("ouvre le sélecteur de persona au clic sur le CTA", async () => {
    (useNatalInterpretation as any).mockReturnValue({
      isLoading: false,
      data: mockInterpretationData,
    });
    (useAstrologers as any).mockReturnValue({
      isLoading: false,
      data: mockAstrologers,
    });

    renderSection();
    fireEvent.click(screen.getByRole("button", { name: /choisir mon astrologue/i }));

    expect(screen.getByText("Luna Céleste")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /demander l'interprétation complète/i })).toBeInTheDocument();
  });

  it("ferme le sélecteur au clic sur annuler", () => {
    (useNatalInterpretation as any).mockReturnValue({
      isLoading: false,
      data: mockInterpretationData,
    });
    (useAstrologers as any).mockReturnValue({
      isLoading: false,
      data: mockAstrologers,
    });

    renderSection();
    fireEvent.click(screen.getByRole("button", { name: /choisir mon astrologue/i }));
    fireEvent.click(screen.getByRole("button", { name: /annuler/i }));

    expect(screen.queryByText("Luna Céleste")).not.toBeInTheDocument();
    expect(screen.getByText(/Interprétation complète/i)).toBeInTheDocument();
  });

  it("déclenche l'upgrade complete avec le bon persona", async () => {
    const mockRefetch = vi.fn();
    (useNatalInterpretation as any).mockReturnValue({
      isLoading: false,
      data: mockInterpretationData,
      refetch: mockRefetch,
    });
    (useAstrologers as any).mockReturnValue({
      isLoading: false,
      data: mockAstrologers,
    });

    renderSection();
    
    // Ouvrir selector
    fireEvent.click(screen.getByRole("button", { name: /choisir mon astrologue/i }));
    
    // Sélectionner persona
    fireEvent.click(screen.getByText("Luna Céleste"));
    
    // Confirmer
    fireEvent.click(screen.getByRole("button", { name: /demander l'interprétation complète/i }));

    // Vérifier que le hook a été appelé avec les bons paramètres au prochain render
    expect(useNatalInterpretation).toHaveBeenCalledWith(expect.objectContaining({
      useCaseLevel: "complete",
      personaId: "1"
    }));
  });
});
