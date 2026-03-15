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
    <div className={`wizard-layout ${className ?? ''}`}>
      <div className="wizard-layout__progress-wrapper">
        {customProgress ? (
          customProgress
        ) : steps ? (
          <div 
            className="wizard-layout__progress" 
            role="progressbar" 
            aria-valuemin={0} 
            aria-valuemax={steps.length - 1} 
            aria-valuenow={currentStep}
          >
            <div className="wizard-progress-steps">
              {steps.map((label, i) => (
                <div 
                  key={i} 
                  className={`wizard-step ${i < currentStep ? 'wizard-step--done' : ''} ${i === currentStep ? 'wizard-step--active' : ''}`}
                >
                  <div className="wizard-step__indicator">
                    {i < currentStep ? '✓' : i + 1}
                  </div>
                  <span className="wizard-step__label">{label}</span>
                  {i < steps.length - 1 && <div className="wizard-step__connector" />}
                </div>
              ))}
            </div>
          </div>
        ) : null}
      </div>

      <div className="wizard-layout__container">
        {onBack && (
          <button 
            type="button" 
            className="wizard-layout__back" 
            onClick={onBack}
            aria-label="Retour"
          >
            <ChevronLeft size={20} />
            <span>Retour</span>
          </button>
        )}
        
        <div className="wizard-layout__content">
          {children}
        </div>
      </div>
    </div>
  )
}
