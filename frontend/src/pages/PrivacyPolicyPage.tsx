// Page legale publique dont la presentation est centralisee dans la feuille CSS adjacente.
import { Button } from "../components/ui/Button/Button"
import { Link } from "react-router-dom"
import { ArrowLeft } from "lucide-react"
import { formatLocalDate } from "../utils/formatDate"
import "./PrivacyPolicyPage.css"

export const PrivacyPolicyPage = () => {
  return (
    <div className="privacy-policy-page">
      <Button
        as={Link}
        to="/"
        variant="secondary"
        size="sm"
        className="privacy-policy-page__back-link"
        leftIcon={<ArrowLeft size={16} aria-hidden="true" />}
      >
        Retour à l'accueil
      </Button>

      <h1 className="privacy-policy-page__title">
        Politique de Confidentialité
      </h1>
      
      <p className="privacy-policy-page__updated-at">
        Dernière mise à jour : {formatLocalDate(new Date().toISOString())}
      </p>

      <section className="privacy-policy-page__section">
        <h2 className="privacy-policy-page__section-title">
          1. Collecte des données
        </h2>
        <p className="privacy-policy-page__paragraph">
          Astrorizon s'engage à protéger votre vie privée. Nous collectons uniquement les données nécessaires à la fourniture de nos services astrologiques personnalisés, notamment vos données de naissance (date, heure et lieu).
        </p>
      </section>

      <section className="privacy-policy-page__section">
        <h2 className="privacy-policy-page__section-title">
          2. Utilisation des données
        </h2>
        <p className="privacy-policy-page__paragraph">
          Vos données de naissance sont utilisées exclusivement pour calculer vos positions planétaires et générer vos prévisions. Vos conversations avec notre IA sont confidentielles et chiffrées.
        </p>
      </section>

      <section className="privacy-policy-page__section">
        <h2 className="privacy-policy-page__section-title">
          3. Protection des données (RGPD)
        </h2>
        <p className="privacy-policy-page__paragraph">
          Conformément au RGPD, vous disposez d'un droit d'accès, de rectification et de suppression de vos données. Vous pouvez exercer ces droits à tout moment depuis vos paramètres utilisateur.
        </p>
      </section>

      <section className="privacy-policy-page__section">
        <h2 className="privacy-policy-page__section-title">
          4. Contact
        </h2>
        <p className="privacy-policy-page__paragraph">
          Pour toute question concernant notre politique de confidentialité, vous pouvez nous contacter à : hello@astrorizon.ai
        </p>
      </section>
    </div>
  )
}
