// Catalogue i18n de la couche publique de lecture du theme natal.
import type { PublicCopyLang } from "./natalPublicFacts"

export type NatalPublicCopy = {
  hero: {
    title: string
    lead: string
    sun: string
    moon: string
    ascendant: string
    missing: string
    traits: string
  }
  synthesis: { eyebrow: string; title: string }
  dna: {
    title: string
    unavailable: string
    publicSignals: string
    publicBalance: string
    why: string
    cards: {
      dominantPlanet: string
      chartRuler: string
      elevatedPlanet: string
      element: string
      modality: string
      polarity: string
    }
  }
  lifeDomains: { eyebrow: string; title: string; items: string[] }
  strengths: { eyebrow: string; title: string; dominant: string; unavailable: string }
  challenges: { eyebrow: string; title: string }
  majorAspects: {
    title: string
    empty: string
    impacts: { major: string; strong: string; secondary: string }
  }
  karmic: { eyebrow: string; title: string; northNode: string; southNode: string; saturn: string; pluto: string }
  hiddenTalents: { eyebrow: string; title: string }
  relationship: { eyebrow: string; title: string }
  career: { eyebrow: string; title: string; elevatedPlanet: string; unavailable: string }
  astrologerMode: {
    eyebrow: string
    title: string
    show: string
    hide: string
    reserved: string
    upsell: string
    offers: string
  }
  narrativeReading: {
    eyebrow: string
    title: string
    chapterOrder: Array<
      "personality" | "emotional_world" | "relationships" | "vocation" | "evolution_path"
    >
  }
  readingSources: {
    title: string
  }
}

const COPY: Record<PublicCopyLang, NatalPublicCopy> = {
  fr: {
    hero: {
      title: "Votre profil astrologique",
      lead: "Les trois portes d'entree de votre theme: elan vital, monde emotionnel et facon d'entrer en relation avec le monde.",
      sun: "Soleil", moon: "Lune", ascendant: "Ascendant", missing: "Donnee indisponible", traits: "Traits dominants",
    },
    synthesis: { eyebrow: "Synthese IA", title: "Ce que votre theme raconte" },
    dna: {
      title: "ADN astrologique", unavailable: "Indisponible", publicSignals: "Repere fourni par les signaux publics.",
      publicBalance: "Equilibre global fourni par le payload public.", why: "Pourquoi ?",
      cards: {
        dominantPlanet: "Dominante planetaire", chartRuler: "Maitre du theme", elevatedPlanet: "Planete culminante",
        element: "Element dominant", modality: "Modalite dominante", polarity: "Polarite dominante",
      },
    },
    lifeDomains: { eyebrow: "Domaines de vie", title: "Les grands domaines de vie", items: ["Personnalite", "Emotions", "Relations", "Carriere", "Argent", "Spiritualite"] },
    strengths: { eyebrow: "Appuis", title: "Forces", dominant: "Dominante", unavailable: "Dominante indisponible" },
    challenges: { eyebrow: "Axes de croissance", title: "Defis" },
    majorAspects: { title: "Aspects majeurs", empty: "Aucun classement d'aspects dominant n'est disponible dans ce payload.", impacts: { major: "Impact majeur", strong: "Impact fort", secondary: "Impact secondaire" } },
    karmic: { eyebrow: "Signature karmique", title: "Votre trajectoire d'evolution", northNode: "Noeud Nord", southNode: "Noeud Sud", saturn: "Saturne", pluto: "Pluton" },
    hiddenTalents: { eyebrow: "Potentiels", title: "Talents caches" },
    relationship: { eyebrow: "Lien", title: "Potentiel relationnel" },
    career: { eyebrow: "Vocation", title: "Potentiel professionnel", elevatedPlanet: "Planete culminante", unavailable: "Planete culminante indisponible" },
    astrologerMode: { eyebrow: "Mode astrologue", title: "Details techniques", show: "Afficher les details techniques", hide: "Masquer les details techniques", reserved: "Mode astrologue reserve", upsell: "Passez a Premium pour consulter le panneau expert et les donnees techniques completes.", offers: "Voir les offres" },
    narrativeReading: {
      eyebrow: "Lecture",
      title: "Votre lecture natale",
      chapterOrder: ["personality", "emotional_world", "relationships", "vocation", "evolution_path"],
    },
    readingSources: { title: "Ce que nous avons utilise" },
  },
  en: {
    hero: { title: "Your astrological profile", lead: "The three entry points of your chart: vitality, emotional world, and the way you meet life.", sun: "Sun", moon: "Moon", ascendant: "Ascendant", missing: "Unavailable data", traits: "Dominant traits" },
    synthesis: { eyebrow: "AI synthesis", title: "What your chart reveals" },
    dna: { title: "Astrological DNA", unavailable: "Unavailable", publicSignals: "Reference provided by public signals.", publicBalance: "Global balance provided by the public payload.", why: "Why?", cards: { dominantPlanet: "Dominant planet", chartRuler: "Chart ruler", elevatedPlanet: "Most elevated planet", element: "Dominant element", modality: "Dominant modality", polarity: "Dominant polarity" } },
    lifeDomains: { eyebrow: "Life domains", title: "Major life domains", items: ["Personality", "Emotions", "Relationships", "Career", "Money", "Spirituality"] },
    strengths: { eyebrow: "Supports", title: "Strengths", dominant: "Dominant", unavailable: "Dominant unavailable" },
    challenges: { eyebrow: "Growth areas", title: "Challenges" },
    majorAspects: { title: "Major aspects", empty: "No dominant-aspect ranking is available in this payload.", impacts: { major: "Major impact", strong: "Strong impact", secondary: "Secondary impact" } },
    karmic: { eyebrow: "Karmic signature", title: "Your path of evolution", northNode: "North Node", southNode: "South Node", saturn: "Saturn", pluto: "Pluto" },
    hiddenTalents: { eyebrow: "Potential", title: "Hidden talents" },
    relationship: { eyebrow: "Connection", title: "Relationship potential" },
    career: { eyebrow: "Vocation", title: "Career potential", elevatedPlanet: "Most elevated planet", unavailable: "Most elevated planet unavailable" },
    astrologerMode: { eyebrow: "Astrologer mode", title: "Technical details", show: "Show technical details", hide: "Hide technical details", reserved: "Astrologer mode reserved", upsell: "Upgrade to Premium to view the expert panel and complete technical data.", offers: "View plans" },
    narrativeReading: {
      eyebrow: "Reading",
      title: "Your natal reading",
      chapterOrder: ["personality", "emotional_world", "relationships", "vocation", "evolution_path"],
    },
    readingSources: { title: "What we used" },
  },
  es: {
    hero: { title: "Tu perfil astrologico", lead: "Las tres puertas de entrada de tu carta: impulso vital, mundo emocional y forma de relacionarte con el mundo.", sun: "Sol", moon: "Luna", ascendant: "Ascendente", missing: "Dato no disponible", traits: "Rasgos dominantes" },
    synthesis: { eyebrow: "Sintesis IA", title: "Lo que cuenta tu carta" },
    dna: { title: "ADN astrologico", unavailable: "No disponible", publicSignals: "Referencia proporcionada por las senales publicas.", publicBalance: "Equilibrio global proporcionado por el payload publico.", why: "Por que?", cards: { dominantPlanet: "Planeta dominante", chartRuler: "Regente de la carta", elevatedPlanet: "Planeta culminante", element: "Elemento dominante", modality: "Modalidad dominante", polarity: "Polaridad dominante" } },
    lifeDomains: { eyebrow: "Areas de vida", title: "Las grandes areas de vida", items: ["Personalidad", "Emociones", "Relaciones", "Carrera", "Dinero", "Espiritualidad"] },
    strengths: { eyebrow: "Apoyos", title: "Fortalezas", dominant: "Dominante", unavailable: "Dominante no disponible" },
    challenges: { eyebrow: "Areas de crecimiento", title: "Desafios" },
    majorAspects: { title: "Aspectos principales", empty: "No hay una clasificacion de aspectos dominantes disponible en este payload.", impacts: { major: "Impacto principal", strong: "Impacto fuerte", secondary: "Impacto secundario" } },
    karmic: { eyebrow: "Firma karmica", title: "Tu trayectoria de evolucion", northNode: "Nodo Norte", southNode: "Nodo Sur", saturn: "Saturno", pluto: "Pluton" },
    hiddenTalents: { eyebrow: "Potenciales", title: "Talentos ocultos" },
    relationship: { eyebrow: "Vinculo", title: "Potencial relacional" },
    career: { eyebrow: "Vocacion", title: "Potencial profesional", elevatedPlanet: "Planeta culminante", unavailable: "Planeta culminante no disponible" },
    astrologerMode: { eyebrow: "Modo astrologo", title: "Detalles tecnicos", show: "Mostrar detalles tecnicos", hide: "Ocultar detalles tecnicos", reserved: "Modo astrologo reservado", upsell: "Pasa a Premium para consultar el panel experto y los datos tecnicos completos.", offers: "Ver ofertas" },
    narrativeReading: {
      eyebrow: "Lectura",
      title: "Tu lectura natal",
      chapterOrder: ["personality", "emotional_world", "relationships", "vocation", "evolution_path"],
    },
    readingSources: { title: "Lo que hemos utilizado" },
  },
  de: {
    hero: { title: "Dein astrologisches Profil", lead: "Die drei Einstiegspunkte deines Horoskops: Lebenskraft, Gefuhlswelt und deine Art, der Welt zu begegnen.", sun: "Sonne", moon: "Mond", ascendant: "Aszendent", missing: "Daten nicht verfugbar", traits: "Dominante Eigenschaften" },
    synthesis: { eyebrow: "KI-Synthese", title: "Was dein Horoskop erzahlt" },
    dna: { title: "Astrologische DNA", unavailable: "Nicht verfugbar", publicSignals: "Hinweis aus den offentlichen Signalen.", publicBalance: "Gesamtbalance aus dem offentlichen Payload.", why: "Warum?", cards: { dominantPlanet: "Dominanter Planet", chartRuler: "Horoskopherrscher", elevatedPlanet: "Hochster Planet", element: "Dominantes Element", modality: "Dominante Modalitat", polarity: "Dominante Polaritat" } },
    lifeDomains: { eyebrow: "Lebensbereiche", title: "Die wichtigsten Lebensbereiche", items: ["Personlichkeit", "Emotionen", "Beziehungen", "Beruf", "Geld", "Spiritualitat"] },
    strengths: { eyebrow: "Stutzen", title: "Starken", dominant: "Dominant", unavailable: "Dominanz nicht verfugbar" },
    challenges: { eyebrow: "Wachstumsfelder", title: "Herausforderungen" },
    majorAspects: { title: "Hauptaspekte", empty: "In diesem Payload ist keine Rangliste dominanter Aspekte verfugbar.", impacts: { major: "Sehr starker Einfluss", strong: "Starker Einfluss", secondary: "Sekundarer Einfluss" } },
    karmic: { eyebrow: "Karmische Signatur", title: "Dein Entwicklungsweg", northNode: "Nordknoten", southNode: "Sudknoten", saturn: "Saturn", pluto: "Pluto" },
    hiddenTalents: { eyebrow: "Potenziale", title: "Verborgene Talente" },
    relationship: { eyebrow: "Verbindung", title: "Beziehungspotenzial" },
    career: { eyebrow: "Berufung", title: "Berufliches Potenzial", elevatedPlanet: "Hochster Planet", unavailable: "Hochster Planet nicht verfugbar" },
    astrologerMode: { eyebrow: "Astrologenmodus", title: "Technische Details", show: "Technische Details anzeigen", hide: "Technische Details ausblenden", reserved: "Astrologenmodus reserviert", upsell: "Wechsle zu Premium, um das Expertenpanel und die vollstandigen technischen Daten zu sehen.", offers: "Angebote ansehen" },
    narrativeReading: {
      eyebrow: "Lesung",
      title: "Deine Geburtshoroskop-Lesung",
      chapterOrder: ["personality", "emotional_world", "relationships", "vocation", "evolution_path"],
    },
    readingSources: { title: "Was wir verwendet haben" },
  },
}

/** Retourne la copy publique localisee avec fallback francais. */
export function getNatalPublicCopy(lang: PublicCopyLang | undefined): NatalPublicCopy {
  return COPY[lang ?? "fr"] ?? COPY.fr
}
