import { Mail, ShieldCheck } from "lucide-react"
import { Link } from "react-router-dom"
import { useTranslation } from "../../../i18n"
import logo from "../../../assets/logo.PNG"
import "./LandingFooter.css"

type FooterLink = {
  key: string
  label: string
  enabled: boolean
  to?: string
  href?: string
}

export const LandingFooter = () => {
  const t = useTranslation("landing")
  const currentYear = new Date().getFullYear()

  const productLinks: FooterLink[] = [
    { key: "howItWorks", href: "#how-it-works", ...t.footer.product.howItWorks },
    { key: "pricing", href: "#pricing", ...t.footer.product.pricing },
    { key: "login", to: "/login", ...t.footer.product.login },
  ]

  const legalLinks: FooterLink[] = [
    { key: "privacy", to: t.footer.legal.privacy.path, ...t.footer.legal.privacy },
    { key: "legal", to: t.footer.legal.legal.path, ...t.footer.legal.legal },
    { key: "terms", to: t.footer.legal.terms.path, ...t.footer.legal.terms },
    { key: "cookies", to: t.footer.legal.cookies.path, ...t.footer.legal.cookies },
  ]

  const contactEmail = t.footer.contact.email

  return (
    <footer className="landing-footer">
      <div className="landing-footer__container">
        <div className="landing-footer__brand">
          <Link to="/" className="landing-footer__logo">
            <img src={logo} alt="" width="34" height="34" loading="lazy" />
            <span className="landing-footer__logo-text">Astrorizon</span>
          </Link>
          <p className="landing-footer__desc">{t.footer.desc}</p>
        </div>

        <div className="landing-footer__column">
          <h3 className="landing-footer__column-title">{t.footer.product.title}</h3>
          <ul className="landing-footer__links">
            {productLinks
              .filter((link) => link.enabled)
              .map((link) => (
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

        <div className="landing-footer__column landing-footer__column--trust">
          <h3 className="landing-footer__column-title">{t.footer.contact.title}</h3>
          <ul className="landing-footer__links">
            {contactEmail.enabled && (
              <li>
                <a
                  href={`mailto:${contactEmail.value}`}
                  className="landing-footer__link landing-footer__link--email"
                >
                  <Mail size={16} aria-hidden="true" />
                  {contactEmail.value}
                </a>
              </li>
            )}
            <li className="landing-footer__trust-item">
              <ShieldCheck size={16} aria-hidden="true" />
              {t.footer.legal.privacy.label}
            </li>
          </ul>
        </div>

        <div className="landing-footer__column">
          <h3 className="landing-footer__column-title">{t.footer.legal.title}</h3>
          <ul className="landing-footer__links">
            {legalLinks
              .filter((link) => link.enabled)
              .map((link) => (
                <li key={link.key}>
                  <Link to={link.to ?? "#"} className="landing-footer__link">
                    {link.label}
                  </Link>
                </li>
              ))}
          </ul>
        </div>
      </div>

      <div className="landing-footer__bottom">
        <span className="landing-footer__copyright">© {currentYear} {t.footer.copyright}</span>
      </div>
    </footer>
  )
}
