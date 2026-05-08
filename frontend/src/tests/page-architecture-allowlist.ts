// Declare les exceptions exactes de l'architecture des pages avec owner et sortie.
export type PageArchitectureException = {
  file: string
  owner: string
  reason: string
  exit: string
}

export const TS_NOCHECK_PAGE_EXCEPTIONS: PageArchitectureException[] = []

export const DIRECT_API_PAGE_EXCEPTIONS: PageArchitectureException[] = []

export const PAGE_SIZE_EXCEPTIONS: Array<PageArchitectureException & { maxLines: number }> = []

export const FORBIDDEN_PUBLIC_ROUTE_ALIASES = [
  `/${"today"}`,
  `/${"natal"}-${"chart"}`,
  `/${"birth"}-${"profile"}`,
] as const
export const FORBIDDEN_ADMIN_BARREL_EXPORTS = [`Pricing${"Admin"}`, `Monitoring${"Admin"}`] as const
