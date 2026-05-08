// Sous-container dedie au choix d'astrologue pour l'interpretation natale.
import { AlertCircle, RefreshCw } from "lucide-react"

import { useAstrologers, type Astrologer } from "../../api/astrologers"
import { AstrologerGrid } from "../../features/astrologers"
import { Button } from "@ui/Button"
import type { InterpretationTranslations } from "./NatalInterpretationTypes"

export function PersonaSelector({
  t,
  onConfirm,
  onCancel,
  isSubmitting,
  excludedPersonaIds,
}: {
  t: InterpretationTranslations
  onConfirm: (id: string) => void
  onCancel: () => void
  isSubmitting?: boolean
  excludedPersonaIds?: Set<string>
}) {
  const { data: astrologers, isLoading, isError, refetch } = useAstrologers()
  const availableAstrologers = (astrologers ?? []).filter(
    (astrologer) => !excludedPersonaIds?.has(astrologer.id),
  )

  return (
    <div className="modal-overlay" onClick={onCancel} role="dialog" aria-modal="true" aria-labelledby="persona-selector-title">
      <div
        className="modal-content natal-interpretation__fullscreen-modal"
        onClick={(event) => event.stopPropagation()}
      >
        <h4 className="modal-title" id="persona-selector-title">{t.personaSelectorTitle}</h4>

        <div className="ni-persona-selector__body">
          {isLoading ? (
            <div className="ni-loader-container">
              <RefreshCw size={32} className="ni-loader-spin" />
            </div>
          ) : isError ? (
            <div className="ni-modal-error">
              <div className="ni-modal-error-icon">
                <AlertCircle size={24} />
              </div>
              <p className="ni-modal-error-text">{t.error}</p>
              <Button variant="secondary" onClick={() => refetch()}>{t.retry}</Button>
            </div>
          ) : availableAstrologers.length > 0 ? (
            <AstrologerGrid
              astrologers={availableAstrologers}
              onSelectAstrologer={(astrologer: Astrologer) => {
                if (isSubmitting) return
                onConfirm(astrologer.id)
              }}
            />
          ) : (
            <p className="ni-modal-empty-text">{t.allAstrologersUsed}</p>
          )}
        </div>

        <div className="modal-actions">
          <button type="button" onClick={onCancel} disabled={isSubmitting} className="ni-modal-cancel-btn">
            {t.cancel}
          </button>
        </div>
      </div>
    </div>
  )
}
