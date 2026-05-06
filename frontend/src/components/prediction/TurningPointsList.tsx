// Composant de liste des points de bascule avec styles statiques portes par CSS.
import React from "react";

import type { Lang } from "../../i18n/predictions";
import type { DailyPredictionTurningPoint } from "../../types/dailyPrediction";
import { getLocale } from "../../utils/locale";
import { 
  getCategoryMeta, 
  getPredictionMessage, 
  humanizePrimaryDriver,
  humanizeTurningPointSemantic,
  humanizeMovement,
  quantifyMovement,
  humanizeCategoryDelta,
  quantifyCategoryDelta,
} from "../../utils/predictionI18n";
import { TURNING_POINT_LABELS, getLabel } from "../../i18n/predictions";
import "./TurningPointsList.css";

interface Props {
  moments: DailyPredictionTurningPoint[];
  lang: Lang;
  onTurningPointClick?: (severity: number) => void;
}

export const TurningPointsList: React.FC<Props> = ({ moments, lang, onTurningPointClick }) => {
  const canonicalMoments = moments.filter((moment) => !!moment.change_type);

  if (canonicalMoments.length === 0) {
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

  return (
    <div className="turning-points-list">
      <h3 className="turning-points-list__title">
        {getPredictionMessage("turning_points", lang)}
      </h3>
      <div className="turning-points-list__items">
        {canonicalMoments.map((moment, index) => {
          const semantic = humanizeTurningPointSemantic(moment, lang);
          const primaryDriver = humanizePrimaryDriver(moment.primary_driver, lang);
          const enrichedImpactedCategories =
            moment.impacted_categories?.length
              ? moment.impacted_categories
              : moment.next_categories?.length
                ? moment.next_categories
                : moment.previous_categories || [];
          
          return (
            <div
              key={`${moment.occurred_at_local}-${index}`}
              className={`panel turning-points-list__card${
                onTurningPointClick ? " turning-points-list__card--clickable" : ""
              }`}
              onClick={() => onTurningPointClick?.(Number(moment.severity) || 0.5)}
            >
              <div className="turning-points-list__accent" />

              <div className="turning-points-list__card-header">
                <span className="turning-points-list__time">
                  {getWindowLabel(moment.occurred_at_local)}
                </span>
                <span className="turning-points-list__tag">
                  {getPredictionMessage("aspect_shift_label", lang)}
                </span>
              </div>

              <div className="turning-points-list__enriched">
                  {/* Section 1: Pourquoi ? */}
                  <div>
                    <span className="turning-points-list__eyebrow">
                      {getLabel(TURNING_POINT_LABELS, "why", lang)}
                    </span>
                    <span className="turning-points-list__primary-text">
                      {semantic.cause}
                    </span>
                    {primaryDriver?.details && (
                      <p className="turning-points-list__detail">
                        {primaryDriver.details}
                      </p>
                    )}
                  </div>

                  {/* Section 2: Ce qui change */}
                  <div>
                    <span className="turning-points-list__eyebrow turning-points-list__eyebrow--spaced">
                      {getLabel(TURNING_POINT_LABELS, "before_after", lang)}
                    </span>
                    <div className="turning-points-list__category-row">
                      <div className="turning-points-list__icon-group">
                        {(moment.previous_categories || []).length > 0 ? (
                          moment.previous_categories?.slice(0, 3).map(c => (
                            <span key={c} title={getCategoryMeta(c, lang).label}>{getCategoryMeta(c, lang).icon}</span>
                          ))
                        ) : (
                          <span className="turning-points-list__muted-inline">{getLabel(TURNING_POINT_LABELS, "none", lang)}</span>
                        )}
                      </div>
                      <span className="turning-points-list__arrow">→</span>
                      <div className="turning-points-list__icon-group">
                        {(moment.next_categories || []).length > 0 ? (
                          moment.next_categories?.slice(0, 3).map(c => (
                            <span key={c} title={getCategoryMeta(c, lang).label}>{getCategoryMeta(c, lang).icon}</span>
                          ))
                        ) : (
                          <span className="turning-points-list__muted-inline">{getLabel(TURNING_POINT_LABELS, "none", lang)}</span>
                        )}
                      </div>
                      <span className="turning-points-list__transition-title">
                        {semantic.title}
                      </span>
                    </div>
                    <p className="turning-points-list__transition">
                      {semantic.transition}
                    </p>
                  </div>

                  {/* Section 3: Mouvement (Story 44.4) */}
                  {moment.movement && (
                    <div>
                      <span className="turning-points-list__eyebrow">
                        {getLabel(TURNING_POINT_LABELS, "global_movement", lang)}
                      </span>
                      <p className="turning-points-list__movement">
                        {humanizeMovement(moment.movement, lang)}
                      </p>
                      <p className="turning-points-list__movement-detail">
                        {quantifyMovement(moment.movement, lang)}
                      </p>
                      
                      {moment.category_deltas && moment.category_deltas.length > 0 && (
                        <div className="turning-points-list__delta-list">
                          {moment.category_deltas.slice(0, 2).map((delta, i) => (
                            <div key={`${delta.code}-${i}`} className="turning-points-list__delta">
                              <span className="turning-points-list__delta-label">
                                {humanizeCategoryDelta(delta, lang)}
                              </span>
                              <span className="turning-points-list__delta-value">
                                {quantifyCategoryDelta(delta, lang)}
                              </span>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {/* Section 4: Implication */}
                  <div>
                    <span className="turning-points-list__eyebrow">
                      {getLabel(TURNING_POINT_LABELS, "implication", lang)}
                    </span>
                    <p className="turning-points-list__implication">
                      {semantic.implication}.
                    </p>
                    {enrichedImpactedCategories.length > 0 && (
                      <div className="turning-points-list__impact-row turning-points-list__impact-row--spaced">
                        <span className="turning-points-list__impact-label">
                          {getPredictionMessage("impacts_label", lang)}
                        </span>
                        {enrichedImpactedCategories.map((category) => {
                          const meta = getCategoryMeta(category, lang);
                          return (
                            <span key={category} className="turning-points-list__category-pill">
                              {meta.icon} {meta.label}
                            </span>
                          );
                        })}
                      </div>
                    )}
                  </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
