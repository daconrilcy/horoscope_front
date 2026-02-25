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
      <defs>
        {/* Glow filter for star nodes */}
        <filter id="star-glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="1.5" result="blur" />
          <feComposite in="SourceGraphic" in2="blur" operator="over" />
        </filter>
      </defs>

      {/* Constellation lines (white, 1.2px) */}
      <line x1="12" y1="30" x2="32" y2="20" stroke="white" strokeWidth="1.2" />
      <line x1="32" y1="20" x2="55" y2="28" stroke="white" strokeWidth="1.2" />
      <line x1="55" y1="28" x2="72" y2="15" stroke="white" strokeWidth="1.2" />
      <line x1="72" y1="15" x2="95" y2="25" stroke="white" strokeWidth="1.2" />
      <line x1="95" y1="25" x2="108" y2="35" stroke="white" strokeWidth="1.2" />

      <line x1="32" y1="20" x2="25" y2="55" stroke="white" strokeWidth="1.2" />
      <line x1="55" y1="28" x2="50" y2="48" stroke="white" strokeWidth="1.2" />
      <line x1="72" y1="15" x2="78" y2="52" stroke="white" strokeWidth="1.2" />

      <line x1="25" y1="55" x2="50" y2="48" stroke="white" strokeWidth="1.2" />
      <line x1="50" y1="48" x2="78" y2="52" stroke="white" strokeWidth="1.2" />
      <line x1="78" y1="52" x2="100" y2="60" stroke="white" strokeWidth="1.2" />

      {/* Star nodes with glow */}
      <circle cx="12" cy="30" r="2" fill="white" filter="url(#star-glow)" />
      <circle cx="32" cy="20" r="2" fill="white" filter="url(#star-glow)" />
      <circle cx="55" cy="28" r="1.5" fill="white" filter="url(#star-glow)" />
      <circle cx="72" cy="15" r="2" fill="white" filter="url(#star-glow)" />
      <circle cx="95" cy="25" r="1.5" fill="white" filter="url(#star-glow)" />
      <circle cx="108" cy="35" r="2" fill="white" filter="url(#star-glow)" />
      <circle cx="25" cy="55" r="1.5" fill="white" filter="url(#star-glow)" />
      <circle cx="50" cy="48" r="2" fill="white" filter="url(#star-glow)" />
      <circle cx="78" cy="52" r="1.5" fill="white" filter="url(#star-glow)" />
      <circle cx="100" cy="60" r="2" fill="white" filter="url(#star-glow)" />

      {/* Accent stars (smaller, semi-transparent) */}
      <circle cx="42" cy="10" r="1" fill="white" opacity="0.6" />
      <circle cx="85" cy="42" r="1" fill="white" opacity="0.6" />
      <circle cx="62" cy="68" r="1" fill="white" opacity="0.5" />
    </svg>
  )
})
