import React from "react";
import type { DailyPredictionCategory } from "../../types/dailyPrediction";
import type { Lang } from "../../i18n/predictions";
import { getNoteBand, getCategoryMeta } from "../../utils/predictionBands";

interface Props {
  categories: DailyPredictionCategory[];
  lang: Lang;
  onCategoryClick?: (code: string) => void;
}

export const CategoryGrid: React.FC<Props> = ({ categories, lang, onCategoryClick }) => {
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
        const band = getNoteBand(cat.note_20, lang);
        const meta = getCategoryMeta(cat.code, lang);
        const shouldShowSummary = Boolean(
          cat.summary &&
            !(cat.note_20 === 10 && cat.power === 0 && cat.volatility === 0 && cat.raw_score === 0),
        );

        return (
          <div 
            key={cat.code} 
            className="panel" 
            onClick={() => onCategoryClick?.(cat.code)}
            style={{ 
              padding: "1rem", 
              display: "flex", 
              flexDirection: "column", 
              alignItems: "center",
              textAlign: "center",
              cursor: onCategoryClick ? "pointer" : "default"
            }}
          >
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
            {shouldShowSummary && (
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
