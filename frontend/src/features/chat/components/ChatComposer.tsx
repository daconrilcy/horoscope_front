import { useState, useEffect, useRef } from "react"
import type { FormEvent, KeyboardEvent } from "react"

type ChatComposerProps = {
  onSend: (message: string) => void
  disabled?: boolean
  placeholder?: string
  initialValue?: string
  onInitialValueConsumed?: () => void
  sendLabel?: string
  inputAriaLabel?: string
}

export function ChatComposer({
  onSend,
  disabled = false,
  placeholder = "Posez votre question aux astres...",
  initialValue,
  onInitialValueConsumed,
  sendLabel = "Envoyer",
  inputAriaLabel = "Message",
}: ChatComposerProps) {
  const [value, setValue] = useState("")
  const initialValueConsumed = useRef(false)

  useEffect(() => {
    if (initialValue && !initialValueConsumed.current) {
      setValue(initialValue)
      initialValueConsumed.current = true
      onInitialValueConsumed?.()
    }
  }, [initialValue, onInitialValueConsumed])

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    const trimmed = value.trim()
    if (trimmed && !disabled) {
      onSend(trimmed)
      setValue("")
    }
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form className="chat-composer" onSubmit={handleSubmit}>
      <textarea
        className="chat-composer-input"
        value={value}
        onChange={(e) => setValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={2}
        aria-label={inputAriaLabel}
      />
      <button
        type="submit"
        className="chat-composer-button"
        disabled={disabled || !value.trim()}
      >
        {sendLabel}
      </button>
    </form>
  )
}
