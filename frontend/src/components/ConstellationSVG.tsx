import { memo } from 'react'

interface ConstellationSVGProps {
  className?: string
}

export const ConstellationSVG = memo(function ConstellationSVG({ className }: ConstellationSVGProps) {
  return (
    <svg
      viewBox="0 0 120 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
      className={className}
      preserveAspectRatio="xMidYMid meet"
    >
      {/* Stars */}
      <circle cx="10" cy="32" r="2" fill="currentColor" />
      <circle cx="30" cy="22" r="1.5" fill="currentColor" />
      <circle cx="55" cy="28" r="2" fill="currentColor" />
      <circle cx="75" cy="18" r="1.5" fill="currentColor" />
      <circle cx="95" cy="25" r="2" fill="currentColor" />
      <circle cx="110" cy="32" r="1.5" fill="currentColor" />

      <circle cx="10" cy="52" r="1.5" fill="currentColor" />
      <circle cx="30" cy="45" r="2" fill="currentColor" />
      <circle cx="55" cy="50" r="1.5" fill="currentColor" />
      <circle cx="75" cy="42" r="2" fill="currentColor" />
      <circle cx="95" cy="48" r="1.5" fill="currentColor" />
      <circle cx="110" cy="52" r="2" fill="currentColor" />

      {/* Extra accent stars */}
      <circle cx="42" cy="14" r="1" fill="currentColor" opacity="0.6" />
      <circle cx="85" cy="60" r="1" fill="currentColor" opacity="0.6" />
      <circle cx="20" cy="68" r="1" fill="currentColor" opacity="0.5" />

      {/* Upper wave - Verseau characteristic double wave */}
      <path
        d="M10 32 Q20 22 30 22 Q42 22 55 28 Q65 34 75 18 Q85 8 95 25 Q102 35 110 32"
        stroke="currentColor"
        strokeWidth="1"
        fill="none"
      />

      {/* Lower wave */}
      <path
        d="M10 52 Q20 42 30 45 Q42 48 55 50 Q65 52 75 42 Q85 32 95 48 Q102 58 110 52"
        stroke="currentColor"
        strokeWidth="1"
        fill="none"
      />

      {/* Connecting vertical lines */}
      <line x1="30" y1="22" x2="30" y2="45" stroke="currentColor" strokeWidth="0.6" />
      <line x1="75" y1="18" x2="75" y2="42" stroke="currentColor" strokeWidth="0.6" />
    </svg>
  )
})
