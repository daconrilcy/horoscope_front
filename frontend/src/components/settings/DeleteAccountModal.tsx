import { useState, useEffect, useRef, useCallback } from "react"
import { useNavigate } from "react-router-dom"
import { clearAccessToken } from "../../utils/authToken"
import { useRequestDelete } from "../../api/privacy"
import { detectLang } from "../../i18n/astrology"
import { settingsTranslations } from "../../i18n/settings"
import { Modal, Button, Field } from "../ui"

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
  const isMountedRef = useRef(true)

  useEffect(() => {
    isMountedRef.current = true
    return () => {
      isMountedRef.current = false
    }
  }, [])

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

  const footer = (
    <>
      {step !== "processing" && (
        <>
          <Button variant="secondary" onClick={onClose}>
            {t.cancel}
          </Button>
          {step === "initial" ? (
            <Button variant="danger" onClick={handleFirstConfirm}>
              {t.confirm}
            </Button>
          ) : (
            <Button 
              variant="danger" 
              onClick={handleFinalConfirm} 
              disabled={!confirmInput}
            >
              {t.confirm}
            </Button>
          )}
        </>
      )}
    </>
  )

  return (
    <Modal
      isOpen={true}
      onClose={step !== "processing" ? onClose : () => {}}
      title={t.title}
      variant="danger"
      size="sm"
      footer={footer}
    >
      {step === "initial" && (
        <p>{t.initialMessage}</p>
      )}

      {step === "confirm" && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
          <p>{t.confirmMessage}</p>
          <p style={{ fontWeight: 'bold', textAlign: 'center', fontSize: 'var(--font-size-lg)' }}>
            {t.confirmWord}
          </p>
          <Field
            type="text"
            placeholder={t.confirmPlaceholder}
            value={confirmInput}
            onChange={(e) => setConfirmInput(e.target.value)}
            error={error || undefined}
            autoFocus
          />
        </div>
      )}

      {step === "processing" && (
        <div style={{ textAlign: 'center', padding: 'var(--space-4)' }}>
          <p>{t.processing}</p>
        </div>
      )}
    </Modal>
  )
}
