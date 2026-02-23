import { useState, useEffect, useRef, useCallback } from "react"
import { useNavigate } from "react-router-dom"
import { clearAccessToken } from "../../utils/authToken"
import { useRequestDelete } from "../../api/privacy"
import { detectLang } from "../../i18n/astrology"
import { settingsTranslations } from "../../i18n/settings"

interface DeleteAccountModalProps {
  onClose: () => void
}

type Step = "initial" | "confirm" | "processing"

function normalizeConfirmInput(input: string): string {
  return input
    .toUpperCase()
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .trim()
}

export function DeleteAccountModal({ onClose }: DeleteAccountModalProps) {
  const lang = detectLang()
  const t = settingsTranslations.deleteModal[lang]
  const navigate = useNavigate()
  const requestDelete = useRequestDelete()

  const [step, setStep] = useState<Step>("initial")
  const [confirmInput, setConfirmInput] = useState("")
  const [error, setError] = useState<string | null>(null)

  const modalRef = useRef<HTMLDivElement>(null)
  const previousActiveElement = useRef<HTMLElement | null>(null)
  const inputRef = useRef<HTMLInputElement>(null)
  const isMountedRef = useRef(true)

  useEffect(() => {
    isMountedRef.current = true
    return () => {
      isMountedRef.current = false
    }
  }, [])

  const getFocusableElements = useCallback((): HTMLElement[] => {
    if (!modalRef.current) return []
    const focusableSelectors =
      'button:not([disabled]), input:not([disabled]), [tabindex]:not([tabindex="-1"])'
    return Array.from(modalRef.current.querySelectorAll<HTMLElement>(focusableSelectors))
  }, [])

  useEffect(() => {
    previousActiveElement.current = document.activeElement as HTMLElement | null

    const firstFocusable = getFocusableElements()[0]
    if (firstFocusable) {
      firstFocusable.focus()
    }

    return () => {
      if (previousActiveElement.current) {
        previousActiveElement.current.focus()
      }
    }
  }, [getFocusableElements])

  useEffect(() => {
    if (step === "confirm" && inputRef.current) {
      inputRef.current.focus()
    }
  }, [step])

  const handleFocusTrap = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key !== "Tab") return

      const focusableElements = getFocusableElements()
      if (focusableElements.length === 0) return

      const firstElement = focusableElements[0]
      const lastElement = focusableElements[focusableElements.length - 1]

      if (e.shiftKey && document.activeElement === firstElement) {
        e.preventDefault()
        lastElement.focus()
      } else if (!e.shiftKey && document.activeElement === lastElement) {
        e.preventDefault()
        firstElement.focus()
      }
    },
    [getFocusableElements]
  )

  const handleFirstConfirm = useCallback(() => {
    setStep("confirm")
  }, [])

  const handleFinalConfirm = useCallback(async () => {
    if (normalizeConfirmInput(confirmInput) !== t.confirmWord) {
      setError(t.mismatch)
      return
    }

    setError(null)
    setStep("processing")

    try {
      await requestDelete.mutateAsync()
      clearAccessToken()
      navigate("/login", { replace: true })
    } catch {
      if (isMountedRef.current) {
        setError(t.error)
        setStep("confirm")
      }
    }
  }, [confirmInput, t, requestDelete, navigate])

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (step === "processing") return
      if (e.key === "Escape") {
        onClose()
      }
      handleFocusTrap(e)
    },
    [step, onClose, handleFocusTrap]
  )

  return (
    <div
      className="modal-overlay"
      onClick={step !== "processing" ? onClose : undefined}
      onKeyDown={handleKeyDown}
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-account-title"
    >
      <div
        ref={modalRef}
        className="modal-content"
        onClick={(e) => e.stopPropagation()}
      >
        <h2 id="delete-account-title" className="modal-title">
          {t.title}
        </h2>

        {step === "initial" && (
          <>
            <p className="modal-message">{t.initialMessage}</p>
            <div className="modal-actions">
              <button type="button" onClick={onClose}>
                {t.cancel}
              </button>
              <button
                type="button"
                className="btn-danger"
                onClick={handleFirstConfirm}
              >
                {t.confirm}
              </button>
            </div>
          </>
        )}

        {step === "confirm" && (
          <>
            <p className="modal-message">{t.confirmMessage}</p>
            <p className="modal-confirm-word">{t.confirmWord}</p>
            <input
              ref={inputRef}
              type="text"
              className="modal-input"
              placeholder={t.confirmPlaceholder}
              value={confirmInput}
              onChange={(e) => setConfirmInput(e.target.value)}
              aria-label={t.confirmHint}
            />
            {error && <p className="modal-error">{error}</p>}
            <div className="modal-actions">
              <button type="button" onClick={onClose}>
                {t.cancel}
              </button>
              <button
                type="button"
                className="btn-danger"
                onClick={handleFinalConfirm}
                disabled={!confirmInput}
              >
                {t.confirm}
              </button>
            </div>
          </>
        )}

        {step === "processing" && (
          <p className="modal-message state-loading" aria-busy="true" aria-live="polite">
            {t.processing}
          </p>
        )}
      </div>
    </div>
  )
}
