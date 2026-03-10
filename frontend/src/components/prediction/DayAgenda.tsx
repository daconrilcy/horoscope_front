import React from "react";
import { Zap } from "lucide-react";

import type { Lang } from "../../i18n/predictions";
import type { DailyAgendaSlot } from "../../utils/dailyAstrology";
import { getCategoryMeta, getPredictionMessage } from "../../utils/predictionI18n";

interface Props {
  slots: DailyAgendaSlot[];
  lang: Lang;
}

export const DayAgenda: React.FC<Props> = ({ slots, lang }) => {
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
        {slots.map((slot) => (
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
              border: slot.hasTurningPoint ? "1px solid var(--primary)" : "1px solid rgba(255,255,255,0.05)",
              backgroundColor: slot.hasTurningPoint ? "rgba(var(--primary-rgb), 0.05)" : undefined,
              minHeight: "120px",
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

            {slot.hasTurningPoint && (
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

            {slot.topCategories.length > 0 ? (
              <>
                <div
                  style={{
                    display: "flex",
                    gap: "0.3rem",
                    marginTop: "1rem",
                    flexWrap: "wrap",
                    justifyContent: "center",
                  }}
                >
                  {slot.topCategories.map((category) => {
                    const meta = getCategoryMeta(category, lang);
                    return (
                      <span key={category} title={meta.label} style={{ fontSize: "1.25rem" }}>
                        {meta.icon}
                      </span>
                    );
                  })}
                </div>

                <div
                  style={{
                    display: "flex",
                    flexDirection: "column",
                    alignItems: "center",
                    gap: "0.15rem",
                  }}
                >
                  {slot.topCategories.map((category) => (
                    <span
                      key={category}
                      style={{
                        fontSize: "0.65rem",
                        color: "var(--text-2)",
                        textAlign: "center",
                        lineHeight: "1.2",
                      }}
                    >
                      {getCategoryMeta(category, lang).label}
                    </span>
                  ))}
                </div>
              </>
            ) : (
              <span
                style={{
                  marginTop: "1rem",
                  fontSize: "0.7rem",
                  color: "var(--text-3)",
                  textAlign: "center",
                  lineHeight: "1.3",
                }}
              >
                {getPredictionMessage("no_major_aspect", lang)}
              </span>
            )}
          </div>
        ))}
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
