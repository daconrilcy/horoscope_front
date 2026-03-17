import React from 'react'
import type { DayPeriodKey } from '../../types/dayTimeline'
import './TimelineRail.css'

interface TimelineRailProps {
  selectedPeriod: DayPeriodKey | null
}

/** Position du thumb en % (centre de chaque quart de journée) */
const PERIOD_THUMB_PCT: Record<DayPeriodKey, number> = {
  nuit: 12.5,
  matin: 37.5,
  apres_midi: 62.5,
  soiree: 87.5,
}

/** Repères visuels aux frontières des 4 périodes + début/fin */
const TICK_PCTS = [0, 25, 50, 75, 100]

export const TimelineRail: React.FC<TimelineRailProps> = ({ selectedPeriod }) => {
  const thumbPct = selectedPeriod !== null ? PERIOD_THUMB_PCT[selectedPeriod] : null

  return (
    <div className="timeline-rail" aria-hidden="true">
      <div className="timeline-rail__track">
        {/* Fill progressif */}
        <div
          className="timeline-rail__fill"
          style={{ width: thumbPct !== null ? `${thumbPct}%` : '0%' }}
        />
        {/* Repères de frontières */}
        {TICK_PCTS.map(pct => (
          <div key={pct} className="timeline-rail__tick" style={{ left: `${pct}%` }} />
        ))}
        {/* Thumb dot sur la période sélectionnée */}
        {thumbPct !== null && (
          <div className="timeline-rail__thumb" style={{ left: `${thumbPct}%` }} />
        )}
      </div>
    </div>
  )
}
