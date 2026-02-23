import { useEffect, useState, useCallback, useRef } from "react"
import type { RefObject } from "react"

const SCROLL_TOLERANCE_PX = 50

export function useAutoScroll(
  containerRef: RefObject<HTMLElement | null>,
  triggerValue: unknown
) {
  const [userScrolled, setUserScrolled] = useState(false)
  const prevTriggerRef = useRef(triggerValue)

  useEffect(() => {
    if (prevTriggerRef.current !== triggerValue) {
      prevTriggerRef.current = triggerValue
      const el = containerRef.current
      if (!userScrolled && el) {
        el.scrollTop = el.scrollHeight
      }
    }
  }, [userScrolled, triggerValue])

  const handleScroll = useCallback(() => {
    const el = containerRef.current
    if (el) {
      const isAtBottom =
        el.scrollHeight - el.scrollTop <= el.clientHeight + SCROLL_TOLERANCE_PX
      setUserScrolled(!isAtBottom)
    }
  }, [])

  const resetScroll = useCallback(() => {
    setUserScrolled(false)
  }, [])

  return { handleScroll, resetScroll }
}
