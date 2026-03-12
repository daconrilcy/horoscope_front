import { render, screen, cleanup } from "@testing-library/react";
import { describe, expect, it, afterEach } from "vitest";
import { TurningPointsList } from "../components/prediction/TurningPointsList";
import { ThemeProvider } from "../state/ThemeProvider";

afterEach(() => {
  cleanup();
});

const mockEnrichedMoments = [
  {
    occurred_at_local: "2026-03-12T10:00:00",
    severity: 0.8,
    summary: "Emergence",
    change_type: "emergence",
    previous_categories: ["work"],
    next_categories: ["work", "love"],
    primary_driver: { event_type: "aspect_exact_to_personal" },
    drivers: []
  },
  {
    occurred_at_local: "2026-03-12T14:00:00",
    severity: 0.6,
    summary: "Recomposition",
    change_type: "recomposition",
    previous_categories: ["love"],
    next_categories: ["health"],
    primary_driver: null, // No primary driver
    drivers: []
  },
  {
    occurred_at_local: "2026-03-12T18:00:00",
    severity: 0.4,
    summary: "Attenuation",
    change_type: "attenuation",
    previous_categories: ["health", "work"],
    next_categories: [], // Back to calm
    primary_driver: { event_type: "moon_sign_ingress" },
    drivers: []
  }
];

describe("TurningPointsList Enriched", () => {
  it("affiche les trois sections Pourquoi, Transition, Implication pour un moment enrichi", () => {
    render(
      <ThemeProvider>
        <TurningPointsList moments={[mockEnrichedMoments[0]] as any} lang="fr" />
      </ThemeProvider>
    );

    expect(screen.getByText(/Pourquoi \?/i)).toBeInTheDocument();
    expect(screen.getByText(/Transition/i)).toBeInTheDocument();
    expect(screen.getByText(/Implication/i)).toBeInTheDocument();
    
    expect(screen.getByText("Résonance avec votre thème natal")).toBeInTheDocument();
    expect(screen.getByText("Émergence d'un nouveau climat")).toBeInTheDocument();
    expect(screen.getByText(/De travail vers travail et amour/i)).toBeInTheDocument();
  });

  it("gère correctement les trois types de changement (FR)", () => {
    render(
      <ThemeProvider>
        <TurningPointsList moments={mockEnrichedMoments as any} lang="fr" />
      </ThemeProvider>
    );

    expect(screen.getByText("Émergence d'un nouveau climat")).toBeInTheDocument();
    expect(screen.getByText("Recomposition des énergies")).toBeInTheDocument();
    expect(screen.getByText("Atténuation de l'intensité")).toBeInTheDocument();
  });

  it("gère correctement les trois types de changement (EN)", () => {
    render(
      <ThemeProvider>
        <TurningPointsList moments={mockEnrichedMoments as any} lang="en" />
      </ThemeProvider>
    );

    expect(screen.getByText("Emergence of a new climate")).toBeInTheDocument();
    expect(screen.getByText("Recomposition of energies")).toBeInTheDocument();
    expect(screen.getByText("Attenuation of intensity")).toBeInTheDocument();
  });

  it("gère l'absence de driver principal avec un fallback", () => {
    render(
      <ThemeProvider>
        <TurningPointsList moments={[mockEnrichedMoments[1]] as any} lang="fr" />
      </ThemeProvider>
    );

    expect(screen.getByText("Évolution naturelle du cycle")).toBeInTheDocument();
  });

  it("gère la transition vers le calme (next_categories vide)", () => {
    render(
      <ThemeProvider>
        <TurningPointsList moments={[mockEnrichedMoments[2]] as any} lang="fr" />
      </ThemeProvider>
    );

    expect(screen.getByText(/vers calme/i)).toBeInTheDocument();
  });

  it("affiche les icônes de catégories dans la transition", () => {
    render(
      <ThemeProvider>
        <TurningPointsList moments={[mockEnrichedMoments[0]] as any} lang="fr" />
      </ThemeProvider>
    );

    // Love icon is ❤️, Work icon is 💼
    expect(screen.getByTitle("Amour & Relations")).toBeInTheDocument();
    expect(screen.getAllByTitle("Travail")).toHaveLength(2); // One in before, one in after
  });

  it("reste compatible avec le format legacy (sans change_type)", () => {
    const legacyMoments = [
      {
        occurred_at_local: "2026-03-12T14:00:00",
        severity: 0.5,
        summary: "Bascule legacy",
        drivers: [{ label: "Aspect important" }],
        next_categories: ["health"]
      }
    ];

    render(
      <ThemeProvider>
        <TurningPointsList moments={legacyMoments as any} lang="fr" />
      </ThemeProvider>
    );

    expect(screen.getByText("Bascule legacy")).toBeInTheDocument();
    expect(screen.getByText("Aspect important")).toBeInTheDocument();
    expect(screen.getByText(/Impacts :/i)).toBeInTheDocument();
    expect(screen.getByTitle("Santé & Hygiène de vie")).toBeInTheDocument();
    
    // Should NOT show enriched headers
    expect(screen.queryByText(/Pourquoi \?/i)).not.toBeInTheDocument();
  });
});
