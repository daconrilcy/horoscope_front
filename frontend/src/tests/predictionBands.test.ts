import { describe, expect, it } from "vitest";

import { getCategoryMeta, getNoteBand } from "../utils/predictionBands";

describe("predictionBands", () => {
  it("respecte les seuils de note definis par la story", () => {
    expect(getNoteBand(5)).toEqual({ label: "fragile", colorVar: "var(--danger)" });
    expect(getNoteBand(9)).toEqual({ label: "tendu", colorVar: "var(--warning)" });
    expect(getNoteBand(12)).toEqual({ label: "neutre", colorVar: "var(--text-2)" });
    expect(getNoteBand(16)).toEqual({ label: "porteur", colorVar: "var(--success)" });
    expect(getNoteBand(20)).toEqual({ label: "très favorable", colorVar: "var(--primary)" });
  });

  it("conserve un libelle exploitable pour les categories inconnues", () => {
    expect(getCategoryMeta("career_luck")).toEqual({
      label: "Career Luck",
      icon: "✨",
    });
  });
});
