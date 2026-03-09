import { describe, expect, it } from "vitest";

import { humanizePredictionDriverLabel } from "../utils/predictionI18n";

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
});
