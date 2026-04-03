import { useTranslation } from "../i18n"
import { Button } from "../components/ui/Button/Button"
import { Link } from "react-router-dom"
import { ArrowLeft } from "lucide-react"

export const PrivacyPolicyPage = () => {
  const t = useTranslation("landing")
  
  return (
    <div className="privacy-policy-page" style={{ 
      padding: "120px 24px", 
      maxWidth: "800px", 
      margin: "0 auto",
      color: "var(--premium-text-main)"
    }}>
      <Button as={Link} to="/" variant="secondary" size="sm" style={{ marginBottom: "40px" }}>
        <ArrowLeft size={16} style={{ marginRight: "8px" }} />
        {t.navbar.howItWorks} {/* Reusing an existing label for back button if needed, but here just home */}
        Retour à l'accueil
      </Button>

      <h1 style={{ 
        fontFamily: "var(--premium-font-serif, serif)", 
        fontSize: "2.5rem",
        marginBottom: "24px",
        color: "var(--premium-text-strong)"
      }}>
        Politique de Confidentialité
      </h1>
      
      <p style={{ marginBottom: "24px", lineHeight: "1.6", color: "var(--premium-text-meta)" }}>
        Dernière mise à jour : {new Date().toLocaleDateString()}
      </p>

      <section style={{ marginBottom: "40px" }}>
        <h2 style={{ fontSize: "1.5rem", marginBottom: "16px", color: "var(--premium-text-strong)" }}>
          1. Collecte des données
        </h2>
        <p style={{ lineHeight: "1.6", marginBottom: "16px" }}>
          Astrorizon s'engage à protéger votre vie privée. Nous collectons uniquement les données nécessaires à la fourniture de nos services astrologiques personnalisés, notamment vos données de naissance (date, heure et lieu).
        </p>
      </section>

      <section style={{ marginBottom: "40px" }}>
        <h2 style={{ fontSize: "1.5rem", marginBottom: "16px", color: "var(--premium-text-strong)" }}>
          2. Utilisation des données
        </h2>
        <p style={{ lineHeight: "1.6", marginBottom: "16px" }}>
          Vos données de naissance sont utilisées exclusivement pour calculer vos positions planétaires et générer vos prévisions. Vos conversations avec notre IA sont confidentielles et chiffrées.
        </p>
      </section>

      <section style={{ marginBottom: "40px" }}>
        <h2 style={{ fontSize: "1.5rem", marginBottom: "16px", color: "var(--premium-text-strong)" }}>
          3. Protection des données (RGPD)
        </h2>
        <p style={{ lineHeight: "1.6", marginBottom: "16px" }}>
          Conformément au RGPD, vous disposez d'un droit d'accès, de rectification et de suppression de vos données. Vous pouvez exercer ces droits à tout moment depuis vos paramètres utilisateur.
        </p>
      </section>

      <section style={{ marginBottom: "40px" }}>
        <h2 style={{ fontSize: "1.5rem", marginBottom: "16px", color: "var(--premium-text-strong)" }}>
          4. Contact
        </h2>
        <p style={{ lineHeight: "1.6", marginBottom: "16px" }}>
          Pour toute question concernant notre politique de confidentialité, vous pouvez nous contacter à : hello@astrorizon.ai
        </p>
      </section>
    </div>
  )
}
