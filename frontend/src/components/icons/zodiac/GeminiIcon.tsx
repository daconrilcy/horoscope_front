import type { SVGProps } from 'react'

export function GeminiIcon(props: SVGProps<SVGSVGElement>) {
  return (
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" role="img" aria-label="Gémeaux" {...props}>
      <path
        d="M1.871 1.882
          C12.259 7.776 19.925 9.848 31.839 9.979
          C44.245 10.114 51.375 8.21 62.081 1.882
          M1.871 62.352
          C12.279 56.512 19.933 54.463 31.839 54.334
          C44.238 54.199 51.352 56.082 62.081 62.352
          M16.877 55.155
          V9.979
          M46.442 55.155
          V9.979"
        fill="none"
        stroke="currentColor"
        strokeWidth={3.8}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}
