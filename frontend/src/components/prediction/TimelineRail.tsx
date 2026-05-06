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
const TICK_CLASSES = [
  'timeline-rail__tick--0',
  'timeline-rail__tick--25',
  'timeline-rail__tick--50',
  'timeline-rail__tick--75',
  'timeline-rail__tick--100',
] as const

const PERIOD_CLASS_SUFFIX: Record<DayPeriodKey, string> = {
  nuit: 'nuit',
  matin: 'matin',
  apres_midi: 'apres-midi',
  soiree: 'soiree',
}

export const TimelineRail: React.FC<TimelineRailProps> = ({ selectedPeriod }) => {
  const thumbPct = selectedPeriod !== null ? PERIOD_THUMB_PCT[selectedPeriod] : null
  const selectedClass = selectedPeriod !== null ? PERIOD_CLASS_SUFFIX[selectedPeriod] : null

  return (
    <div className="timeline-rail" aria-hidden="true">
      <div className="timeline-rail__track">
        {/* Fill progressif */}
        <div
          className={`timeline-rail__fill${selectedClass ? ` timeline-rail__fill--${selectedClass}` : ''}`}
        />
        {/* Repères de frontières */}
        {TICK_CLASSES.map(tickClass => (
          <div key={tickClass} className={`timeline-rail__tick ${tickClass}`} />
        ))}
        {/* Thumb dot sur la période sélectionnée */}
        {thumbPct !== null && (
          <div className={`timeline-rail__thumb timeline-rail__thumb--${selectedClass}`} />
        )}
      </div>
    </div>
  )
}
