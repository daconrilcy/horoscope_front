import { describe, expect, it } from "vitest";

import { humanizePredictionDriverLabel, humanizeTurningPointSemantic } from "../utils/predictionI18n";

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
});
