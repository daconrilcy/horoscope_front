import React from 'react'
import { SettingsTabs } from '../components/settings/SettingsTabs'

interface SettingsLayoutProps {
  title: string
  children: React.ReactNode
  className?: string
}

export function SettingsLayout({ title, children, className }: SettingsLayoutProps) {
  return (
    <div className={`settings-layout ${className ?? ''}`}>
      <h1 className="settings-title">{title}</h1>
      <SettingsTabs />
      <div className="settings-content">
        {children}
      </div>
    </div>
  )
}
