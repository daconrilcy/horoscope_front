import React from 'react'
import './TwoColumnLayout.css'

interface TwoColumnLayoutProps {
  sidebar: React.ReactNode
  main: React.ReactNode
  sidebarWidth?: string         // default: "320px"
  collapsibleOnMobile?: boolean // default: true
  className?: string
}

export function TwoColumnLayout({ 
  sidebar, 
  main, 
  sidebarWidth = '320px', 
  collapsibleOnMobile = true, 
  className 
}: TwoColumnLayoutProps) {
  return (
    <div 
      className={`two-col-layout ${className ?? ''}`} 
      style={{ '--sidebar-width': sidebarWidth } as React.CSSProperties}
    >
      <div className={`two-col-layout__sidebar ${collapsibleOnMobile ? 'two-col-layout__sidebar--collapsible' : ''}`}>
        {sidebar}
      </div>
      <div className="two-col-layout__main">
        {main}
      </div>
    </div>
  )
}
