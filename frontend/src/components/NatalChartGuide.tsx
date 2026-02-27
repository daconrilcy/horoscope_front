import type { AstrologyLang } from "../i18n/astrology"
import { natalChartTranslations } from "../i18n/natalChart"

interface NatalChartGuideProps {
  lang: AstrologyLang
  missingBirthTime: boolean
}

export function NatalChartGuide({ lang, missingBirthTime }: NatalChartGuideProps) {
  const g = natalChartTranslations[lang].guide

  return (
    <details className="card natal-chart-guide">
      <summary className="natal-chart-guide__summary">{g.title}</summary>
      <div className="natal-chart-guide__content">
        <p className="natal-chart-guide__intro">{g.intro}</p>

        <section className="natal-chart-guide__section">
          <h3>{g.signsTitle}</h3>
          <p>{g.signsDesc}</p>
          <p>
            <code>{g.signExample}</code>
          </p>
        </section>

        <section className="natal-chart-guide__section">
          <h3>{g.planetsTitle}</h3>
          <p>{g.planetsDesc}</p>
          <p>{g.planetsRetrogradeTip}</p>
        </section>

        <section className="natal-chart-guide__section">
          <h3>{g.housesTitle}</h3>
          <p>
            <strong>{g.housesIntervalTitle}</strong>
          </p>
          <p>{g.housesIntervalDesc}</p>
          <p>
            <strong>{g.wrapTitle}</strong>
          </p>
          <p>{g.wrapDesc}</p>
          <p>
            <code>{g.wrapExample}</code>
          </p>
        </section>

        <section className="natal-chart-guide__section">
          <h3>{g.anglesTitle}</h3>
          <p>{g.anglesDesc}</p>
        </section>

        <section className="natal-chart-guide__section">
          <h3>{g.sunAscendantTitle}</h3>
          <p>{g.sunAscendantDesc}</p>
          {missingBirthTime && (
            <p className="natal-chart-guide__missing-time" role="note">
              {g.ascendantMissing}
            </p>
          )}
        </section>

        <section className="natal-chart-guide__section">
          <h3>{g.aspectsTitle}</h3>
          <p>{g.aspectsDesc}</p>
        </section>

        <section className="natal-chart-guide__section natal-chart-guide__faq">
          <h3>{g.faqTitle}</h3>
          <dl>
            {g.faq.map((item) => (
              <div key={item.question} className="natal-chart-guide__faq-item">
                <dt>{item.question}</dt>
                <dd>{item.answer}</dd>
              </div>
            ))}
          </dl>
        </section>
      </div>
    </details>
  )
}
