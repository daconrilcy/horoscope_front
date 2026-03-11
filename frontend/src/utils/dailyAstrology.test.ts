import { describe, expect, it } from "vitest";

import { buildDailyKeyMoments } from "./dailyAstrology";

describe("dailyAstrology", () => {
  it("keeps late neutral regime shifts while excluding the synthetic midnight boundary", () => {
    const moments = buildDailyKeyMoments(
      "2026-03-11",
      null,
      [
        {
          start_local: "2026-03-11T00:00:00",
          end_local: "2026-03-11T22:45:00",
          tone_code: "neutral",
          dominant_categories: ["health", "social_network", "work"],
          summary: null,
          turning_point: false,
        },
        {
          start_local: "2026-03-11T22:45:00",
          end_local: "2026-03-11T23:45:00",
          tone_code: "neutral",
          dominant_categories: ["health", "social_network", "money"],
          summary: null,
          turning_point: false,
        },
        {
          start_local: "2026-03-11T23:45:00",
          end_local: "2026-03-12T00:00:00",
          tone_code: "neutral",
          dominant_categories: ["health", "social_network", "money"],
          summary: null,
          turning_point: false,
        },
      ],
      [
        { code: "health", note_20: 15, raw_score: 0, power: 0, volatility: 0, rank: 1, summary: null },
        { code: "social_network", note_20: 13, raw_score: 0, power: 0, volatility: 0, rank: 2, summary: null },
        { code: "work", note_20: 13, raw_score: 0, power: 0, volatility: 0, rank: 3, summary: null },
        { code: "money", note_20: 13, raw_score: 0, power: 0, volatility: 0, rank: 4, summary: null },
      ],
    );

    expect(moments).toHaveLength(1);
    expect(moments[0]).toMatchObject({
      occurredAtLocal: "2026-03-11T22:45:00",
      impactedCategories: ["health", "money", "social_network"],
      previousCategories: ["health", "social_network", "work"],
      nextCategories: ["health", "money", "social_network"],
    });
  });
});
