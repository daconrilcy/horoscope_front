import type { SVGProps } from 'react'

export function PiscesIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Poissons" {...props}>
      <g fill="none" stroke="currentColor" strokeWidth={4} strokeLinecap="round" strokeLinejoin="round">
        <path d="M28 20 C22 26, 22 38, 28 44" />
        <path d="M36 20 C42 26, 42 38, 36 44" />
        <path d="M24 32 H40" />
      </g>
    </svg>
  )
}
