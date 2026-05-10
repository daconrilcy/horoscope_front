// Compose la route detaillee du profil astrologue et ses interactions locales.
import { useNavigate, useParams } from "react-router-dom"
import { useState } from "react"
import { Award, BookOpen, Calendar, Check, ChevronLeft, Clock, GraduationCap, Heart, MapPin, Orbit, Quote, Sparkles, Star, Users, Zap } from "lucide-react"

import { useAstrologer, rateAstrologer } from "../api/astrologers"
import { useUserSettings, useUpdateUserSettings } from "@api/userSettings"
import { detectLang } from "../i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"
import {
  AstrologerProfileFinalCta,
  AstrologerProfileMethodSection,
  AstrologerProfileMetricsBar,
  AstrologerProfileReviewsSection,
  type AstrologerProfileMetricItem,
  type AstrologerProfileTrustItem,
} from "../features/astrologers/components/AstrologerProfileSections"
import { PageLayout } from "../layouts"
import { ErrorState, Button } from "@ui"
import "./AstrologerProfilePage.css"
type BackgroundMetric = {
  value: string
  label: string
}
function formatCompactCount(value: number): string {
  if (value >= 1000) {
    const rounded = Math.round(value / 100) / 10
    return `+${String(rounded).replace(".0", "")}k`
  }
  return `+${value}`
}
function formatReviewPercentage(value: number): number {
  return Math.max(0, Math.min(100, Math.round((value / 5) * 100)))
}
function normalizeBackgroundLabel(label: string): string {
  return label
    .replace(/\((.*?)\)/g, "$1")
    .replace(/\s*\/\s*/g, " & ")
    .replace(/\s{2,}/g, " ")
    .trim()
}

function extractYearsMetric(
  entries: string[],
  matcher: (entry: string) => boolean,
  fallbackYears?: number,
  fallbackLabel?: string
): BackgroundMetric | null {
  const matchedEntry = entries.find((entry) => matcher(entry))
  if (matchedEntry) {
    const match = matchedEntry.match(/(\d+\s*ans?)\s+(.*)/i)
    if (match) {
      return {
        value: match[1].replace(/\s+/g, " ").trim(),
        label: normalizeBackgroundLabel(match[2]),
      }
    }

    const normalized = normalizeBackgroundLabel(matchedEntry)
    if (normalized) {
      const [head, ...rest] = normalized.split(" ")
      return {
        value: head,
        label: rest.join(" ") || fallbackLabel || normalized,
      }
    }
  }

  if (fallbackYears && fallbackYears > 0) {
    return {
      value: `${fallbackYears} ans`,
      label: fallbackLabel ?? "Expérience",
    }
  }

  return null
}

function getProfessionalMetric(entries: string[], totalExperienceYears?: number): BackgroundMetric | null {
  const nonAstrologyMetric = extractYearsMetric(
    entries,
    (entry) => !/astrolog|astro/i.test(entry) && /\d+\s*ans?/i.test(entry),
    totalExperienceYears,
    "Expérience métier"
  )
  if (nonAstrologyMetric) {
    return {
      value: nonAstrologyMetric.value,
      label: nonAstrologyMetric.label || "Expérience métier",
    }
  }

  return extractYearsMetric(
    entries,
    (entry) => !/astrolog|astro/i.test(entry),
    undefined,
    "Parcours métier"
  )
}

function getAstrologyMetric(entries: string[], astrologyExperienceYears: number): BackgroundMetric {
  const astrologyMetric = extractYearsMetric(
    entries,
    (entry) => /astrolog|astro/i.test(entry),
    astrologyExperienceYears,
    "Astrologue"
  )
  return astrologyMetric ?? {
    value: `${astrologyExperienceYears} ans`,
    label: "Astrologue",
  }
}

function getApproachTitle(style: string, firstName: string): string {
  const lowered = style.toLowerCase()
  if (lowered.includes("pédag")) {
    return "Son approche pédagogique"
  }
  if (lowered.includes("analyt")) {
    return "Son approche analytique"
  }
  if (lowered.includes("myst") || lowered.includes("symbol")) {
    return "Son approche symbolique"
  }
  if (lowered.includes("pragm")) {
    return "Son approche pragmatique"
  }
  return `La méthode de ${firstName}`
}

function getProfileSubtitle(style: string, bioShort: string): string {
  const loweredStyle = style.toLowerCase()
  const loweredBio = bioShort.toLowerCase()

  if (loweredStyle.includes("pédag")) {
    return loweredBio.includes("généraliste")
      ? "Astrologue Généraliste & Pédagogue"
      : "Astrologue Pédagogue"
  }
  if (loweredStyle.includes("analyt")) {
    return "Astrologue Technique & Analytique"
  }
  if (loweredStyle.includes("myst") || loweredStyle.includes("symbol")) {
    return "Astrologue Mystique & Symbolique"
  }
  if (loweredStyle.includes("pragm")) {
    return "Astrologue Direct & Pragmatique"
  }
  if (loweredStyle.includes("relation") || loweredStyle.includes("bienve")) {
    return "Astrologue Relationnelle & Chaleureuse"
  }
  return `Astrologue ${style}`
}

function getIdealForLabel(value: string | undefined): string | null {
  if (!value) {
    return null
  }

  const lowered = value.toLowerCase()
  if (lowered.includes("début")) return "Idéal pour débutants"
  if (lowered.includes("relation")) return "Idéal pour relations"
  if (lowered.includes("analys")) return "Idéal pour analyse précise"
  if (lowered.includes("transit")) return "Idéal pour transitions"
  return value
}

function getSpecialtyIcon(title: string, index: number) {
  const lowered = title.toLowerCase()
  if (lowered.includes("thème") || lowered.includes("natal")) return BookOpen
  if (lowered.includes("signe") || lowered.includes("maison")) return GraduationCap
  if (lowered.includes("aspect")) return Sparkles
  if (lowered.includes("cycle") || lowered.includes("transit")) return Orbit
  return [BookOpen, GraduationCap, Sparkles, Orbit][index % 4]
}

function getProviderTypeLabel(providerType: string | undefined): string {
  return providerType === "real" ? "Astrologue réel" : "Astrologue IA"
}

export function AstrologerProfilePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: profile, isPending, error, refetch } = useAstrologer(id)
  const { data: preferences } = useUserSettings()
  const updateSettings = useUpdateUserSettings()
  const lang = detectLang()
  const [isRating, setIsRating] = useState(false)
  const [imgError, setImgError] = useState(false)
  const [isReviewComposerOpen, setIsReviewComposerOpen] = useState(false)
  const [draftRating, setDraftRating] = useState<number | null>(null)
  const [reviewDraft, setReviewDraft] = useState("")
  const [reviewError, setReviewError] = useState<string | null>(null)

  const isDefault = profile?.id === preferences?.default_astrologer_id

  const handleBack = () => {
    navigate("/astrologers")
  }

  const handleToggleDefault = () => {
    if (!profile || updateSettings.isPending) return
    updateSettings.mutate({ default_astrologer_id: isDefault ? null : profile.id })
  }

  const handleReviewComposerOpen = (rating: number) => {
    if (!profile || isRating || profile.user_rating) {
      return
    }
    setDraftRating(rating)
    setReviewDraft(profile.user_review?.comment ?? "")
    setReviewError(null)
    setIsReviewComposerOpen(true)
  }

  const closeReviewComposer = () => {
    setIsReviewComposerOpen(false)
    setDraftRating(null)
    setReviewDraft("")
    setReviewError(null)
  }

  const submitReview = async (comment?: string) => {
    if (!profile || isRating) {
      return
    }

    const rating = profile.user_rating ?? draftRating
    if (!rating) {
      return
    }

    setIsRating(true)
    try {
      await rateAstrologer(profile.id, { rating, comment, tags: [] })
      await refetch()
      closeReviewComposer()
    } catch {
      // Keep the current rating visible; the API error is already surfaced elsewhere.
    } finally {
      setIsRating(false)
    }
  }

  const handlePublishReview = async () => {
    const trimmedReview = reviewDraft.trim()
    if (!trimmedReview) {
      setReviewError(null)
      await submitReview(undefined)
      return
    }
    if (trimmedReview.length < 10) {
      setReviewError(t("review_form_min_length", lang))
      return
    }
    setReviewError(null)
    await submitReview(trimmedReview)
  }

  const handleChatCta = () => {
    if (!profile) {
      return
    }
    if (profile.action_state.has_chat && profile.action_state.last_chat_id) {
      navigate(`/chat/${encodeURIComponent(profile.action_state.last_chat_id)}`)
      return
    }
    navigate(`/chat?personaId=${encodeURIComponent(profile.id)}`)
  }

  const handleNatalCta = () => {
    if (!profile) {
      return
    }
    if (
      profile.action_state.has_natal_interpretation &&
      profile.action_state.last_natal_interpretation_id
    ) {
      navigate(
        `/natal?interpretationId=${encodeURIComponent(profile.action_state.last_natal_interpretation_id)}`
      )
      return
    }
    navigate(`/natal?personaId=${encodeURIComponent(profile.id)}`)
  }

  const handleConsultationCta = () => {
    if (!profile) {
      return
    }
    navigate(`/consultations/new?astrologerId=${encodeURIComponent(profile.id)}`)
  }

  if (isPending) {
    return (
      <PageLayout className="is-astrologer-profile-page">
        <div className="astrologer-profile-container">
          <div className="astrologer-profile-page-loading">
            {t("loading", lang)}
          </div>
        </div>
      </PageLayout>
    )
  }

  if (error || !profile) {
    if (error) {
      return (
        <PageLayout className="is-astrologer-profile-page">
          <div className="astrologer-profile-container">
            <ErrorState 
              title={t("error_loading", lang)}
              message={t("error_loading_description", lang)}
              onRetry={() => void refetch()}
            />
          </div>
        </PageLayout>
      )
    }

    return (
      <PageLayout className="is-astrologer-profile-page">
        <div className="astrologer-profile-container">
          <div className="profile-inline-error" role="alert">
            <h2 className="profile-inline-error__title">{t("profile_not_found", lang)}</h2>
            <p className="profile-inline-error__message">{t("profile_not_found_description", lang)}</p>
            <Button type="button" variant="secondary" onClick={handleBack}>
              {t("back_to_catalogue", lang)}
            </Button>
          </div>
        </div>
      </PageLayout>
    )
  }

  const fullName = [profile.first_name, profile.last_name].filter(Boolean).join(" ") || profile.name
  const metrics = profile.metrics ?? {
    total_experience_years: 0,
    experience_years: 0,
    consultations_count: 0,
    average_rating: 0,
  }
  const professionalMetric = getProfessionalMetric(
    profile.professional_background,
    profile.metrics?.total_experience_years
  )
  const astrologyMetric = getAstrologyMetric(
    profile.professional_background,
    metrics.experience_years
  )
  const averageRating = profile.review_summary.average_rating || metrics.average_rating || 0
  const reviewCount = profile.review_summary.review_count || 0
  const publicReviewCount = Math.max(reviewCount, profile.reviews.length)
  const hasPublicReviews = publicReviewCount > 0
  const satisfactionRate = formatReviewPercentage(averageRating)
  const recommendationRate = Math.max(0, satisfactionRate - 2)
  const subtitle = getProfileSubtitle(profile.style, profile.bio_short)
  const idealForLabel = getIdealForLabel(profile.ideal_for)
  const providerType = profile.provider_type ?? "ia"
  const trustItems: AstrologerProfileTrustItem[] =
    providerType === "real"
      ? [
          { icon: Clock, label: "Réservation sur demande" },
          { icon: Calendar, label: "Selon disponibilité" },
          { icon: Heart, label: "Réponse sous 24h" },
        ]
      : [
          { icon: Sparkles, label: "Inclus selon forfait" },
          { icon: Zap, label: "Ou via crédits" },
          { icon: Clock, label: "Accès immédiat" },
        ]
  const metricItems: AstrologerProfileMetricItem[] = [
    ...(professionalMetric
      ? [{
          key: "background",
          value: professionalMetric.value,
          label: professionalMetric.label,
          icon: BookOpen,
        }]
      : []),
    {
      key: "experience",
      value: astrologyMetric.value,
      label: astrologyMetric.label,
      icon: GraduationCap,
    },
    {
      key: "consultations",
      value: formatCompactCount(metrics.consultations_count),
      label: "Personnes accompagnées",
      icon: Users,
    },
    {
      key: "rating",
      value: hasPublicReviews ? `${averageRating.toFixed(1)}/5` : "Nouveau",
      label: hasPublicReviews ? "Note moyenne" : "Avis publics",
      icon: Star,
    },
  ]
  const showImage = profile.avatar_url && !imgError
  const displayedUserRating = profile.user_rating ?? draftRating ?? 0
  const hasWrittenReview = Boolean(profile.user_review?.comment?.trim())
  const canAddReviewText = Boolean(profile.user_rating) && !hasWrittenReview

  return (
    <PageLayout className="is-astrologer-profile-page">
      <div className="profile-bg-halo" />
      <div className="profile-noise" />
      
      <div className="astrologer-profile-container">
        <nav className="profile-nav">
          <button className="profile-back-btn" onClick={handleBack} aria-label={t("back_to_catalogue", lang)}>
            <ChevronLeft size={24} />
            <span className="profile-back-btn__label">Tous les astrologues</span>
          </button>
        </nav>

        <section className="profile-hero">
          <div className="profile-hero-avatar-container">
            <div className="profile-hero-avatar-glow" />
            <div className="profile-hero-avatar-orbit" />
            {showImage ? (
              <img 
                src={profile.avatar_url!} 
                alt={fullName} 
                className="profile-hero-avatar"
                onError={() => setImgError(true)}
              />
            ) : (
              <div className="profile-hero-avatar profile-hero-avatar--placeholder">
                <Users size={80} />
              </div>
            )}
          </div>
          <div className="profile-hero-content">
            <div className="profile-badge-row profile-badge-row--identity">
              <div className={`profile-provider-badge profile-provider-badge--${providerType}`}>
                <Sparkles size={14} />
                {getProviderTypeLabel(providerType)}
              </div>
              {idealForLabel && (
                <div className="profile-positioning-badge">
                  <Star size={14} />
                  {idealForLabel}
                </div>
              )}
            </div>
            <h1 className="profile-full-name">{fullName}</h1>
            <p className="profile-style-title">{subtitle}</p>
            <div className="profile-hero-actions">
              <Button
                type="button"
                variant="primary"
                size="lg"
                className="premium-cta premium-cta--primary profile-hero-cta"
                onClick={handleConsultationCta}
              >
                {t("cta_consultation", lang)}
              </Button>
              {isDefault ? (
                <span className="profile-default-badge profile-default-badge--selected">
                  <Check size={14} />
                  {t("your_default", lang)}
                </span>
              ) : null}
            </div>
            <div className="profile-metadata-row">
              {profile.age && (
                <div className="profile-meta-pill">
                  <Calendar size={16} />
                  <span>{profile.age} ans</span>
                </div>
              )}
              {metrics.experience_years > 0 && (
                <div className="profile-meta-pill">
                  <Award size={16} />
                  <span>{metrics.experience_years} {t("years_experience", lang)}</span>
                </div>
              )}
              {profile.location && (
                <div className="profile-meta-pill">
                  <MapPin size={16} />
                  <span>{profile.location}</span>
                </div>
              )}
              <button 
                className={`profile-meta-pill profile-meta-pill--default-action ${isDefault ? 'profile-meta-pill--default-active' : ''}`}
                onClick={handleToggleDefault}
                disabled={updateSettings.isPending}
              >
                {isDefault ? <Check size={16} /> : <Star size={16} />}
                <span>{isDefault ? "Astrologue par défaut" : "Définir par défaut"}</span>
              </button>
            </div>

            {profile.quote && (
              <blockquote className="profile-quote">
                <Quote size={24} className="quote-icon" />
                <p>{profile.quote}</p>
                <footer className="profile-quote-signature">— {profile.first_name}</footer>
              </blockquote>
            )}
          </div>
        </section>

        <AstrologerProfileMetricsBar items={metricItems} />

        <div className="profile-main-grid">
          <div className="profile-col-left">
            <section className="profile-about">
              <h2 className="profile-section-title profile-section-title--underlined">{`À propos de ${profile.first_name}`}</h2>
              <p className="profile-bio-text">{profile.bio_full}</p>
            </section>

            {profile.mission_statement && (
              <section className="profile-mission-card">
                <div className="profile-mission-card__icon">
                  <Heart size={20} />
                </div>
                <div className="profile-mission-card__content">
                  <h3>{t("mission_title", lang)}</h3>
                  <p className="profile-mission-text">{profile.mission_statement}</p>
                </div>
              </section>
            )}
          </div>

          <aside className="profile-col-right">
            <div className="sticky-sidebar">
              <div className="specialties-card">
                <h2 className="profile-section-title profile-section-title--sidebar">
                  Spécialités
                </h2>
                <div className="specialties-list">
                  {profile.specialties_details.length > 0 ? (
                    profile.specialties_details.map((s, i) => {
                      const Icon = getSpecialtyIcon(s.title, i)
                      return (
                        <div key={i} className="specialty-item">
                          <div className="specialty-item-icon-wrap">
                            <Icon size={22} className="specialty-item-icon" />
                          </div>
                          <div className="specialty-item-copy">
                            <span className="specialty-item-title">{s.title}</span>
                            <p className="specialty-item-desc">{s.description}</p>
                          </div>
                        </div>
                      )
                    })
                  ) : (
                    profile.specialties.map((s, i) => {
                      const Icon = getSpecialtyIcon(s, i)
                      return (
                        <div key={i} className="specialty-item">
                          <div className="specialty-item-icon-wrap">
                            <Icon size={22} className="specialty-item-icon" />
                          </div>
                          <div className="specialty-item-copy">
                            <span className="specialty-item-title">{s}</span>
                          </div>
                        </div>
                      )
                    })
                  )}
                </div>
              </div>
            </div>
          </aside>
        </div>

        <AstrologerProfileMethodSection
          title={getApproachTitle(profile.style, profile.first_name)}
          steps={[
            t("method_step_1", lang),
            t("method_step_2", lang),
            t("method_step_3", lang),
            t("method_step_4", lang),
          ]}
          helpers={[
            t("method_step_1_helper", lang),
            t("method_step_2_helper", lang),
            t("method_step_3_helper", lang),
            t("method_step_4_helper", lang),
          ]}
        />

        <AstrologerProfileReviewsSection
          profile={profile}
          averageRating={averageRating}
          reviewCount={publicReviewCount}
          satisfactionRate={satisfactionRate}
          recommendationRate={recommendationRate}
          displayedUserRating={displayedUserRating}
          canAddReviewText={canAddReviewText}
          isRating={isRating}
          labels={{
            reviewsTitle: t("reviews_title", lang),
            yourRatingTitle: t("your_rating_title", lang),
            reviewAddButton: t("review_add_button", lang),
            emptyReviewsBadge: t("reviews_empty_badge", lang),
            emptyReviewsPrompt: t("reviews_empty_prompt", lang),
            emptyReviewsDescription: t("reviews_empty_description", lang),
            reviewsWithoutExcerptsPrompt: t("reviews_without_excerpts_prompt", lang),
            reviewsWithoutExcerptsDescription: t("reviews_without_excerpts_description", lang),
            publicReviewsLabel: t("reviews_public_label", lang),
            discoveryLabel: t("reviews_discovery_label", lang),
          }}
          onReviewComposerOpen={handleReviewComposerOpen}
          onReviewTextComposerOpen={() => {
            setDraftRating(profile.user_rating ?? null)
            setReviewDraft(profile.user_review?.comment ?? "")
            setReviewError(null)
            setIsReviewComposerOpen(true)
          }}
        />
        <AstrologerProfileFinalCta
          profile={profile}
          trustItems={trustItems}
          isPrimary={hasPublicReviews}
          labels={{
            session: t("cta_consultation", lang),
            chat: profile.action_state.has_chat ? t("cta_chat_resume", lang) : t("cta_chat_new", lang),
            natal: profile.action_state.has_natal_interpretation ? t("cta_natal_view", lang) : t("cta_natal_new", lang),
          }}
          onConsultation={handleConsultationCta}
          onChat={handleChatCta}
          onNatal={handleNatalCta}
        />

        <div className="profile-bottom-back">
          <button type="button" className="profile-bottom-back__button" onClick={handleBack}>
            <ChevronLeft size={18} />
            <span>Retour aux astrologues</span>
          </button>
        </div>

        {isReviewComposerOpen ? (
          <div
            className="app-overlay review-composer-overlay"
            role="dialog"
            aria-modal="true"
            aria-labelledby="person-review-title"
            onClick={closeReviewComposer}
          >
            <div
              className="app-modal review-composer-modal"
              onClick={(event) => event.stopPropagation()}
            >
              <button
                type="button"
                className="review-composer-modal__close"
                onClick={closeReviewComposer}
                aria-label={t("close", lang)}
                disabled={isRating}
              >
                <span className="review-composer-modal__close-glyph" aria-hidden="true">
                  ×
                </span>
              </button>
              <h3 className="app-modal__title review-composer-modal__title" id="person-review-title">
                {t("review_form_title", lang)}
              </h3>
              <textarea
                id="person-review-textarea"
                className="review-composer-card__textarea"
                value={reviewDraft}
                onChange={(event) => {
                  setReviewDraft(event.target.value)
                  if (reviewError) {
                    setReviewError(null)
                  }
                }}
                placeholder={t("review_form_placeholder", lang)}
                rows={5}
              />
              {reviewError ? (
                <p className="review-composer-card__error" role="alert">
                  {reviewError}
                </p>
              ) : null}
              <div className="review-composer-card__actions">
                <Button
                  type="button"
                  variant="primary"
                  onClick={() => void handlePublishReview()}
                  disabled={isRating}
                >
                  {t("review_form_publish", lang)}
                </Button>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </PageLayout>
  )
}

