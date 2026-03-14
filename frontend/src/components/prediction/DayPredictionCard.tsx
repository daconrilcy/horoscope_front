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

  return (
    <div className="panel hero-card day-prediction-card">
      {astroBackgroundProps ? (
        <div className="day-prediction-card__header-bg-wrapper">
          <AstroMoodBackground
            sign={astroBackgroundProps.sign}
            userId={astroBackgroundProps.userId}
            dateKey={astroBackgroundProps.dateKey}
            dayScore={astroBackgroundProps.dayScore}
          >
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
              <div style={{ position: "relative", zIndex: 10 }}>
                <h2 style={{ margin: 0, fontSize: "1.5rem", color: "white" }}>{formattedDate}</h2>
                <span style={{ 
                  display: "inline-block", 
                  marginTop: "0.5rem",
                  padding: "0.25rem 0.75rem", 
                  borderRadius: "1rem", 
                  backgroundColor: "rgba(255,255,255,0.2)", 
                  color: "white",
                  fontSize: "0.875rem",
                  fontWeight: "bold",
                  backdropFilter: "blur(4px)",
                  WebkitBackdropFilter: "blur(4px)"
                }}>
                  {toneLabel}
                </span>
              </div>
            </div>
          </AstroMoodBackground>
        </div>
      ) : (
        <div className="day-prediction-card__header-fallback">
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
        </div>
      )}

      <div className="day-prediction-card__body">
        <p style={{ fontSize: "1.125rem", lineHeight: "1.6", color: "var(--text-1)" }}>
          {summary.overall_summary || getPredictionMessage("pending_summary", lang)}
        </p>

        {meta.is_provisional_calibration && (
          <p
            style={{
              marginTop: "0.75rem",
              padding: "0.75rem 1rem",
              borderRadius: "0.75rem",
              backgroundColor: "rgba(255, 184, 77, 0.12)",
              border: "1px solid rgba(255, 184, 77, 0.35)",
              color: "var(--text-1)",
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
    </div>
  );
};
