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
  basicTitle: string
  completeTitle: string
  loading: string
  notFound: string
  notFoundSub: string
  noData: string
  incompleteData: string
  incompleteDataSub: string
  completeProfile: string
  genericError: string
  backToDashboard: string
  generateNow: string
  generating: string
  generateError: string
  retry: string
  unlockCompleteInterpretation: string
  requestAnotherAstrologer: string
  interpretedByLabel: string
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
  planetsLead: string
  housesLead: string
  aspectsLead: string
  cuspide: string
  angle: string
  orb: string
  orbUsed: string
  positionLabel: string
  longitudeLabel: string
  houseLabel: string
  houseIntervalLabel: string
  cuspLongitudeLabel: string
  houseSignLabel: string
  aspectPlanetsLabel: string
  aspectExactAngleLabel: string
  aspectMeaningLabel: string
  aspectMeaningMap: Record<string, string>
  wrapConnector: string
  interpretation: {
    loading: string
    title: string
    upsellTitle: string
    upsellCta: string
    upgradeToBasicCta: string
    upsellDescription: string
    completeBy: string
    completeBadge: string
    highlightsTitle: string
    adviceTitle: string
    lockedAdviceBullets: string[]
    lockedAdviceBody: string
    evidenceTitle: string
    evidenceIntro: string
    showEvidence: string
    hideEvidence: string
    disclaimerTitle: string
    legalNoticeLines: string[]
    error: string
    retry: string
    regenerate: string
    degradedNotice: string
    requestingComplete: string
    personaSelectorTitle: string
    personaSelectorConfirm: string
    cancel: string
    generatedOnLabel: string
    standardVersionLabel: string
    summaryBadge: string
    shortBadge: string
    historyTitle: string
    deleteConfirm: string
    deleteConfirmSub: string
    deleteCta: string
    templateLabel: string
    historyGroupLabel: string
    pdfGroupLabel: string
    previewPdf: string
    downloadPdf: string
    pdfActionsLabel: string
    versionLabel: string
    noHistory: string
    allAstrologersUsed: string
    evidenceEmpty: string
    dedupedCount: (count: number) => string
    sectionsMap: Record<string, string>
    evidenceCategories: {
      angles: string
      personalPlanets: string
      slowPlanets: string
      dominantHouses: string
      majorAspects: string
      other: string
    }
  }
  guide: NatalChartGuideTranslations
}

export type NatalChartTranslation = NatalChartTranslations;
export const natalChartTranslations: Record<AstrologyLang, NatalChartTranslations> = {
  fr: {
    title: "Thème natal",
    basicTitle: "Thème natal de base",
    completeTitle: "Thème natal complet",
    loading: "Chargement de votre dernier thème natal...",
    notFound: "Aucun thème natal disponible pour le moment.",
    notFoundSub: "Générez d'abord votre thème initial pour afficher cette page.",
    noData: "Aucune donnée de thème disponible pour le moment.",
    incompleteData: "Vos données de naissance sont incomplètes.",
    incompleteDataSub: "Complétez votre profil pour générer votre thème natal.",
    completeProfile: "Compléter mon profil",
    genericError: "Une erreur est survenue. Veuillez réessayer ultérieurement.",
    backToDashboard: "Retour au dashboard",
    generateNow: "Générer mon thème natal",
    generating: "Génération en cours...",
    generateError: "Impossible de générer le thème pour le moment. Veuillez réessayer.",
    retry: "Réessayer",
    unlockCompleteInterpretation: "Obtenir le thème natal complet",
    requestAnotherAstrologer: "Choisir un autre astrologue",
    interpretedByLabel: "Interprétation actuelle par",
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
    planetsLead: "Les positions clés de vos planètes, avec leur signe, leur maison et leur longitude de référence.",
    housesLead: "Les douze maisons structurent les domaines de vie. Chaque cuspide marque l'ouverture d'un secteur du thème.",
    aspectsLead: "Les aspects décrivent les liens majeurs entre deux planètes. Les valeurs ci-dessous indiquent l'angle théorique et la précision observée.",
    cuspide: "cuspide",
    angle: "angle",
    orb: "orbe",
    orbUsed: "orbe effective",
    positionLabel: "Position",
    longitudeLabel: "Longitude brute",
    houseLabel: "Maison active",
    houseIntervalLabel: "Intervalle",
    cuspLongitudeLabel: "Cuspide",
    houseSignLabel: "Ouverture en",
    aspectPlanetsLabel: "Planètes",
    aspectExactAngleLabel: "Angle exact",
    aspectMeaningLabel: "Lecture rapide",
    aspectMeaningMap: {
      CONJUNCTION: "Les deux énergies se superposent et se vivent ensemble dans le thème.",
      SEXTILE: "Le lien ouvre une facilité de circulation et un potentiel de coopération.",
      SQUARE: "L'aspect crée une tension utile, qui pousse à ajuster ou à dépasser un blocage.",
      TRINE: "Le flux entre les deux planètes est naturel et soutenant.",
      OPPOSITION: "L'aspect met en miroir deux pôles à équilibrer dans la vie du natif.",
    },
    wrapConnector: "puis 0°",
    interpretation: {
      loading: "L'IA analyse votre thème natal...",
      title: "Interprétation de votre thème",
      upsellTitle: "Interprétation complète",
      upsellCta: "Choisir mon astrologue",
      upgradeToBasicCta: "Passer à Basic pour le thème complet",
      upsellDescription: "Débloquez une analyse approfondie et personnalisée par l'un de nos experts.",
      completeBy: "Interprétation par",
      completeBadge: "Complet",
      highlightsTitle: "Points clés",
      adviceTitle: "Conseils",
      lockedAdviceBullets: [
        "Des axes d'action concrets reliés à vos placements majeurs",
        "Des repères pour mieux canaliser vos élans et vos priorités",
        "Une lecture plus fine de ce qu'il vaut mieux renforcer ou alléger",
      ],
      lockedAdviceBody:
        "Dans la version Basic, ce bloc transforme votre thème en conseils opérationnels, avec une lecture plus développée de vos rythmes, de vos points d'appui et des ajustements qui peuvent vous aider à avancer avec davantage de clarté, de stabilité et de cohérence personnelle.",
      evidenceTitle: "Ce que j’ai utilisé pour écrire cette interprétation",
      evidenceIntro: "Transparence : voici les éléments utilisés pour générer ce texte.",
      showEvidence: "Afficher le panneau d’audit",
      hideEvidence: "Masquer le panneau d’audit",
      disclaimerTitle: "Mentions légales",
      legalNoticeLines: [
        "Cette interprétation astrologique est un contenu de réflexion personnelle, non scientifique et non prédictif.",
        "Ce contenu ne constitue pas un conseil médical, psychologique, juridique, fiscal ou financier, et ne remplace pas un professionnel qualifié.",
        "Aucune garantie de résultat n'est fournie ; vos décisions relèvent de votre responsabilité et de votre libre arbitre.",
      ],
      error: "L'interprétation n'est pas disponible pour le moment.",
      retry: "Réessayer",
      regenerate: "Nouvelle interprétation",
      degradedNotice: "Interprétation partielle (données de naissance incomplètes)",
      requestingComplete: "Votre astrologue interprète votre thème...",
      personaSelectorTitle: "Choisissez votre astrologue",
      personaSelectorConfirm: "Demander l'interprétation complète",
      cancel: "Annuler",
      generatedOnLabel: "Généré le",
      standardVersionLabel: "Standard",
      summaryBadge: "Résumé",
      shortBadge: "Short",
      historyTitle: "Versions disponibles",
      deleteConfirm: "Supprimer cette version ?",
      deleteConfirmSub: "Cette interprétation sera définitivement supprimée de votre historique.",
      deleteCta: "Supprimer",
      templateLabel: "Style",
      historyGroupLabel: "Autres interprétations du thème disponibles",
      pdfGroupLabel: "Exports PDF",
      previewPdf: "Aperçu PDF",
      downloadPdf: "Télécharger PDF",
      pdfActionsLabel: "Actions PDF",
      versionLabel: "Version du",
      noHistory: "Aucune autre version disponible.",
      allAstrologersUsed: "Tous les astrologues disponibles ont déjà une interprétation.",
      evidenceEmpty: "Aucun repère technique n’est disponible pour cette version.",
      dedupedCount: (count: number) =>
        `${count} élément${count > 1 ? "s" : ""} dédupliqué${count > 1 ? "s" : ""}`,
      sectionsMap: {
        overall: "Vue d'ensemble",
        career: "Carrière et vocation",
        relationships: "Relations et amour",
        inner_life: "Vie intérieure",
        daily_life: "Vie quotidienne",
        strengths: "Forces",
        challenges: "Défis",
        event_context: "Contexte événementiel",
      },
      evidenceCategories: {
        angles: "Angles",
        personalPlanets: "Planètes personnelles",
        slowPlanets: "Planètes lentes",
        dominantHouses: "Maisons dominantes",
        majorAspects: "Aspects majeurs",
        other: "Autres repères",
      },
    },
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
    basicTitle: "Basic natal chart",
    completeTitle: "Complete natal chart",
    loading: "Loading your latest natal chart...",
    notFound: "No natal chart available at the moment.",
    notFoundSub: "Generate your initial chart first to view this page.",
    noData: "No chart data available at the moment.",
    incompleteData: "Your birth data is incomplete.",
    incompleteDataSub: "Complete your profile to generate your natal chart.",
    completeProfile: "Complete my profile",
    genericError: "An error occurred. Please try again later.",
    backToDashboard: "Back to dashboard",
    generateNow: "Generate my natal chart",
    generating: "Generating...",
    generateError: "Unable to generate the chart right now. Please try again.",
    retry: "Retry",
    unlockCompleteInterpretation: "Unlock the complete natal chart",
    requestAnotherAstrologer: "Choose another astrologer",
    interpretedByLabel: "Current interpretation by",
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
    planetsLead: "Key planetary placements with their sign, house and reference longitude.",
    housesLead: "The twelve houses structure life areas. Each cusp opens a specific chart sector.",
    aspectsLead: "Aspects describe the main links between two planets. The values below show the exact angle and measured precision.",
    cuspide: "cusp",
    angle: "angle",
    orb: "orb",
    orbUsed: "effective orb",
    positionLabel: "Position",
    longitudeLabel: "Raw longitude",
    houseLabel: "Active house",
    houseIntervalLabel: "Range",
    cuspLongitudeLabel: "Cusp",
    houseSignLabel: "Opens in",
    aspectPlanetsLabel: "Planets",
    aspectExactAngleLabel: "Exact angle",
    aspectMeaningLabel: "Quick reading",
    aspectMeaningMap: {
      CONJUNCTION: "Both energies merge and tend to be experienced together in the chart.",
      SEXTILE: "This link creates flow and cooperative potential.",
      SQUARE: "The aspect creates productive tension that pushes for adjustment.",
      TRINE: "The flow between both planets is natural and supportive.",
      OPPOSITION: "The aspect mirrors two poles that need balance in the native's life.",
    },
    wrapConnector: "then 0°",
    interpretation: {
      loading: "AI is analyzing your natal chart...",
      title: "Chart Interpretation",
      upsellTitle: "Complete Interpretation",
      upsellCta: "Choose my astrologer",
      upgradeToBasicCta: "Upgrade to Basic for the full reading",
      upsellDescription: "Unlock an in-depth and personalized analysis by one of our experts.",
      completeBy: "Interpretation by",
      completeBadge: "Complete",
      highlightsTitle: "Key Points",
      adviceTitle: "Advice",
      lockedAdviceBullets: [
        "Concrete action angles connected to your strongest placements",
        "Clear markers to channel your momentum and priorities better",
        "A finer reading of what to reinforce and what to ease",
      ],
      lockedAdviceBody:
        "In the Basic version, this block turns your chart into practical guidance, with a fuller reading of your rhythms, strengths, and the adjustments that can help you move forward with more clarity, stability, and personal coherence.",
      evidenceTitle: "What I used to write this interpretation",
      evidenceIntro: "Transparency: here is what was used to generate this text.",
      showEvidence: "Show audit panel",
      hideEvidence: "Hide audit panel",
      disclaimerTitle: "Legal Notice",
      legalNoticeLines: [
        "This astrological interpretation is content for personal reflection, non-scientific and non-predictive.",
        "This content does not constitute medical, psychological, legal, tax, or financial advice, and does not replace a qualified professional.",
        "No guarantee of results is provided; your decisions remain your responsibility and your free will.",
      ],
      error: "Interpretation is not available at the moment.",
      retry: "Retry",
      regenerate: "New interpretation",
      degradedNotice: "Partial interpretation (incomplete birth data)",
      requestingComplete: "Your astrologer is interpreting your chart...",
      personaSelectorTitle: "Choose your astrologer",
      personaSelectorConfirm: "Request complete interpretation",
      cancel: "Cancel",
      generatedOnLabel: "Generated on",
      standardVersionLabel: "Standard",
      summaryBadge: "Summary",
      shortBadge: "Short",
      historyTitle: "Available versions",
      deleteConfirm: "Delete this version?",
      deleteConfirmSub: "This interpretation will be permanently removed from your history.",
      deleteCta: "Delete",
      templateLabel: "Style",
      historyGroupLabel: "Other available chart interpretations",
      pdfGroupLabel: "PDF exports",
      previewPdf: "Preview PDF",
      downloadPdf: "Download PDF",
      pdfActionsLabel: "PDF actions",
      versionLabel: "Version from",
      noHistory: "No other versions available.",
      allAstrologersUsed: "All available astrologers already have an interpretation.",
      evidenceEmpty: "No technical evidence is available for this version.",
      dedupedCount: (count: number) => `${count} deduplicated item${count > 1 ? "s" : ""}`,
      sectionsMap: {
        overall: "Overall Overview",
        career: "Career and Vocation",
        relationships: "Relationships and Love",
        inner_life: "Inner Life",
        daily_life: "Daily Life",
        strengths: "Strengths",
        challenges: "Challenges",
        event_context: "Event Context",
      },
      evidenceCategories: {
        angles: "Angles",
        personalPlanets: "Personal planets",
        slowPlanets: "Slow-moving planets",
        dominantHouses: "Dominant houses",
        majorAspects: "Major aspects",
        other: "Other markers",
      },
    },
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
    basicTitle: "Carta natal básica",
    completeTitle: "Carta natal completa",
    loading: "Cargando tu última carta natal...",
    notFound: "No hay carta natal disponible por el momento.",
    notFoundSub: "Genera primero tu carta inicial para ver esta página.",
    noData: "No hay datos de carta disponibles por el momento.",
    incompleteData: "Tus datos de nacimiento están incompletos.",
    incompleteDataSub: "Completa tu perfil para generar tu carta natal.",
    completeProfile: "Completar mi perfil",
    genericError: "Ocurrió un error. Por favor, inténtalo más tarde.",
    backToDashboard: "Volver al panel",
    generateNow: "Generar mi carta natal",
    generating: "Generando...",
    generateError: "No se puede generar la carta en este momento. Inténtalo de nuevo.",
    retry: "Reintentar",
    unlockCompleteInterpretation: "Obtener la carta natal completa",
    requestAnotherAstrologer: "Elegir otro astrólogo",
    interpretedByLabel: "Interpretación actual por",
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
      aspects: "Los aspects",
    },
    noAspects: "No se detectaron aspectos mayores para este cálculo.",
    planetsLead: "Las posiciones planetarias clave con su signo, casa y longitud de referencia.",
    housesLead: "Las doce casas estructuran las áreas de vida. Cada cúspide abre un sector específico de la carta.",
    aspectsLead: "Los aspectos describen los vínculos principales entre dos planetas. Los valores indican el ángulo exacto y la precisión observada.",
    cuspide: "cúspide",
    angle: "ángulo",
    orb: "orbe",
    orbUsed: "orbe efectivo",
    positionLabel: "Posición",
    longitudeLabel: "Longitud bruta",
    houseLabel: "Casa activa",
    houseIntervalLabel: "Intervalo",
    cuspLongitudeLabel: "Cúspide",
    houseSignLabel: "Se abre en",
    aspectPlanetsLabel: "Planetas",
    aspectExactAngleLabel: "Ángulo exacto",
    aspectMeaningLabel: "Lectura rápida",
    aspectMeaningMap: {
      CONJUNCTION: "Ambas energías se superponen y suelen vivirse juntas en la carta.",
      SEXTILE: "El vínculo abre facilidad de circulación y potencial de cooperación.",
      SQUARE: "El aspecto crea una tensión útil que empuja a reajustar.",
      TRINE: "El flujo entre ambos planetas es natural y favorecedor.",
      OPPOSITION: "El aspecto pone en espejo dos polos que deben equilibrarse en la vida del nativo.",
    },
    wrapConnector: "luego 0°",
    interpretation: {
      loading: "La IA está analizando tu carta natal...",
      title: "Interpretación de tu carta",
      upsellTitle: "Interpretación completa",
      upsellCta: "Elegir mi astrólogo",
      upgradeToBasicCta: "Pasar a Basic para la lectura completa",
      upsellDescription: "Desbloquea un análisis profundo y personalizado por uno de nuestros expertos.",
      completeBy: "Interpretación por",
      completeBadge: "Completo",
      highlightsTitle: "Puntos clave",
      adviceTitle: "Consejos",
      lockedAdviceBullets: [
        "Ángulos de acción concretos conectados con tus posiciones más fuertes",
        "Referencias claras para canalizar mejor tu impulso y tus prioridades",
        "Una lectura más fina de lo que conviene reforzar y de lo que conviene aligerar",
      ],
      lockedAdviceBody:
        "En la versión Basic, este bloque convierte tu carta en consejos prácticos, con una lectura más desarrollada de tus ritmos, tus apoyos y los ajustes que pueden ayudarte a avanzar con más claridad, estabilidad y coherencia personal.",
      evidenceTitle: "Lo que utilicé para redactar esta interpretación",
      evidenceIntro: "Transparencia: aquí tienes lo utilizado para generar este texto.",
      showEvidence: "Mostrar panel de auditoría",
      hideEvidence: "Ocultar panel de auditoría",
      disclaimerTitle: "Aviso legal",
      legalNoticeLines: [
        "Esta interpretación astrológica es un contenido de reflexión personal, no científico y no predictivo.",
        "Este contenido no constituye asesoramiento médico, psicológico, jurídico, fiscal o financiero, y no sustituye a un profesional cualificado.",
        "No se ofrece ninguna garantía de resultado; sus decisiones son su responsabilidad y forman parte de su libre albedrío.",
      ],
      error: "La interpretación no está disponible en este momento.",
      retry: "Reintentar",
      regenerate: "Nueva interpretación",
      degradedNotice: "Interpretación parcial (datos de nacimiento incompletos)",
      requestingComplete: "Tu astrólogo está interpretando tu carta...",
      personaSelectorTitle: "Elige a tu astrólogo",
      personaSelectorConfirm: "Solicitar interpretación completa",
      cancel: "Cancelar",
      generatedOnLabel: "Generado el",
      standardVersionLabel: "Standard",
      summaryBadge: "Resumen",
      shortBadge: "Short",
      historyTitle: "Versiones disponibles",
      deleteConfirm: "¿Eliminar esta versión?",
      deleteConfirmSub: "Esta interpretación se eliminará permanentemente de tu historial.",
      deleteCta: "Eliminar",
      templateLabel: "Estilo",
      historyGroupLabel: "Otras interpretaciones disponibles de la carta",
      pdfGroupLabel: "Exportaciones PDF",
      previewPdf: "Vista previa PDF",
      downloadPdf: "Descargar PDF",
      pdfActionsLabel: "Acciones PDF",
      versionLabel: "Versión del",
      noHistory: "No hay otras versiones disponibles.",
      allAstrologersUsed: "Todos los astrólogos disponibles ya tienen una interpretación.",
      evidenceEmpty: "No hay evidencia técnica disponible para esta versión.",
      dedupedCount: (count: number) => `${count} elemento${count > 1 ? "s" : ""} deduplicado${count > 1 ? "s" : ""}`,
      sectionsMap: {
        overall: "Visión general",
        career: "Carrera y vocación",
        relationships: "Relaciones et amor",
        inner_life: "Vida interior",
        daily_life: "Vida diaria",
        strengths: "Fortalezas",
        challenges: "Desafíos",
        event_context: "Contexto del evento",
      },
      evidenceCategories: {
        angles: "Ángulos",
        personalPlanets: "Planetas personales",
        slowPlanets: "Planetas lentos",
        dominantHouses: "Casas dominantes",
        majorAspects: "Aspectos mayores",
        other: "Otros indicadores",
      },
    },
    guide: {
      title: "Cómo leer tu carta natal",
      intro:
        "Tu carta natal es una representación geométrica del cielo en el momento y lugar de tu nacimiento. Los cálculos sitúan puntos (planetas) en un círculo de 360°. Luego, estas posiciones se traducen en referencias legibles: signos, casas, ángulos y aspectos.",
      signsTitle: "Los signos zodiacales",
      signsDesc:
        "El zodíaco está dividido en 12 signos de 30° cada uno. Un signo no es un planeta: es una zona del círculo que sirve de cuadrícula para expresar una posición. Cada posición astronómica es primero una longitud eclíptica entre 0° et 360°, que luego se convierte en un signo (en qué segmento de 30°) et un grado dentro del signo (de 0°00' a 29°59').",
      signExample: "Sol 34,08° → Tauro 4°05′ (Tauro comienza en 30°)",
      planetsTitle: "Los planetas",
      planetsDesc:
        "Los planetas (y, en astrología, el Sol y la Luna) sont puntos situados en el círculo zodiacal a una longitud precisa. Para cada planeta, se muestra: su posición en signo + grado (lectura humana), su longitud bruta (valor de cálculo) y la casa en la que se encuentra (sector del tema).",
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
            "Es el valor numérique (0-360°) utilizado para los cálculos. La representación signo + grado es una conversión más legible de ese mismo valor.",
        },
        {
          question: "¿Qué es una cúspide?",
          answer:
            "Es el punto de inicio de una casa. Las cúspides son referencias calculadas sobre el círculo que definen los límites de los sectores (casas).",
        },
        {
          question: "¿Por qué algunas casas parecen extrañas o cruzan el 0°?",
          answer:
            "Porque el círculo no tiene un inicio real: 360° y 0° sont el mismo punto. Si una casa empieza cerca del final del círculo, puede continuar después del 0°.",
        },
        {
          question: "¿Para qué sirve el orbe en los aspectos?",
          answer:
            "El orbe sirve de tolerancia. Sin orbe, casi ningún aspecto sería exacto. Con el orbe, se incluyen los ángulos próximos a un ángulo de referencia.",
        },
        {
          question: "¿Qué significa el símbolo ℞?",
          answer:
            "℞ indica un movimiento retrógrado aparente: visto desde la Tierra, el planeta parece retroceder temporalmente en el zodíaco. Es información de movimiento aparente procedente de las efemérides.",
        },
        {
          question: "¿Por qué se destacan el signo solar y el ascendente?",
          answer:
            "Porque son dos referencias muy usadas: una es la posición del Sol (un punto), la otra es un ángulo de las casas (una cúspide). Resumen elementos differentes de la estructura de la carta, sin ser interpretaciones por sí solos.",
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
  return (
    natalChartTranslations[lang]?.guide ?? natalChartTranslations[DEFAULT_ASTRO_LANG].guide
  )
}

export type NatalTeaserKey = 'overall' | 'career' | 'relationships' | 'inner_life' | 'daily_life' | 'strengths' | 'challenges' | 'event_context' | 'generic'

export const NATAL_SECTION_TEASERS: Record<NatalTeaserKey, { fr: string; en: string; es: string }> = {
  overall: {
    fr: "Votre vue d'ensemble astrologique complète, révélant les grands axes de votre personnalité et de votre destinée...",
    en: "Your complete astrological overview, revealing the major axes of your personality and destiny...",
    es: "Tu visión astrológica completa, revelando los grandes ejes de tu personalidad y destino...",
  },
  career: {
    fr: "Vos potentiels de carrière et de vocation, lus à travers vos placements planétaires...",
    en: "Your career and vocation potential, read through your planetary placements...",
    es: "Tu potencial de carrera y vocación, leído a través de tus posiciones planetarias...",
  },
  relationships: {
    fr: "Votre style relationnel et amoureux, révélé par Vénus et votre Maison VII...",
    en: "Your relational and romantic style, revealed by Venus and your House VII...",
    es: "Tu estilo relacional y amoroso, revelado por Venus y tu Casa VII...",
  },
  inner_life: {
    fr: "Les profondeurs de votre vie intérieure, vos ressources cachées et votre monde émotionnel...",
    en: "The depths of your inner life, your hidden resources and emotional world...",
    es: "Las profundidades de tu vida interior, tus recursos ocultos y mundo emocional...",
  },
  daily_life: {
    fr: "Comment votre thème natal influence votre quotidien, vos routines et votre santé...",
    en: "How your natal chart influences your daily life, routines and health...",
    es: "Cómo tu tema natal influye en tu vida cotidiana, rutinas y salud...",
  },
  strengths: {
    fr: "Vos forces astrales majeures et les talents naturels inscrits dans votre thème...",
    en: "Your major astral strengths and natural talents inscribed in your chart...",
    es: "Tus principales fortalezas astrales y talentos naturales inscritos en tu tema...",
  },
  challenges: {
    fr: "Les défis et axes de croissance révélés par les tensions de votre thème natal...",
    en: "The challenges and growth areas revealed by the tensions in your natal chart...",
    es: "Los desafíos y áreas de crecimiento revelados por las tensiones de tu tema natal...",
  },
  event_context: {
    fr: "Le contexte événementiel et les cycles planétaires qui marquent votre période actuelle...",
    en: "The event context and planetary cycles marking your current period...",
    es: "El contexto de eventos y ciclos planetarios que marcan tu período actual...",
  },
  generic: {
    fr: "Section disponible avec l'abonnement Basic — analyse approfondie de votre thème natal.",
    en: "Section available with Basic subscription — in-depth analysis of your natal chart.",
    es: "Sección disponible con la suscripción Basic — análisis profundo de tu tema natal.",
  },
}

export function getNatalSectionTeaser(key: string, lang: AstrologyLang): string {
  const entry = NATAL_SECTION_TEASERS[key as NatalTeaserKey] ?? NATAL_SECTION_TEASERS.generic
  if (lang === 'fr') return entry.fr
  if (lang === 'es') return entry.es
  return entry.en
}

export const NATAL_SECTION_LOCKED_COPY: Record<
  NatalTeaserKey,
  { fr: string; en: string; es: string }
> = {
  overall: {
    fr: "Dans la version Basic, cette section déroule une lecture ample de vos grands moteurs intérieurs, de vos contradictions structurantes et de la manière dont votre thème relie intuition, volonté, rapport aux autres et rythme de vie. Vous y découvrez une synthèse plus longue, progressive et concrète, pensée pour faire ressortir vos lignes de force au quotidien. Elle détaille aussi les nuances entre vos élans spontanés, vos besoins émotionnels et la façon dont votre personnalité s'organise dans la durée, pour donner une vision plus incarnée et plus exploitable de votre thème.",
    en: "In the Basic version, this section unfolds a broader reading of your core inner drives, your structuring tensions, and the way your chart connects intuition, willpower, relationships, and daily rhythm. It gives you a longer, more progressive synthesis designed to highlight your main strengths in practical life.",
    es: "En la versión Basic, esta sección desarrolla una lectura amplia de tus motores internos, de tus tensiones estructurales y de la forma en que tu carta conecta intuición, voluntad, relaciones y ritmo cotidiano. Te ofrece una síntesis más larga y progresiva para resaltar tus principales fortalezas en la vida diaria.",
  },
  career: {
    fr: "La version complète approfondit vos appuis de vocation, vos leviers d'expression, votre manière d'entrer dans l'effort et les conditions dans lesquelles votre potentiel professionnel se déploie le mieux. Elle relie vos placements à des dynamiques concrètes de trajectoire, de motivation et de positionnement. Vous obtenez aussi une lecture plus fine de vos rythmes de progression, des contextes qui soutiennent votre constance et des environnements où vos capacités ont le plus de chances d'être reconnues.",
    en: "The complete version goes deeper into your vocational strengths, your modes of expression, your relationship to effort, and the conditions in which your professional potential unfolds best. It connects your placements to concrete dynamics of trajectory, motivation, and positioning.",
    es: "La versión completa profundiza en tus apoyos vocacionales, tus formas de expresión, tu relación con el esfuerzo y las condiciones en las que tu potencial profesional se despliega mejor. Relaciona tus posiciones con dinámicas concretas de trayectoria, motivación y posicionamiento.",
  },
  relationships: {
    fr: "Cette lecture détaillée explore votre style relationnel, votre manière d'entrer dans l'attachement, ce que vous attendez d'un lien équilibré et les zones de vigilance à apprivoiser. Elle articule vos besoins affectifs, votre façon de séduire et la qualité du dialogue que votre thème favorise. La version complète aide aussi à mieux comprendre vos schémas de rapprochement, les points de sensibilité à sécuriser et la manière dont vous construisez la confiance sur la durée.",
    en: "This detailed reading explores your relational style, the way you enter attachment, what you expect from a balanced bond, and the areas of vigilance to work with. It connects your emotional needs, your way of attracting others, and the quality of dialogue suggested by your chart.",
    es: "Esta lectura detallada explora tu estilo relacional, la manera en que entras en el vínculo, lo que esperas de una relación equilibrada y las áreas de atención que conviene trabajar. Conecta tus necesidades afectivas, tu forma de atraer y la calidad del diálogo sugerida por tu carta.",
  },
  inner_life: {
    fr: "Avec Basic, cette section ouvre une analyse plus intime de votre monde émotionnel, de vos ressources cachées, de vos mécanismes de protection et de ce qui vous aide à retrouver de la cohérence intérieure. Le texte complet met en lumière vos profondeurs sans tomber dans un discours vague ou fataliste. Il met également en perspective vos réflexes de retrait, vos besoins de réparation symbolique et les ressources plus discrètes qui nourrissent votre stabilité psychique.",
    en: "With Basic, this section opens a more intimate analysis of your emotional world, your hidden resources, your protection mechanisms, and what helps you regain inner coherence. The full text highlights your depths without falling into vague or fatalistic language.",
    es: "Con Basic, esta sección abre un análisis más íntimo de tu mundo emocional, de tus recursos ocultos, de tus mecanismos de protección y de lo que te ayuda a recuperar coherencia interior. El texto completo ilumina tus profundidades sin caer en un discurso vago o fatalista.",
  },
  daily_life: {
    fr: "La lecture complète montre comment votre thème agit dans vos routines, votre rapport au temps, votre niveau d'énergie, vos habitudes et votre manière d'organiser le concret. Elle transforme vos placements en repères utilisables pour mieux piloter votre quotidien. Vous y gagnez des indications plus fines sur vos points de dispersion, vos tempos naturels et la manière d'ajuster vos habitudes pour mieux soutenir votre équilibre général.",
    en: "The full reading shows how your chart operates in your routines, your relationship to time, your energy level, your habits, and the way you organize practical life. It turns your placements into usable reference points for navigating everyday life.",
    es: "La lectura completa muestra cómo actúa tu carta en tus rutinas, tu relación con el tiempo, tu nivel de energía, tus hábitos y tu manera de organizar lo concreto. Convierte tus posiciones en referencias útiles para orientar tu vida cotidiana.",
  },
  strengths: {
    fr: "Dans Basic, cette partie isole vos talents naturels, vos ressources spontanées et les combinaisons planétaires qui soutiennent votre confiance, votre créativité ou votre constance. Elle donne une lecture plus généreuse et plus précise de ce sur quoi vous pouvez réellement vous appuyer. Le texte complet aide aussi à distinguer vos dons les plus visibles de vos atouts plus silencieux, ceux qui prennent de la valeur lorsqu'ils sont reconnus et cultivés consciemment.",
    en: "In Basic, this part isolates your natural talents, your spontaneous resources, and the planetary combinations that support your confidence, creativity, or consistency. It provides a fuller and more precise reading of what you can genuinely rely on.",
    es: "En Basic, esta parte identifica tus talentos naturales, tus recursos espontáneos y las combinaciones planetarias que sostienen tu confianza, creatividad o constancia. Ofrece una lectura más amplia y precisa de aquello en lo que realmente puedes apoyarte.",
  },
  challenges: {
    fr: "La version complète éclaire les tensions utiles de votre thème, les points de friction récurrents et les axes d'évolution qui demandent davantage de conscience. Elle aide à distinguer les vrais défis structurants des simples passages de doute, avec une lecture nuancée et exploitable. Elle précise aussi les endroits où vous pouvez transformer une résistance en apprentissage, plutôt que de subir des répétitions qui fatiguent ou dispersent votre énergie.",
    en: "The complete version sheds light on the useful tensions in your chart, the recurring friction points, and the growth axes that require more awareness. It helps separate real structuring challenges from temporary doubts through a nuanced, usable reading.",
    es: "La versión completa ilumina las tensiones útiles de tu carta, los puntos de fricción recurrentes y los ejes de evolución que requieren más conciencia. Ayuda a diferenciar los verdaderos desafíos estructurales de las dudas pasajeras mediante una lectura matizada y útil.",
  },
  event_context: {
    fr: "Cette section détaillée relie votre thème natal à un contexte plus large de cycles, de périodes et de rythmes d'activation. Elle donne une perspective plus longue sur ce qui s'ouvre, ce qui demande du recul et les moments où vos placements deviennent particulièrement parlants. La lecture complète met aussi en avant les phases de maturation, les seuils de transition et les périodes où certaines thématiques personnelles prennent davantage de relief.",
    en: "This detailed section links your natal chart to a broader context of cycles, periods, and activation rhythms. It offers a longer-range perspective on what is opening up, what calls for distance, and when your placements become especially meaningful.",
    es: "Esta sección detallada conecta tu carta natal con un contexto más amplio de ciclos, períodos y ritmos de activación. Ofrece una perspectiva más larga sobre lo que se abre, lo que pide distancia y los momentos en que tus posiciones se vuelven especialmente significativas.",
  },
  generic: {
    fr: "Avec l'abonnement Basic, vous accédez à une lecture plus développée, plus structurée et plus concrète de cette partie de votre thème natal. Le texte complet transforme les placements astrologiques en interprétation suivie, avec davantage de nuances, d'exemples et de matière utile. Il ajoute plus de contexte, plus de transitions explicatives et une matière interprétative qui donne nettement plus de profondeur à votre lecture personnelle.",
    en: "With the Basic subscription, you unlock a fuller, more structured, and more practical reading of this part of your natal chart. The full text turns astrological placements into a continuous interpretation with more nuance, examples, and useful detail.",
    es: "Con la suscripción Basic, desbloqueas una lectura más desarrollada, estructurada y práctica de esta parte de tu carta natal. El texto completo transforma las posiciones astrológicas en una interpretación continua con más matices, ejemplos y contenido útil.",
  },
}

export function getNatalLockedSectionCopy(key: string, lang: AstrologyLang): string {
  const entry = NATAL_SECTION_LOCKED_COPY[key as NatalTeaserKey] ?? NATAL_SECTION_LOCKED_COPY.generic
  if (lang === "fr") return entry.fr
  if (lang === "es") return entry.es
  return entry.en
}
