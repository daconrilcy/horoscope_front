import type { AstrologyLang } from "./astrology"

export type NatalChartFaqItem = {
  question: string
  answer: string
}

export const DEFAULT_ASTRO_LANG: AstrologyLang = "fr"

export type NatalChartGuideTranslations = {
  title: string
  intro: string
  signsTitle: string
  signsDesc: string
  signExample: string
  planetsTitle: string
  planetsDesc: string
  planetsRetrogradeTip: string
  housesTitle: string
  housesIntervalTitle: string
  housesIntervalDesc: string
  wrapTitle: string
  wrapDesc: string
  wrapExample: string
  anglesTitle: string
  anglesDesc: string
  sunAscendantTitle: string
  sunAscendantDesc: string
  ascendantMissing: string
  aspectsTitle: string
  aspectsDesc: string
  faqTitle: string
  faq: NatalChartFaqItem[]
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
  placidusHouseSystem: string
  kochHouseSystem: string
  regiomontanusHouseSystem: string
  astroProfile: {
    title: string
    sunSign: string
    ascendant: string
    missingTime: string
  }
  sections: {
    planets: string
    houses: string
    aspects: string
  }
  noAspects: string
  cuspide: string
  angle: string
  orb: string
  orbUsed: string
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
    placidusHouseSystem: "Placidus",
    kochHouseSystem: "Koch",
    regiomontanusHouseSystem: "Regiomontanus",
    astroProfile: {
      title: "Profil astrologique",
      sunSign: "Signe solaire",
      ascendant: "Ascendant",
      missingTime: "heure de naissance manquante",
    },
    sections: {
      planets: "Planètes",
      houses: "Maisons",
      aspects: "Les aspects",
    },
    noAspects: "Aucun aspect majeur détecté pour ce calcul.",
    cuspide: "cuspide",
    angle: "angle",
    orb: "orbe",
    orbUsed: "orbe eff.",
    wrapConnector: "puis 0°",
    guide: {
      title: "Comment lire ton thème natal",
      intro:
        "Ton thème natal est une représentation géométrique du ciel au moment et au lieu de ta naissance. Les calculs placent des points (planètes) sur un cercle de 360°. Ensuite, on traduit ces positions en repères lisibles : signes, maisons, angles et aspects.",
      signsTitle: "Les signes astrologiques",
      signsDesc:
        "Le zodiaque est divisé en 12 signes de 30° chacun. Un signe n'est pas une planète : c'est une zone du cercle qui sert de grille de lecture pour exprimer une position. Chaque position astronomique est d'abord une longitude écliptique entre 0° et 360°. Cette longitude est ensuite convertie en un signe (dans quel segment de 30° on se situe) et un degré à l'intérieur du signe (de 0°00' à 29°59'). Les minutes (') sont des sous-unités du degré (1° = 60').",
      signExample: "Soleil 34,08° → Taureau 4°05′ (car Taureau commence à 30°)",
      planetsTitle: "Les planètes",
      planetsDesc:
        "Les planètes (et, en astrologie, le Soleil et la Lune) sont des points placés sur le cercle zodiacal à une longitude précise. Pour chaque planète, l'affichage donne : sa position en signe + degré (lecture humaine), sa longitude brute (valeur de calcul) et la maison dans laquelle elle se situe (secteur du thème).",
      planetsRetrogradeTip:
        "Le symbole ℞ signifie que la planète est en mouvement rétrograde apparent : vue depuis la Terre, elle semble reculer temporairement dans le zodiaque. C'est un état de mouvement apparent, pas un objet supplémentaire.",
      housesTitle: "Les maisons",
      housesIntervalTitle: "Convention d'appartenance : intervalle semi-ouvert [début, fin)",
      housesIntervalDesc:
        "Les maisons découpent le cercle en 12 secteurs calculés à partir du lieu et de l'heure de naissance. Chaque maison commence à une cuspide (son point d'ouverture) et s'étend jusqu'à la cuspide de la maison suivante. Si une planète est exactement sur la cuspide de fin d'une maison, elle appartient à la maison suivante. Le système utilisé est affiché en en-tête, car il change les cuspides et donc la répartition des planètes dans les maisons.",
      wrapTitle: "Passage par 0° (wrap 360°)",
      wrapDesc:
        "Certaines maisons traversent la jonction 360° → 0°. Dans ce cas, l'intervalle boucle : il couvre la fin du cercle puis reprend au début.",
      wrapExample: "Exemple: 348,46° → 360° puis 0° → 18,46°",
      anglesTitle: "Les angles",
      anglesDesc:
        "Les angles sont quatre points de référence majeurs issus des cuspides de maisons clés. Ascendant (ASC) : cuspide de la Maison I, point où le zodiaque coupe l'horizon Est à la naissance. Descendant (DSC) : cuspide de la Maison VII, opposé à l'Ascendant (~180°). Milieu du Ciel (MC) : cuspide de la Maison X, lié au méridien supérieur. Fond du Ciel (IC) : cuspide de la Maison IV, opposé au MC (~180°). En pratique, \"Ascendant\" correspond au signe qui contient la cuspide de la Maison I, et MC au signe qui contient la cuspide de la Maison X.",
      sunAscendantTitle: "Signe solaire et ascendant",
      sunAscendantDesc:
        "Le signe solaire est le signe dans lequel se trouve le Soleil au moment de la naissance. L'ascendant est le signe de la cuspide de la Maison I. Ce sont deux repères très utilisés, mais ils proviennent des mêmes données de base : des positions en degrés sur le cercle (pour le Soleil) et des cuspides calculées (pour l'Ascendant).",
      ascendantMissing:
        "L'heure de naissance n'est pas renseignée\u00a0: l'ascendant n'est pas calculé.",
      aspectsTitle: "Les aspects",
      aspectsDesc:
        "Les aspects sont des angles géométriques entre deux planètes, mesurés sur le cercle zodiacal. Chaque aspect correspond à un angle de référence (0°, 60°, 90°, 120°...). L'orbe est l'écart maximal accepté autour de l'angle théorique pour considérer l'aspect comme valide. L'orbe effective (orbe eff.) indique l'écart réel mesuré pour cet aspect spécifique.",
      faqTitle: "FAQ",
      faq: [
        {
          question: "Pourquoi parle-t-on de 360° ?",
          answer:
            "Parce que le thème est représenté comme un cercle complet. Les positions des planètes et des cuspides sont exprimées en degrés sur ce cercle, ce qui permet de calculer facilement maisons et aspects.",
        },
        {
          question: "Pourquoi y a-t-il deux découpages (signes et maisons) ?",
          answer:
            "Les signes sont un découpage fixe du zodiaque (12 x 30°), identique pour tout le monde. Les maisons sont un découpage local calculé à partir du lieu et de l'heure de naissance, donc spécifique à chaque personne.",
        },
        {
          question: "Qu'est-ce qu'une longitude brute ?",
          answer:
            "C'est la valeur numérique (0-360°) utilisée pour les calculs. L'affichage signe + degré est une conversion plus lisible de cette même valeur.",
        },
        {
          question: "Qu'est-ce qu'une cuspide ?",
          answer:
            "C'est le point de départ d'une maison. Les cuspides sont des repères calculés sur le cercle, qui définissent les limites des secteurs (maisons).",
        },
        {
          question: "Pourquoi certaines maisons semblent bizarres ou traversent 0° ?",
          answer:
            "Parce que le cercle n'a pas de début réel : 360° et 0° sont le même point. Si une maison démarre près de la fin du cercle, elle peut continuer après 0°.",
        },
        {
          question: "À quoi sert l'orbe dans les aspects ?",
          answer:
            "L'orbe sert de tolérance. Sans orbe, presque aucun aspect ne serait exact. Avec l'orbe, on retient les angles proches d'un angle de référence.",
        },
        {
          question: "Que signifie le symbole ℞ ?",
          answer:
            "℞ indique une rétrogradation apparente : depuis la Terre, la planète semble reculer temporairement dans le zodiaque. C'est une information de mouvement apparent issue des éphémérides.",
        },
        {
          question: "Pourquoi le signe solaire et l'ascendant sont-ils mis en avant ?",
          answer:
            "Parce que ce sont deux repères très utilisés : l'un est la position du Soleil (un point), l'autre est un angle issu des maisons (une cuspide). Ils résument des éléments différents de la structure du thème, sans être une interprétation à eux seuls.",
        },
      ],
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
    placidusHouseSystem: "Placidus",
    kochHouseSystem: "Koch",
    regiomontanusHouseSystem: "Regiomontanus",
    astroProfile: {
      title: "Astro Profile",
      sunSign: "Sun sign",
      ascendant: "Ascendant",
      missingTime: "birth time missing",
    },
    sections: {
      planets: "Planets",
      houses: "Houses",
      aspects: "Aspects",
    },
    noAspects: "No major aspects detected for this calculation.",
    cuspide: "cusp",
    angle: "angle",
    orb: "orb",
    orbUsed: "eff. orb",
    wrapConnector: "then 0°",
    guide: {
      title: "How to read your natal chart",
      intro:
        "Your natal chart is a geometric snapshot of the sky at the moment and place of your birth. Calculations place points (planets) on a 360° circle, then translate positions into readable markers: signs, houses, angles and aspects.",
      signsTitle: "Zodiac signs",
      signsDesc:
        "The zodiac is divided into 12 signs of 30° each. A sign is not a planet: it is a zone of the circle used as a reading grid to express a position. Each astronomical position is first an ecliptic longitude between 0° and 360°, then converted into a sign (which 30° segment) and a degree within the sign (0°00' to 29°59').",
      signExample: "Sun 34.08° → Taurus 4°05′ (Taurus starts at 30°)",
      planetsTitle: "Planets",
      planetsDesc:
        "Planets (including the Sun and Moon in astrology) are points placed on the zodiacal circle at a precise longitude. For each planet, the display shows: its position in sign + degree (human-readable), its raw longitude (calculation value) and the house it occupies (chart sector).",
      planetsRetrogradeTip:
        "The ℞ symbol means the planet is in apparent retrograde motion: seen from Earth, it appears to temporarily move backwards through the zodiac. It is a state of apparent motion, not an additional object.",
      housesTitle: "Houses",
      housesIntervalTitle: "Membership convention: semi-open interval [start, end)",
      housesIntervalDesc:
        "Houses divide the circle into 12 sectors calculated from the birth place and time. Each house begins at a cusp (its opening point) and extends to the next house cusp. If a planet falls exactly on the end cusp of a house, it belongs to the next house. The house system is shown in the header, as it changes the cusps and the distribution of planets.",
      wrapTitle: "Crossing 360°",
      wrapDesc:
        "Some houses cross the 360° → 0° junction. In this case, the interval wraps: it covers the end of the circle then continues from the beginning.",
      wrapExample: "Example: 348.46° → 360° then 0° → 18.46°",
      anglesTitle: "Angles",
      anglesDesc:
        "Angles are four major reference points derived from key house cusps. Ascendant (ASC): House I cusp, the point where the zodiac crosses the eastern horizon at birth. Descendant (DSC): House VII cusp, opposite the Ascendant (~180°). Midheaven (MC): House X cusp, linked to the upper meridian. Imum Coeli (IC): House IV cusp, opposite the MC (~180°). In practice, 'Ascendant' refers to the sign containing House I cusp, and MC to the sign containing House X cusp.",
      sunAscendantTitle: "Sun sign and ascendant",
      sunAscendantDesc:
        "The sun sign is the sign where the Sun is located at birth. The ascendant is the sign of House I cusp. These are two widely used markers, but they come from the same base data: degree positions on the circle (for the Sun) and calculated cusps (for the Ascendant).",
      ascendantMissing: "Birth time is not provided: the ascendant is not calculated.",
      aspectsTitle: "Aspects",
      aspectsDesc:
        "Aspects are geometric angles between two planets, measured on the zodiacal circle. Each aspect corresponds to a reference angle (0°, 60°, 90°, 120°...). The orb is the maximum deviation accepted around the theoretical angle for an aspect to be considered valid. The effective orb (eff. orb) indicates the actual measured deviation for this specific aspect.",
      faqTitle: "FAQ",
      faq: [
        {
          question: "Why do we talk about 360°?",
          answer:
            "Because the chart is represented as a complete circle. Planet and cusp positions are expressed in degrees on this circle, making it easy to calculate houses and aspects.",
        },
        {
          question: "Why are there two divisions (signs and houses)?",
          answer:
            "Signs are a fixed zodiac division (12 × 30°), the same for everyone. Houses are a local division calculated from the birth place and time, specific to each person.",
        },
        {
          question: "What is a raw longitude?",
          answer:
            "It is the numerical value (0-360°) used for calculations. The sign + degree display is a more readable conversion of that same value.",
        },
        {
          question: "What is a cusp?",
          answer:
            "It is the starting point of a house. Cusps are calculated markers on the circle that define the boundaries of the sectors (houses).",
        },
        {
          question: "Why do some houses look unusual or cross 0°?",
          answer:
            "Because the circle has no real beginning: 360° and 0° are the same point. If a house starts near the end of the circle, it can continue after 0°.",
        },
        {
          question: "What is the orb used for in aspects?",
          answer:
            "The orb serves as a tolerance. Without an orb, almost no aspect would be exact. With the orb, angles close to a reference angle are included.",
        },
        {
          question: "What does the ℞ symbol mean?",
          answer:
            "℞ indicates apparent retrograde motion: from Earth, the planet appears to temporarily move backwards through the zodiac. It is apparent motion information from the ephemeris.",
        },
        {
          question: "Why are the sun sign and ascendant highlighted?",
          answer:
            "Because they are two widely used markers: one is the Sun's position (a point), the other is an angle from the houses (a cusp). They summarize different elements of the chart structure, not interpretations by themselves.",
        },
      ],
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
    placidusHouseSystem: "Placidus",
    kochHouseSystem: "Koch",
    regiomontanusHouseSystem: "Regiomontanus",
    astroProfile: {
      title: "Perfil astrológico",
      sunSign: "Signo solar",
      ascendant: "Ascendente",
      missingTime: "hora de nacimiento no disponible",
    },
    sections: {
      planets: "Planetas",
      houses: "Casas",
      aspects: "Los aspectos",
    },
    noAspects: "No se detectaron aspectos mayores para este cálculo.",
    cuspide: "cúspide",
    angle: "ángulo",
    orb: "orbe",
    orbUsed: "orbe efec.",
    wrapConnector: "luego 0°",
    guide: {
      title: "Cómo leer tu carta natal",
      intro:
        "Tu carta natal es una representación geométrica del cielo en el momento y lugar de tu nacimiento. Los cálculos sitúan puntos (planetas) en un círculo de 360°. Luego, estas posiciones se traducen en referencias legibles: signos, casas, ángulos y aspectos.",
      signsTitle: "Los signos zodiacales",
      signsDesc:
        "El zodíaco está dividido en 12 signos de 30° cada uno. Un signo no es un planeta: es una zona del círculo que sirve de cuadrícula para expresar una posición. Cada posición astronómica es primero una longitud eclíptica entre 0° y 360°, que luego se convierte en un signo (en qué segmento de 30°) y un grado dentro del signo (de 0°00' a 29°59').",
      signExample: "Sol 34,08° → Tauro 4°05′ (Tauro comienza en 30°)",
      planetsTitle: "Los planetas",
      planetsDesc:
        "Los planetas (y, en astrología, el Sol y la Luna) son puntos situados en el círculo zodiacal a una longitud precisa. Para cada planeta, se muestra: su posición en signo + grado (lectura humana), su longitud bruta (valor de cálculo) y la casa en la que se encuentra (sector del tema).",
      planetsRetrogradeTip:
        "El símbolo ℞ indica que el planeta está en movimiento retrógrado aparente: visto desde la Tierra, parece retroceder temporalmente en el zodíaco. Es un estado de movimiento aparente, no un objeto adicional.",
      housesTitle: "Las casas",
      housesIntervalTitle: "Convención de pertenencia: intervalo semiabierto [inicio, fin)",
      housesIntervalDesc:
        "Las casas dividen el círculo en 12 sectores calculados a partir del lugar y la hora de nacimiento. Cada casa comienza en una cúspide (su punto de apertura) y se extiende hasta la cúspide de la siguiente casa. Si un planeta cae exactamente en la cúspide de fin de una casa, pertenece a la siguiente. El sistema de casas se indica en el encabezado, ya que cambia las cúspides y la distribución de los planetas.",
      wrapTitle: "Cruce de 360°",
      wrapDesc:
        "Algunas casas atraviesan la unión 360° → 0°. En ese caso, el intervalo da la vuelta: cubre el final del círculo y continúa desde el principio.",
      wrapExample: "Ejemplo: 348,46° → 360° luego 0° → 18,46°",
      anglesTitle: "Los ángulos",
      anglesDesc:
        "Los ángulos son cuatro puntos de referencia principales derivados de las cúspides de las casas clave. Ascendente (ASC): cúspide de la Casa I, punto donde el zodíaco cruza el horizonte Este al nacer. Descendente (DSC): cúspide de la Casa VII, opuesto al Ascendente (~180°). Medio Cielo (MC): cúspide de la Casa X, ligado al meridiano superior. Fondo del Cielo (IC): cúspide de la Casa IV, opuesto al MC (~180°). En la práctica, 'Ascendente' es el signo que contiene la cúspide de la Casa I, y MC el signo que contiene la cúspide de la Casa X.",
      sunAscendantTitle: "Signo solar y ascendente",
      sunAscendantDesc:
        "El signo solar es el signo donde se encuentra el Sol en el momento del nacimiento. El ascendente es el signo de la cúspide de la Casa I. Son dos referencias muy usadas, pero provienen de los mismos datos base: posiciones en grados sobre el círculo (para el Sol) y cúspides calculadas (para el Ascendente).",
      ascendantMissing: "La hora de nacimiento no está registrada: el ascendente no se calcula.",
      aspectsTitle: "Los aspectos",
      aspectsDesc:
        "Los aspectos son ángulos geométricos entre dos planetas, medidos en el círculo zodiacal. Cada aspecto corresponde a un ángulo de referencia (0°, 60°, 90°, 120°...). El orbe es la desviación máxima aceptada alrededor del ángulo teórico para que un aspecto sea válido. El orbe efectivo (orbe efec.) indica la desviación real medida para ese aspecto específico.",
      faqTitle: "FAQ",
      faq: [
        {
          question: "¿Por qué se habla de 360°?",
          answer:
            "Porque la carta se representa como un círculo completo. Las posiciones de los planetas y las cúspides se expresan en grados sobre ese círculo, lo que facilita calcular casas y aspectos.",
        },
        {
          question: "¿Por qué hay dos divisiones (signos y casas)?",
          answer:
            "Los signos son una división fija del zodíaco (12 × 30°), igual para todos. Las casas son una división local calculada a partir del lugar y la hora de nacimiento, específica para cada persona.",
        },
        {
          question: "¿Qué es una longitud bruta?",
          answer:
            "Es el valor numérico (0-360°) utilizado para los cálculos. La representación signo + grado es una conversión más legible de ese mismo valor.",
        },
        {
          question: "¿Qué es una cúspide?",
          answer:
            "Es el punto de inicio de una casa. Las cúspides son referencias calculadas sobre el círculo que definen los límites de los sectores (casas).",
        },
        {
          question: "¿Por qué algunas casas parecen extrañas o cruzan el 0°?",
          answer:
            "Porque el círculo no tiene un inicio real: 360° y 0° son el mismo punto. Si una casa empieza cerca del final del círculo, puede continuar después del 0°.",
        },
        {
          question: "¿Para qué sirve el orbe en los aspectos?",
          answer:
            "El orbe sirve de tolerancia. Sin orbe, casi ningún aspecto sería exacto. Con el orbe, se incluyen los ángulos próximos a un ángulo de referencia.",
        },
        {
          question: "¿Qué significa el símbolo ℞?",
          answer:
            "℞ indica un movimiento retrógrado aparente: desde la Tierra, el planeta parece retroceder temporalmente en el zodíaco. Es información de movimiento aparente procedente de las efemérides.",
        },
        {
          question: "¿Por qué se destacan el signo solar y el ascendente?",
          answer:
            "Porque son dos referencias muy usadas: una es la posición del Sol (un punto), la otra es un ángulo de las casas (una cúspide). Resumen elementos diferentes de la estructura de la carta, sin ser interpretaciones por sí solos.",
        },
      ],
    },
  },
}

/**
 * Retourne les traductions du guide natal pour la langue donnée.
 * Si la langue n'est pas dans le dictionnaire (runtime), fallback sur la langue par défaut.
 * Cela garantit qu'aucune section du guide ne peut être vide ou provoquer un crash.
 */
export function getGuideTranslations(lang: AstrologyLang): NatalChartGuideTranslations {
  return natalChartTranslations[lang]?.guide ?? natalChartTranslations[DEFAULT_ASTRO_LANG].guide
}
