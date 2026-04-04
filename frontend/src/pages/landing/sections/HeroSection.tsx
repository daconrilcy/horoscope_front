import { useEffect, useMemo, useState } from "react"
import { ArrowRight, Check, Clock3, MessageCircleMore, Sparkles, Star } from "lucide-react"
import { Link } from "react-router-dom"
import { Button } from "../../../components/ui/Button/Button"
import { useAnalytics } from "../../../hooks/useAnalytics"
import { useAstrologyLabels, useTranslation } from "../../../i18n"

export const HeroSection = () => {
  const t = useTranslation("landing")
  const { lang } = useAstrologyLabels()
  const { track } = useAnalytics()
  const questionChars = useMemo(() => Array.from(t.hero.chatQuestion), [t.hero.chatQuestion])
  const answerChars = useMemo(() => Array.from(t.hero.chatAnswer), [t.hero.chatAnswer])
  const [liveState, setLiveState] = useState({
    toolIndex: 0,
    trendIndex: 0,
    questionLength: 0,
    answerLength: 0,
  })

  useEffect(() => {
    const cycleDurationMs = 5400
    const answerStartMs = 1100
    const startTime = Date.now()

    const updateLiveState = () => {
      const elapsed = (Date.now() - startTime) % cycleDurationMs
      const toolIndex = elapsed < 1800 ? 0 : elapsed < 3600 ? 1 : 2
      const trendIndex = elapsed < 1400 ? 0 : elapsed < 2800 ? 1 : 2
      const questionProgress = Math.min(1, elapsed / 900)
      const answerProgress = elapsed <= answerStartMs ? 0 : Math.min(1, (elapsed - answerStartMs) / 1700)

      setLiveState({
        toolIndex,
        trendIndex,
        questionLength: Math.floor(questionChars.length * questionProgress),
        answerLength: Math.floor(answerChars.length * answerProgress),
      })
    }

    updateLiveState()
    const intervalId = window.setInterval(updateLiveState, 80)

    return () => window.clearInterval(intervalId)
  }, [answerChars, questionChars])

  const liveQuestion = questionChars.slice(0, liveState.questionLength).join("")
  const liveAnswer = answerChars.slice(0, liveState.answerLength).join("")

  return (
    <section className="hero-section" aria-labelledby="hero-title">
      <div className="hero-content">
        <div className="hero-eyebrow">
          <Sparkles size={14} aria-hidden="true" />
          {t.hero.eyebrow}
        </div>

        <h1 id="hero-title">
          <span className="hero-title__lead">{t.hero.titleLead}</span>
          <span className="hero-title__accent">{t.hero.titleAccent}</span>
        </h1>
        <p className="hero-subtitle">{t.hero.subtitle}</p>

        <ul className="hero-bullets">
          <li className="hero-bullet-item">
            <Check className="hero-bullet-icon" size={18} aria-hidden="true" />
            <span>{t.hero.bullet1}</span>
          </li>
          <li className="hero-bullet-item">
            <Check className="hero-bullet-icon" size={18} aria-hidden="true" />
            <span>{t.hero.bullet2}</span>
          </li>
          <li className="hero-bullet-item">
            <Check className="hero-bullet-icon" size={18} aria-hidden="true" />
            <span>{t.hero.bullet3}</span>
          </li>
        </ul>

        <div className="hero-ctas">
          <Button
            as={Link}
            to="/register"
            variant="primary"
            size="lg"
            className="hero-cta-primary"
            onClick={() => track("hero_cta_click", { cta_label: t.hero.ctaPrimary })}
          >
            {t.hero.ctaPrimary}
            <ArrowRight size={18} className="hero-cta-icon-right" aria-hidden="true" />
          </Button>

          <a
            href="#how-it-works"
            className="hero-cta-secondary"
            onClick={() => track("secondary_cta_click", { cta_label: t.hero.ctaSecondary })}
          >
            <MessageCircleMore size={18} className="hero-cta-icon-left" aria-hidden="true" />
            {t.hero.ctaSecondary}
          </a>
        </div>

        <div className="hero-reassurance">
          <div className="hero-reassurance-item">
            <span className="hero-reassurance-dot" aria-hidden="true"></span>
            {t.hero.micro1}
          </div>
          <div className="hero-reassurance-item">
            <span className="hero-reassurance-dot" aria-hidden="true"></span>
            {t.hero.micro2}
          </div>
          <div className="hero-reassurance-item">
            <span className="hero-reassurance-dot" aria-hidden="true"></span>
            {t.hero.micro3}
          </div>
        </div>
      </div>

      <div className="hero-visual" aria-label={t.hero.imageAlt}>
        <div className="hero-visual-shell">
          <div className="hero-device">
            <div className="hero-device__bar">
              <div className="hero-device__brand">
                <span className="hero-device__dot"></span>
                <span className="hero-device__dot"></span>
                <span className="hero-device__dot"></span>
                <span className="hero-device__brand-name">Astrorizon</span>
              </div>
              <span className="hero-device__status">{t.hero.caption1}</span>
            </div>

            <div className="hero-device__preview">
              <span className="hero-device__preview-label">{t.hero.previewLabel}</span>
            </div>

            <div className="hero-device__toolbar" aria-hidden="true">
              <span
                className={`hero-device__tool ${liveState.toolIndex === 0 ? "hero-device__tool--active" : ""}`}
              >
                <Clock3 size={13} />
                <span>{t.hero.dailyLabel}</span>
              </span>
              <span
                className={`hero-device__tool ${liveState.toolIndex === 1 ? "hero-device__tool--active" : ""}`}
              >
                <MessageCircleMore size={13} />
                <span>{t.hero.chatLabel}</span>
              </span>
              <span
                className={`hero-device__tool ${liveState.toolIndex === 2 ? "hero-device__tool--active" : ""}`}
              >
                <Star size={13} />
                <span>{t.hero.momentLabel}</span>
              </span>
            </div>

            <article className="hero-card hero-card--summary">
              <div className="hero-panel__meta">
                <span className="hero-panel__label">
                  <Clock3 size={14} aria-hidden="true" />
                  {t.hero.dailyLabel}
                </span>
                <span className="hero-panel__badge">{t.hero.caption2}</span>
              </div>
              <h2 className="hero-panel__title">{t.hero.dailyTitle}</h2>
              <div className="hero-card__trend-grid">
                {t.hero.dailyItems.map(({ label, value }) => (
                  <div
                    key={label}
                    className={`hero-card__trend-item ${
                      t.hero.dailyItems[liveState.trendIndex]?.label === label
                        ? "hero-card__trend-item--active"
                        : ""
                    }`}
                  >
                    <span className="hero-card__trend-label">{label}</span>
                    <strong className="hero-card__trend-value">{value}</strong>
                  </div>
                ))}
              </div>
            </article>

            <div className="hero-device__grid">
              <article className="hero-card hero-card--chat">
                <div className="hero-panel__meta">
                  <span className="hero-panel__label">
                    <MessageCircleMore size={14} aria-hidden="true" />
                    {t.hero.chatLabel}
                  </span>
                </div>
                <p
                  className={`hero-chat__bubble hero-chat__bubble--question ${
                    liveState.toolIndex === 1 ? "hero-chat__bubble--active" : ""
                  }`}
                >
                  <span className="hero-chat__text hero-chat__text--question">{liveQuestion}</span>
                </p>
                <p
                  className={`hero-chat__bubble hero-chat__bubble--answer ${
                    liveState.toolIndex === 1 ? "hero-chat__bubble--active" : ""
                  }`}
                >
                  <span className="hero-chat__text hero-chat__text--answer">{liveAnswer}</span>
                </p>
              </article>

              <article className="hero-card hero-card--moment">
                <div className="hero-panel__meta">
                  <span className="hero-panel__label">
                    <Star size={14} aria-hidden="true" />
                    {t.hero.momentLabel}
                  </span>
                </div>
                <div className="hero-moment__value">
                  <Sparkles size={16} aria-hidden="true" />
                  <span>{t.solution.step3.benefit}</span>
                </div>
                <p className="hero-panel__text">{t.hero.momentText}</p>
              </article>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
