import React from "react";
import type { DailyPredictionResponse } from "../../types/dailyPrediction";
import type { Lang } from "../../i18n/predictions";
import { getLocale } from "../../utils/locale";
import {
  getCategoryLabel,
  getPredictionMessage,
  getToneColor,
  getToneLabel,
} from "../../utils/predictionI18n";

interface Props {
  prediction: DailyPredictionResponse;
  lang: Lang;
}

export const DayPredictionCard: React.FC<Props> = ({ prediction, lang }) => {
  const { summary, meta } = prediction;
  const locale = getLocale(lang);
  const toneLabel = getToneLabel(summary.overall_tone, lang);
  const toneColor = getToneColor(summary.overall_tone);

  const formattedDate = new Date(meta.date_local).toLocaleDateString(locale, {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  return (
    <div className="panel hero-card" style={{ marginBottom: "1.5rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
        <div>
          <h2 style={{ margin: 0, fontSize: "1.5rem" }}>{formattedDate}</h2>
          <span style={{ 
            display: "inline-block", 
            marginTop: "0.5rem",
            padding: "0.25rem 0.75rem", 
            borderRadius: "1rem", 
            backgroundColor: toneColor, 
            color: "white",
            fontSize: "0.875rem",
            fontWeight: "bold"
          }}>
            {toneLabel}
          </span>
        </div>
      </div>

      <p style={{ fontSize: "1.125rem", lineHeight: "1.6", color: "var(--text-1)" }}>
        {summary.overall_summary || getPredictionMessage("pending_summary", lang)}
      </p>

      {summary.best_window && (
        <div style={{ 
          marginTop: "1.5rem", 
          padding: "1rem", 
          borderRadius: "0.75rem", 
          backgroundColor: "rgba(255, 255, 255, 0.05)",
          border: "1px solid rgba(255, 255, 255, 0.1)"
        }}>
          <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.9rem", color: "var(--text-3)", textTransform: "uppercase" }}>
            {getPredictionMessage("best_window", lang)}
          </h4>
          <div style={{ fontSize: "1rem", fontWeight: "500" }}>
            {new Date(summary.best_window.start_local).toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" })}
            {" - "}
            {new Date(summary.best_window.end_local).toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" })}
          </div>
          <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.875rem", color: "var(--text-2)" }}>
            {getPredictionMessage("dominant", lang)} : {getCategoryLabel(summary.best_window.dominant_category, lang)}
          </p>
        </div>
      )}
    </div>
  );
};
