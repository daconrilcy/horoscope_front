import { Link } from "react-router-dom"
import { Twitter, Instagram, Mail } from "lucide-react"
import { useTranslation } from "../../../i18n"
import "./LandingFooter.css"

export const LandingFooter = () => {
  const t = useTranslation("landing")
  const currentYear = new Date().getFullYear()

  const productLinks = [
    { key: "howItWorks", href: "#how-it-works", ...t.footer.product.howItWorks },
    { key: "pricing", href: "#pricing", ...t.footer.product.pricing },
    { key: "login", to: "/login", ...t.footer.product.login },
  ]

  const legalLinks = [
    { key: "privacy", to: t.footer.legal.privacy.path, ...t.footer.legal.privacy },
    { key: "legal", to: t.footer.legal.legal.path, ...t.footer.legal.legal },
    { key: "terms", to: t.footer.legal.terms.path, ...t.footer.legal.terms },
    { key: "cookies", to: t.footer.legal.cookies.path, ...t.footer.legal.cookies },
  ]

  const socialLinks = [
    { key: "twitter", icon: <Twitter size={20} />, ...t.footer.social.twitter },
    { key: "instagram", icon: <Instagram size={20} />, ...t.footer.social.instagram },
  ]

  const contactEmail = t.footer.contact.email

  return (
    <footer className="landing-footer">
      <div className="landing-footer__container">
        {/* Brand Column */}
        <div className="landing-footer__brand">
          <Link to="/" className="landing-footer__logo">
            <img src="/src/assets/logo.PNG" alt="Astrorizon Logo" />
            <span className="landing-footer__logo-text">Astrorizon</span>
          </Link>
          <p className="landing-footer__desc">{t.footer.desc}</p>
        </div>

        {/* Product Column */}
        <div className="landing-footer__column">
          <span className="landing-footer__column-title">{t.footer.product.title}</span>
          <ul className="landing-footer__links">
            {productLinks.filter(l => l.enabled).map((link) => (
              <li key={link.key}>
                {link.to ? (
                  <Link to={link.to} className="landing-footer__link">
                    {link.label}
                  </Link>
                ) : (
                  <a href={link.href} className="landing-footer__link">
                    {link.label}
                  </a>
                )}
              </li>
            ))}
          </ul>
        </div>

        {/* Legal Column */}
        <div className="landing-footer__column">
          <span className="landing-footer__column-title">{t.footer.legal.title}</span>
          <ul className="landing-footer__links">
            {legalLinks.filter(l => l.enabled).map((link) => (
              <li key={link.key}>
                <Link to={link.to || "#"} className="landing-footer__link">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        {/* Contact Column */}
        <div className="landing-footer__column">
          <span className="landing-footer__column-title">{t.footer.contact.title}</span>
          <ul className="landing-footer__links">
            {contactEmail.enabled && (
              <li>
                <a href={`mailto:${contactEmail.value}`} className="landing-footer__link" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <Mail size={16} />
                  {contactEmail.label}
                </a>
              </li>
            )}
          </ul>
        </div>
      </div>

      <div className="landing-footer__bottom">
        <div className="landing-footer__copyright">
          © {currentYear} {t.footer.copyright}
        </div>

        {socialLinks.some(s => s.enabled) && (
          <div className="landing-footer__social">
            {socialLinks.filter(s => s.enabled).map((social) => (
              <a 
                key={social.key} 
                href={social.url} 
                className="landing-footer__social-link"
                target="_blank"
                rel="noopener noreferrer"
                aria-label={social.key}
              >
                {social.icon}
              </a>
            ))}
          </div>
        )}
      </div>
    </footer>
  )
}
