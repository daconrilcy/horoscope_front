import React from 'react'
import { MiniInsightCard } from './MiniInsightCard'
import { useDailyInsights, type InsightItem } from '../hooks/useDailyInsights'

export interface DailyInsightsSectionProps {
  ariaLabel?: string
  items?: InsightItem[]
  onSectionClick?: () => void
}

/**
 * Presentational component for DailyInsightsSection.
 */
export function DailyInsightsSectionPresenter({ 
  ariaLabel, 
  items = [], 
  onSectionClick 
}: DailyInsightsSectionProps & { ariaLabel: string; items: InsightItem[] }) {
  return (
    <section aria-label={ariaLabel}>
      <div className="mini-cards-grid">
        {items.map((item) => (
          <MiniInsightCard
            key={item.id}
            title={item.title}
            description={item.description}
            icon={item.icon}
            badgeColor={item.badgeColor}
            onClick={onSectionClick}
          />
        ))}
      </div>
    </section>
  )
}

/**
 * Container component (default export) to maintain backward compatibility.
 */
export function DailyInsightsSection(props: DailyInsightsSectionProps) {
  const { ariaLabel, items } = useDailyInsights()
  
  return (
    <DailyInsightsSectionPresenter
      ariaLabel={props.ariaLabel ?? ariaLabel}
      items={props.items ?? items}
      onSectionClick={props.onSectionClick}
    />
  )
}
