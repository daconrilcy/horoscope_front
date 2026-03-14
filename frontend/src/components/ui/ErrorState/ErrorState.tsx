import React from 'react'
import { AlertCircle, RefreshCw } from 'lucide-react'
import { Button } from '../Button'
import './ErrorState.css'

export interface ErrorStateProps {
  title?: string
  message: string
  onRetry?: () => void
  className?: string
}

export const ErrorState: React.FC<ErrorStateProps> = ({
  title,
  message,
  onRetry,
  className,
}) => {
  return (
    <div className={`error-state ${className ?? ''}`} role="alert">
      <div className="error-state__icon-wrapper">
        <AlertCircle className="error-state__icon" />
      </div>
      {title && <h3 className="error-state__title">{title}</h3>}
      <p className="error-state__message">{message}</p>
      {onRetry && (
        <Button 
          variant="ghost" 
          onClick={onRetry}
          className="error-state__button"
        >
          <RefreshCw size={16} className="mr-2" />
          Réessayer
        </Button>
      )}
    </div>
  )
}
