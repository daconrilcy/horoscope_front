import React from "react";
import type { DailyPredictionCategory } from "../../types/dailyPrediction";
import type { Lang } from "../../i18n/predictions";
import { getNoteBand, getCategoryMeta } from "../../utils/predictionBands";
import "./CategoryGrid.css";

interface Props {
  categories: DailyPredictionCategory[];
  lang: Lang;
  onCategoryClick?: (code: string) => void;
}

export const CategoryGrid: React.FC<Props> = ({ categories, lang, onCategoryClick }) => {
  const sortedCategories = [...categories].sort((a, b) => a.rank - b.rank);

  return (
    <div className="category-grid gap-4 mb-8">
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
            className={`panel p-4 category-grid__item ${onCategoryClick ? "category-grid__item--clickable" : ""}`}
            onClick={() => onCategoryClick?.(cat.code)}
          >
            <span className="category-grid__icon mb-2">{meta.icon}</span>
            <span className="category-grid__label text-muted">
              {meta.label}
            </span>
            <div 
              className="category-grid__score"
              style={{ color: band.colorVar }}
            >
              {cat.note_20}
            </div>
            <span 
              className="category-grid__band"
              style={{ color: band.colorVar }}
            >
              {band.label}
            </span>
            {shouldShowSummary && (
              <p className="category-grid__summary mt-4 text-secondary">
                {cat.summary}
              </p>
            )}
          </div>
        );
      })}
    </div>
  );
};
