// Registre exact des exceptions d'architecture du dossier components.

export type ComponentArchitectureException = {
  file: string
  owner: string
  reason: string
  exitCondition: string
}

export const COMPONENT_API_IMPORT_EXCEPTIONS: ComponentArchitectureException[] = []

export const COMPONENT_TS_NOCHECK_EXCEPTIONS: ComponentArchitectureException[] = []
