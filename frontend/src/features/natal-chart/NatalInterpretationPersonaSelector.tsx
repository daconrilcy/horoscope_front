// Sous-container dedie au choix d'astrologue pour l'interpretation natale.
import { AlertCircle, RefreshCw } from "lucide-react"

import { useAstrologers, type Astrologer } from "../../api/astrologers"
import { AstrologerGrid } from "../astrologers"
import { Button } from "@ui/Button"
import type { InterpretationTranslations } from "../../components/natal-interpretation/NatalInterpretationTypes"

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
  const { data: experts, isLoading, isError, refetch } = useAstrologers()
  const availableAstrologers = (experts ?? []).filter(
    (expert) => !excludedPersonaIds?.has(expert.id),
  )

  return (
    <div className="app-overlay" onClick={onCancel} role="dialog" aria-modal="true" aria-labelledby="persona-selector-title">
      <div
        className="app-modal natal-interpretation__fullscreen-modal"
        onClick={(event) => event.stopPropagation()}
      >
        <h4 className="app-modal__title" id="persona-selector-title">{t.personaSelectorTitle}</h4>

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
              experts={availableAstrologers}
              onSelectAstrologer={(expert: Astrologer) => {
                if (isSubmitting) return
                onConfirm(expert.id)
              }}
            />
          ) : (
            <p className="ni-modal-empty-text">{t.allAstrologersUsed}</p>
          )}
        </div>

        <div className="app-actions app-actions--end">
          <button type="button" onClick={onCancel} disabled={isSubmitting} className="ni-modal-cancel-btn">
            {t.cancel}
          </button>
        </div>
      </div>
    </div>
  )
}
