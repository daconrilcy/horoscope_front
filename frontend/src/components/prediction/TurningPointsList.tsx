import React from "react";

import type { Lang } from "../../i18n/predictions";
import type { DailyPredictionTurningPoint } from "../../types/dailyPrediction";
import { getLocale } from "../../utils/locale";
import { 
  getCategoryMeta, 
  getPredictionMessage, 
  humanizePredictionDriverLabel,
  humanizePrimaryDriver,
  humanizeTurningPointSemantic,
  humanizeTurningPointSummary,
  humanizeMovement,
  quantifyMovement,
  humanizeCategoryDelta,
  quantifyCategoryDelta,
} from "../../utils/predictionI18n";
import { TURNING_POINT_LABELS, getLabel } from "../../i18n/predictions";

interface Props {
  moments: DailyPredictionTurningPoint[];
  lang: Lang;
  onTurningPointClick?: (severity: number) => void;
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

  return (
    <div style={{ marginBottom: "2rem" }}>
      <h3 style={{ marginBottom: "1rem", color: "var(--text-1)" }}>
        {getPredictionMessage("turning_points", lang)}
      </h3>
      <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
        {moments.map((moment, index) => {
          const semantic = humanizeTurningPointSemantic(moment, lang);
          const primaryDriver = humanizePrimaryDriver(moment.primary_driver, lang);
          const hasEnrichment = !!moment.change_type;
          const enrichedImpactedCategories =
            moment.impacted_categories?.length
              ? moment.impacted_categories
              : moment.next_categories?.length
                ? moment.next_categories
                : moment.previous_categories || [];
          const hasExplicitDriverLabel = (moment.drivers || []).some((driver) => !!driver.label?.trim());
          const legacyImpactedCategories =
            moment.next_categories?.length
              ? moment.next_categories
              : moment.impacted_categories?.length
                ? moment.impacted_categories
                : moment.previous_categories || [];
          
          return (
            <div
              key={`${moment.occurred_at_local}-${index}`}
              className="panel"
              onClick={() => onTurningPointClick?.(Number(moment.severity) || 0.5)}
              style={{
                padding: "1.25rem",
                border: "1px solid var(--primary)",
                position: "relative",
                overflow: "hidden",
                cursor: onTurningPointClick ? "pointer" : "default",
                backgroundColor: "rgba(var(--primary-rgb), 0.03)"
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
                  marginBottom: "1rem",
                }}
              >
                <span style={{ fontSize: "1.1rem", fontWeight: "bold", color: "var(--primary)" }}>
                  {getWindowLabel(moment.occurred_at_local)}
                </span>
                <span style={{ fontSize: "0.8rem", color: "var(--text-3)", textTransform: "uppercase", fontWeight: "600" }}>
                  {getPredictionMessage("aspect_shift_label", lang)}
                </span>
              </div>

              {hasEnrichment ? (
                <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                  {/* Section 1: Pourquoi ? */}
                  <div>
                    <span style={{ fontSize: "0.7rem", color: "var(--text-3)", textTransform: "uppercase", fontWeight: "bold", display: "block", marginBottom: "0.2rem" }}>
                      {getLabel(TURNING_POINT_LABELS, "why", lang)}
                    </span>
                    <span style={{ fontSize: "1rem", color: "var(--text-1)", fontWeight: "500" }}>
                      {semantic.cause}
                    </span>
                    {primaryDriver?.details && (
                      <p style={{ margin: "0.35rem 0 0 0", fontSize: "0.85rem", lineHeight: "1.4", color: "var(--text-2)" }}>
                        {primaryDriver.details}
                      </p>
                    )}
                  </div>

                  {/* Section 2: Ce qui change */}
                  <div>
                    <span style={{ fontSize: "0.7rem", color: "var(--text-3)", textTransform: "uppercase", fontWeight: "bold", display: "block", marginBottom: "0.4rem" }}>
                      {getLabel(TURNING_POINT_LABELS, "before_after", lang)}
                    </span>
                    <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", flexWrap: "wrap" }}>
                      <div style={{ display: "flex", gap: "0.2rem" }}>
                        {(moment.previous_categories || []).length > 0 ? (
                          moment.previous_categories?.slice(0, 3).map(c => (
                            <span key={c} title={getCategoryMeta(c, lang).label}>{getCategoryMeta(c, lang).icon}</span>
                          ))
                        ) : (
                          <span style={{ fontSize: "0.8rem", color: "var(--text-2)" }}>{getLabel(TURNING_POINT_LABELS, "none", lang)}</span>
                        )}
                      </div>
                      <span style={{ fontSize: "0.8rem", color: "var(--text-3)" }}>→</span>
                      <div style={{ display: "flex", gap: "0.2rem" }}>
                        {(moment.next_categories || []).length > 0 ? (
                          moment.next_categories?.slice(0, 3).map(c => (
                            <span key={c} title={getCategoryMeta(c, lang).label}>{getCategoryMeta(c, lang).icon}</span>
                          ))
                        ) : (
                          <span style={{ fontSize: "0.8rem", color: "var(--text-2)" }}>{getLabel(TURNING_POINT_LABELS, "none", lang)}</span>
                        )}
                      </div>
                      <span style={{ fontSize: "0.9rem", color: "var(--text-1)", marginLeft: "0.25rem" }}>
                        {semantic.title}
                      </span>
                    </div>
                    <p style={{ margin: "0.5rem 0 0 0", fontSize: "0.9rem", lineHeight: "1.4", color: "var(--text-2)" }}>
                      {semantic.transition}
                    </p>
                  </div>

                  {/* Section 3: Mouvement (Story 44.4) */}
                  {moment.movement && (
                    <div>
                      <span style={{ fontSize: "0.7rem", color: "var(--text-3)", textTransform: "uppercase", fontWeight: "bold", display: "block", marginBottom: "0.2rem" }}>
                        {getLabel(TURNING_POINT_LABELS, "global_movement", lang)}
                      </span>
                      <p style={{ margin: 0, fontSize: "0.95rem", color: "var(--text-1)", fontWeight: "500" }}>
                        {humanizeMovement(moment.movement, lang)}
                      </p>
                      <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.85rem", color: "var(--text-2)" }}>
                        {quantifyMovement(moment.movement, lang)}
                      </p>
                      
                      {moment.category_deltas && moment.category_deltas.length > 0 && (
                        <div style={{ marginTop: "0.4rem", display: "flex", flexDirection: "column", gap: "0.2rem" }}>
                          {moment.category_deltas.slice(0, 2).map((delta, i) => (
                            <div key={`${delta.code}-${i}`} style={{ display: "flex", flexDirection: "column", gap: "0.1rem" }}>
                              <span style={{ fontSize: "0.85rem", color: "var(--text-2)" }}>
                                {humanizeCategoryDelta(delta, lang)}
                              </span>
                              <span style={{ fontSize: "0.8rem", color: "var(--text-3)" }}>
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
                    <span style={{ fontSize: "0.7rem", color: "var(--text-3)", textTransform: "uppercase", fontWeight: "bold", display: "block", marginBottom: "0.2rem" }}>
                      {getLabel(TURNING_POINT_LABELS, "implication", lang)}
                    </span>
                    <p style={{ margin: 0, fontSize: "0.95rem", lineHeight: "1.4", color: "var(--text-2)" }}>
                      {semantic.implication}.
                    </p>
                    {enrichedImpactedCategories.length > 0 && (
                      <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", alignItems: "center", marginTop: "0.6rem" }}>
                        <span style={{ fontSize: "0.7rem", color: "var(--text-3)", textTransform: "uppercase", fontWeight: "bold" }}>
                          {getPredictionMessage("impacts_label", lang)}
                        </span>
                        {enrichedImpactedCategories.map((category) => {
                          const meta = getCategoryMeta(category, lang);
                          return (
                            <span key={category} style={{ fontSize: "0.8rem" }}>
                              {meta.icon} {meta.label}
                            </span>
                          );
                        })}
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                /* Fallback Legacy */
                <>
                  <p style={{ margin: "0 0 0.75rem 0", fontSize: "1rem", lineHeight: "1.5", color: "var(--text-1)" }}>
                    {humanizeTurningPointSummary(moment.summary, lang) || getPredictionMessage("aspect_shift_label", lang)}
                  </p>

                  {hasExplicitDriverLabel && (moment.drivers || []).length > 0 && (
                    <div style={{ marginBottom: "0.5rem", fontSize: "0.85rem", color: "var(--text-2)" }}>
                      {humanizePredictionDriverLabel(moment.drivers[0], lang)}
                    </div>
                  )}

                  {legacyImpactedCategories.length > 0 && (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", alignItems: "center" }}>
                      <span style={{ fontSize: "0.7rem", color: "var(--text-3)", textTransform: "uppercase", fontWeight: "bold" }}>
                        {getPredictionMessage("impacts_label", lang)}
                      </span>
                      {legacyImpactedCategories.map((category) => {
                        const meta = getCategoryMeta(category, lang);
                        return (
                          <span key={category} title={meta.label} style={{ fontSize: "0.8rem" }}>
                            {meta.icon} {meta.label}
                          </span>
                        );
                      })}
                    </div>
                  )}
                </>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
