import React from "react";
import type { DailyPredictionTimeBlock } from "../../types/dailyPrediction";
import { CATEGORY_META } from "../../utils/predictionBands";

interface Props {
  timeline: DailyPredictionTimeBlock[];
}

export const DayTimeline: React.FC<Props> = ({ timeline }) => {
  const formatTime = (iso: string) => {
    return new Date(iso).toLocaleTimeString("fr-FR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div style={{ marginBottom: "2rem" }}>
      <h3 style={{ marginBottom: "1rem", color: "var(--text-1)" }}>Chronologie du jour</h3>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {timeline.map((block, idx) => {
          const isPivot = block.turning_point;
          
          return (
            <div 
              key={idx} 
              className="panel" 
              style={{ 
                padding: "0.75rem 1rem",
                display: "flex",
                alignItems: "center",
                gap: "1rem",
                borderLeft: isPivot ? "4px solid var(--primary)" : "4px solid transparent",
                backgroundColor: isPivot ? "rgba(255, 255, 255, 0.08)" : undefined
              }}
            >
              <div style={{ 
                minWidth: "80px", 
                fontSize: "0.875rem", 
                color: "var(--text-3)",
                fontWeight: "bold"
              }}>
                {formatTime(block.start_local)}
              </div>
              
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <span style={{ fontSize: "1rem", fontWeight: "500" }}>{block.summary}</span>
                  {isPivot && (
                    <span style={{ 
                      fontSize: "0.7rem", 
                      backgroundColor: "var(--primary)", 
                      color: "white", 
                      padding: "0.1rem 0.4rem", 
                      borderRadius: "4px",
                      textTransform: "uppercase"
                    }}>
                      Pivot
                    </span>
                  )}
                </div>
                <div style={{ display: "flex", gap: "0.4rem", marginTop: "0.25rem" }}>
                  {block.dominant_categories.map(cat => (
                    <span key={cat} title={CATEGORY_META[cat]?.label}>
                      {CATEGORY_META[cat]?.icon || "✨"}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
