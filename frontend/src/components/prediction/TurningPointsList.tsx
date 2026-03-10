import React from "react";

import type { Lang } from "../../i18n/predictions";
import type { DailyKeyMoment } from "../../utils/dailyAstrology";
import { getLocale } from "../../utils/locale";
import { getCategoryMeta, getPredictionMessage } from "../../utils/predictionI18n";

interface Props {
  moments: DailyKeyMoment[];
  lang: Lang;
  onTurningPointClick?: (severity: number) => void;
}

function formatCategoryList(categories: string[], lang: Lang): string {
  return categories.map((category) => getCategoryMeta(category, lang).label).join(", ");
}

export const TurningPointsList: React.FC<Props> = ({ moments, lang, onTurningPointClick }) => {
  if (!moments || moments.length === 0) {
    return null;
  }

  const locale = getLocale(lang);

  const getWindowLabel = (iso: string) => {
    const date = new Date(iso);
    const start = new Date(date.getTime() - 15 * 60000);
    const end = new Date(date.getTime() + 15 * 60000);

    const format = (value: Date) =>
      value.toLocaleTimeString(locale, {
        hour: "2-digit",
        minute: "2-digit",
      });

    return `${format(start)} – ${format(end)}`;
  };

  const getSummary = (moment: DailyKeyMoment) => {
    const formattedTime = new Date(moment.occurredAtLocal).toLocaleTimeString(locale, {
      hour: "2-digit",
      minute: "2-digit",
    });

    if (moment.previousCategories.length === 0 && moment.nextCategories.length > 0) {
      return `${
        lang === "fr" ? "À" : "At"
      } ${formattedTime}, ${lang === "fr" ? "des aspects majeurs émergent" : "major themes emerge"} : ${formatCategoryList(moment.nextCategories, lang)}.`;
    }

    if (moment.previousCategories.length > 0 && moment.nextCategories.length === 0) {
      return `${
        lang === "fr" ? "À" : "At"
      } ${formattedTime}, ${lang === "fr" ? "les aspects majeurs s'estompent" : "major themes fade"} : ${formatCategoryList(moment.previousCategories, lang)}.`;
    }

    return `${
      lang === "fr" ? "À" : "At"
    } ${formattedTime}, ${
      lang === "fr" ? "les aspects majeurs changent" : "major themes shift"
    } : ${formatCategoryList(moment.nextCategories, lang)}.`;
  };

  return (
    <div style={{ marginBottom: "2rem" }}>
      <h3 style={{ marginBottom: "1rem", color: "var(--text-1)" }}>
        {getPredictionMessage("turning_points", lang)}
      </h3>
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {moments.map((moment, index) => (
          <div
            key={`${moment.occurredAtLocal}-${index}`}
            className="panel"
            onClick={() => onTurningPointClick?.(1)}
            style={{
              padding: "1rem",
              border: "1px solid var(--primary)",
              position: "relative",
              overflow: "hidden",
              cursor: onTurningPointClick ? "pointer" : "default",
            }}
          >
            <div
              style={{
                position: "absolute",
                top: 0,
                left: 0,
                width: "4px",
                height: "100%",
                backgroundColor: "var(--primary)",
              }}
            />

            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "baseline",
                marginBottom: "0.5rem",
              }}
            >
              <span style={{ fontSize: "1.1rem", fontWeight: "bold", color: "var(--primary)" }}>
                {getWindowLabel(moment.occurredAtLocal)}
              </span>
              <span style={{ fontSize: "0.8rem", color: "var(--text-3)", textTransform: "uppercase" }}>
                {getPredictionMessage("aspect_shift_label", lang)}
              </span>
            </div>

            <p style={{ margin: "0 0 0.75rem 0", fontSize: "1rem", lineHeight: "1.5", color: "var(--text-1)" }}>
              {getSummary(moment)}
            </p>

            {moment.impactedCategories.length > 0 && (
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginBottom: "0.25rem", alignItems: "center" }}>
                <span style={{ fontSize: "0.7rem", color: "var(--text-3)", textTransform: "uppercase", fontWeight: "bold" }}>
                  {getPredictionMessage("impacts_label", lang)}
                </span>
                {moment.impactedCategories.map((category) => {
                  const meta = getCategoryMeta(category, lang);
                  return (
                    <span key={category} title={meta.label} style={{ fontSize: "0.8rem" }}>
                      {meta.icon} {meta.label}
                    </span>
                  );
                })}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
