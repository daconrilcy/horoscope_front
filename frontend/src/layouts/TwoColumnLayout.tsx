// Primitive React du layout deux colonnes avec largeur gouvernee par CSS.
import React from 'react'
import './TwoColumnLayout.css'

interface TwoColumnLayoutProps {
  sidebar: React.ReactNode
  main: React.ReactNode
  collapsibleOnMobile?: boolean // default: true
  className?: string
}

export function TwoColumnLayout({ 
  sidebar, 
  main, 
  collapsibleOnMobile = true, 
  className 
}: TwoColumnLayoutProps) {
  return (
    <div className={`two-col-layout ${className ?? ''}`}>
      <div className={`two-col-layout__sidebar ${collapsibleOnMobile ? 'two-col-layout__sidebar--collapsible' : ''}`}>
        {sidebar}
      </div>
      <div className="two-col-layout__main">
        {main}
      </div>
    </div>
  )
}
