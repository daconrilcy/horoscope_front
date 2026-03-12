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
    primary_driver: {
      event_type: "aspect_exact_to_personal",
      body: "Moon",
      target: "Mars",
      aspect: "sextile",
      orb_deg: 0.12,
      phase: "applying",
      metadata: { natal_house_transited: 5, natal_house_target: 8 },
    },
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
    
    expect(screen.getByText("Moon sextile Mars")).toBeInTheDocument();
    expect(screen.getByText(/Orbe 0,12° · Phase appliquante · Maisons 5 -> 8/i)).toBeInTheDocument();
    expect(screen.getByText("Émergence d'un nouveau climat")).toBeInTheDocument();
    expect(screen.getByText(/amour & relations rejoint travail au premier plan/i)).toBeInTheDocument();
    expect(
      screen.getByText(/Le climat s'ouvre davantage à amour & relations, aux côtés de travail/i),
    ).toBeInTheDocument();
  });

  it("affiche la section Mouvement Global et Variations Locales si présentes", () => {
    const movementMoment = {
      ...mockEnrichedMoments[0],
      movement: {
        direction: "rising",
        strength: 8.0,
        previous_composite: 5.0,
        next_composite: 12.5,
        delta_composite: 4.0,
      },
      category_deltas: [
        { code: "love", direction: "up", delta_score: 2.0, delta_intensity: 5.0 }
      ]
    };

    render(
      <ThemeProvider>
        <TurningPointsList moments={[movementMoment] as any} lang="fr" />
      </ThemeProvider>
    );

    expect(screen.getAllByText(/Mouvement global/i).length).toBeGreaterThan(0);
    expect(screen.getByText(/Mouvement global en hausse \(marqué\)/i)).toBeInTheDocument();
    expect(screen.getByText(/variation globale \+4,00 \(5,00 -> 12,50\)/i)).toBeInTheDocument();
    expect(screen.getByText(/❤️ progression sur amour & relations/i)).toBeInTheDocument();
    expect(screen.getByText(/delta score \+2,00 · delta intensité \+5,00/i)).toBeInTheDocument();
  });

  it("affiche un mouvement global en baisse (notable)", () => {
    const fallingMoment = {
      ...mockEnrichedMoments[0],
      movement: {
        direction: "falling",
        strength: 5.0,
        previous_composite: 12.5,
        next_composite: 10.0,
        delta_composite: -2.5,
      },
      category_deltas: [
        { code: "work", direction: "down", delta_score: -1.0, delta_intensity: 2.0 }
      ]
    };

    render(
      <ThemeProvider>
        <TurningPointsList moments={[fallingMoment] as any} lang="fr" />
      </ThemeProvider>
    );

    expect(screen.getByText(/Mouvement global en baisse \(net\)/i)).toBeInTheDocument();
    expect(screen.getByText(/💼 recul sur travail/i)).toBeInTheDocument();
  });

  it("affiche un mouvement de mutation sans intensité qualitative", () => {
    const shiftingMoment = {
      ...mockEnrichedMoments[0],
      movement: {
        direction: "recomposition",
        strength: 1.0,
        previous_composite: 8.0,
        next_composite: 8.1,
        delta_composite: 0.1,
      },
      category_deltas: []
    };

    render(
      <ThemeProvider>
        <TurningPointsList moments={[shiftingMoment] as any} lang="fr" />
      </ThemeProvider>
    );

    expect(screen.getByText(/Mouvement global en mutation/i)).toBeInTheDocument();
    // No qualitative level for recomposition in my humanizeMovement implementation
  });

  it("ne pollue pas avec des variations locales si vides (sous seuil)", () => {
    const belowThresholdMoment = {
      ...mockEnrichedMoments[0],
      movement: {
        direction: "rising",
        strength: 2.0,
        previous_composite: 6.0,
        next_composite: 7.0,
        delta_composite: 1.0,
      },
      category_deltas: []
    };

    render(
      <ThemeProvider>
        <TurningPointsList moments={[belowThresholdMoment] as any} lang="fr" />
      </ThemeProvider>
    );

    expect(screen.getByText(/Mouvement global en hausse \(léger\)/i)).toBeInTheDocument();
    // Ensure no category icons/text from deltas section
    expect(screen.queryByText(/progression sur/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/recul sur/i)).not.toBeInTheDocument();
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

    expect(screen.getByText("Les priorités du moment se réorganisent")).toBeInTheDocument();
  });

  it("gère la transition vers le calme (next_categories vide)", () => {
    render(
      <ThemeProvider>
        <TurningPointsList moments={[mockEnrichedMoments[2]] as any} lang="fr" />
      </ThemeProvider>
    );

    expect(screen.getByText(/laisse place à un climat plus calme/i)).toBeInTheDocument();
  });

  it("explicite l'entrée d'un nouveau thème sans driver principal", () => {
    const enteringMoment = {
      occurred_at_local: "2026-03-12T08:45:00",
      severity: 0.5,
      summary: null,
      change_type: "emergence",
      previous_categories: ["health", "money"],
      next_categories: ["health", "money", "work"],
      impacted_categories: ["health", "money", "work"],
      primary_driver: null,
      drivers: [],
    };

    render(
      <ThemeProvider>
        <TurningPointsList moments={[enteringMoment] as any} lang="fr" />
      </ThemeProvider>
    );

    expect(screen.getByText("Une nouvelle priorité entre au premier plan")).toBeInTheDocument();
    expect(
      screen.getByText(/travail rejoint santé & hygiène de vie et argent & ressources au premier plan/i),
    ).toBeInTheDocument();
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
