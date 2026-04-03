import { useState, useEffect, useMemo } from "react"
import { Link } from "react-router-dom"
import { Menu, X, Globe, ChevronDown } from "lucide-react"
import { Button } from "../../../components/ui/Button/Button"
import { useTranslation, useAstrologyLabels, SUPPORTED_LANGS } from "../../../i18n"
import logo from "../../../assets/logo.PNG"
import "./LandingNavbar.css"

export const LandingNavbar = () => {
  const t = useTranslation("landing")
  const { lang, setLang } = useAstrologyLabels()
  const [isScrolled, setIsScrolled] = useState(false)
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false)
  const [isLangMenuOpen, setIsLangMenuOpen] = useState(false)

  const langLabels: Record<string, string> = useMemo(() => ({
    fr: "Français",
    en: "English",
    es: "Español"
  }), [])

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 50)
    }
    window.addEventListener("scroll", handleScroll)
    return () => window.removeEventListener("scroll", handleScroll)
  }, [])

  const toggleMobileMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen)
  const closeMobileMenu = () => setIsMobileMenuOpen(false)

  return (
    <>
      <nav className={`landing-navbar ${isScrolled ? "landing-navbar--glass" : ""}`}>
        <div className="landing-navbar__container">
          {/* Logo */}
          <Link to="/" className="landing-navbar__logo" onClick={closeMobileMenu}>
            <img src={logo} alt="Astrorizon Logo" width="32" height="32" />
            <span className="landing-navbar__logo-text">Astrorizon</span>
          </Link>

          {/* Desktop Links */}
          <div className="landing-navbar__links">
            <a href="#how-it-works" className="landing-navbar__link">
              {t.navbar.howItWorks}
            </a>
            <a href="#pricing" className="landing-navbar__link">
              {t.navbar.pricing}
            </a>
          </div>

          {/* Actions */}
          <div className="landing-navbar__actions">
            {/* Language Selector */}
            <div className="landing-navbar__lang-wrapper">
              <button 
                className="landing-navbar__lang"
                onClick={() => setIsLangMenuOpen(!isLangMenuOpen)}
                aria-label={t.navbar.language}
              >
                <Globe size={16} />
                <span>{lang}</span>
                <ChevronDown size={14} />
              </button>
              
              {isLangMenuOpen && (
                <div className="landing-navbar__lang-dropdown premium-glass-card">
                  {SUPPORTED_LANGS.map((l) => (
                    <button
                      key={l}
                      onClick={() => {
                        setLang(l)
                        setIsLangMenuOpen(false)
                      }}
                      className={`landing-navbar__lang-option ${lang === l ? "landing-navbar__lang-option--active" : ""}`}
                    >
                      {langLabels[l] || l.toUpperCase()}
                    </button>
                  ))}
                </div>
              )}
            </div>

            <Link to="/login" className="landing-navbar__login">
              {t.navbar.login}
            </Link>

            <Button as={Link} to="/register" variant="primary" size="sm">
              {t.navbar.register}
            </Button>

            {/* Mobile Toggle */}
            <button className="landing-navbar__mobile-toggle" onClick={toggleMobileMenu}>
              {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu Overlay */}
      {isMobileMenuOpen && (
        <div className="landing-navbar__mobile-menu">
          <div className="landing-navbar__mobile-header">
            <Link to="/" className="landing-navbar__logo" onClick={closeMobileMenu}>
              <img src={logo} alt="Astrorizon Logo" />
              <span className="landing-navbar__logo-text">Astrorizon</span>
            </Link>
            <button className="landing-navbar__mobile-toggle" onClick={closeMobileMenu}>
              <X size={24} />
            </button>
          </div>

          <div className="landing-navbar__mobile-links">
            <a href="#how-it-works" className="landing-navbar__mobile-link" onClick={closeMobileMenu}>
              {t.navbar.howItWorks}
            </a>
            <a href="#pricing" className="landing-navbar__mobile-link" onClick={closeMobileMenu}>
              {t.navbar.pricing}
            </a>
          </div>

          <div className="landing-navbar__mobile-actions">
            <Button as={Link} to="/register" variant="primary" size="lg" fullWidth onClick={closeMobileMenu}>
              {t.navbar.register}
            </Button>
            <Button as={Link} to="/login" variant="secondary" size="lg" fullWidth onClick={closeMobileMenu}>
              {t.navbar.login}
            </Button>
          </div>
        </div>
      )}
    </>
  )
}

