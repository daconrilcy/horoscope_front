import React from "react";
import type { DailyPredictionTimeBlock } from "../../types/dailyPrediction";
import type { Lang } from "../../i18n/predictions";
import { getLocale } from "../../utils/locale";
import {
  buildTimelineFallbackSummary,
  getCategoryMeta,
  getPredictionMessage,
} from "../../utils/predictionI18n";
import "./DayTimeline.css";

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
    <div className="day-timeline">
      <h3
        className={`day-timeline__title ${onTimelineClick ? "day-timeline__title--clickable" : ""}`}
        onClick={onTimelineClick}
      >
        {getPredictionMessage("timeline", lang)}
      </h3>
      <div className="day-timeline__list">
        {condensedTimeline.map((block, idx) => {
          const isPivot = block.turning_point;
          const label = block.summary || buildTimelineFallbackSummary(block.dominant_categories, block.tone_code, lang);
          const timeLabel = `${formatTime(block.start_local)} - ${formatTime(block.end_local)}`;
          
          return (
            <div 
              key={idx} 
              className={`panel day-timeline__block py-4 px-6 ${isPivot ? "day-timeline__block--pivot" : ""}`}
            >
              <div className="day-timeline__time">
                {timeLabel}
              </div>
              
              <div className="day-timeline__content">
                <div className="day-timeline__label-row">
                  <span className="day-timeline__label">{label}</span>
                  {isPivot && (
                    <span className="day-timeline__badge">
                      {getPredictionMessage("pivot_badge", lang)}
                    </span>
                  )}
                </div>
                <div className="day-timeline__categories">
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
