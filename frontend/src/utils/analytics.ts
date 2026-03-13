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
  CONSULTATION_STARTED: 'consultation_started',
  CONSULTATION_PRECHECK: 'consultation_precheck',
  CONSULTATION_GENERATED: 'consultation_generated',
  CONSULTATION_ERROR: 'consultation_error',
  CONSULTATION_CHAT_OPENED: 'consultation_chat_opened',
} as const;

export type EventName = typeof EVENTS[keyof typeof EVENTS];

export function trackEvent(name: EventName, props: Record<string, unknown> = {}): void {
  // Delegate to window.analytics if present (Segment, custom, etc.)
  if (typeof window !== 'undefined' && (window as any).analytics?.track) {
    (window as any).analytics.track(name, props);
  }

  // console.debug only in development mode
  if (import.meta.env.DEV && import.meta.env.MODE !== 'test') {
    console.debug('[analytics]', name, props);
  }
}
