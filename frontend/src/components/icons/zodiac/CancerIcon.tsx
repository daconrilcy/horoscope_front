import type { SVGProps } from 'react'

export function CancerIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Cancer" {...props}>
      <g fill="none" stroke="currentColor" strokeWidth={3.8} strokeLinecap="round" strokeLinejoin="round">
        <circle cx={12.025} cy={32.073} r={10.128} />
        <circle cx={51.969} cy={32.073} r={10.128} />
        <path d="M1.89 31.242 C1.89 63.744 39.832 69.748 53.231 53.418" />
        <path d="M61.961 31.993 C61.961 -0.509 24.019 -6.514 10.62 9.817" />
      </g>
    </svg>
  )
}
