import React from "react";
import type { DailyPredictionCategory } from "../../types/dailyPrediction";
import { getNoteBand, getCategoryMeta } from "../../utils/predictionBands";

interface Props {
  categories: DailyPredictionCategory[];
}

export const CategoryGrid: React.FC<Props> = ({ categories }) => {
  // Sort by rank asc
  const sortedCategories = [...categories].sort((a, b) => a.rank - b.rank);

  return (
    <div style={{ 
      display: "grid", 
      gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", 
      gap: "1rem",
      marginBottom: "2rem" 
    }}>
      {sortedCategories.map((cat) => {
        const band = getNoteBand(cat.note_20);
        const meta = getCategoryMeta(cat.code);

        return (
          <div key={cat.code} className="panel" style={{ 
            padding: "1rem", 
            display: "flex", 
            flexDirection: "column", 
            alignItems: "center",
            textAlign: "center"
          }}>
            <span style={{ fontSize: "1.5rem", marginBottom: "0.5rem" }}>{meta.icon}</span>
            <span style={{ fontSize: "0.8rem", color: "var(--text-3)", textTransform: "uppercase", fontWeight: "bold" }}>
              {meta.label}
            </span>
            <div style={{ 
              fontSize: "1.75rem", 
              fontWeight: "bold", 
              color: band.colorVar,
              margin: "0.25rem 0"
            }}>
              {cat.note_20}
            </div>
            <span style={{ fontSize: "0.75rem", color: band.colorVar, fontWeight: "500" }}>
              {band.label}
            </span>
            {cat.summary && (
              <p style={{ marginTop: "0.75rem", fontSize: "0.8rem", lineHeight: "1.4", color: "var(--text-2)" }}>
                {cat.summary}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
};
