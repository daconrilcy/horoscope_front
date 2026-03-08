import React from "react";
import type { DailyPredictionResponse } from "../../types/dailyPrediction";
import { TONE_LABELS, TONE_COLORS } from "../../utils/predictionBands";

interface Props {
  prediction: DailyPredictionResponse;
}

export const DayPredictionCard: React.FC<Props> = ({ prediction }) => {
  const { summary, meta } = prediction;
  const toneLabel = summary.overall_tone ? TONE_LABELS[summary.overall_tone] || summary.overall_tone : "Neutre";
  const toneColor = summary.overall_tone ? TONE_COLORS[summary.overall_tone] || "var(--text-2)" : "var(--text-2)";

  // Format date: "8 mars 2026"
  const formattedDate = new Date(meta.date_local).toLocaleDateString("fr-FR", {
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
        {summary.overall_summary || "Calcul de votre tendance en cours..."}
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
            Meilleur créneau
          </h4>
          <div style={{ fontSize: "1rem", fontWeight: "500" }}>
            {new Date(summary.best_window.start_local).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}
            {" - "}
            {new Date(summary.best_window.end_local).toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" })}
          </div>
          <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.875rem", color: "var(--text-2)" }}>
            Dominante : {summary.best_window.dominant_category}
          </p>
        </div>
      )}
    </div>
  );
};
