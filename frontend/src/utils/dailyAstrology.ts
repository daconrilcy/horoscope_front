import type {
  DailyPredictionCategory,
  DailyPredictionDecisionWindow,
  DailyPredictionTimeBlock,
} from "../types/dailyPrediction";

export interface DailyAgendaSlot {
  label: string;
  topCategories: string[];
  hasTurningPoint: boolean;
}

export interface DailyKeyMoment {
  occurredAtLocal: string;
  impactedCategories: string[];
  previousCategories: string[];
  nextCategories: string[];
}

interface TimeRange {
  start_local: string;
  end_local: string;
  dominant_categories: string[];
  weight: number;
}

interface ParsedDateTime {
  date: string;
  minutes: number;
}

const SLOT_COUNT = 12;
const SLOT_DURATION_MINUTES = 120;

function parseLocalDateTimeParts(iso: string): ParsedDateTime | null {
  const match = iso.match(/^(\d{4}-\d{2}-\d{2})T(\d{2}):(\d{2})/);
  if (!match) {
    return null;
  }

  const [, date, hour, minute] = match;
  return {
    date,
    minutes: Number(hour) * 60 + Number(minute),
  };
}

function getRangeOverlap(
  range: Pick<TimeRange, "start_local" | "end_local">,
  startMinute: number,
  endMinute: number,
  dateContext: string,
): number {
  const start = parseLocalDateTimeParts(range.start_local);
  const end = parseLocalDateTimeParts(range.end_local);
  if (!start || !end) {
    return 0;
  }

  const rangeStartMinute = start.date === dateContext ? start.minutes : 0;
  const rangeEndMinute = end.date === dateContext ? end.minutes : 24 * 60;

  if (start.date !== dateContext && end.date !== dateContext) {
    return 0;
  }

  return Math.max(0, Math.min(rangeEndMinute, endMinute) - Math.max(rangeStartMinute, startMinute));
}

function buildMajorAspectRanges(
  decisionWindows: DailyPredictionDecisionWindow[] | null | undefined,
  timeline: DailyPredictionTimeBlock[],
  categories: DailyPredictionCategory[],
): TimeRange[] {
  const categoryNoteByCode = new Map(categories.map((category) => [category.code, category.note_20]));
  const majorThreshold = 7;

  const rangesFromWindows = (decisionWindows ?? [])
    .filter((window) => window.window_type !== "pivot")
    .map((window) => ({
      start_local: window.start_local,
      end_local: window.end_local,
      dominant_categories: window.dominant_categories.filter(
        (code) => (categoryNoteByCode.get(code) ?? 10) > majorThreshold,
      ),
      weight: window.window_type === "favorable" ? 2 : 1,
    }))
    .filter((window) => window.dominant_categories.length > 0);

  if (rangesFromWindows.length > 0) {
    return rangesFromWindows;
  }

  return timeline
    .filter((block) => !["neutral", "steady"].includes(block.tone_code))
    .map((block) => ({
      start_local: block.start_local,
      end_local: block.end_local,
      dominant_categories: block.dominant_categories.filter(
        (code) => (categoryNoteByCode.get(code) ?? 10) > majorThreshold,
      ),
      weight: 1,
    }))
    .filter((block) => block.dominant_categories.length > 0);
}

function getTopCategoriesForInterval(
  ranges: TimeRange[],
  startMinute: number,
  endMinute: number,
  dateContext: string,
): string[] {
  const categoriesByWeight = new Map<string, number>();

  for (const range of ranges) {
    const overlap = getRangeOverlap(range, startMinute, endMinute, dateContext);
    if (overlap <= 0) {
      continue;
    }

    for (const category of range.dominant_categories) {
      categoriesByWeight.set(category, (categoriesByWeight.get(category) ?? 0) + overlap * range.weight);
    }
  }

  return Array.from(categoriesByWeight.entries())
    .sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))
    .slice(0, 3)
    .map(([category]) => category);
}

function hasTurningPointInSlot(
  ranges: TimeRange[],
  slotStartMinute: number,
  slotEndMinute: number,
  dateContext: string,
): boolean {
  return ranges.some((range) => {
    const start = parseLocalDateTimeParts(range.start_local);
    const end = parseLocalDateTimeParts(range.end_local);
    if (!start || !end) {
      return false;
    }

    const boundaryMinutes = [start, end]
      .filter((point) => point.date === dateContext)
      .map((point) => point.minutes);

    return boundaryMinutes.some(
      (boundaryMinute) => boundaryMinute >= slotStartMinute && boundaryMinute < slotEndMinute,
    );
  });
}

function categoriesEqual(left: string[], right: string[]): boolean {
  return left.length === right.length && left.every((category, index) => category === right[index]);
}

function buildLocalIso(dateContext: string, minutes: number): string {
  const boundedMinutes = Math.max(0, Math.min(minutes, 24 * 60));
  const hour = Math.floor(boundedMinutes / 60) % 24;
  const minute = boundedMinutes % 60;
  return `${dateContext}T${String(hour).padStart(2, "0")}:${String(minute).padStart(2, "0")}:00`;
}

export function buildDailyAgendaSlots(
  dateContext: string,
  decisionWindows: DailyPredictionDecisionWindow[] | null | undefined,
  timeline: DailyPredictionTimeBlock[],
  categories: DailyPredictionCategory[],
): DailyAgendaSlot[] {
  const ranges = buildMajorAspectRanges(decisionWindows, timeline, categories);

  return Array.from({ length: SLOT_COUNT }, (_, index) => {
    const startMinute = index * SLOT_DURATION_MINUTES;
    const endMinute = startMinute + SLOT_DURATION_MINUTES;
    const topCategories = getTopCategoriesForInterval(ranges, startMinute, endMinute, dateContext);

    return {
      label: `${String(index * 2).padStart(2, "0")}:00`,
      topCategories,
      hasTurningPoint: hasTurningPointInSlot(ranges, startMinute, endMinute, dateContext),
    };
  });
}

export function buildDailyKeyMoments(
  dateContext: string,
  decisionWindows: DailyPredictionDecisionWindow[] | null | undefined,
  timeline: DailyPredictionTimeBlock[],
  categories: DailyPredictionCategory[],
): DailyKeyMoment[] {
  const ranges = buildMajorAspectRanges(decisionWindows, timeline, categories);
  const boundaryMinutes = Array.from(
    new Set(
      ranges.flatMap((range) => {
        const start = parseLocalDateTimeParts(range.start_local);
        const end = parseLocalDateTimeParts(range.end_local);
        return [start, end]
          .filter((point): point is ParsedDateTime => point !== null && point.date === dateContext)
          .map((point) => point.minutes);
      }),
    ),
  ).sort((left, right) => left - right);

  const moments: DailyKeyMoment[] = [];
  for (const minute of boundaryMinutes) {
    const previousCategories = getTopCategoriesForInterval(ranges, Math.max(0, minute - 1), minute, dateContext);
    const nextCategories = getTopCategoriesForInterval(ranges, minute, Math.min(24 * 60, minute + 1), dateContext);

    if (categoriesEqual(previousCategories, nextCategories)) {
      continue;
    }

    const impactedCategories = nextCategories.length > 0 ? nextCategories : previousCategories;
    moments.push({
      occurredAtLocal: buildLocalIso(dateContext, minute),
      impactedCategories,
      previousCategories,
      nextCategories,
    });
  }

  return moments;
}
