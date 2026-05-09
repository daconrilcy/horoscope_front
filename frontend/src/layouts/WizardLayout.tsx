import React from 'react'
import { ChevronLeft } from 'lucide-react'
import './WizardLayout.css'

interface WizardLayoutProps {
  steps?: string[]
  currentStep?: number
  customProgress?: React.ReactNode
  children: React.ReactNode
  onBack?: () => void
  className?: string
}

export function WizardLayout({ 
  steps, 
  currentStep = 0, 
  customProgress,
  children, 
  onBack, 
  className 
}: WizardLayoutProps) {
  return (
    <div className={`flow-layout ${className ?? ''}`}>
      <div className="flow-layout__progress-wrapper">
        {customProgress ? (
          customProgress
        ) : steps ? (
          <div 
            className="flow-layout__progress"
            role="progressbar" 
            aria-valuemin={0} 
            aria-valuemax={steps.length - 1} 
            aria-valuenow={currentStep}
          >
            <div className="flow-progress-steps">
              {steps.map((label, i) => (
                <div
                  key={i}
                  className={`flow-progress-step ${i < currentStep ? 'flow-progress-step--done' : ''} ${i === currentStep ? 'flow-progress-step--active' : ''}`}
                >
                  <div className="flow-progress-step__indicator">
                    {i < currentStep ? '✓' : i + 1}
                  </div>
                  <span className="flow-progress-step__label">{label}</span>
                  {i < steps.length - 1 && <div className="flow-progress-step__connector" />}
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>

      <div className="flow-layout__container">
        {onBack && (
          <button 
            type="button" 
            className="flow-layout__back"
            onClick={onBack}
            aria-label="Retour"
          >
            <ChevronLeft size={20} />
            <span>Retour</span>
          </button>
        )}
        
        <div className="flow-layout__content">
          {children}
        </div>
      </div>
    </div>
  )
}
