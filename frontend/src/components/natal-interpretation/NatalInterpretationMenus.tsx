// Composants presentational des menus et etats de l'interpretation natale.
import { useEffect, useRef, useState } from "react"
import { AlertCircle, ChevronDown, Download, Eye, History, RefreshCw, Trash2 } from "lucide-react"

import { Button } from "@ui/Button"
import type { InterpretationTranslations, NatalInterpretationHistoryItemView } from "./NatalInterpretationTypes"

export function PdfActionsMenu({
  t,
  onPreview,
  onDownload,
}: {
  t: InterpretationTranslations
  onPreview: () => void
  onDownload: () => void
}) {
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    if (!isOpen) return
    const handleOutsideClick = (event: MouseEvent | TouchEvent) => {
      const target = event.target as Node | null
      if (target && containerRef.current && !containerRef.current.contains(target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener("mousedown", handleOutsideClick)
    document.addEventListener("touchstart", handleOutsideClick)
    return () => {
      document.removeEventListener("mousedown", handleOutsideClick)
      document.removeEventListener("touchstart", handleOutsideClick)
    }
  }, [isOpen])

  return (
    <div className="ni-version-selector" ref={containerRef}>
      <button
        type="button"
        onClick={() => setIsOpen((previous) => !previous)}
        className="ni-control-trigger ni-version-btn"
        aria-haspopup="menu"
        aria-expanded={isOpen}
      >
        <Download size={16} />
        <span>{t.pdfActionsLabel}</span>
        <ChevronDown
          size={12}
          className={`ni-version-btn__chevron${isOpen ? " ni-version-btn__chevron--open" : ""}`}
        />
      </button>

      {isOpen && (
        <div className="ni-version-dropdown ni-version-dropdown--actions" role="menu">
          <div className="ni-version-dropdown__header">
            <span className="ni-version-dropdown__label">{t.pdfGroupLabel}</span>
          </div>
          <div className="ni-version-dropdown__list">
            <button
              type="button"
              className="ni-menu-action"
              onClick={() => {
                onPreview()
                setIsOpen(false)
              }}
            >
              <Eye size={16} />
              <span>{t.previewPdf}</span>
            </button>
            <button
              type="button"
              className="ni-menu-action ni-menu-action--primary"
              onClick={() => {
                onDownload()
                setIsOpen(false)
              }}
            >
              <Download size={16} />
              <span>{t.downloadPdf}</span>
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export function VersionSelector({
  items,
  selectedId,
  onSelect,
  onDeleteRequest,
  t,
  lang,
}: {
  items: NatalInterpretationHistoryItemView[]
  selectedId: number | null
  onSelect: (id: number | null) => void
  onDeleteRequest?: (id: number) => void
  t: InterpretationTranslations
  lang: string
}) {
  const [isOpen, setIsOpen] = useState(false)
  const containerRef = useRef<HTMLDivElement | null>(null)
  const selectedItem = items.find((item) => item.id === selectedId)

  useEffect(() => {
    if (!isOpen) return
    const handleOutsideClick = (event: MouseEvent | TouchEvent) => {
      const target = event.target as Node | null
      if (target && containerRef.current && !containerRef.current.contains(target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener("mousedown", handleOutsideClick)
    document.addEventListener("touchstart", handleOutsideClick)
    return () => {
      document.removeEventListener("mousedown", handleOutsideClick)
      document.removeEventListener("touchstart", handleOutsideClick)
    }
  }, [isOpen])

  return (
    <div className="ni-version-selector" ref={containerRef}>
      <button type="button" onClick={() => setIsOpen((previous) => !previous)} className="ni-control-trigger ni-version-btn">
        <History size={16} className="ni-version-btn__history-icon" />
        <span>
          {selectedItem
            ? `${new Date(selectedItem.created_at).toLocaleDateString(lang)} - ${
                selectedItem.persona_name || t.standardVersionLabel
              }`
            : t.historyTitle}
        </span>
        <ChevronDown
          size={12}
          className={`ni-version-btn__chevron${isOpen ? " ni-version-btn__chevron--open" : ""}`}
        />
      </button>

      {isOpen && (
        <div className="ni-version-dropdown">
          <div className="ni-version-dropdown__header">
            <span className="ni-version-dropdown__label">{t.historyTitle}</span>
          </div>
          <div className="ni-version-dropdown__list">
            {items.map((item) => (
              <div key={item.id} className="ni-version-item" data-selected={selectedId === item.id ? "true" : undefined}>
                <div className="ni-version-item__row">
                  <button
                    type="button"
                    className="ni-version-item__btn"
                    onClick={() => {
                      onSelect(item.id)
                      setIsOpen(false)
                    }}
                  >
                    <span className="ni-version-item__name">{item.persona_name || t.standardVersionLabel}</span>
                    <span className="ni-version-item__date">
                      {new Date(item.created_at).toLocaleString(lang, {
                        day: "2-digit",
                        month: "2-digit",
                        hour: "2-digit",
                        minute: "2-digit",
                      })}{" "}
                      · {item.level === "complete" ? t.completeBadge : t.shortBadge}
                    </span>
                  </button>
                  {onDeleteRequest ? (
                    <button
                      type="button"
                      onClick={(event) => {
                        event.stopPropagation()
                        onDeleteRequest(item.id)
                      }}
                      className="ni-version-item__delete"
                      title={t.deleteCta}
                    >
                      <Trash2 size={14} />
                    </button>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export function ConfirmDeleteModal({
  t,
  onConfirm,
  onCancel,
  isDeleting,
}: {
  t: InterpretationTranslations
  onConfirm: () => void
  onCancel: () => void
  isDeleting: boolean
}) {
  return (
    <div className="app-overlay" onClick={onCancel} role="dialog" aria-modal="true" aria-labelledby="delete-confirm-title">
      <div className="app-modal natal-interpretation__modal" onClick={(event) => event.stopPropagation()}>
        <div className="ni-modal-header">
          <div className="ni-modal-icon">
            <AlertCircle size={24} />
          </div>
          <h4 className="ni-modal-heading" id="delete-confirm-title">{t.deleteConfirm}</h4>
        </div>
        <p className="ni-modal-body">{t.deleteConfirmSub}</p>
        <div className="ni-modal-footer">
          <Button variant="ghost" onClick={onCancel} disabled={isDeleting}>
            {t.cancel}
          </Button>
          <Button variant="danger" onClick={onConfirm} loading={isDeleting} leftIcon={<RefreshCw size={12} />}>
            {t.deleteCta}
          </Button>
        </div>
      </div>
    </div>
  )
}

export function InterpretationSkeleton({ t, isComplete }: { t: InterpretationTranslations; isComplete?: boolean }) {
  return (
    <div className="ni-skeleton">
      <div className="ni-skeleton__line ni-skeleton__line--75" />
      <div className="ni-skeleton__line" />
      <div className="ni-skeleton__line ni-skeleton__line--83" />
      <div className="ni-skeleton__tabs">
        {[1, 2, 3].map((item) => <div key={item} className="ni-skeleton__tab" />)}
      </div>
      <div className="ni-skeleton__block" />
      <p className="ni-skeleton__caption">{isComplete ? t.requestingComplete : t.loading}</p>
    </div>
  )
}

export function InterpretationError({
  t,
  onRetry,
}: {
  t: InterpretationTranslations
  onRetry: () => void
}) {
  return (
    <div className="ni-error">
      <div className="ni-error__icon">
        <AlertCircle size={32} />
      </div>
      <p className="ni-error__message">{t.error}</p>
      <Button variant="danger" onClick={onRetry} leftIcon={<RefreshCw size={16} />}>
        {t.retry}
      </Button>
    </div>
  )
}
