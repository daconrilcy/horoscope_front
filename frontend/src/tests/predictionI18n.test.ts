import { describe, expect, it } from "vitest";

import { 
  humanizePredictionDriverLabel, 
  humanizeTurningPointSemantic,
  humanizePrimaryDriver,
  humanizeMovement,
  quantifyMovement,
  humanizeCategoryDelta
  ,
  quantifyCategoryDelta
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
      expect(res.transition).toBe("amour & relations rejoint travail au premier plan.");
      expect(res.implication).toBe(
        "Le climat s'ouvre davantage à amour & relations, aux côtés de travail.",
      );
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
      expect(res.transition).toBe("work gives way to love & relationships.");
      expect(res.implication).toBe(
        "The center of gravity of the day is shifting toward different priorities.",
      );
    });

    it("gère les données manquantes avec des fallbacks", () => {
      const res = humanizeTurningPointSemantic({}, "fr");
      expect(res.title).toBe("Recomposition des énergies");
      expect(res.cause).toBe("Évolution naturelle du cycle");
      expect(res.transition).toBe("De calme vers calme");
    });
  });

  describe("humanizePrimaryDriver", () => {
    it("rend un driver astrologique détaillé en FR", () => {
      const res = humanizePrimaryDriver(
        {
          event_type: "aspect_exact_to_personal",
          body: "Moon",
          target: "Mars",
          aspect: "sextile",
          orb_deg: 0.12,
          phase: "applying",
          metadata: { natal_house_transited: 5, natal_house_target: 8 },
        },
        "fr",
      );

      expect(res?.headline).toBe("Moon sextile Mars");
      expect(res?.details).toBe("Orbe 0,12° · Phase appliquante · Maisons 5 -> 8");
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

  describe("quantifyMovement", () => {
    it("rend une variation chiffrée du mouvement global", () => {
      const res = quantifyMovement(
        { previous_composite: 5, next_composite: 12.5, delta_composite: 7.5 },
        "fr",
      );
      expect(res).toBe("variation globale +7,50 (5,00 -> 12,50)");
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

  describe("quantifyCategoryDelta", () => {
    it("rend les deltas score et intensité", () => {
      const res = quantifyCategoryDelta(
        { delta_score: 2, delta_intensity: 5 },
        "fr",
      );
      expect(res).toBe("delta score +2,00 · delta intensité +5,00");
    });

    it("inclut le delta de rang quand il est disponible", () => {
      const res = quantifyCategoryDelta(
        { delta_score: 0.02, delta_intensity: 0.01, delta_rank: 4 },
        "fr",
      );
      expect(res).toBe("delta rang +4 · delta intensité +0,01");
    });
  });
});
