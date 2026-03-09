import React from "react";
import type { DailyPredictionDecisionWindow } from "../../types/dailyPrediction";
import type { Lang } from "../../i18n/predictions";
import { getLocale } from "../../utils/locale";
import { getCategoryMeta, getPredictionMessage } from "../../utils/predictionI18n";

interface Props {
  windows: DailyPredictionDecisionWindow[];
  lang: Lang;
}

const WINDOW_TYPE_CONFIG: Record<string, { 
  colorClass: string; 
  bgClass: string; 
  borderClass: string;
  priority: number;
}> = {
  pivot: {
    colorClass: "text-primary",
    bgClass: "bg-primary/10",
    borderClass: "border-primary/30",
    priority: 3, // Highest priority
  },
  prudence: {
    colorClass: "text-warning",
    bgClass: "bg-warning/10",
    borderClass: "border-warning/30",
    priority: 2,
  },
  favorable: {
    colorClass: "text-success",
    bgClass: "bg-success/10",
    borderClass: "border-success/30",
    priority: 1,
  },
};

export const DecisionWindowsSection: React.FC<Props> = ({ windows, lang }) => {
  if (!windows || windows.length === 0) return null;

  const locale = getLocale(lang);

  // AC - Priority Sorting: we want to make sure the most important or intense windows
  // are shown if we have to slice. We sort by type priority then by intensity.
  const displayed = [...windows]
    .sort((a, b) => {
      const pA = WINDOW_TYPE_CONFIG[a.window_type]?.priority ?? 0;
      const pB = WINDOW_TYPE_CONFIG[b.window_type]?.priority ?? 0;
      if (pA !== pB) return pB - pA;
      return (b.score * b.confidence) - (a.score * a.confidence);
    })
    .slice(0, 6)
    // Re-sort chronologically for the final display
    .sort((a, b) => a.start_local.localeCompare(b.start_local));

  const formatTime = (iso: string) =>
    new Date(iso).toLocaleTimeString(locale, { hour: "2-digit", minute: "2-digit" });

  return (
    <div className="mb-8">
      <h3 className="mb-4 text-text-1 font-semibold">
        {getPredictionMessage("decision_windows_title", lang)}
      </h3>
      <div className="flex flex-col gap-3">
        {displayed.map((win, idx) => {
          const config = WINDOW_TYPE_CONFIG[win.window_type] ?? WINDOW_TYPE_CONFIG.pivot;
          const typeLabel = getPredictionMessage(`window_type_${win.window_type}`, lang);
          const messageKey = `window_msg_${win.window_type}`;
          const message = getPredictionMessage(messageKey, lang);

          return (
            <div
              key={idx}
              className={`panel p-4 border-l-4 ${config.bgClass} ${config.borderClass} border-l-current ${config.colorClass}`}
            >
              <div className="flex items-center gap-3 mb-2">
                <span className="text-sm font-bold text-text-3 min-w-[80px]">
                  {formatTime(win.start_local)} – {formatTime(win.end_local)}
                </span>
                <span className={`text-[0.7rem] font-bold px-2 py-0.5 rounded border ${config.bgClass} ${config.borderClass} uppercase tracking-wider`}>
                  {typeLabel}
                </span>
              </div>

              <p className="m-0 mb-2 text-sm text-text-1 leading-relaxed">
                {message}
              </p>

              {win.dominant_categories.length > 0 && (
                <div className="flex gap-2 flex-wrap mt-1">
                  {win.dominant_categories.slice(0, 3).map((cat) => {
                    const meta = getCategoryMeta(cat, lang);
                    return (
                      <span
                        key={cat}
                        title={meta.label}
                        className="text-[0.85rem] flex items-center gap-1 opacity-90"
                      >
                        {meta.icon} {meta.label}
                      </span>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
