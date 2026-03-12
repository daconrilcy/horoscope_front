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
  }
];

describe("TurningPointsList Enriched", () => {
  it("affiche les trois sections Pourquoi, Transition, Implication pour un moment enrichi", () => {
    render(
      <ThemeProvider>
        <TurningPointsList moments={mockEnrichedMoments as any} lang="fr" />
      </ThemeProvider>
    );

    expect(screen.getByText(/Pourquoi \?/i)).toBeInTheDocument();
    expect(screen.getByText(/Transition/i)).toBeInTheDocument();
    expect(screen.getByText(/Implication/i)).toBeInTheDocument();
    
    expect(screen.getByText("Résonance avec votre thème natal")).toBeInTheDocument();
    expect(screen.getByText("Émergence d'un nouveau climat")).toBeInTheDocument();
    expect(screen.getByText(/De travail vers travail et amour/i)).toBeInTheDocument();
  });

  it("affiche les icônes de catégories dans la transition", () => {
    render(
      <ThemeProvider>
        <TurningPointsList moments={mockEnrichedMoments as any} lang="fr" />
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
