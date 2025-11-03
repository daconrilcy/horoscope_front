import React from 'react';
import { usePaywall } from './hooks/usePaywall';
import { UpgradeBanner } from '@/widgets/UpgradeBanner/UpgradeBanner';
import { QuotaMessage } from '@/widgets/QuotaMessage/QuotaMessage';

/**
 * Props pour le composant PaywallGate
 */
export interface PaywallGateProps {
  /** Clé de la feature à vérifier */
  feature: string;
  /** Contenu à afficher si autorisé */
  children: React.ReactNode;
  /** Contenu à afficher pendant le chargement (optionnel) */
  fallback?: React.ReactNode;
  /** Callback appelé lors du clic sur le bouton upgrade */
  onUpgrade?: () => void;
}

/**
 * Composant passe-plat pour gérer l'affichage conditionnel selon le paywall
 * Ne déclenche pas lui-même de navigation/checkout
 * Délègue la navigation via callback onUpgrade
 */
export function PaywallGate({
  feature,
  children,
  fallback,
  onUpgrade,
}: PaywallGateProps): React.ReactElement | null {
  const { isLoading, isAllowed, reason, upgradeUrl, retryAfter } =
    usePaywall(feature);

  // Pendant le chargement, afficher le fallback ou rien
  if (isLoading) {
    return (fallback as React.ReactElement) ?? null;
  }

  // Si autorisé, afficher les children
  if (isAllowed) {
    return children as React.ReactElement;
  }

  // Si bloqué, afficher le message approprié
  if (reason === 'plan') {
    // 402 : Plan insuffisant → UpgradeBanner
    return (
      <UpgradeBanner
        reason="plan"
        upgradeUrl={upgradeUrl}
        onUpgrade={onUpgrade}
      />
    );
  }

  if (reason === 'rate') {
    // 429 : Quota dépassé → QuotaMessage
    return (
      <QuotaMessage
        retryAfter={retryAfter}
        upgradeUrl={upgradeUrl}
        onUpgrade={onUpgrade}
      />
    );
  }

  // Fallback si reason inconnu
  return (
    <div
      role="alert"
      style={{
        padding: '1rem',
        backgroundColor: '#fee2e2',
        borderRadius: '0.5rem',
      }}
    >
      <p style={{ margin: 0 }}>Cette fonctionnalité nécessite un upgrade.</p>
    </div>
  );
}
