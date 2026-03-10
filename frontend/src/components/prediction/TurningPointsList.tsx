import React from "react";
import type { DailyPredictionTurningPoint, DailyPredictionTimeBlock } from "../../types/dailyPrediction";
import type { Lang } from "../../i18n/predictions";
import { getLocale } from "../../utils/locale";
import {
  getCategoryMeta,
  getPivotSeverityLabel,
  getPredictionMessage,
  humanizePredictionDriverLabel,
  humanizeTurningPointSummary,
} from "../../utils/predictionI18n";

interface Props {
  turningPoints: DailyPredictionTurningPoint[];
  timeline?: DailyPredictionTimeBlock[];
  lang: Lang;
  onTurningPointClick?: (severity: number) => void;
}

export const TurningPointsList: React.FC<Props> = ({ turningPoints, timeline, lang, onTurningPointClick }) => {
  if (!turningPoints || turningPoints.length === 0) return null;

  const locale = getLocale(lang);

  const getWindowLabel = (iso: string) => {
    const date = new Date(iso);
    const start = new Date(date.getTime() - 15 * 60000);
    const end = new Date(date.getTime() + 15 * 60000);
    
    const fmt = (d: Date) => d.toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" });
    return `${fmt(start)} – ${fmt(end)}`;
  };

  const getImpactedCategories = (tp: DailyPredictionTurningPoint) => {
    if (!timeline) return [];
    
    // Find the block that starts exactly at this time or contains it
    const tpTime = new Date(tp.occurred_at_local).getTime();
    const block = timeline.find(b => {
      const bStart = new Date(b.start_local).getTime();
      const bEnd = new Date(b.end_local).getTime();
      return tpTime >= bStart && tpTime < bEnd;
    });

    return block?.dominant_categories || [];
  };

  return (
    <div style={{ marginBottom: "2rem" }}>
      <h3 style={{ marginBottom: "1rem", color: "var(--text-1)" }}>{getPredictionMessage("turning_points", lang)}</h3>
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {turningPoints.map((tp, idx) => {
          const impacted = getImpactedCategories(tp);
          
          return (
            <div 
              key={idx} 
              className="panel" 
              onClick={() => onTurningPointClick?.(Number(tp.severity))}
              style={{ 
                padding: "1rem",
                border: "1px solid var(--primary)",
                position: "relative",
                overflow: "hidden",
                cursor: onTurningPointClick ? "pointer" : "default"
              }}
            >
              <div style={{ 
                position: "absolute", 
                top: 0, 
                left: 0, 
                width: "4px", 
                height: "100%", 
                backgroundColor: "var(--primary)" 
              }} />
              
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "baseline", marginBottom: "0.5rem" }}>
                <span style={{ fontSize: "1.1rem", fontWeight: "bold", color: "var(--primary)" }}>
                  {getWindowLabel(tp.occurred_at_local)}
                </span>
                <span style={{ fontSize: "0.8rem", color: "var(--text-3)", textTransform: "uppercase" }}>
                  {getPredictionMessage("intensity", lang)} : {getPivotSeverityLabel(Number(tp.severity), lang)}
                </span>
              </div>
              
              <p style={{ margin: "0 0 0.75rem 0", fontSize: "1rem", lineHeight: "1.5", color: "var(--text-1)" }}>
                {humanizeTurningPointSummary(tp.summary, lang)}
              </p>

              {impacted.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginBottom: "0.75rem", alignItems: "center" }}>
                  <span style={{ fontSize: "0.7rem", color: "var(--text-3)", textTransform: "uppercase", fontWeight: "bold" }}>
                    {getPredictionMessage("impacts_label", lang)}
                  </span>
                  {impacted.slice(0, 3).map((cat) => {
                    const meta = getCategoryMeta(cat, lang);
                    return (
                      <span key={cat} title={meta.label} style={{ fontSize: "0.8rem" }}>
                        {meta.icon} {meta.label}
                      </span>
                    );
                  })}
                </div>
              )}
              
              {tp.drivers && tp.drivers.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}>
                  {tp.drivers.map((driver, dIdx) => (
                    <span key={dIdx} style={{ 
                      fontSize: "0.75rem", 
                      color: "var(--text-2)", 
                      backgroundColor: "rgba(255, 255, 255, 0.05)",
                      padding: "0.2rem 0.5rem",
                      borderRadius: "4px"
                    }}>
                      {humanizePredictionDriverLabel(driver, lang)}
                    </span>
                  ))}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
