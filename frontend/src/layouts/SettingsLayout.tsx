import React from 'react'
import { SettingsTabs } from '../components/settings/SettingsTabs'
import { PageLayout } from './PageLayout'
import '../pages/settings/Settings.css'

interface SettingsLayoutProps {
  title: string
  children: React.ReactNode
  className?: string
}

export function SettingsLayout({ title, children, className }: SettingsLayoutProps) {
  return (
    <PageLayout className={`is-settings-page ${className ?? ''}`}>
      <div className="settings-bg-halo" />
      <div className="settings-noise" />
      
      <div className="settings-container">
        <h1 className="settings-section-title" style={{ fontSize: '2.4rem', marginBottom: '32px' }}>
          {title}
        </h1>
        
        <SettingsTabs />
        
        <div className="settings-content">
          {children}
        </div>
      </div>
    </PageLayout>
  )
}
