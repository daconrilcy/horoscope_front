import type { DailyPredictionResponse } from '../types/dailyPrediction';

export interface AstroDailyEventsViewData {
  ingresses: { text: string; time: string | null }[];
  aspects: string[];
  planetPositions: string[];
}

export function mapAstroDailyEvents(
  response: DailyPredictionResponse
): AstroDailyEventsViewData | null {
  if (!response.astro_daily_events) return null;

  return {
    ingresses: response.astro_daily_events.ingresses,
    aspects: response.astro_daily_events.aspects,
    planetPositions: response.astro_daily_events.planet_positions || [],
  };
}
