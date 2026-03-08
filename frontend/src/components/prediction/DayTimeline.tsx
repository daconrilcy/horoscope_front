import React from "react";
import type { DailyPredictionTimeBlock } from "../../types/dailyPrediction";
import type { Lang } from "../../i18n/predictions";
import { getLocale } from "../../utils/locale";
import {
  buildTimelineFallbackSummary,
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
  const condensedTimeline = condenseTimeline(timeline);

  const formatTime = (iso: string) => {
    return new Date(iso).toLocaleTimeString(locale, {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <div style={{ marginBottom: "2rem" }}>
      <h3
        style={{ marginBottom: "1rem", color: "var(--text-1)", cursor: onTimelineClick ? "pointer" : "default" }}
        onClick={onTimelineClick}
      >
        {getPredictionMessage("timeline", lang)}
      </h3>
      <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        {condensedTimeline.map((block, idx) => {
          const isPivot = block.turning_point;
          const label = block.summary || buildTimelineFallbackSummary(block.dominant_categories, block.tone_code, lang);
          const timeLabel = `${formatTime(block.start_local)} - ${formatTime(block.end_local)}`;
          
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
                {timeLabel}
              </div>
              
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                  <span style={{ fontSize: "1rem", fontWeight: "500" }}>{label}</span>
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

function condenseTimeline(timeline: DailyPredictionTimeBlock[]): DailyPredictionTimeBlock[] {
  if (timeline.length <= 1) {
    return timeline;
  }

  const condensed: DailyPredictionTimeBlock[] = [];

  for (const block of timeline) {
    const previous = condensed[condensed.length - 1];
    if (
      previous &&
      !previous.turning_point &&
      !block.turning_point &&
      previous.tone_code === block.tone_code &&
      previous.summary === block.summary &&
      previous.dominant_categories.join("|") === block.dominant_categories.join("|")
    ) {
      previous.end_local = block.end_local;
      continue;
    }

    condensed.push({ ...block });
  }

  return condensed;
}
