import type { AstrologyLang } from "./astrology"

type NatalChartTranslations = {
  title: string
  loading: string
  notFound: string
  notFoundSub: string
  noData: string
  incompleteData: string
  incompleteDataSub: string
  completeProfile: string
  genericError: string
  retry: string
  generatedOn: string
  referenceVersion: string
  rulesetVersion: string
  sections: {
    planets: string
    houses: string
    aspects: string
  }
  noAspects: string
  cuspide: string
  angle: string
  orb: string
}

export const natalChartTranslations: Record<AstrologyLang, NatalChartTranslations> = {
  fr: {
    title: "Thème natal",
    loading: "Chargement de votre dernier thème natal...",
    notFound: "Aucun thème natal disponible pour le moment.",
    notFoundSub: "Générez d'abord votre thème initial pour afficher cette page.",
    noData: "Aucune donnée de thème disponible pour le moment.",
    incompleteData: "Vos données de naissance sont incomplètes.",
    incompleteDataSub: "Complétez votre profil pour générer votre thème natal.",
    completeProfile: "Compléter mon profil",
    genericError: "Une erreur est survenue. Veuillez réessayer ultérieurement.",
    retry: "Réessayer",
    generatedOn: "Généré le",
    referenceVersion: "Version référentiel",
    rulesetVersion: "Ruleset",
    sections: {
      planets: "Planètes",
      houses: "Maisons",
      aspects: "Aspects majeurs",
    },
    noAspects: "Aucun aspect majeur détecté pour ce calcul.",
    cuspide: "cuspide",
    angle: "angle",
    orb: "orbe",
  },
  en: {
    title: "Natal Chart",
    loading: "Loading your latest natal chart...",
    notFound: "No natal chart available at the moment.",
    notFoundSub: "Generate your initial chart first to view this page.",
    noData: "No chart data available at the moment.",
    incompleteData: "Your birth data is incomplete.",
    incompleteDataSub: "Complete your profile to generate your natal chart.",
    completeProfile: "Complete my profile",
    genericError: "An error occurred. Please try again later.",
    retry: "Retry",
    generatedOn: "Generated on",
    referenceVersion: "Reference version",
    rulesetVersion: "Ruleset",
    sections: {
      planets: "Planets",
      houses: "Houses",
      aspects: "Major aspects",
    },
    noAspects: "No major aspects detected for this calculation.",
    cuspide: "cusp",
    angle: "angle",
    orb: "orb",
  },
  es: {
    title: "Carta Natal",
    loading: "Cargando tu última carta natal...",
    notFound: "No hay carta natal disponible por el momento.",
    notFoundSub: "Genera primero tu carta inicial para ver esta página.",
    noData: "No hay datos de carta disponibles por el momento.",
    incompleteData: "Tus datos de nacimiento están incompletos.",
    incompleteDataSub: "Completa tu perfil para generar tu carta natal.",
    completeProfile: "Completar mi perfil",
    genericError: "Ocurrió un error. Por favor, inténtalo más tarde.",
    retry: "Reintentar",
    generatedOn: "Generado el",
    referenceVersion: "Versión de referencia",
    rulesetVersion: "Conjunto de reglas",
    sections: {
      planets: "Planetas",
      houses: "Casas",
      aspects: "Aspectos mayores",
    },
    noAspects: "No se detectaron aspectos mayores para este cálculo.",
    cuspide: "cúspide",
    angle: "ángulo",
    orb: "orbe",
  },
}
