import React from 'react'
import type { KeyPointsSectionModel } from '../../types/keyPointsSection'
import { SectionTitle } from './SectionTitle'
import { KeyPointCard } from './KeyPointCard'
import './KeyPointsSection.css'

interface KeyPointsSectionProps {
  model: KeyPointsSectionModel
}

export const KeyPointsSection: React.FC<KeyPointsSectionProps> = ({ model }) => {
  if (model.items.length === 0) {
    return null
  }

  return (
    <section className="key-points-section" id="key-points">
      <SectionTitle title={model.title} />
      <div className="key-points-section__grid">
        {model.items.map((item) => (
          <KeyPointCard key={item.id} item={item} />
        ))}
      </div>
    </section>
  )
}
