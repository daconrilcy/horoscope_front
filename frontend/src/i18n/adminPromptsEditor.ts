import type { AstrologyLang } from "./astrology"

export type AdminPromptsEditorStrings = {
  sectionTitle: string
  sectionIntro: string
  currentStatusLabel: string
  basedOnLabel: string
  basedOnHint: string
  noBaseVersion: string
  developerPromptLabel: string
  developerPromptHint: string
  modelLabel: string
  modelHint: string
  temperatureLabel: string
  temperatureHint: string
  maxOutputTokensLabel: string
  maxOutputTokensHint: string
  fallbackUseCaseLabel: string
  fallbackUseCaseHint: string
  fallbackEmptyOption: string
  summaryTitle: string
  summaryEmpty: string
  summaryDeveloperPrompt: (beforeChars: number, afterChars: number) => string
  summaryModel: (before: string, after: string) => string
  summaryTemperature: (before: number, after: number) => string
  summaryMaxOutputTokens: (before: number, after: number) => string
  summaryFallback: (before: string, after: string) => string
  saving: string
  saveDraft: string
  success: (shortId: string) => string
  backendErrorPrefix: string
  validationDeveloperPromptRequired: string
  validationModelRequired: string
  validationTemperatureNumber: string
  validationTemperatureRange: string
  validationMaxOutputTokensRequired: string
  validationFallbackSameUseCase: string
  statusDraft: string
  statusPublished: string
  statusInactive: string
  statusUnknown: string
  noFallbackSummary: string
}

export const adminPromptsEditorByLang: Record<AstrologyLang, AdminPromptsEditorStrings> = {
  fr: {
    sectionTitle: "Préparer une nouvelle version",
    sectionIntro:
      "Le formulaire crée une nouvelle version non publiée à partir de la version de référence la plus pertinente. La publication reste une action distincte.",
    currentStatusLabel: "Statut courant",
    basedOnLabel: "Version de référence",
    basedOnHint: "Le formulaire est prérempli depuis cette version pour éviter toute édition en JSON brut.",
    noBaseVersion: "Aucune version de référence disponible pour ce cas d'usage.",
    developerPromptLabel: "Prompt développeur",
    developerPromptHint: "Texte principal envoyé au modèle. Conservez les placeholders et la structure métier attendue.",
    modelLabel: "Modèle",
    modelHint: "Nom du modèle utilisé pour cette future version.",
    temperatureLabel: "Température",
    temperatureHint: "Valeur numérique entre 0 et 2. Gardez la variabilité cohérente avec le cas d'usage.",
    maxOutputTokensLabel: "Budget de sortie",
    maxOutputTokensHint: "Nombre maximal de tokens de sortie autorisés pour cette version.",
    fallbackUseCaseLabel: "Fallback use case",
    fallbackUseCaseHint: "Cas d'usage de repli optionnel si la résolution nominale échoue.",
    fallbackEmptyOption: "Aucun fallback",
    summaryTitle: "Résumé des changements avant sauvegarde",
    summaryEmpty: "Aucun changement détecté pour l'instant. Modifiez au moins un champ avant d'enregistrer.",
    summaryDeveloperPrompt: (beforeChars, afterChars) =>
      `Prompt développeur mis à jour (${beforeChars} → ${afterChars} caractères).`,
    summaryModel: (before, after) => `Modèle: ${before} → ${after}.`,
    summaryTemperature: (before, after) => `Température: ${before} → ${after}.`,
    summaryMaxOutputTokens: (before, after) => `Budget de sortie: ${before} → ${after}.`,
    summaryFallback: (before, after) => `Fallback use case: ${before} → ${after}.`,
    saving: "Sauvegarde en cours…",
    saveDraft: "Créer une nouvelle version",
    success: (shortId) =>
      `Nouvelle version non publiée créée (${shortId}…). Elle est maintenant visible dans l'historique.`,
    backendErrorPrefix: "Le backend a refusé la sauvegarde",
    validationDeveloperPromptRequired: "Le prompt développeur est requis.",
    validationModelRequired: "Le modèle est requis.",
    validationTemperatureNumber: "La température doit être un nombre valide.",
    validationTemperatureRange: "La température doit rester comprise entre 0 et 2.",
    validationMaxOutputTokensRequired: "Le budget de sortie doit être un entier strictement positif.",
    validationFallbackSameUseCase: "Le fallback doit pointer vers un autre cas d'usage.",
    statusDraft: "Brouillon",
    statusPublished: "Publié",
    statusInactive: "Inactive",
    statusUnknown: "Statut inconnu",
    noFallbackSummary: "Aucun fallback",
  },
  en: {
    sectionTitle: "Prepare a new version",
    sectionIntro:
      "The form creates a new unpublished version from the most relevant reference version. Publishing remains a separate action.",
    currentStatusLabel: "Current status",
    basedOnLabel: "Reference version",
    basedOnHint: "The form is prefilled from this version to avoid raw JSON editing.",
    noBaseVersion: "No reference version available for this use case.",
    developerPromptLabel: "Developer prompt",
    developerPromptHint: "Main text sent to the model. Keep placeholders and expected business structure.",
    modelLabel: "Model",
    modelHint: "Model name used for this future version.",
    temperatureLabel: "Temperature",
    temperatureHint: "Numeric value between 0 and 2. Keep variability aligned with the use case.",
    maxOutputTokensLabel: "Output budget",
    maxOutputTokensHint: "Maximum output tokens allowed for this version.",
    fallbackUseCaseLabel: "Fallback use case",
    fallbackUseCaseHint: "Optional fallback use case if nominal resolution fails.",
    fallbackEmptyOption: "No fallback",
    summaryTitle: "Change summary before save",
    summaryEmpty: "No changes detected yet. Update at least one field before saving.",
    summaryDeveloperPrompt: (beforeChars, afterChars) =>
      `Developer prompt updated (${beforeChars} → ${afterChars} characters).`,
    summaryModel: (before, after) => `Model: ${before} → ${after}.`,
    summaryTemperature: (before, after) => `Temperature: ${before} → ${after}.`,
    summaryMaxOutputTokens: (before, after) => `Output budget: ${before} → ${after}.`,
    summaryFallback: (before, after) => `Fallback use case: ${before} → ${after}.`,
    saving: "Saving…",
    saveDraft: "Create a new version",
    success: (shortId) =>
      `New unpublished version created (${shortId}…). It is now visible in history.`,
    backendErrorPrefix: "Backend rejected the save",
    validationDeveloperPromptRequired: "Developer prompt is required.",
    validationModelRequired: "Model is required.",
    validationTemperatureNumber: "Temperature must be a valid number.",
    validationTemperatureRange: "Temperature must stay between 0 and 2.",
    validationMaxOutputTokensRequired: "Output budget must be a positive integer.",
    validationFallbackSameUseCase: "Fallback must target another use case.",
    statusDraft: "Draft",
    statusPublished: "Published",
    statusInactive: "Inactive",
    statusUnknown: "Unknown status",
    noFallbackSummary: "No fallback",
  },
  es: {
    sectionTitle: "Preparar una nueva versión",
    sectionIntro:
      "El formulario crea una nueva versión no publicada a partir de la versión de referencia más pertinente. La publicación sigue siendo una acción aparte.",
    currentStatusLabel: "Estado actual",
    basedOnLabel: "Versión de referencia",
    basedOnHint: "El formulario se rellena a partir de esta versión para evitar editar JSON bruto.",
    noBaseVersion: "No hay una versión de referencia disponible para este caso de uso.",
    developerPromptLabel: "Prompt de desarrollador",
    developerPromptHint: "Texto principal enviado al modelo. Mantenga los placeholders y la estructura esperada.",
    modelLabel: "Modelo",
    modelHint: "Nombre del modelo usado para esta futura versión.",
    temperatureLabel: "Temperatura",
    temperatureHint: "Valor numérico entre 0 y 2. Mantenga una variabilidad coherente con el caso de uso.",
    maxOutputTokensLabel: "Presupuesto de salida",
    maxOutputTokensHint: "Número máximo de tokens de salida permitidos para esta versión.",
    fallbackUseCaseLabel: "Fallback use case",
    fallbackUseCaseHint: "Caso de uso alternativo opcional si falla la resolución nominal.",
    fallbackEmptyOption: "Sin fallback",
    summaryTitle: "Resumen de cambios antes de guardar",
    summaryEmpty: "Aún no hay cambios detectados. Modifique al menos un campo antes de guardar.",
    summaryDeveloperPrompt: (beforeChars, afterChars) =>
      `Prompt de desarrollador actualizado (${beforeChars} → ${afterChars} caracteres).`,
    summaryModel: (before, after) => `Modelo: ${before} → ${after}.`,
    summaryTemperature: (before, after) => `Temperatura: ${before} → ${after}.`,
    summaryMaxOutputTokens: (before, after) => `Presupuesto de salida: ${before} → ${after}.`,
    summaryFallback: (before, after) => `Fallback use case: ${before} → ${after}.`,
    saving: "Guardado en curso…",
    saveDraft: "Crear una nueva versión",
    success: (shortId) =>
      `Nueva versión no publicada creada (${shortId}…). Ahora es visible en el historial.`,
    backendErrorPrefix: "El backend rechazó el guardado",
    validationDeveloperPromptRequired: "El prompt de desarrollador es obligatorio.",
    validationModelRequired: "El modelo es obligatorio.",
    validationTemperatureNumber: "La temperatura debe ser un número válido.",
    validationTemperatureRange: "La temperatura debe mantenerse entre 0 y 2.",
    validationMaxOutputTokensRequired: "El presupuesto de salida debe ser un entero positivo.",
    validationFallbackSameUseCase: "El fallback debe apuntar a otro caso de uso.",
    statusDraft: "Borrador",
    statusPublished: "Publicado",
    statusInactive: "Inactiva",
    statusUnknown: "Estado desconocido",
    noFallbackSummary: "Sin fallback",
  },
}
