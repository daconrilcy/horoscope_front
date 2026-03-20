import type { DailyPredictionResponse } from '../types/dailyPrediction';

export interface AstroDailyEventsViewData {
  ingresses: { text: string; time: string | null }[];
  aspects: string[];
  planetPositions: string[];
  returns: string[];
  progressions: string[];
  nodes: string[];
  skyAspects: string[];
  fixedStars: string[];
}

export function mapAstroDailyEvents(
  response: DailyPredictionResponse
): AstroDailyEventsViewData | null {
  if (!response.astro_daily_events) return null;

  return {
    ingresses: response.astro_daily_events.ingresses,
    aspects: response.astro_daily_events.aspects,
    planetPositions: response.astro_daily_events.planet_positions || [],
    returns: response.astro_daily_events.returns || [],
    progressions: response.astro_daily_events.progressions || [],
    nodes: response.astro_daily_events.nodes || [],
    skyAspects: response.astro_daily_events.sky_aspects || [],
    fixedStars: response.astro_daily_events.fixed_stars || [],
  };
}
