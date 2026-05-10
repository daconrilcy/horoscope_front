// Regroupe les sections lourdes du profil astrologue pour garder la route composeuse.
import type { ReactNode } from "react"
import type { LucideIcon } from "lucide-react"
import { ArrowRight, Heart, MessageSquare, Sparkles, Star } from "lucide-react"

import type { AstrologerProfile } from "@api/astrologers"
import { Button } from "@ui"

export type AstrologerProfileTrustItem = {
  icon: LucideIcon
  label: string
}

export type AstrologerProfileMetricItem = {
  key: string
  value: string
  label: string
  helper?: string
  icon: LucideIcon
}

type AstrologerProfileMetricsBarProps = {
  items: AstrologerProfileMetricItem[]
}

type AstrologerProfileMethodSectionProps = {
  title: string
  steps: string[]
  helpers?: string[]
}

type AstrologerProfileReviewsSectionProps = {
  profile: AstrologerProfile
  averageRating: number
  reviewCount: number
  satisfactionRate: number
  recommendationRate: number
  displayedUserRating: number
  canAddReviewText: boolean
  isRating: boolean
  labels: {
    reviewsTitle: string
    yourRatingTitle: string
    reviewAddButton: string
    emptyReviewsBadge: string
    emptyReviewsPrompt: string
    emptyReviewsDescription: string
    reviewsWithoutExcerptsPrompt: string
    reviewsWithoutExcerptsDescription: string
    publicReviewsLabel: string
    averageRatingPendingLabel: string
    averageRatingReadyLabel: string
  }
  onReviewComposerOpen: (rating: number) => void
  onReviewTextComposerOpen: () => void
}

type AstrologerProfileFinalCtaProps = {
  profile: AstrologerProfile
  trustItems: AstrologerProfileTrustItem[]
  isPrimary?: boolean
  labels: {
    session: string
    chat: string
    natal: string
  }
  onConsultation: () => void
  onChat: () => void
  onNatal: () => void
}

/** Rend les metriques du profil en barre autonome. */
export function AstrologerProfileMetricsBar({ items }: AstrologerProfileMetricsBarProps) {
  return (
    <section className="profile-metrics-bar">
      {items.map((item) => {
        const Icon = item.icon
        return (
          <div key={item.key} className="metric-card">
            <div className="metric-card__icon-wrap">
              <Icon size={24} className="metric-icon" />
            </div>
            <div className="metric-card__body">
              <span className="metric-value">{item.value}</span>
              <span className="metric-title">{item.label}</span>
              {item.helper ? <span className="metric-helper">{item.helper}</span> : null}
            </div>
          </div>
        )
      })}
    </section>
  )
}

/** Rend le deroule de methode du profil astrologue. */
export function AstrologerProfileMethodSection({ title, steps, helpers = [] }: AstrologerProfileMethodSectionProps) {
  return (
    <section className="profile-method">
      <h2 className="profile-section-title profile-section-title--method">
        <Sparkles size={22} />
        {title}
      </h2>
      <div className="profile-method-stepper">
        {steps.map((step, index) => (
          <FragmentWithArrow key={step} isLast={index === steps.length - 1}>
            <div className="method-step">
              <div className="step-number">{index + 1}</div>
              <div className="step-content">
                <p className="step-title">{step}</p>
                {helpers[index] ? <p className="step-helper">{helpers[index]}</p> : null}
              </div>
            </div>
          </FragmentWithArrow>
        ))}
      </div>
    </section>
  )
}

/** Rend la section avis du profil sans posseder les mutations de notation. */
export function AstrologerProfileReviewsSection({
  profile,
  averageRating,
  reviewCount,
  satisfactionRate,
  recommendationRate,
  displayedUserRating,
  canAddReviewText,
  isRating,
  labels,
  onReviewComposerOpen,
  onReviewTextComposerOpen,
}: AstrologerProfileReviewsSectionProps) {
  const hasPublicReviews = reviewCount > 0
  const hasReviewExcerpts = profile.reviews.length > 0
  const roundedAverage = Math.round(averageRating)

  return (
    <section className="profile-reviews-section">
      <div className="profile-reviews-section__header">
        <h2 className="profile-section-title profile-section-title--reviews">{labels.reviewsTitle}</h2>
        {hasPublicReviews ? (
          <div className="profile-reviews-summary">
            <div className="profile-reviews-stars" aria-hidden="true">
              {[1, 2, 3, 4, 5].map((star) => (
                <Star key={star} size={18} fill={star <= roundedAverage ? "currentColor" : "none"} />
              ))}
            </div>
            <span className="profile-reviews-summary__score">{`${averageRating.toFixed(1)}/5`}</span>
            <span className="profile-reviews-summary__count">{`(${reviewCount} avis)`}</span>
          </div>
        ) : (
          <div className="profile-reviews-summary profile-reviews-summary--empty">
            <Sparkles size={18} />
            <span className="profile-reviews-summary__score">{labels.emptyReviewsBadge}</span>
            <span className="profile-reviews-summary__count">{labels.emptyReviewsPrompt}</span>
          </div>
        )}
      </div>
      <div className="reviews-container">
        <div className="reviews-list">
          {hasReviewExcerpts ? (
            profile.reviews.map((review) => (
              <div key={review.id} className="review-item">
                <div className="review-quote-mark">“</div>
                {review.comment && <p className="review-comment">{review.comment}</p>}
                <div className="review-footer">
                  <div className="review-user-info">
                    <span className="review-user-name">{`— ${review.user_name}`}</span>
                    {review.tags.length > 0 ? (
                      <div className="review-tags">
                        {review.tags.map((tag) => (
                          <span key={tag} className="review-tag">
                            {tag}
                          </span>
                        ))}
                      </div>
                    ) : null}
                  </div>
                  <div className="review-rating">
                    {[...Array(5)].map((_, index) => (
                      <Star key={index} size={15} fill={index < review.rating ? "currentColor" : "none"} />
                    ))}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="review-item review-item--empty">
              <div className="review-empty-icon" aria-hidden="true">
                <Sparkles size={20} />
              </div>
              <p className="review-comment">
                {hasPublicReviews ? labels.reviewsWithoutExcerptsPrompt : labels.emptyReviewsPrompt}
              </p>
              <p className="review-empty-description">
                {hasPublicReviews ? labels.reviewsWithoutExcerptsDescription : labels.emptyReviewsDescription}
              </p>
            </div>
          )}
        </div>
        <div className="review-stats-card">
          <div className="review-stats-card__grid">
            <ReviewMetric value={reviewCount}>{labels.publicReviewsLabel}</ReviewMetric>
            <ReviewMetric value={hasPublicReviews ? `${satisfactionRate}%` : "À venir"}>
              {hasPublicReviews ? labels.averageRatingReadyLabel : labels.averageRatingPendingLabel}
            </ReviewMetric>
          </div>
          {hasPublicReviews ? (
            <div className="review-stats-card__recommendation">
              <Heart size={18} />
              <span>{`Recommandé par ${recommendationRate}%`}</span>
            </div>
          ) : null}

          <div className="review-stats-card__rating">
            <p className="step-title review-stats-card__rating-title">{labels.yourRatingTitle}</p>
            <div className="review-rating review-rating--interactive">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  className="review-rating__button"
                  onClick={() => onReviewComposerOpen(star)}
                  disabled={Boolean(profile.user_rating) || isRating}
                  aria-label={`${labels.yourRatingTitle} ${star}/5`}
                >
                  <Star
                    size={24}
                    fill={displayedUserRating >= star ? "currentColor" : "none"}
                    className="review-rating__star"
                  />
                </button>
              ))}
            </div>
            {canAddReviewText ? (
              <div className="review-stats-card__write-review">
                <Button type="button" variant="secondary" onClick={onReviewTextComposerOpen}>
                  {labels.reviewAddButton}
                </Button>
              </div>
            ) : null}
          </div>
        </div>
      </div>
    </section>
  )
}

/** Rend les appels a l'action finaux sans connaitre la navigation de la route. */
export function AstrologerProfileFinalCta({
  profile,
  trustItems,
  isPrimary = true,
  labels,
  onConsultation,
  onChat,
  onNatal,
}: AstrologerProfileFinalCtaProps) {
  return (
    <section className="profile-final-cta">
      <div className="profile-final-cta__sparkles" aria-hidden="true">✦</div>
      <h2 className="profile-full-name profile-full-name--cta">{`Commencer avec ${profile.first_name}`}</h2>
      <p className="profile-final-cta__subtitle">Réservez votre première session découverte</p>
      <Button
        size="lg"
        variant={isPrimary ? "primary" : "secondary"}
        className={`premium-cta ${isPrimary ? "premium-cta--primary" : "premium-cta--soft"}`}
        onClick={onConsultation}
        rightIcon={<ArrowRight size={20} />}
      >
        {labels.session}
      </Button>
      <div className="profile-final-cta__trust">
        {trustItems.map((item) => {
          const Icon = item.icon
          return (
            <span key={item.label}>
              <Icon size={14} />
              {item.label}
            </span>
          )
        })}
      </div>
      <div className="cta-group cta-group--secondary">
        <Button size="lg" variant="secondary" className="premium-cta" onClick={onChat} leftIcon={<MessageSquare size={18} />}>
          {labels.chat}
        </Button>

        <Button size="lg" variant="secondary" onClick={onNatal} leftIcon={<Sparkles size={18} />}>
          {labels.natal}
        </Button>
      </div>
    </section>
  )
}

function FragmentWithArrow({ children, isLast }: { children: ReactNode; isLast: boolean }) {
  return (
    <>
      {children}
      {!isLast ? <div className="method-arrow" aria-hidden="true">→</div> : null}
    </>
  )
}

function ReviewMetric({ value, children }: { value: number | string; children: ReactNode }) {
  const isTextValue = typeof value === "string" && Number.isNaN(Number(value.replace("%", "").replace(",", ".")))

  return (
    <div className="review-stats-card__metric">
      <div className={`big-rating${isTextValue ? " big-rating--text" : ""}`}>{value}</div>
      <p className="metric-title">{children}</p>
    </div>
  )
}
