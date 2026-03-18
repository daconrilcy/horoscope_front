import React from "react";
import { ArrowRightLeft } from "lucide-react";

import type { Lang } from "../../i18n/predictions";
import type { DailyAgendaSlot } from "../../utils/dailyAstrology";
import { getCategoryMeta, getPredictionMessage } from "../../utils/predictionI18n";
import "./DayAgenda.css";

interface Props {
  slots: DailyAgendaSlot[];
  lang: Lang;
}


export const DayAgenda: React.FC<Props> = ({ slots, lang }) => {
  return (
    <div className="day-agenda">
      <h3 className="day-agenda__title">
        {getPredictionMessage("decision_windows_title", lang)}
      </h3>

      <div className="agenda-grid gap-4">
        {slots.map((slot) => {
          const slotContent = (
            <>
              <span className="agenda-slot__label">{slot.label}</span>

              {slot.topCategories.length > 0 ? (
                <>
                  <div className="agenda-slot__categories mt-4">
                    {slot.topCategories.map((category) => {
                      const meta = getCategoryMeta(category, lang);
                      return (
                        <span key={category} title={meta.label} className="agenda-slot__category-icon">
                          {meta.icon}
                        </span>
                      );
                    })}
                  </div>

                  <div className="agenda-slot__category-labels">
                    {slot.topCategories.map((category) => (
                      <span key={category} className="agenda-slot__category-label">
                        {getCategoryMeta(category, lang).label}
                      </span>
                    ))}
                  </div>
                </>
              ) : (
                <span className="agenda-slot__empty mt-4">
                  {getPredictionMessage("no_major_aspect", lang)}
                </span>
              )}
            </>
          );

          if (!slot.hasTurningPoint) {
            return (
              <div
                key={slot.label}
                className="panel agenda-slot p-4"
                data-testid="agenda-slot"
                data-slot-label={slot.label}
              >
                {slotContent}
              </div>
            );
          }

          /* Pivot slot: shift-marker sorti du slot pour passer au-dessus de la corona */
          return (
            <div key={slot.label} className="pivot-corona-wrapper" data-testid="agenda-slot-pivot">
              <div
                className="panel agenda-slot agenda-slot--pivot p-4"
                data-testid="agenda-slot"
                data-slot-label={slot.label}
              >
                {slotContent}
              </div>
              <div
                className="agenda-slot__shift-marker"
                data-testid="agenda-slot-shift-marker"
                aria-label={getPredictionMessage("pivot_badge", lang)}
                title={getPredictionMessage("pivot_badge", lang)}
              >
                <ArrowRightLeft size={14} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
