import React from 'react'
import type { KeyPointItem } from '../../types/keyPointsSection'
import './KeyPointCard.css'

interface KeyPointCardProps {
  item: KeyPointItem
}

export const KeyPointCard: React.FC<KeyPointCardProps> = ({ item }) => {
  return (
    <article className="key-point-card">
      <div className="key-point-card__top">
        <div className="key-point-card__icon-pill">
          {item.icon}
        </div>
        <span className="key-point-card__label">{item.label}</span>
      </div>
      <div className="key-point-card__gauge" aria-hidden="true">
        <div className="key-point-card__gauge-track">
          <div 
            className="key-point-card__gauge-fill" 
            style={{ width: `${item.strength ?? 0}%` }}
          />
        </div>
      </div>
    </article>
  )
}
