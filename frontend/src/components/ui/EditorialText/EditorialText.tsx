// Rend les contenus éditoriaux avec les règles typographiques partagées du site.
import { Fragment } from "react"

type EditorialTextProps = {
  text: string
}

/** Insère un retour à la ligne après chaque deux-points sans altérer le texte source. */
export function EditorialText({ text }: EditorialTextProps) {
  if (!text) {
    return null
  }

  const segments = text.split(":")

  return (
    <>
      {segments.map((segment, index) => (
        <Fragment key={`${index}-${segment}`}>
          {segment}
          {index < segments.length - 1 ? (
            <>
              :<br />
            </>
          ) : null}
        </Fragment>
      ))}
    </>
  )
}
