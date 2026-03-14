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

import { AstroMoodBackground } from "../astro/AstroMoodBackground";
import type { ZodiacSign } from "../astro/zodiacPatterns";

interface Props {
  prediction: DailyPredictionResponse;
  lang: Lang;
  astroBackgroundProps?: {
    sign: ZodiacSign;
    userId: string;
    dayScore: number;
    dateKey: string;
  };
}

export const DayPredictionCard: React.FC<Props> = ({ prediction, lang, astroBackgroundProps }) => {
  const { summary, meta } = prediction;
  const locale = getLocale(lang);
  const toneLabel = getToneLabel(summary.overall_tone, lang);
  const toneColor = getToneColor(summary.overall_tone);
  const calibrationMessage =
    summary.calibration_note || getPredictionMessage("provisional_calibration", lang);

  const formattedDate = new Date(meta.date_local).toLocaleDateString(locale, {
    day: "numeric",
    month: "long",
    year: "numeric",
  });

  const isAstro = !!astroBackgroundProps;
  const textColor = isAstro ? "white" : "var(--text-1)";
  const textMuted = isAstro ? "rgba(255, 255, 255, 0.7)" : "var(--text-2)";

  const bodyContent = (
    <div className={`day-prediction-card__body ${isAstro ? 'astro-text' : ''}`} style={{ marginTop: '1.5rem' }}>
      <p style={{ fontSize: "1.125rem", lineHeight: "1.6", color: textColor }}>
        {summary.overall_summary || getPredictionMessage("pending_summary", lang)}
      </p>

      {meta.is_provisional_calibration && (
        <p
          style={{
            marginTop: "0.75rem",
            padding: "0.75rem 1rem",
            borderRadius: "0.75rem",
            backgroundColor: isAstro ? "rgba(255, 255, 255, 0.15)" : "rgba(255, 184, 77, 0.12)",
            border: isAstro ? "1px solid rgba(255, 255, 255, 0.3)" : "1px solid rgba(255, 184, 77, 0.35)",
            color: textColor,
            fontSize: "0.9rem",
          }}
        >
          {calibrationMessage}
        </p>
      )}

      {summary.best_window && (
        <div style={{ 
          marginTop: "1.5rem", 
          padding: "1rem", 
          borderRadius: "0.75rem", 
          backgroundColor: isAstro ? "rgba(255, 255, 255, 0.1)" : "rgba(255, 255, 255, 0.05)",
          border: isAstro ? "1px solid rgba(255, 255, 255, 0.2)" : "1px solid rgba(255, 255, 255, 0.1)"
        }}>
          <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.9rem", color: isAstro ? "rgba(255, 255, 255, 0.85)" : "var(--text-3)", textTransform: "uppercase" }}>
            {getPredictionMessage("best_window", lang)}
          </h4>
          <div style={{ fontSize: "1rem", fontWeight: "500", color: textColor }}>
            {new Date(summary.best_window.start_local).toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" })}
            {" - "}
            {new Date(summary.best_window.end_local).toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" })}
          </div>
          <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.875rem", color: textMuted }}>
            {getPredictionMessage("dominant", lang)} : {getCategoryLabel(summary.best_window.dominant_category, lang)}
          </p>
        </div>
      )}
    </div>
  );

  const headerContent = (
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
      <div>
        <h2 style={{ margin: 0, fontSize: "1.5rem", color: isAstro ? "white" : "inherit" }}>{formattedDate}</h2>
        <span style={{ 
          display: "inline-block", 
          marginTop: "0.5rem",
          padding: "0.25rem 0.75rem", 
          borderRadius: "1rem", 
          backgroundColor: isAstro ? "rgba(255,255,255,0.2)" : toneColor, 
          color: "white",
          fontSize: "0.875rem",
          fontWeight: "bold",
          backdropFilter: isAstro ? "blur(4px)" : "none",
          WebkitBackdropFilter: isAstro ? "blur(4px)" : "none"
        }}>
          {toneLabel}
        </span>
      </div>
    </div>
  );

  if (astroBackgroundProps) {
    return (
      <AstroMoodBackground
        className="panel day-prediction-card"
        sign={astroBackgroundProps.sign}
        userId={astroBackgroundProps.userId}
        dateKey={astroBackgroundProps.dateKey}
        dayScore={astroBackgroundProps.dayScore}
      >
        <div style={{ position: "relative", zIndex: 10, padding: "1.5rem" }}>
          {headerContent}
          {bodyContent}
        </div>
      </AstroMoodBackground>
    );
  }

  return (
    <div className="panel day-prediction-card" style={{ padding: "1.5rem" }}>
      {headerContent}
      {bodyContent}
    </div>
  );
};
