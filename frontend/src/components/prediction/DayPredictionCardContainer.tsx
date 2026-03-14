import React from "react";
import { useDayPrediction } from "../../hooks/useDayPrediction";
import { DayPredictionCard } from "./DayPredictionCard";
import type { ZodiacSign } from "../astro/zodiacPatterns";
import type { Lang } from "../../i18n/predictions";

interface Props {
  date?: string;
  lang: Lang;
  astroBackgroundProps?: {
    sign: ZodiacSign;
    userId: string;
    dayScore: number;
    dateKey: string;
  };
}

/**
 * Container component for DayPredictionCard (Story 55.2).
 * Manages fetching logic via useDayPrediction hook.
 */
export const DayPredictionCardContainer: React.FC<Props> = ({ date, lang, astroBackgroundProps }) => {
  const { prediction, isLoading, isError, refetch } = useDayPrediction(date);

  return (
    <DayPredictionCard
      prediction={prediction}
      lang={lang}
      isLoading={isLoading}
      isError={isError}
      onRetry={refetch}
      astroBackgroundProps={astroBackgroundProps}
    />
  );
};
