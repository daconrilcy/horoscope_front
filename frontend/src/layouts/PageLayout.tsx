import React from "react"
import "./PageLayout.css"

interface PageLayoutProps {
  title?: string
  header?: React.ReactNode
  aside?: React.ReactNode
  children: React.ReactNode
  className?: string
}

export function PageLayout({ title, header, aside, children, className }: PageLayoutProps) {
  return (
    <div className={`page-layout ${className ?? ""}`}>
      {(title || header) && (
        <div className="page-layout__header">
          {title && <h1 className="page-layout__title">{title}</h1>}
          {header}
        </div>
      )}
      <div className={`page-layout__body ${aside ? "page-layout__body--with-aside" : ""}`}>
        <div className="page-layout__main">{children}</div>
        {aside && <aside className="page-layout__aside">{aside}</aside>}
      </div>
    </div>
  )
}
