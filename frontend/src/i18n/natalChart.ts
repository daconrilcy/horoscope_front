// Traductions applicatives du theme natal, y compris les libelles des lectures publiques.
import type { AstrologyLang } from "./astrology"

type NatalChartGuideCard = {
  cue: string
  title: string
  description: string
  example: string
}

type NatalChartGuideStep = {
  title: string
  description: string
}

type NatalChartGuideGlossaryItem = {
  term: string
  definition: string
}

export const DEFAULT_ASTRO_LANG: AstrologyLang = "fr"

export type NatalChartGuideTranslations = {
  title: string
  openLabel: string
  closeLabel: string
  intro: string
  takeawayLabel: string
  takeaway: string
  formulaTitle: string
  formulaIntro: string
  formulaCards: NatalChartGuideCard[]
  firstMarkersTitle: string
  firstMarkersDescription: string
  partialReadingNote: string
  readingPathTitle: string
  readingPath: NatalChartGuideStep[]
  interpretationTitle: string
  interpretationCards: NatalChartGuideCard[]
  aspectsTitle: string
  aspectsDescription: string
  aspectsExample: string
  confidenceTitle: string
  confidenceDescription: string
  glossaryTitle: string
  glossary: NatalChartGuideGlossaryItem[]
  closingTip: string
}

export type NatalChartPageCopy = {
  meta: string
  title: string
  context: string
  portraitLabel: string
  portraitFactsLabel: string
  jobError: string
  jobLaunchError: string
  jobLoading: string
  jobStatusLabel: string
  readingUnavailable: string
  startButton: string
  retryButton: string
  profileLink: string
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
  page: NatalChartPageCopy
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
    themesTitle: string
    conclusionTitle: string
    limitationsTitle: string
    lockedAdviceBullets: string[]
    lockedAdviceBody: string
    evidenceTitle: string
    evidenceIntro: string
    evidenceUsagePrefix: string
    showEvidence: string
    hideEvidence: string
    disclaimerTitle: string
    legalNoticeLines: string[]
    error: string
    retry: string
    regenerate: string
    narrativeMissingTitle: string
    narrativeMissingBody: string
    degradedNotice: string
    requestingComplete: string
    personaSelectorTitle: string
    personaSelectorConfirm: string
    cancel: string
    generatedOnLabel: string
    standardVersionLabel: string
    summaryBadge: string
    shortBadge: string
    quotaExhaustedCta: string
    basicCompleteLimitMessage: string
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
    projections: {
      panelLabel: string
      panelTitle: string
      loading: string
      entitlement: string
      error: string
      retry: string
      empty: string
      degraded: string
      cardEmpty: string
      beginnerTitle: string
      beginnerDescription: string
      clientTitle: string
      clientDescription: string
    }
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
const natalChartTranslationsBase: Record<Exclude<AstrologyLang, "de">, NatalChartTranslations> = {
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
    page: {
      meta: "Thème natal Astral",
      title: "Votre thème natal",
      context:
        "Une synthèse structurée de vos marqueurs personnels, de leurs appuis et des tensions majeures de votre ciel de naissance.",
      portraitLabel: "Portrait astral",
      portraitFactsLabel: "Marqueurs clés du portrait astral",
      jobError:
        "Le service Astral n'a pas pu produire votre thème natal pour le moment. Veuillez réessayer plus tard.",
      jobLaunchError: "Le calcul Astral n'a pas pu être lancé ou récupéré.",
      jobLoading: "Votre thème natal est en cours de génération. Cette étape peut prendre quelques instants.",
      jobStatusLabel: "Statut",
      readingUnavailable: "La lecture est indisponible pour ce job Astral.",
      startButton: "Lancer le thème natal",
      retryButton: "Relancer le thème natal",
      profileLink: "Vérifier mon profil de naissance",
    },
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
      themesTitle: "Thèmes de lecture",
      conclusionTitle: "Conclusion",
      limitationsTitle: "Limites de cette lecture",
      lockedAdviceBullets: [
        "Des axes d'action concrets reliés à vos placements majeurs",
        "Des repères pour mieux canaliser vos élans et vos priorités",
        "Une lecture plus fine de ce qu'il vaut mieux renforcer ou alléger",
      ],
      lockedAdviceBody:
        "Dans la version Basic, ce bloc transforme votre thème en conseils opérationnels, avec une lecture plus développée de vos rythmes, de vos points d'appui et des ajustements qui peuvent vous aider à avancer avec davantage de clarté, de stabilité et de cohérence personnelle.",
      evidenceTitle: "Ce que j’ai utilisé pour écrire cette interprétation",
      evidenceIntro: "Transparence : voici les éléments utilisés pour générer ce texte.",
      evidenceUsagePrefix: "Utilisé dans",
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
      narrativeMissingTitle: "Lecture complète à régénérer",
      narrativeMissingBody:
        "Cette interprétation utilise un format obsolète. Demandez une nouvelle interprétation complète pour afficher la lecture en cinq chapitres.",
      degradedNotice: "Interprétation partielle (données de naissance incomplètes)",
      requestingComplete: "Votre astrologue interprète votre thème...",
      personaSelectorTitle: "Choisissez votre astrologue",
      personaSelectorConfirm: "Demander l'interprétation complète",
      cancel: "Annuler",
      generatedOnLabel: "Généré le",
      standardVersionLabel: "Standard",
      summaryBadge: "Résumé",
      shortBadge: "Short",
      quotaExhaustedCta: "Passer à Premium pour plus d'interprétations",
      basicCompleteLimitMessage:
        "Le plan Basic inclut une seule interprétation complète de votre thème natal. Passez à Premium pour en demander d'autres.",
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
      projections: {
        panelLabel: "Lectures publiques du thème",
        panelTitle: "Deux niveaux de lecture disponibles",
        loading: "Préparation des lectures du thème...",
        entitlement: "Cette lecture demande une formule plus avancée.",
        error: "Les lectures du thème ne sont pas disponibles pour le moment.",
        retry: "Réessayer",
        empty: "Aucune lecture publique n'est encore disponible pour ce thème.",
        degraded: "Lecture partielle : des données de naissance manquent.",
        cardEmpty: "Aucun contenu lisible n'est disponible pour cette lecture.",
        beginnerTitle: "Résumé découverte",
        beginnerDescription: "Une vue simple pour comprendre les repères principaux du thème.",
        clientTitle: "Interprétation client",
        clientDescription: "Une lecture plus suivie qui relie les éléments du thème en langage clair.",
      },
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
      openLabel: "Lire le guide",
      closeLabel: "Réduire le guide",
      intro:
        "Pas besoin de tout connaître pour commencer. Ton thème natal se lit comme une histoire : chaque chapitre rassemble plusieurs indices pour éclairer une facette de ta personnalité et de ton parcours.",
      takeawayLabel: "À retenir",
      takeaway:
        "Une interprétation astrologique propose des pistes symboliques, pas une étiquette ni une prédiction certaine. Garde ce qui t'aide à réfléchir et laisse le reste de côté.",
      formulaTitle: "La formule magique en 4 clés",
      formulaIntro:
        "Quand une phrase semble compliquée, découpe-la avec ces quatre questions. Elles transforment le jargon en une petite scène facile à imaginer.",
      formulaCards: [
        {
          cue: "Quoi ?",
          title: "La planète",
          description:
            "Elle représente une fonction intérieure : le Soleil parle d'élan personnel, la Lune des besoins émotionnels, Mercure de la façon de penser.",
          example: "Exemple : Mars décrit la manière d'agir et de défendre son énergie.",
        },
        {
          cue: "Comment ?",
          title: "Le signe",
          description:
            "Il donne le style de cette fonction. Un même besoin peut s'exprimer avec spontanéité, prudence, curiosité ou intensité selon le signe.",
          example: "Exemple : une énergie en Taureau avance avec constance et recherche du concret.",
        },
        {
          cue: "Où ?",
          title: "La maison",
          description:
            "Elle indique le domaine de vie où l'énergie se joue : identité, relations, foyer, activité, projets ou vie collective.",
          example: "Exemple : la Maison X met l'accent sur la vocation et la place publique.",
        },
        {
          cue: "Quel dialogue ?",
          title: "L'aspect",
          description:
            "Il relie deux planètes. Leur dialogue peut être fluide, stimulant ou demander des ajustements, comme deux personnages qui apprennent à jouer ensemble.",
          example: "Exemple : un carré crée une tension féconde, un trigone facilite la circulation.",
        },
      ],
      firstMarkersTitle: "Tes trois premiers repères",
      firstMarkersDescription:
        "Commence par le Soleil pour l'élan d'identité, la Lune pour les besoins émotionnels et l'Ascendant pour la manière d'entrer en relation avec le monde. Ils ouvrent la lecture, mais aucun ne résume une personne à lui seul.",
      partialReadingNote:
        "Quand l'heure de naissance manque, ou que les données sont partielles ou peu précises, l'Ascendant, les maisons, la Lune et certains aspects peuvent manquer ou être moins fiables. Lis les repères disponibles comme des indications à nuancer.",
      readingPathTitle: "Ton parcours de lecture",
      readingPath: [
        {
          title: "Lis la synthèse",
          description: "Elle donne le fil rouge général avant d'entrer dans les détails.",
        },
        {
          title: "Repère Soleil, Lune et Ascendant",
          description: "Ces trois portes d'entrée aident à situer identité, émotions et présence.",
        },
        {
          title: "Choisis un chapitre",
          description: "Relations, vocation, talents ou croissance : commence par le thème qui t'attire.",
        },
        {
          title: "Regarde ses bases astrologiques",
          description: "Elles montrent quels placements, maisons et aspects soutiennent l'interprétation.",
        },
      ],
      interpretationTitle: "Comment la lecture construit une idée",
      interpretationCards: [
        {
          cue: "Zoom",
          title: "Dominantes et axes",
          description:
            "Une dominante signale qu'un thème revient souvent. Un axe relie deux domaines complémentaires, comme identité et relation ou vie privée et vie publique.",
          example: "Ce n'est pas un destin imposé : c'est une zone particulièrement mise en lumière.",
        },
        {
          cue: "Fil rouge",
          title: "Le maître d'une maison",
          description:
            "Chaque maison commence dans un signe. La planète associée à ce signe devient son maître et relie le domaine de la maison à une autre partie du thème.",
          example: "Imagine un guide qui transporte l'histoire d'une maison vers la scène où il se trouve.",
        },
        {
          cue: "Équipe",
          title: "Cœur, appui et nuance",
          description:
            "Le facteur principal porte l'idée, les appuis la renforcent et les nuances évitent une lecture trop simple. Plusieurs indices sont croisés avant de former un chapitre.",
          example: "Comme une équipe : un moteur, des soutiens et un regard qui modère.",
        },
      ],
      aspectsTitle: "Les aspects : ni bons ni mauvais",
      aspectsDescription:
        "Les trigones et sextiles montrent souvent ce qui circule facilement. Les carrés et oppositions révèlent plutôt des besoins qui tirent dans des directions différentes. La conjonction fusionne deux énergies. Une tension peut devenir une force lorsqu'elle est reconnue et apprivoisée.",
      aspectsExample:
        "Astuce : remplace « problème » par « dialogue à ajuster ». La lecture devient tout de suite plus vivante et moins fataliste.",
      confidenceTitle: "Que veut dire le niveau de confiance ?",
      confidenceDescription:
        "Il indique à quel point plusieurs indices astrologiques soutiennent le chapitre. Une confiance élevée signifie que les indices convergent ; elle ne transforme pas l'interprétation en vérité absolue sur toi.",
      glossaryTitle: "Mini-glossaire",
      glossary: [
        {
          term: "Dominante",
          definition: "Un signe, une planète ou une maison qui revient fortement dans plusieurs indices.",
        },
        {
          term: "Axe",
          definition: "Deux maisons opposées qui invitent à équilibrer deux domaines de vie.",
        },
        {
          term: "Maître de maison",
          definition: "La planète associée au signe qui ouvre une maison et qui en prolonge l'histoire.",
        },
        {
          term: "Orbe",
          definition: "La marge autour de l'angle exact qui permet de considérer un aspect actif.",
        },
        {
          term: "Rétrograde",
          definition: "Le mouvement apparent d'une planète qui semble reculer depuis la Terre.",
        },
        {
          term: "Cuspide",
          definition: "Le point de départ calculé d'une maison sur le cercle natal.",
        },
      ],
      closingTip:
        "Lis ton thème comme une conversation, pas comme un verdict. Les répétitions donnent le tempo ; les contradictions donnent du relief.",
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
    page: {
      meta: "Astral natal chart",
      title: "Your natal chart",
      context:
        "A structured synthesis of your personal markers, their supports, and the major tensions in your birth sky.",
      portraitLabel: "Astral portrait",
      portraitFactsLabel: "Key astral portrait markers",
      jobError: "Astral could not produce your natal chart right now. Please try again later.",
      jobLaunchError: "The Astral calculation could not be started or retrieved.",
      jobLoading: "Your natal chart is being generated. This step may take a few moments.",
      jobStatusLabel: "Status",
      readingUnavailable: "The reading is unavailable for this Astral job.",
      startButton: "Start natal chart",
      retryButton: "Restart natal chart",
      profileLink: "Check my birth profile",
    },
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
      themesTitle: "Reading themes",
      conclusionTitle: "Conclusion",
      limitationsTitle: "Reading limitations",
      lockedAdviceBullets: [
        "Concrete action angles connected to your strongest placements",
        "Clear markers to channel your momentum and priorities better",
        "A finer reading of what to reinforce and what to ease",
      ],
      lockedAdviceBody:
        "In the Basic version, this block turns your chart into practical guidance, with a fuller reading of your rhythms, strengths, and the adjustments that can help you move forward with more clarity, stability, and personal coherence.",
      evidenceTitle: "What I used to write this interpretation",
      evidenceIntro: "Transparency: here is what was used to generate this text.",
      evidenceUsagePrefix: "Used in",
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
      narrativeMissingTitle: "Full reading needs regeneration",
      narrativeMissingBody:
        "This interpretation uses an outdated format. Request a new complete interpretation to display the five-chapter reading.",
      degradedNotice: "Partial interpretation (incomplete birth data)",
      requestingComplete: "Your astrologer is interpreting your chart...",
      personaSelectorTitle: "Choose your astrologer",
      personaSelectorConfirm: "Request complete interpretation",
      cancel: "Cancel",
      generatedOnLabel: "Generated on",
      standardVersionLabel: "Standard",
      summaryBadge: "Summary",
      shortBadge: "Short",
      quotaExhaustedCta: "Upgrade to Premium for more readings",
      basicCompleteLimitMessage:
        "The Basic plan includes one complete natal chart interpretation. Upgrade to Premium to request additional readings.",
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
      projections: {
        panelLabel: "Public chart readings",
        panelTitle: "Two reading levels available",
        loading: "Preparing the chart readings...",
        entitlement: "This reading requires a more advanced plan.",
        error: "Chart readings are not available right now.",
        retry: "Retry",
        empty: "No public reading is available for this chart yet.",
        degraded: "Partial reading: some birth data is missing.",
        cardEmpty: "No readable content is available for this reading.",
        beginnerTitle: "Discovery summary",
        beginnerDescription: "A simple view to understand the chart's main markers.",
        clientTitle: "Client interpretation",
        clientDescription: "A more continuous reading that links chart elements in clear language.",
      },
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
      openLabel: "Read the guide",
      closeLabel: "Collapse the guide",
      intro:
        "You do not need to know everything to begin. Read your natal chart like a story: each chapter gathers several clues to shed light on one part of your personality and journey.",
      takeawayLabel: "Key idea",
      takeaway:
        "An astrological interpretation offers symbolic prompts, not a label or a certain prediction. Keep what helps you reflect and leave the rest aside.",
      formulaTitle: "The 4-key formula",
      formulaIntro:
        "When a sentence feels complicated, break it down with these four questions. They turn jargon into a small scene you can picture.",
      formulaCards: [
        {
          cue: "What?",
          title: "The planet",
          description:
            "It represents an inner function: the Sun speaks to personal drive, the Moon to emotional needs and Mercury to the way you think.",
          example: "Example: Mars describes how you act and stand up for your energy.",
        },
        {
          cue: "How?",
          title: "The sign",
          description:
            "It gives that function its style. The same need can appear spontaneous, careful, curious or intense depending on the sign.",
          example: "Example: energy in Taurus moves steadily and looks for tangible results.",
        },
        {
          cue: "Where?",
          title: "The house",
          description:
            "It points to the life area where the energy plays out: identity, relationships, home, work, projects or community.",
          example: "Example: House X highlights vocation and public life.",
        },
        {
          cue: "What dialogue?",
          title: "The aspect",
          description:
            "It connects two planets. Their dialogue may flow, stimulate or require adjustment, like two characters learning to play together.",
          example: "Example: a square creates productive tension, while a trine helps energy flow.",
        },
      ],
      firstMarkersTitle: "Your first three markers",
      firstMarkersDescription:
        "Start with the Sun for identity and drive, the Moon for emotional needs and the Ascendant for how you meet the world. They open the reading, but none of them sums up a whole person.",
      partialReadingNote:
        "When the birth time is missing, or birth data is incomplete or imprecise, the Ascendant, houses, Moon and some aspects may be missing or less reliable. Read the available markers as clues that deserve nuance.",
      readingPathTitle: "Your reading path",
      readingPath: [
        {
          title: "Read the overview",
          description: "It gives you the main thread before you enter the details.",
        },
        {
          title: "Find the Sun, Moon and Ascendant",
          description: "These three entry points locate identity, emotions and presence.",
        },
        {
          title: "Choose one chapter",
          description: "Relationships, vocation, talents or growth: begin with what draws you in.",
        },
        {
          title: "Check its astrological basis",
          description: "It shows which placements, houses and aspects support the interpretation.",
        },
      ],
      interpretationTitle: "How the reading builds an idea",
      interpretationCards: [
        {
          cue: "Zoom",
          title: "Dominants and axes",
          description:
            "A dominant means a theme appears repeatedly. An axis connects two complementary areas, such as self and relationship or private and public life.",
          example: "This is not a fixed destiny: it is an area receiving extra emphasis.",
        },
        {
          cue: "Thread",
          title: "A house ruler",
          description:
            "Each house begins in a sign. The planet linked to that sign becomes its ruler and connects the house's life area to another part of the chart.",
          example: "Picture a guide carrying one house's story to the place where it stands.",
        },
        {
          cue: "Team",
          title: "Core, support and nuance",
          description:
            "The core factor carries the idea, supporting factors strengthen it and nuances prevent an overly simple reading. Several clues are combined to form a chapter.",
          example: "Like a team: a driving force, supporters and a moderating voice.",
        },
      ],
      aspectsTitle: "Aspects: neither good nor bad",
      aspectsDescription:
        "Trines and sextiles often show what flows easily. Squares and oppositions reveal needs pulling in different directions. A conjunction blends two energies. Tension can become a strength once it is noticed and handled.",
      aspectsExample:
        "Tip: replace “problem” with “dialogue to adjust.” The reading immediately feels more alive and less fatalistic.",
      confidenceTitle: "What does confidence mean?",
      confidenceDescription:
        "It shows how strongly several astrological clues support a chapter. High confidence means the clues converge; it does not turn the interpretation into an absolute truth about you.",
      glossaryTitle: "Mini glossary",
      glossary: [
        {
          term: "Dominant",
          definition: "A sign, planet or house that stands out across several clues.",
        },
        {
          term: "Axis",
          definition: "Two opposite houses inviting balance between two areas of life.",
        },
        {
          term: "House ruler",
          definition: "The planet linked to the sign opening a house, carrying its story further.",
        },
        {
          term: "Orb",
          definition: "The margin around an exact angle used to consider an aspect active.",
        },
        {
          term: "Retrograde",
          definition: "A planet's apparent motion backwards as seen from Earth.",
        },
        {
          term: "Cusp",
          definition: "The calculated starting point of a house on the natal circle.",
        },
      ],
      closingTip:
        "Read your chart as a conversation, not a verdict. Repetition sets the rhythm; contradictions add depth.",
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
    page: {
      meta: "Carta natal Astral",
      title: "Tu carta natal",
      context:
        "Una síntesis estructurada de tus marcadores personales, sus apoyos y las tensiones principales de tu cielo natal.",
      portraitLabel: "Retrato astral",
      portraitFactsLabel: "Marcadores clave del retrato astral",
      jobError: "Astral no pudo producir tu carta natal por el momento. Inténtalo de nuevo más tarde.",
      jobLaunchError: "No se pudo iniciar o recuperar el cálculo Astral.",
      jobLoading: "Tu carta natal se está generando. Este paso puede tardar unos instantes.",
      jobStatusLabel: "Estado",
      readingUnavailable: "La lectura no está disponible para este job Astral.",
      startButton: "Iniciar carta natal",
      retryButton: "Reiniciar carta natal",
      profileLink: "Verificar mi perfil de nacimiento",
    },
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
      themesTitle: "Temas de lectura",
      conclusionTitle: "Conclusión",
      limitationsTitle: "Límites de esta lectura",
      lockedAdviceBullets: [
        "Ángulos de acción concretos conectados con tus posiciones más fuertes",
        "Referencias claras para canalizar mejor tu impulso y tus prioridades",
        "Una lectura más fina de lo que conviene reforzar y de lo que conviene aligerar",
      ],
      lockedAdviceBody:
        "En la versión Basic, este bloque convierte tu carta en consejos prácticos, con una lectura más desarrollada de tus ritmos, tus apoyos y los ajustes que pueden ayudarte a avanzar con más claridad, estabilidad y coherencia personal.",
      evidenceTitle: "Lo que utilicé para redactar esta interpretación",
      evidenceIntro: "Transparencia: aquí tienes lo utilizado para generar este texto.",
      evidenceUsagePrefix: "Utilizado en",
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
      narrativeMissingTitle: "Lectura completa por regenerar",
      narrativeMissingBody:
        "Esta interpretación usa un formato obsoleto. Solicite una nueva interpretación completa para ver la lectura en cinco capítulos.",
      degradedNotice: "Interpretación parcial (datos de nacimiento incompletos)",
      requestingComplete: "Tu astrólogo está interpretando tu carta...",
      personaSelectorTitle: "Elige a tu astrólogo",
      personaSelectorConfirm: "Solicitar interpretación completa",
      cancel: "Cancelar",
      generatedOnLabel: "Generado el",
      standardVersionLabel: "Standard",
      summaryBadge: "Resumen",
      shortBadge: "Short",
      quotaExhaustedCta: "Pasar a Premium para más interpretaciones",
      basicCompleteLimitMessage:
        "El plan Basic incluye una sola interpretación completa de tu carta natal. Pasa a Premium para solicitar otras.",
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
      projections: {
        panelLabel: "Lecturas públicas de la carta",
        panelTitle: "Dos niveles de lectura disponibles",
        loading: "Preparando las lecturas de la carta...",
        entitlement: "Esta lectura requiere un plan más avanzado.",
        error: "Las lecturas de la carta no están disponibles por el momento.",
        retry: "Reintentar",
        empty: "Todavía no hay ninguna lectura pública disponible para esta carta.",
        degraded: "Lectura parcial: faltan algunos datos de nacimiento.",
        cardEmpty: "No hay contenido legible disponible para esta lectura.",
        beginnerTitle: "Resumen de descubrimiento",
        beginnerDescription: "Una vista sencilla para entender las referencias principales de la carta.",
        clientTitle: "Interpretación cliente",
        clientDescription: "Una lectura más continua que conecta los elementos de la carta con lenguaje claro.",
      },
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
      openLabel: "Leer la guía",
      closeLabel: "Cerrar la guía",
      intro:
        "No necesitas saberlo todo para empezar. Lee tu carta natal como una historia: cada capítulo reúne varias pistas para iluminar una faceta de tu personalidad y de tu recorrido.",
      takeawayLabel: "Idea clave",
      takeaway:
        "Una interpretación astrológica ofrece pistas simbólicas, no una etiqueta ni una predicción segura. Conserva lo que te ayude a reflexionar y deja a un lado lo demás.",
      formulaTitle: "La fórmula de las 4 claves",
      formulaIntro:
        "Cuando una frase parezca complicada, divídela con estas cuatro preguntas. Así el vocabulario técnico se convierte en una escena fácil de imaginar.",
      formulaCards: [
        {
          cue: "¿Qué?",
          title: "El planeta",
          description:
            "Representa una función interior: el Sol habla del impulso personal, la Luna de las necesidades emocionales y Mercurio de la forma de pensar.",
          example: "Ejemplo: Marte describe cómo actúas y defiendes tu energía.",
        },
        {
          cue: "¿Cómo?",
          title: "El signo",
          description:
            "Da estilo a esa función. Una misma necesidad puede expresarse con espontaneidad, prudencia, curiosidad o intensidad según el signo.",
          example: "Ejemplo: una energía en Tauro avanza con constancia y busca lo concreto.",
        },
        {
          cue: "¿Dónde?",
          title: "La casa",
          description:
            "Indica el ámbito de vida donde actúa la energía: identidad, relaciones, hogar, actividad, proyectos o vida colectiva.",
          example: "Ejemplo: la Casa X destaca la vocación y la vida pública.",
        },
        {
          cue: "¿Qué diálogo?",
          title: "El aspecto",
          description:
            "Conecta dos planetas. Su diálogo puede ser fluido, estimulante o pedir ajustes, como dos personajes que aprenden a tocar juntos.",
          example: "Ejemplo: una cuadratura crea tensión fértil y un trígono facilita el flujo.",
        },
      ],
      firstMarkersTitle: "Tus tres primeras referencias",
      firstMarkersDescription:
        "Empieza por el Sol para la identidad y el impulso, la Luna para las necesidades emocionales y el Ascendente para la forma de entrar en contacto con el mundo. Abren la lectura, pero ninguno resume a una persona.",
      partialReadingNote:
        "Cuando falta la hora de nacimiento, o los datos son incompletos o poco precisos, el Ascendente, las casas, la Luna y algunos aspectos pueden faltar o ser menos fiables. Lee las referencias disponibles como indicios que conviene matizar.",
      readingPathTitle: "Tu recorrido de lectura",
      readingPath: [
        {
          title: "Lee la síntesis",
          description: "Te da el hilo general antes de entrar en los detalles.",
        },
        {
          title: "Localiza Sol, Luna y Ascendente",
          description: "Estas tres entradas sitúan identidad, emociones y presencia.",
        },
        {
          title: "Elige un capítulo",
          description: "Relaciones, vocación, talentos o crecimiento: empieza por lo que te atraiga.",
        },
        {
          title: "Consulta sus bases astrológicas",
          description: "Muestran qué posiciones, casas y aspectos sostienen la interpretación.",
        },
      ],
      interpretationTitle: "Cómo construye una idea la lectura",
      interpretationCards: [
        {
          cue: "Zoom",
          title: "Dominantes y ejes",
          description:
            "Una dominante indica que un tema se repite. Un eje conecta dos ámbitos complementarios, como identidad y relación o vida privada y vida pública.",
          example: "No es un destino fijo: es una zona especialmente iluminada.",
        },
        {
          cue: "Hilo",
          title: "El regente de una casa",
          description:
            "Cada casa comienza en un signo. El planeta asociado a ese signo se convierte en su regente y conecta el ámbito de la casa con otra parte de la carta.",
          example: "Imagina un guía que lleva la historia de una casa hasta el lugar donde se encuentra.",
        },
        {
          cue: "Equipo",
          title: "Núcleo, apoyo y matiz",
          description:
            "El factor principal sostiene la idea, los apoyos la refuerzan y los matices evitan una lectura demasiado simple. Varias pistas forman cada capítulo.",
          example: "Como un equipo: un motor, varios apoyos y una voz que modera.",
        },
      ],
      aspectsTitle: "Los aspectos: ni buenos ni malos",
      aspectsDescription:
        "Los trígonos y sextiles suelen mostrar lo que fluye con facilidad. Las cuadraturas y oposiciones revelan necesidades que tiran en direcciones distintas. La conjunción mezcla dos energías. Una tensión puede convertirse en fuerza cuando se reconoce y se trabaja.",
      aspectsExample:
        "Consejo: cambia «problema» por «diálogo que ajustar». La lectura se vuelve más viva y menos fatalista.",
      confidenceTitle: "¿Qué significa el nivel de confianza?",
      confidenceDescription:
        "Indica hasta qué punto varias pistas astrológicas sostienen un capítulo. Una confianza alta significa que las pistas convergen; no convierte la interpretación en una verdad absoluta sobre ti.",
      glossaryTitle: "Mini glosario",
      glossary: [
        {
          term: "Dominante",
          definition: "Un signo, planeta o casa que destaca en varias pistas.",
        },
        {
          term: "Eje",
          definition: "Dos casas opuestas que invitan a equilibrar dos ámbitos de vida.",
        },
        {
          term: "Regente de casa",
          definition: "El planeta asociado al signo que abre una casa y prolonga su historia.",
        },
        {
          term: "Orbe",
          definition: "El margen alrededor del ángulo exacto que permite considerar activo un aspecto.",
        },
        {
          term: "Retrógrado",
          definition: "El movimiento aparente de un planeta que parece retroceder visto desde la Tierra.",
        },
        {
          term: "Cúspide",
          definition: "El punto de inicio calculado de una casa en el círculo natal.",
        },
      ],
      closingTip:
        "Lee tu carta como una conversación, no como un veredicto. Las repeticiones marcan el ritmo y las contradicciones aportan relieve.",
    },
  },
}

export const natalChartTranslations: Record<AstrologyLang, NatalChartTranslations> = {
  ...natalChartTranslationsBase,
  de: natalChartTranslationsBase.en,
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
    fr: "Section disponible avec l'abonnement Basic - analyse approfondie de votre thème natal.",
    en: "Section available with Basic subscription - in-depth analysis of your natal chart.",
    es: "Sección disponible con la suscripción Basic - análisis profundo de tu tema natal.",
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
