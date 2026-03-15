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
import { SkeletonGroup } from "../ui";
import "./DayPredictionCard.css";

interface Props {
  prediction: DailyPredictionResponse | null;
  lang: Lang;
  isLoading?: boolean;
  isError?: boolean;
  onRetry?: () => void;
  astroBackgroundProps?: {
    sign: ZodiacSign;
    userId: string;
    dayScore: number;
    dateKey: string;
  };
}

export const DayPredictionCard: React.FC<Props> = ({ 
  prediction, 
  lang, 
  isLoading, 
  isError, 
  onRetry,
  astroBackgroundProps 
}) => {
  const locale = getLocale(lang);

  if (isLoading) {
    return (
      <div className="panel day-prediction-card day-prediction-card--loading p-6" aria-busy="true">
        <SkeletonGroup count={3} widths={["40%", "90%", "70%"]} height="1.25rem" />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="panel day-prediction-card day-prediction-card--error p-6" role="status">
        <p>{getPredictionMessage("error", lang)}</p>
        <button type="button" className="mt-4" onClick={onRetry}>
          {getPredictionMessage("retry", lang)}
        </button>
      </div>
    );
  }

  if (!prediction) {
    return (
      <div className="panel day-prediction-card day-prediction-card--empty p-6">
        <p>{getPredictionMessage("empty", lang)}</p>
      </div>
    );
  }

  const { summary, meta } = prediction;
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

  const bodyContent = (
    <div className="day-prediction-card__body">
      <p className="day-prediction-card__summary">
        {summary.overall_summary || getPredictionMessage("pending_summary", lang)}
      </p>

      {meta.is_provisional_calibration && (
        <p className="day-prediction-card__calibration">
          {calibrationMessage}
        </p>
      )}

      {summary.best_window && (
        <div className="day-prediction-card__best-window">
          <h4 className="day-prediction-card__best-window-title">
            {getPredictionMessage("best_window", lang)}
          </h4>
          <div className="day-prediction-card__best-window-time">
            {new Date(summary.best_window.start_local).toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" })}
            {" - "}
            {new Date(summary.best_window.end_local).toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" })}
          </div>
          <p className="day-prediction-card__best-window-desc">
            {getPredictionMessage("dominant", lang)} : {getCategoryLabel(summary.best_window.dominant_category, lang)}
          </p>
        </div>
      )}
    </div>
  );

  const headerContent = (
    <div className="day-prediction-card__header">
      <div>
        <h2 className="day-prediction-card__date">{formattedDate}</h2>
        <span 
          className="day-prediction-card__tone"
          style={isAstro ? undefined : { backgroundColor: toneColor }}
        >
          {toneLabel}
        </span>
      </div>
    </div>
  );

  if (astroBackgroundProps) {
    return (
      <AstroMoodBackground
        className="panel day-prediction-card day-prediction-card--astro"
        sign={astroBackgroundProps.sign}
        userId={astroBackgroundProps.userId}
        dateKey={astroBackgroundProps.dateKey}
        dayScore={astroBackgroundProps.dayScore}
      >
        <div className="day-prediction-card__content-wrapper p-6">
          {headerContent}
          {bodyContent}
        </div>
      </AstroMoodBackground>
    );
  }

  return (
    <div className="panel day-prediction-card p-6">
      {headerContent}
      {bodyContent}
    </div>
  );
};
