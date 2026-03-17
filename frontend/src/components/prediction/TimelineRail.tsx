import React from 'react'
import type { AggregatedDayPeriod, DayPeriodKey } from '../../types/dayTimeline'
import './TimelineRail.css'

interface TimelineRailProps {
  periods: AggregatedDayPeriod[]
  selectedPeriod: DayPeriodKey | null
}

export const TimelineRail: React.FC<TimelineRailProps> = ({ periods, selectedPeriod }) => {
  return (
    <div className="timeline-rail" aria-hidden="true">
      {periods.map(p => (
        <div 
          key={p.key}
          className={`timeline-rail__segment ${selectedPeriod === p.key ? 'timeline-rail__segment--active' : ''} ${p.hasTurningPoint ? 'timeline-rail__segment--pivot' : ''}`}
          data-tone={p.tone ?? 'neutral'}
          style={{ flex: 1 }}
        />
      ))}
    </div>
  )
}
