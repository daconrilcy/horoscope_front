import React from 'react'
import './SectionTitle.css'

interface SectionTitleProps {
  title: string
  id?: string
}

export const SectionTitle: React.FC<SectionTitleProps> = ({ title, id }) => {
  return (
    <header className="section-title" id={id}>
      <div className="section-title__dot" />
      <h3 className="section-title__text">{title}</h3>
      <hr className="section-title__line" />
    </header>
  )
}
