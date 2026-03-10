import React from "react";
import { Zap } from "lucide-react";

import type { DailyPredictionTimeBlock, DailyPredictionTurningPoint } from "../../types/dailyPrediction";
import type { Lang } from "../../i18n/predictions";
import { getCategoryMeta, getPredictionMessage } from "../../utils/predictionI18n";

interface Props {
  timeline: DailyPredictionTimeBlock[];
  turningPoints: DailyPredictionTurningPoint[];
  dateContext: string; // YYYY-MM-DD in prediction local timezone
  lang: Lang;
}

interface AgendaSlot {
  startMinute: number;
  endMinute: number;
  label: string;
}

const AGENDA_SLOTS: AgendaSlot[] = Array.from({ length: 12 }, (_, index) => {
  const startHour = index * 2;
  const endHour = startHour + 2;

  return {
    startMinute: startHour * 60,
    endMinute: endHour * 60,
    label: `${String(startHour).padStart(2, "0")}:00`,
  };
});

function parseLocalDateTimeParts(iso: string): { date: string; minutes: number } | null {
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

function getBlockOverlapForSlot(
  block: DailyPredictionTimeBlock,
  slot: AgendaSlot,
  dateContext: string,
): number {
  const start = parseLocalDateTimeParts(block.start_local);
  const end = parseLocalDateTimeParts(block.end_local);
  if (!start || !end) {
    return 0;
  }

  const blockStartMinute = start.date === dateContext ? start.minutes : 0;
  const blockEndMinute = end.date === dateContext ? end.minutes : 24 * 60;

  if (start.date !== dateContext && end.date !== dateContext) {
    return 0;
  }

  return Math.max(0, Math.min(blockEndMinute, slot.endMinute) - Math.max(blockStartMinute, slot.startMinute));
}

function hasTurningPointInSlot(
  turningPoints: DailyPredictionTurningPoint[],
  slot: AgendaSlot,
  dateContext: string,
): boolean {
  return turningPoints.some((turningPoint) => {
    const parsed = parseLocalDateTimeParts(turningPoint.occurred_at_local);
    return (
      parsed !== null &&
      parsed.date === dateContext &&
      parsed.minutes >= slot.startMinute &&
      parsed.minutes < slot.endMinute
    );
  });
}

function getTopCategoriesForSlot(
  timeline: DailyPredictionTimeBlock[],
  slot: AgendaSlot,
  dateContext: string,
): string[] {
  const categoriesByWeight = new Map<string, number>();

  for (const block of timeline) {
    const overlap = getBlockOverlapForSlot(block, slot, dateContext);
    if (overlap <= 0) {
      continue;
    }

    for (const category of block.dominant_categories) {
      categoriesByWeight.set(category, (categoriesByWeight.get(category) ?? 0) + overlap);
    }
  }

  return Array.from(categoriesByWeight.entries())
    .sort((left, right) => right[1] - left[1] || left[0].localeCompare(right[0]))
    .slice(0, 3)
    .map(([category]) => category);
}

export const DayAgenda: React.FC<Props> = ({ timeline, turningPoints, dateContext, lang }) => {
  return (
    <div style={{ marginBottom: "2.5rem" }}>
      <h3 style={{ marginBottom: "1.25rem", color: "var(--text-1)", fontWeight: "600" }}>
        {getPredictionMessage("decision_windows_title", lang)}
      </h3>

      <div
        className="agenda-grid"
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
          gap: "0.75rem",
        }}
      >
        {AGENDA_SLOTS.map((slot) => {
          const topCategories = getTopCategoriesForSlot(timeline, slot, dateContext);
          const hasTurningPoint = hasTurningPointInSlot(turningPoints, slot, dateContext);

          return (
            <div
              key={slot.label}
              className="panel"
              data-testid="agenda-slot"
              data-slot-label={slot.label}
              style={{
                padding: "0.75rem",
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
                gap: "0.5rem",
                position: "relative",
                border: hasTurningPoint ? "1px solid var(--primary)" : "1px solid rgba(255,255,255,0.05)",
                backgroundColor: hasTurningPoint ? "rgba(var(--primary-rgb), 0.05)" : undefined,
                minHeight: "100px",
                justifyContent: "center",
              }}
            >
              <span
                style={{
                  fontSize: "0.75rem",
                  color: "var(--text-3)",
                  fontWeight: "bold",
                  position: "absolute",
                  top: "0.5rem",
                  left: "0.5rem",
                }}
              >
                {slot.label}
              </span>

              {hasTurningPoint && (
                <div
                  data-testid="agenda-slot-pivot"
                  style={{
                    position: "absolute",
                    top: "0.4rem",
                    right: "0.4rem",
                    color: "var(--primary)",
                  }}
                  title={getPredictionMessage("pivot_badge", lang)}
                >
                  <Zap size={14} fill="currentColor" />
                </div>
              )}

              <div
                style={{
                  display: "flex",
                  gap: "0.3rem",
                  marginTop: "1rem",
                  flexWrap: "wrap",
                  justifyContent: "center",
                }}
              >
                {topCategories.map((category) => {
                  const meta = getCategoryMeta(category, lang);
                  return (
                    <span key={category} title={meta.label} style={{ fontSize: "1.25rem" }}>
                      {meta.icon}
                    </span>
                  );
                })}
              </div>

              {topCategories.length > 0 && (
                <span
                  style={{
                    fontSize: "0.65rem",
                    color: "var(--text-2)",
                    textAlign: "center",
                    display: "-webkit-box",
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden",
                    lineHeight: "1.2",
                  }}
                >
                  {getCategoryMeta(topCategories[0], lang).label}
                </span>
              )}
            </div>
          );
        })}
      </div>

      <style
        dangerouslySetInnerHTML={{
          __html: `
            @media (min-width: 768px) {
              .agenda-grid {
                grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
              }
            }
          `,
        }}
      />
    </div>
  );
};
