import { useNavigate, useParams } from "react-router-dom"
import { useState } from "react"
import { 
  ChevronLeft, 
  MapPin, 
  Calendar, 
  Award, 
  Star, 
  Quote, 
  CheckCircle2, 
  Users, 
  MessageSquare, 
  Clock,
  Sparkles,
  Zap,
  Heart
} from "lucide-react"

import { useAstrologer, rateAstrologer } from "../api/astrologers"
import { detectLang } from "../i18n/astrology"
import { tAstrologers as t } from "@i18n/astrologers"
import { PageLayout } from "../layouts"
import { ErrorState, Button } from "@ui"
import "./AstrologerProfilePage.css"

export function AstrologerProfilePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { data: profile, isPending, error, refetch } = useAstrologer(id)
  const lang = detectLang()
  
  const [isRating, setIsRating] = useState(false)
  const [imgError, setImgError] = useState(false)

  const handleBack = () => {
    navigate("/astrologers")
  }

  const handleRate = async (rating: number) => {
    if (!profile || isRating) return
    setIsRating(true)
    try {
      await rateAstrologer(profile.id, { rating })
      await refetch()
    } catch (err) {
      console.error("Failed to rate:", err)
    } finally {
      setIsRating(false)
    }
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
    return (
      <PageLayout className="is-astrologer-profile-page">
        <div className="astrologer-profile-container">
          <ErrorState 
            title={t("profile_not_found", lang)}
            message={t("profile_not_found_description", lang)}
            onRetry={handleBack}
          />
        </div>
      </PageLayout>
    )
  }

  const fullName = `${profile.first_name} ${profile.last_name}`.trim() || profile.name
  const showImage = profile.avatar_url && !imgError

  return (
    <PageLayout className="is-astrologer-profile-page">
      <div className="profile-bg-halo" />
      <div className="profile-noise" />
      
      <div className="astrologer-profile-container">
        {/* Header Nav */}
        <nav className="profile-nav">
          <button className="profile-back-btn" onClick={handleBack} aria-label={t("back_to_catalogue", lang)}>
            <ChevronLeft size={24} />
          </button>
        </nav>

        {/* Hero Section */}
        <section className="profile-hero">
          <div className="profile-hero-avatar-container">
            <div className="profile-hero-avatar-glow" />
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
            {profile.ideal_for && (
              <div className="profile-positioning-badge">
                {profile.ideal_for}
              </div>
            )}
            <h1 className="profile-full-name">{fullName}</h1>
            <p className="profile-style-title">{profile.style}</p>
            
            <div className="profile-metadata-row">
              {profile.age && (
                <div className="profile-meta-pill">
                  <Calendar size={16} />
                  <span>{profile.age} ans</span>
                </div>
              )}
              {profile.metrics.experience_years > 0 && (
                <div className="profile-meta-pill">
                  <Award size={16} />
                  <span>{profile.metrics.experience_years} {t("years_experience", lang)}</span>
                </div>
              )}
              {profile.location && (
                <div className="profile-meta-pill">
                  <MapPin size={16} />
                  <span>{profile.location}</span>
                </div>
              )}
            </div>

            {profile.quote && (
              <blockquote className="profile-quote">
                <Quote size={24} className="quote-icon" />
                <p>{profile.quote}</p>
              </blockquote>
            )}
          </div>
        </section>

        {/* Metrics Bar */}
        <section className="profile-metrics-bar">
          <div className="metric-card">
            <Clock size={24} className="metric-icon" />
            <span className="metric-value">{profile.metrics.experience_years}+</span>
            <span className="metric-label">{t("years_experience", lang)}</span>
          </div>
          <div className="metric-card">
            <Users size={24} className="metric-icon" />
            <span className="metric-value">{profile.metrics.consultations_count}+</span>
            <span className="metric-label">{t("consultations_count", lang)}</span>
          </div>
          <div className="metric-card">
            <Star size={24} className="metric-icon" />
            <span className="metric-value">{profile.review_summary.average_rating.toFixed(1)}/5</span>
            <span className="metric-label">{t("average_rating_label", lang)}</span>
          </div>
        </section>

        {/* Main Grid */}
        <div className="profile-main-grid">
          <div className="profile-col-left">
            {/* About */}
            <section className="profile-about">
              <h2 className="profile-section-title">{t("about", lang)}</h2>
              <p className="profile-bio-text">{profile.bio_full}</p>
            </section>

            {/* Mission */}
            {profile.mission_statement && (
              <section className="profile-mission-card">
                <h3>{t("mission_title", lang)}</h3>
                <p className="profile-mission-text">“ {profile.mission_statement} ”</p>
              </section>
            )}

            {/* Method */}
            <section className="profile-method">
              <h2 className="profile-section-title">{t("method_title", lang)}</h2>
              <div className="profile-method-stepper">
                <div className="method-step">
                  <div className="step-number">1</div>
                  <div className="step-content">
                    <p className="step-title">{t("method_step_1", lang)}</p>
                  </div>
                </div>
                <div className="method-step">
                  <div className="step-number">2</div>
                  <div className="step-content">
                    <p className="step-title">{t("method_step_2", lang)}</p>
                  </div>
                </div>
                <div className="method-step">
                  <div className="step-number">3</div>
                  <div className="step-content">
                    <p className="step-title">{t("method_step_3", lang)}</p>
                  </div>
                </div>
                <div className="method-step">
                  <div className="step-number">4</div>
                  <div className="step-content">
                    <p className="step-title">{t("method_step_4", lang)}</p>
                  </div>
                </div>
              </div>
            </section>
          </div>

          <aside className="profile-col-right">
            <div className="sticky-sidebar">
              <div className="specialties-card">
                <h2 className="profile-section-title" style={{ fontSize: '18px' }}>
                  {t("specialties_title", lang)}
                </h2>
                <div className="specialties-list">
                  {profile.specialties_details.length > 0 ? (
                    profile.specialties_details.map((s, i) => (
                      <div key={i} className="specialty-item">
                        <span className="specialty-item-title">
                          <CheckCircle2 size={14} style={{ color: 'var(--premium-accent-purple)', marginRight: '8px' }} />
                          {s.title}
                        </span>
                        <p className="specialty-item-desc">{s.description}</p>
                      </div>
                    ))
                  ) : (
                    profile.specialties.map((s, i) => (
                      <div key={i} className="specialty-item">
                        <span className="specialty-item-title">
                          <CheckCircle2 size={14} style={{ color: 'var(--premium-accent-purple)', marginRight: '8px' }} />
                          {s}
                        </span>
                      </div>
                    ))
                  )}
                </div>
              </div>
            </div>
          </aside>
        </div>

        {/* Reviews Section */}
        <section className="profile-reviews-section">
          <h2 className="profile-section-title">{t("reviews_title", lang)}</h2>
          <div className="reviews-container">
            <div className="reviews-list">
              {profile.reviews.length > 0 ? (
                profile.reviews.map((r) => (
                  <div key={r.id} className="review-item">
                    <div className="review-header">
                      <div className="review-user-info">
                        <span className="review-user-name">{r.user_name}</span>
                        <span className="review-date">
                          {new Date(r.created_at).toLocaleDateString(lang, { day: 'numeric', month: 'long', year: 'numeric' })}
                        </span>
                      </div>
                      <div className="review-rating">
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} size={14} fill={i < r.rating ? "currentColor" : "none"} />
                        ))}
                      </div>
                    </div>
                    {r.comment && <p className="review-comment">{r.comment}</p>}
                  </div>
                ))
              ) : (
                <div className="review-item" style={{ textAlign: 'center', opacity: 0.7 }}>
                  Aucun avis pour le moment.
                </div>
              )}
            </div>
            <div className="review-stats-card">
              <div className="big-rating">{profile.review_summary.average_rating.toFixed(1)}</div>
              <p className="metric-label">{profile.review_summary.review_count} {t("reviews_count", lang)}</p>
              
              <div style={{ marginTop: '24px', paddingTop: '24px', borderTop: '1px solid var(--premium-glass-border)' }}>
                <p className="step-title" style={{ marginBottom: '12px' }}>{t("your_rating_title", lang)}</p>
                <div className="review-rating" style={{ justifyContent: 'center', gap: '8px', cursor: 'pointer' }}>
                  {[1, 2, 3, 4, 5].map((star) => (
                    <Star 
                      key={star} 
                      size={24} 
                      onClick={() => handleRate(star)}
                      fill={(profile.user_rating || 0) >= star ? "currentColor" : "none"}
                      style={{ transition: 'transform 0.1s ease' }}
                      onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.2)'}
                      onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
                    />
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Final CTA Section */}
        <section className="profile-final-cta">
          <h2 className="profile-full-name" style={{ fontSize: '32px' }}>Prêt à explorer votre ciel avec {profile.first_name} ?</h2>
          <div className="cta-group">
            <Button 
              size="lg" 
              variant="primary"
              className="premium-cta"
              onClick={() => navigate(`/chat?astrologerId=${encodeURIComponent(profile.id)}`)}
              leftIcon={<MessageSquare size={20} />}
            >
              {profile.action_state.has_chat ? t("cta_chat_resume", lang) : t("cta_chat_new", lang)}
            </Button>
            
            <Button
              size="lg"
              variant="secondary"
              onClick={() => navigate(`/natal?astrologerId=${encodeURIComponent(profile.id)}`)}
              leftIcon={<Sparkles size={20} />}
            >
              {profile.action_state.has_natal_interpretation ? t("cta_natal_view", lang) : t("cta_natal_new", lang)}
            </Button>

            <Button
              size="lg"
              variant="outline"
              onClick={() => navigate(`/consultations?astrologerId=${encodeURIComponent(profile.id)}`)}
              leftIcon={<Zap size={20} />}
            >
              {t("cta_consultation", lang)}
            </Button>
          </div>
        </section>
      </div>
    </PageLayout>
  )
}
