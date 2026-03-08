// frontend/src/utils/analytics.ts

/**
 * Analytics event tracking utility.
 * Minimal implementation delegating to window.analytics.track if available.
 * AC1, AC3, AC4
 */

export const EVENTS = {
  PREDICTION_VIEWED: 'prediction_viewed',
  CATEGORY_CLICKED: 'category_clicked',
  TIMELINE_OPENED: 'timeline_opened',
  TURNING_POINT_OPENED: 'turning_point_opened',
  PREDICTION_REFRESHED: 'prediction_refreshed',
  HISTORY_VIEWED: 'history_viewed',
} as const;

export function trackEvent(name: string, props: Record<string, unknown> = {}): void {
  // Delegate to window.analytics if present (Segment, custom, etc.)
  if (typeof window !== 'undefined' && (window as any).analytics?.track) {
    (window as any).analytics.track(name, props);
  }

  // console.debug only in development mode
  if (import.meta.env.DEV) {
    console.debug('[analytics]', name, props);
  }
}
