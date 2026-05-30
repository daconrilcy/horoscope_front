// Justification astrologique vulgarisee en fin de lecture natale.
import { useId, useState } from "react"
import { ChevronDown } from "lucide-react"

import type { UsedAstrologicalElementV1 } from "../../api/natal-chart"
import type { PublicCopyLang } from "./natalPublicFacts"
import { getNatalPublicCopy } from "./natalPublicCopy"
import "./NatalReadingSources.css"

type NatalReadingSourcesProps = {
  elements: UsedAstrologicalElementV1[]
  lang: PublicCopyLang
}

/** Bloc replie listant les appuis astrologiques lisibles sans identifiants techniques. */
export function NatalReadingSources({ elements, lang }: NatalReadingSourcesProps) {
  const copy = getNatalPublicCopy(lang).readingSources
  const [expanded, setExpanded] = useState(false)
  const panelId = useId()
  const buttonId = useId()

  if (elements.length === 0) {
    return null
  }

  return (
    <section className="natal-reading-sources" aria-labelledby={buttonId}>
      <h2 className="sr-only">{copy.title}</h2>
      <button
        id={buttonId}
        type="button"
        className="natal-reading-sources__toggle"
        aria-expanded={expanded}
        aria-controls={panelId}
        onClick={() => setExpanded((value) => !value)}
      >
        <span>{copy.title}</span>
        <ChevronDown
          size={18}
          className={expanded ? "natal-reading-sources__chevron is-open" : "natal-reading-sources__chevron"}
          aria-hidden="true"
        />
      </button>
      <div
        id={panelId}
        role="region"
        aria-labelledby={buttonId}
        className={expanded ? "natal-reading-sources__panel" : "natal-reading-sources__panel is-collapsed"}
        hidden={!expanded}
      >
        <ul className="natal-reading-sources__list">
          {elements.map((element) => (
            <li key={`${element.astrological_label}-${element.consequence}`}>
              <strong>{element.astrological_label}</strong>
              <span>{element.consequence}</span>
            </li>
          ))}
        </ul>
      </div>
    </section>
  )
}
