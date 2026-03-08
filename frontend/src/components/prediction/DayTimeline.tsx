import React from "react";
import type { DailyPredictionTimeBlock } from "../../types/dailyPrediction";
import type { Lang } from "../../i18n/predictions";
import { getLocale } from "../../utils/locale";
import {
  getCategoryMeta,
  getPredictionMessage,
} from "../../utils/predictionI18n";

interface Props {
  timeline: DailyPredictionTimeBlock[];
  lang: Lang;
  onTimelineClick?: () => void;
}

export const DayTimeline: React.FC<Props> = ({ timeline, lang, onTimelineClick }) => {
  const locale = getLocale(lang);

  const formatTime = (iso: string) => {
    return new Date(iso).toLocaleTimeString(locale, {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div style={{ marginBottom: "2rem", cursor: onTimelineClick ? "pointer" : "default" }} onClick={onTimelineClick}>
      <h3 style={{ marginBottom: "1rem", color: "var(--text-1)" }}>{getPredictionMessage("timeline", lang)}</h3>
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
                      {getPredictionMessage("pivot_badge", lang)}
                    </span>
                  )}
                </div>
                <div style={{ display: "flex", gap: "0.4rem", marginTop: "0.25rem" }}>
                  {block.dominant_categories.map((cat) => {
                    const meta = getCategoryMeta(cat, lang);
                    return (
                    <span key={cat} title={meta.label}>
                      {meta.icon}
                    </span>
                    );
                  })}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
