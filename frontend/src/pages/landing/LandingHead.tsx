// Owner local des balises SEO exposees par la page marketing landing.
import { useEffect } from "react"
import type { LandingTranslation } from "../../i18n"

type ManagedElement<T extends Element> = {
  element: T
  created: boolean
}

type ManagedMeta = ManagedElement<HTMLMetaElement> & {
  previousContent: string | null
}

type ManagedLink = ManagedElement<HTMLLinkElement> & {
  previousHref: string | null
}

type ManagedScript = ManagedElement<HTMLScriptElement> & {
  previousText: string | null
}

type LandingHeadProps = {
  seo: LandingTranslation["seo"]
  faqItems: LandingTranslation["faq"]["items"]
}

const JSON_LD_APP_ID = "json-ld-app"
const JSON_LD_FAQ_ID = "json-ld-faq"

/**
 * Retrouve ou cree une balise meta par nom pour la restaurer au demontage.
 */
function ensureMetaByName(name: string): ManagedMeta {
  const existing = document.querySelector<HTMLMetaElement>(`meta[name="${name}"]`)
  if (existing) {
    return {
      element: existing,
      created: false,
      previousContent: existing.getAttribute("content"),
    }
  }

  const element = document.createElement("meta")
  element.name = name
  document.head.appendChild(element)

  return { element, created: true, previousContent: null }
}

/**
 * Retrouve ou cree une balise Open Graph pour la restaurer au demontage.
 */
function ensureMetaByProperty(property: string): ManagedMeta {
  const existing = document.querySelector<HTMLMetaElement>(`meta[property="${property}"]`)
  if (existing) {
    return {
      element: existing,
      created: false,
      previousContent: existing.getAttribute("content"),
    }
  }

  const element = document.createElement("meta")
  element.setAttribute("property", property)
  document.head.appendChild(element)

  return { element, created: true, previousContent: null }
}

/**
 * Retrouve ou cree le lien canonique gere par la landing.
 */
function ensureCanonicalLink(): ManagedLink {
  const existing = document.querySelector<HTMLLinkElement>('link[rel="canonical"]')
  if (existing) {
    return {
      element: existing,
      created: false,
      previousHref: existing.getAttribute("href"),
    }
  }

  const element = document.createElement("link")
  element.setAttribute("rel", "canonical")
  document.head.appendChild(element)

  return { element, created: true, previousHref: null }
}

/**
 * Retrouve ou cree un script JSON-LD gere par la landing.
 */
function ensureJsonLdScript(id: string): ManagedScript {
  const existing = document.getElementById(id)
  if (existing instanceof HTMLScriptElement) {
    return {
      element: existing,
      created: false,
      previousText: existing.textContent,
    }
  }

  const element = document.createElement("script")
  element.id = id
  element.type = "application/ld+json"
  document.head.appendChild(element)

  return { element, created: true, previousText: null }
}

/**
 * Remet une balise meta dans son etat precedent.
 */
function restoreMeta(meta: ManagedMeta): void {
  if (meta.created) {
    meta.element.remove()
    return
  }

  if (meta.previousContent === null) {
    meta.element.removeAttribute("content")
    return
  }

  meta.element.setAttribute("content", meta.previousContent)
}

/**
 * Remet le lien canonique dans son etat precedent.
 */
function restoreCanonicalLink(link: ManagedLink): void {
  if (link.created) {
    link.element.remove()
    return
  }

  if (link.previousHref === null) {
    link.element.removeAttribute("href")
    return
  }

  link.element.setAttribute("href", link.previousHref)
}

/**
 * Remet un script JSON-LD dans son etat precedent.
 */
function restoreJsonLdScript(script: ManagedScript): void {
  if (script.created) {
    script.element.remove()
    return
  }

  script.element.textContent = script.previousText
}

/**
 * Construit le schema JSON-LD de l'application publique.
 */
function createAppSchema() {
  return {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    name: "Astrorizon",
    applicationCategory: "LifestyleApplication",
    offers: { "@type": "Offer", price: "0", priceCurrency: "EUR" },
    operatingSystem: "Web",
  }
}

/**
 * Construit le schema JSON-LD FAQ depuis les traductions landing.
 */
function createFaqSchema(items: LandingHeadProps["faqItems"]) {
  return {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    mainEntity: items.map((item) => ({
      "@type": "Question",
      name: item.q,
      acceptedAnswer: {
        "@type": "Answer",
        text: item.a,
      },
    })),
  }
}

/**
 * Calcule l'URL canonique de production pour la route courante.
 */
function productionCanonicalUrl(): string {
  const productionUrl = import.meta.env.VITE_PRODUCTION_URL || "https://astrorizon.ai"
  return `${productionUrl}${window.location.pathname}`
}

/**
 * Applique et nettoie les balises head propres a la route landing.
 */
export function LandingHead({ seo, faqItems }: LandingHeadProps) {
  useEffect(() => {
    const previousTitle = document.title
    document.title = seo.title

    const description = ensureMetaByName("description")
    description.element.setAttribute("content", seo.description)

    const openGraphTags = [
      [ensureMetaByProperty("og:title"), seo.ogTitle],
      [ensureMetaByProperty("og:description"), seo.ogDescription],
      [ensureMetaByProperty("og:type"), "website"],
      [ensureMetaByProperty("og:url"), window.location.href],
    ] as const

    openGraphTags.forEach(([meta, content]) => {
      meta.element.setAttribute("content", content)
    })

    const canonical = ensureCanonicalLink()
    canonical.element.setAttribute("href", productionCanonicalUrl())

    const appSchema = ensureJsonLdScript(JSON_LD_APP_ID)
    appSchema.element.textContent = JSON.stringify(createAppSchema())

    const faqSchema = ensureJsonLdScript(JSON_LD_FAQ_ID)
    faqSchema.element.textContent = JSON.stringify(createFaqSchema(faqItems))

    return () => {
      document.title = previousTitle
      restoreMeta(description)
      openGraphTags.forEach(([meta]) => restoreMeta(meta))
      restoreCanonicalLink(canonical)
      restoreJsonLdScript(appSchema)
      restoreJsonLdScript(faqSchema)
    }
  }, [faqItems, seo])

  return null
}
