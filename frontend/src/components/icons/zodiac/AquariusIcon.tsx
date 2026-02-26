import type { SVGProps } from 'react'

export function AquariusIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Verseau" {...props}>
      <g fill="none" stroke="currentColor" strokeWidth={4} strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 26 C18 22, 22 22, 26 26 S34 30, 38 26 S46 22, 50 26" />
        <path d="M14 38 C18 34, 22 34, 26 38 S34 42, 38 38 S46 34, 50 38" />
      </g>
    </svg>
  )
}
