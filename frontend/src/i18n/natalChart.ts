import type { AstrologyLang } from "./astrology"

type NatalChartGuideTranslations = {
  title: string
  intro: string
  signsTitle: string
  signsDesc: string
  signExample: string
  planetsTitle: string
  planetsDesc: string
  housesTitle: string
  housesIntervalTitle: string
  housesIntervalDesc: string
  wrapTitle: string
  wrapDesc: string
  wrapExample: string
  ascendantTitle: string
  ascendantDesc: string
  ascendantMissing: string
}

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
  generateNow: string
  generating: string
  generateError: string
  retry: string
  generatedOn: string
  referenceVersion: string
  rulesetVersion: string
  houseSystem: string
  equalHouseSystem: string
  sections: {
    planets: string
    houses: string
    aspects: string
  }
  noAspects: string
  cuspide: string
  angle: string
  orb: string
  wrapConnector: string
  guide: NatalChartGuideTranslations
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
    generateNow: "Générer mon thème natal",
    generating: "Génération en cours...",
    generateError: "Impossible de générer le thème pour le moment. Veuillez réessayer.",
    retry: "Réessayer",
    generatedOn: "Généré le",
    referenceVersion: "Version référentiel",
    rulesetVersion: "Ruleset",
    houseSystem: "Système de maisons",
    equalHouseSystem: "Maisons égales",
    sections: {
      planets: "Planètes",
      houses: "Maisons",
      aspects: "Aspects majeurs",
    },
    noAspects: "Aucun aspect majeur détecté pour ce calcul.",
    cuspide: "cuspide",
    angle: "angle",
    orb: "orbe",
    wrapConnector: "puis 0°",
    guide: {
      title: "Comment lire ton thème natal",
      intro:
        "Cette page affiche les résultats du calcul (référentiel et ruleset indiqués en en-tête) et les conventions utilisées pour convertir les données astronomiques simplifiées en informations lisibles.",
      signsTitle: "Les signes",
      signsDesc:
        "Le zodiaque est divisé en 12 signes de 30° chacun : Bélier (0°), Taureau (30°), Gémeaux (60°), Cancer (90°), Lion (120°), Vierge (150°), Balance (180°), Scorpion (210°), Sagittaire (240°), Capricorne (270°), Verseau (300°), Poissons (330°). Une position est donnée par une longitude écliptique (0–360°), puis convertie en signe + degré dans le signe.",
      signExample: "Soleil 34,08° → Taureau 4°05′ (car Taureau commence à 30°)",
      planetsTitle: "Les planètes",
      planetsDesc:
        "Chaque planète est positionnée par sa longitude (0–360°). La liste affiche : Planète — Signe et degré (longitude brute), Maison — Thème (intervalle de maison). Le degré affiché (ex. 19°47′) correspond au décalage à l'intérieur du signe (0° à 29°59′).",
      housesTitle: "Les maisons",
      housesIntervalTitle: "Convention d'appartenance: intervalle semi-ouvert [début, fin)",
      housesIntervalDesc:
        "Le système utilisé est affiché en en-tête (ici : Maisons égales). Chaque maison correspond à un intervalle de longitudes, défini par sa cuspide (début) et la cuspide de la maison suivante (fin). La cuspide est le point d'ouverture de la maison sur le cercle zodiacal. Si une planète est exactement sur la cuspide de fin d'une maison, elle appartient à la maison suivante. Exemple (principe) : si une maison couvre 18,46° → 48,46°, alors 48,46° appartient à la maison suivante.",
      wrapTitle: "Dépassement de 360°",
      wrapDesc:
        "Certaines maisons traversent 0°. Dans ce cas, l'intervalle wrap couvre la fin du cercle puis son début.",
      wrapExample: "Exemple: 348,46° → 360° puis 0° → 18,46°",
      ascendantTitle: "Ascendant",
      ascendantDesc:
        "L'ascendant correspond au signe de la cuspide de la Maison I. Il dépend de l'heure et du lieu de naissance, et il est calculé selon le référentiel indiqué en en-tête.",
      ascendantMissing:
        "L'heure de naissance n'est pas renseignée\u00a0: l'ascendant n'est pas calculé.",
    },
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
    generateNow: "Generate my natal chart",
    generating: "Generating...",
    generateError: "Unable to generate the chart right now. Please try again.",
    retry: "Retry",
    generatedOn: "Generated on",
    referenceVersion: "Reference version",
    rulesetVersion: "Ruleset",
    houseSystem: "House system",
    equalHouseSystem: "Equal houses",
    sections: {
      planets: "Planets",
      houses: "Houses",
      aspects: "Major aspects",
    },
    noAspects: "No major aspects detected for this calculation.",
    cuspide: "cusp",
    angle: "angle",
    orb: "orb",
    wrapConnector: "then 0°",
    guide: {
      title: "How to read your natal chart",
      intro: "Understanding the calculation conventions and representations used on this page.",
      signsTitle: "Signs",
      signsDesc:
        "The zodiac is divided into 12 signs of 30° each: Aries (0°), Taurus (30°), Gemini (60°), Cancer (90°), Leo (120°), Virgo (150°), Libra (180°), Scorpio (210°), Sagittarius (240°), Capricorn (270°), Aquarius (300°), Pisces (330°).",
      signExample: "Sun 34.08° → Taurus 4°05′ (Taurus starts at 30°)",
      planetsTitle: "Planets",
      planetsDesc:
        "Each planet is positioned by its ecliptic longitude (0–360°), converted to sign and degree within the sign. The list shows: Planet — Sign Degree (raw longitude), House (house interval).",
      housesTitle: "Houses",
      housesIntervalTitle: "Membership convention: semi-open interval [start, end)",
      housesIntervalDesc:
        "If a planet is exactly on the end cusp of a house, it belongs to the next house. Example: if House I spans from 18.46° to 48.46°, a planet at exactly 48.46° is in House II.",
      wrapTitle: "Crossing 360°",
      wrapDesc: "When a house crosses 0°, the interval is shown with the 360° break.",
      wrapExample: "Example: 348.46° → 360° then 0° → 18.46°",
      ascendantTitle: "Ascendant",
      ascendantDesc:
        "The ascendant is the degree of the ecliptic rising on the eastern horizon at the time of birth. It is calculated from the birth time and location.",
      ascendantMissing: "Birth time is not provided: the ascendant is not calculated.",
    },
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
    generateNow: "Generar mi carta natal",
    generating: "Generando...",
    generateError: "No se puede generar la carta en este momento. Inténtalo de nuevo.",
    retry: "Reintentar",
    generatedOn: "Generado el",
    referenceVersion: "Versión de referencia",
    rulesetVersion: "Conjunto de reglas",
    houseSystem: "Sistema de casas",
    equalHouseSystem: "Casas iguales",
    sections: {
      planets: "Planetas",
      houses: "Casas",
      aspects: "Aspectos mayores",
    },
    noAspects: "No se detectaron aspectos mayores para este cálculo.",
    cuspide: "cúspide",
    angle: "ángulo",
    orb: "orbe",
    wrapConnector: "luego 0°",
    guide: {
      title: "Cómo leer tu carta natal",
      intro: "Comprende las convenciones de cálculo y las representaciones usadas en esta página.",
      signsTitle: "Los signos",
      signsDesc:
        "El zodíaco está dividido en 12 signos de 30° cada uno: Aries (0°), Tauro (30°), Géminis (60°), Cáncer (90°), Leo (120°), Virgo (150°), Libra (180°), Escorpio (210°), Sagitario (240°), Capricornio (270°), Acuario (300°), Piscis (330°).",
      signExample: "Sol 34,08° → Tauro 4°05′ (Tauro comienza en 30°)",
      planetsTitle: "Los planetas",
      planetsDesc:
        "Cada planeta está posicionado por su longitud eclíptica (0–360°), convertida en signo y grado dentro del signo. La lista muestra: Planeta — Signo Grado (longitud bruta), Casa (intervalo de la casa).",
      housesTitle: "Las casas",
      housesIntervalTitle: "Convención de pertenencia: intervalo semiabierto [inicio, fin)",
      housesIntervalDesc:
        "Si un planeta está exactamente en la cúspide de fin de una casa, pertenece a la siguiente casa. Ejemplo: si la Casa I va de 18,46° a 48,46°, un planeta a exactamente 48,46° está en Casa II.",
      wrapTitle: "Cruce de 360°",
      wrapDesc: "Cuando una casa atraviesa 0°, el intervalo se muestra con el corte en 360°.",
      wrapExample: "Ejemplo: 348,46° → 360° luego 0° → 18,46°",
      ascendantTitle: "Ascendente",
      ascendantDesc:
        "El ascendente es el grado de la eclíptica que asciende por el horizonte este en el momento del nacimiento. Se calcula a partir de la hora y el lugar de nacimiento.",
      ascendantMissing: "La hora de nacimiento no está registrada: el ascendente no se calcula.",
    },
  },
}
