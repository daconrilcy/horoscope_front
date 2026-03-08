import { describe, expect, it } from "vitest";

import { getCategoryMeta, getNoteBand } from "../utils/predictionBands";

describe("predictionBands", () => {
  it("respecte les seuils de note definis par la story", () => {
    expect(getNoteBand(5, "fr")).toEqual({
      key: "fragile",
      label: "Fragile",
      colorVar: "var(--danger)",
    });
    expect(getNoteBand(9, "fr")).toEqual({
      key: "tense",
      label: "Tendu",
      colorVar: "var(--warning)",
    });
    expect(getNoteBand(12, "fr")).toEqual({
      key: "neutral",
      label: "Neutre",
      colorVar: "var(--text-2)",
    });
    expect(getNoteBand(16, "fr")).toEqual({
      key: "favorable",
      label: "Porteur",
      colorVar: "var(--success)",
    });
    expect(getNoteBand(20, "fr")).toEqual({
      key: "very_favorable",
      label: "Très favorable",
      colorVar: "var(--primary)",
    });
  });

  it("normalise les anciennes categories FR vers les codes canoniques", () => {
    expect(getCategoryMeta("travail", "en")).toEqual({
      label: "Work",
      icon: "💼",
    });
  });

  it("conserve un libelle exploitable pour les categories inconnues", () => {
    expect(getCategoryMeta("career_luck", "fr")).toEqual({
      label: "Career Luck",
      icon: "✨",
    });
  });
});
