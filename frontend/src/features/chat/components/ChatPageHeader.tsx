import React from 'react'
import { useNavigate } from 'react-router-dom'
import { ChevronLeft } from 'lucide-react'
import { detectLang } from '@i18n/astrology'
import { tAstrologers as t } from '@i18n/astrologers'
import './ChatPageHeader.css'

interface ChatPageHeaderProps {
  title?: string
  eyebrow?: string
  showBackButton?: boolean
  onBack?: () => void
}

export const ChatPageHeader: React.FC<ChatPageHeaderProps> = ({ 
  title, 
  eyebrow, 
  showBackButton = true,
  onBack
}) => {
  const navigate = useNavigate()
  const lang = detectLang()
  
  const displayTitle = title || t("conversations_title", lang)
  const displayEyebrow = eyebrow || (lang === 'fr' ? 'Messagerie' : 'Messaging')

  const handleBack = () => {
    if (onBack) {
      onBack()
    } else {
      navigate('/dashboard')
    }
  }

  return (
    <header className="chat-page-header">
      {showBackButton && (
        <button 
          className="chat-page-header__back" 
          onClick={handleBack}
          aria-label={t("chat_back", lang)}
        >
          <ChevronLeft size={18} strokeWidth={2.4} />
        </button>
      )}

      <div className="chat-page-header__content">
        <div className="chat-page-header__eyebrow">{displayEyebrow}</div>
        <h1 className="chat-page-header__title">{displayTitle}</h1>
      </div>
    </header>
  )
}
