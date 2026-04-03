import { useEffect } from "react"
import { useTranslation } from "../../i18n"
import { useAnalytics, getUtmParams } from "../../hooks/useAnalytics"
import "./LandingPage.css"
import { HeroSection } from "./sections/HeroSection"
import { SocialProofSection } from "./sections/SocialProofSection"
import { ProblemSection } from "./sections/ProblemSection"
import { SolutionSection } from "./sections/SolutionSection"
import { TestimonialsSection } from "./sections/TestimonialsSection"
import { PricingSection } from "./sections/PricingSection"
import { FaqSection } from "./sections/FaqSection"

export const LandingPage = () => {
  const t = useTranslation("landing")
  const { track } = useAnalytics()

  useEffect(() => {
    // AC2: Track landing view
    track("landing_view", getUtmParams())

    // AC1: Meta tags SEO
    const previousTitle = document.title
    document.title = t.seo.title
    
    const metaDescription = document.querySelector('meta[name="description"]')
    const originalDescription = metaDescription?.getAttribute("content")
    
    if (metaDescription) {
      metaDescription.setAttribute("content", t.seo.description)
    } else {
      const meta = document.createElement('meta')
      meta.name = "description"
      meta.content = t.seo.description
      document.head.appendChild(meta)
    }

    // Open Graph helper
    const setOgMeta = (property: string, content: string) => {
      let meta = document.querySelector(`meta[property="${property}"]`)
      let created = false
      if (!meta) {
        meta = document.createElement('meta')
        meta.setAttribute('property', property)
        document.head.appendChild(meta)
        created = true
      }
      const original = meta.getAttribute('content')
      meta.setAttribute('content', content)
      return { meta, original, created }
    }

    const ogs = [
      setOgMeta('og:title', t.seo.ogTitle),
      setOgMeta('og:description', t.seo.ogDescription),
      setOgMeta('og:type', 'website'),
      setOgMeta('og:url', window.location.href)
    ]

    // Canonical
    let linkCanonical = document.querySelector('link[rel="canonical"]')
    const originalCanonical = linkCanonical?.getAttribute("href")
    let canonicalCreated = false
    if (!linkCanonical) {
      linkCanonical = document.createElement('link')
      linkCanonical.setAttribute('rel', 'canonical')
      document.head.appendChild(linkCanonical)
      canonicalCreated = true
    }
    // AC1.1.4: pointant vers l'URL de production
    const prodUrl = import.meta.env.VITE_PRODUCTION_URL || "https://astrorizon.ai"
    linkCanonical.setAttribute('href', prodUrl + window.location.pathname)

    // AC2: Structured Data
    const appSchema = {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "Astrorizon",
      "applicationCategory": "LifestyleApplication",
      "offers": { "@type": "Offer", "price": "0", "priceCurrency": "EUR" },
      "operatingSystem": "Web"
    }

    const faqSchema = {
      "@context": "https://schema.org",
      "@type": "FAQPage",
      "mainEntity": t.faq.items.map(item => ({
        "@type": "Question",
        "name": item.q,
        "acceptedAnswer": {
          "@type": "Answer",
          "text": item.a
        }
      }))
    }

    const injectScript = (id: string, schema: object) => {
      let script = document.getElementById(id) as HTMLScriptElement
      if (!script) {
        script = document.createElement('script')
        script.type = 'application/ld+json'
        script.id = id
        document.head.appendChild(script)
      }
      script.text = JSON.stringify(schema)
    }

    injectScript('json-ld-app', appSchema)
    injectScript('json-ld-faq', faqSchema)

    return () => {
      // Cleanup
      document.title = previousTitle
      if (originalDescription) {
        metaDescription?.setAttribute("content", originalDescription)
      } else if (!originalDescription && metaDescription) {
        // If we created it, remove it
        if (!document.querySelector('meta[name="description"]')) {
           // This case is tricky if other pages expect it to exist but be empty
        }
      }
      
      ogs.forEach(og => {
        if (og.created) {
          og.meta.remove()
        } else if (og.original) {
          og.meta.setAttribute('content', og.original)
        }
      })

      if (canonicalCreated) {
        linkCanonical?.remove()
      } else if (originalCanonical) {
        linkCanonical?.setAttribute('href', originalCanonical)
      }

      document.getElementById('json-ld-app')?.remove()
      document.getElementById('json-ld-faq')?.remove()
    }
  }, [t])

  return (
    <div className="landing-page">
      <HeroSection />
      <SocialProofSection />
      <ProblemSection />
      <SolutionSection />
      <TestimonialsSection />
      <PricingSection />
      <FaqSection />
    </div>
  )
}

// Ensure default export for React.lazy
export default LandingPage
