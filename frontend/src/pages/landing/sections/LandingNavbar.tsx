import { useEffect, useMemo, useState } from "react"
import { Link } from "react-router-dom"
import { ChevronDown, Globe, Menu, X } from "lucide-react"
import { Button } from "../../../components/ui/Button/Button"
import { SUPPORTED_LANGS, useAstrologyLabels, useTranslation } from "../../../i18n"
import logo from "../../../assets/logo.PNG"
import "./LandingNavbar.css"

export const LandingNavbar = () => {
  const t = useTranslation("landing")
  const { lang, setLang } = useAstrologyLabels()
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isLangMenuOpen, setIsLangMenuOpen] = useState(false)

  const langLabels: Record<string, string> = useMemo(
    () => ({
      fr: "Français",
      en: "English",
      es: "Español",
    }),
    [],
  )

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 24)
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return
      setIsMobileMenuOpen(false)
      setIsLangMenuOpen(false)
    }

    window.addEventListener("keydown", handleEscape)
    return () => window.removeEventListener("keydown", handleEscape)
  }, [])

  const closeAllMenus = () => {
    setIsMobileMenuOpen(false)
    setIsLangMenuOpen(false)
  }

  return (
    <>
      <nav
        className={`landing-navbar ${isScrolled ? "landing-navbar--scrolled" : ""}`}
        aria-label={t.navbarA11y.navLabel}
      >
        <div className="landing-navbar__shell">
          <Link
            to="/"
            className="landing-navbar__logo"
            onClick={closeAllMenus}
            aria-label={t.navbarA11y.logoLabel}
          >
            <img src={logo} alt="" width="34" height="34" />
            <span className="landing-navbar__logo-text">Astrorizon</span>
          </Link>

          <div className="landing-navbar__links">
            <a href="#social-proof" className="landing-navbar__link">
              {t.navbar.trust}
            </a>
            <a href="#how-it-works" className="landing-navbar__link">
              {t.navbar.howItWorks}
            </a>
            <a href="#pricing" className="landing-navbar__link">
              {t.navbar.pricing}
            </a>
            <a href="#faq" className="landing-navbar__link">
              {t.navbar.faq}
            </a>
          </div>

          <div className="landing-navbar__actions">
            <div className="landing-navbar__lang-wrapper">
              <button
                className="landing-navbar__lang"
                onClick={() => setIsLangMenuOpen((value) => !value)}
                aria-label={t.navbar.language}
                aria-haspopup="true"
                aria-expanded={isLangMenuOpen}
                aria-controls="landing-lang-dropdown"
              >
                <Globe size={15} aria-hidden="true" />
                <span>{lang.toUpperCase()}</span>
                <ChevronDown size={14} aria-hidden="true" />
              </button>

              {isLangMenuOpen && (
                <div
                  id="landing-lang-dropdown"
                  className="landing-navbar__lang-dropdown"
                  role="menu"
                >
                  {SUPPORTED_LANGS.map((languageCode) => (
                    <button
                      key={languageCode}
                      role="menuitem"
                      className={`landing-navbar__lang-option ${
                        lang === languageCode ? "landing-navbar__lang-option--active" : ""
                      }`}
                      onClick={() => {
                        setLang(languageCode)
                        setIsLangMenuOpen(false)
                      }}
                    >
                      {langLabels[languageCode] ?? languageCode.toUpperCase()}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <Link to="/login" className="landing-navbar__login">
              {t.navbar.login}
            </Link>

            <Button
              as={Link}
              to="/register"
              variant="primary"
              size="sm"
              className="landing-navbar__cta"
            >
              {t.navbar.register}
            </Button>

            <button
              className="landing-navbar__mobile-toggle"
              onClick={() => setIsMobileMenuOpen((value) => !value)}
              aria-label={isMobileMenuOpen ? t.navbarA11y.closeMenu : t.navbarA11y.openMenu}
              aria-expanded={isMobileMenuOpen}
              aria-controls="landing-mobile-menu"
            >
              {isMobileMenuOpen ? <X size={22} aria-hidden="true" /> : <Menu size={22} aria-hidden="true" />}
            </button>
          </div>
        </div>
      </nav>

      {isMobileMenuOpen && (
        <div
          id="landing-mobile-menu"
          className="landing-navbar__mobile-menu"
          role="dialog"
          aria-modal="true"
          aria-label={t.navbarA11y.mobileMenu}
        >
          <div className="landing-navbar__mobile-panel">
            <div className="landing-navbar__mobile-header">
              <Link to="/" className="landing-navbar__logo" onClick={closeAllMenus}>
                <img src={logo} alt="" width="34" height="34" />
                <span className="landing-navbar__logo-text">Astrorizon</span>
              </Link>
              <button
                className="landing-navbar__mobile-close"
                onClick={closeAllMenus}
                aria-label={t.navbarA11y.closeMenu}
              >
                <X size={20} aria-hidden="true" />
              </button>
            </div>

            <div className="landing-navbar__mobile-links">
              <a href="#social-proof" className="landing-navbar__mobile-link" onClick={closeAllMenus}>
                {t.navbar.trust}
              </a>
              <a href="#how-it-works" className="landing-navbar__mobile-link" onClick={closeAllMenus}>
                {t.navbar.howItWorks}
              </a>
              <a href="#pricing" className="landing-navbar__mobile-link" onClick={closeAllMenus}>
                {t.navbar.pricing}
              </a>
              <a href="#faq" className="landing-navbar__mobile-link" onClick={closeAllMenus}>
                {t.navbar.faq}
              </a>
            </div>

            <div className="landing-navbar__mobile-lang">
              {SUPPORTED_LANGS.map((languageCode) => (
                <button
                  key={languageCode}
                  className={`landing-navbar__mobile-lang-option ${
                    lang === languageCode ? "landing-navbar__mobile-lang-option--active" : ""
                  }`}
                  onClick={() => {
                    setLang(languageCode)
                    setIsMobileMenuOpen(false)
                  }}
                >
                  {langLabels[languageCode] ?? languageCode.toUpperCase()}
                </button>
              ))}
            </div>

            <div className="landing-navbar__mobile-actions">
              <Button as={Link} to="/register" variant="primary" size="lg" fullWidth onClick={closeAllMenus}>
                {t.navbar.register}
              </Button>
              <Button as={Link} to="/login" variant="secondary" size="lg" fullWidth onClick={closeAllMenus}>
                {t.navbar.login}
              </Button>
            </div>
          </div>
        </div>
      )}
    </>
  )
}
