import { describe, expect, it } from "vitest";

import { 
  humanizePredictionDriverLabel, 
  humanizeTurningPointSemantic,
  humanizeMovement,
  humanizeCategoryDelta
} from "../utils/predictionI18n";

const TECHNICAL_DRIVER_CODES = [
  "enter_orb",
  "exit_orb",
  "moon_sign_ingress",
  "asc_sign_change",
  "aspect_enter_orb",
  "aspect_exit_orb",
  "aspect_exact_to_angle",
  "aspect_exact_to_luminary",
  "aspect_exact_to_personal",
] as const;

describe("predictionI18n", () => {
  it("humanise tous les event_type techniques V2 en labels lisibles", () => {
    for (const eventType of TECHNICAL_DRIVER_CODES) {
      const label = humanizePredictionDriverLabel({ event_type: eventType }, "fr");
      expect(label).not.toBe(eventType);
      expect(label).not.toBe("Signal astrologique");
    }
  });

  describe("humanizeTurningPointSemantic", () => {
    it("génère une composition FR complète pour une émergence", () => {
      const res = humanizeTurningPointSemantic({
        change_type: "emergence",
        previous_categories: ["work"],
        next_categories: ["work", "love"],
        primary_driver: { event_type: "aspect_exact_to_personal" }
      }, "fr");

      expect(res.title).toBe("Émergence d'un nouveau climat");
      expect(res.cause).toBe("Résonance avec votre thème natal");
      expect(res.transition).toContain("De travail vers travail et amour");
    });

    it("génère une composition EN complète pour une recomposition", () => {
      const res = humanizeTurningPointSemantic({
        change_type: "recomposition",
        previous_categories: ["work"],
        next_categories: ["love"],
        primary_driver: { event_type: "moon_sign_ingress" }
      }, "en");

      expect(res.title).toBe("Recomposition of energies");
      expect(res.cause).toBe("Moon sign change");
      expect(res.transition).toContain("From work to love");
    });

    it("gère les données manquantes avec des fallbacks", () => {
      const res = humanizeTurningPointSemantic({}, "fr");
      expect(res.title).toBe("Recomposition des énergies");
      expect(res.cause).toBe("Évolution naturelle du cycle");
      expect(res.transition).toBe("De calme vers calme");
    });
  });

  describe("humanizeMovement", () => {
    it("génère un mouvement global en hausse marqué", () => {
      const res = humanizeMovement({ direction: "rising", strength: 8.5, delta_composite: 5.0 }, "fr");
      expect(res).toBe("Mouvement global en hausse (marqué).");
    });

    it("génère un mouvement global en baisse notable (EN)", () => {
      const res = humanizeMovement({ direction: "falling", strength: 4.5, delta_composite: -2.0 }, "en");
      expect(res).toBe("Global movement is falling (notable).");
    });

    it("gère la recomposition sans intensité", () => {
      const res = humanizeMovement({ direction: "recomposition", strength: 1.0, delta_composite: 0.1 }, "fr");
      expect(res).toBe("Mouvement global en mutation.");
    });
  });

  describe("humanizeCategoryDelta", () => {
    it("génère une progression sur une catégorie", () => {
      const res = humanizeCategoryDelta({ code: "love", direction: "up", delta_intensity: 2.0 }, "fr");
      expect(res).toBe("❤️ progression sur amour & relations");
    });

    it("génère un recul sur une catégorie (EN)", () => {
      const res = humanizeCategoryDelta({ code: "work", direction: "down", delta_intensity: 3.0 }, "en");
      expect(res).toBe("💼 Work decrease");
    });
  });
});
