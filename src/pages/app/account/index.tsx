import { useState } from 'react';
import { useTitle } from '@/shared/hooks/useTitle';
import { useExportZip } from '@/features/account/hooks/useExportZip';
import { useDeleteAccount } from '@/features/account/hooks/useDeleteAccount';
import { ConfirmModal } from '@/shared/ui/ConfirmModal';

/**
 * Page Account (privée)
 * Permet l'export des données (RGPD) et la suppression du compte
 */
export function AccountPage(): JSX.Element {
  useTitle('Horoscope - Mon compte');
  const { exportZip, isPending: isExportPending } = useExportZip();
  const { deleteAccount, isPending: isDeletePending } = useDeleteAccount();
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

  const handleExportClick = (): void => {
    void exportZip();
  };

  const handleDeleteClick = (): void => {
    setIsDeleteModalOpen(true);
  };

  const handleDeleteConfirm = (): void => {
    setIsDeleteModalOpen(false);
    void deleteAccount();
  };

  const handleDeleteCancel = (): void => {
    setIsDeleteModalOpen(false);
  };

  return (
    <div>
      <h1>Mon compte</h1>
      <p>Gérez vos données personnelles et votre compte</p>

      {/* Section Export */}
      <div
        style={{
          marginTop: '2rem',
          padding: '1.5rem',
          backgroundColor: '#f9f9f9',
          borderRadius: '8px',
          border: '1px solid #e0e0e0',
        }}
      >
        <h2 style={{ marginTop: 0, marginBottom: '1rem' }}>
          Exporter mes données
        </h2>
        <p style={{ marginBottom: '1rem', color: '#666' }}>
          Téléchargez une copie de toutes vos données au format ZIP. Ce fichier
          contient :
        </p>
        <ul style={{ marginBottom: '1.5rem', paddingLeft: '1.5rem', color: '#666' }}>
          <li>Vos informations de compte</li>
          <li>Vos thèmes natals</li>
          <li>Votre historique de chat</li>
          <li>Vos préférences</li>
        </ul>
        <button
          type="button"
          onClick={handleExportClick}
          disabled={isExportPending}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: isExportPending ? '#ccc' : '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isExportPending ? 'not-allowed' : 'pointer',
            fontSize: '1rem',
            fontWeight: 500,
          }}
        >
          {isExportPending ? 'Téléchargement...' : 'Télécharger mes données'}
        </button>
      </div>

      {/* Section Delete */}
      <div
        style={{
          marginTop: '2rem',
          padding: '1.5rem',
          backgroundColor: '#fff3cd',
          borderRadius: '8px',
          border: '1px solid #ffc107',
        }}
      >
        <h2 style={{ marginTop: 0, marginBottom: '1rem', color: '#856404' }}>
          Supprimer mon compte
        </h2>
        <p style={{ marginBottom: '1rem', color: '#856404' }}>
          <strong>Attention :</strong> La suppression de votre compte est
          irréversible. Toutes vos données seront définitivement supprimées, y
          compris :
        </p>
        <ul style={{ marginBottom: '1.5rem', paddingLeft: '1.5rem', color: '#856404' }}>
          <li>Vos informations de compte</li>
          <li>Vos thèmes natals</li>
          <li>Votre historique de chat</li>
          <li>Vos préférences et paramètres</li>
          <li>Votre abonnement (si actif)</li>
        </ul>
        <p style={{ marginBottom: '1.5rem', color: '#856404' }}>
          Conformément au RGPD, cette action est définitive et ne peut pas être
          annulée.
        </p>
        <button
          type="button"
          onClick={handleDeleteClick}
          disabled={isDeletePending}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: isDeletePending ? '#ccc' : '#dc3545',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: isDeletePending ? 'not-allowed' : 'pointer',
            fontSize: '1rem',
            fontWeight: 500,
          }}
        >
          Supprimer mon compte
        </button>
      </div>

      {/* Modal de confirmation de suppression */}
      <ConfirmModal
        isOpen={isDeleteModalOpen}
        onClose={handleDeleteCancel}
        onConfirm={handleDeleteConfirm}
        title="Confirmer la suppression"
        message="Êtes-vous absolument sûr de vouloir supprimer votre compte ? Cette action est irréversible et toutes vos données seront définitivement perdues."
        confirmText="SUPPRIMER"
        confirmButtonLabel="Confirmer la suppression"
        confirmButtonStyle={{
          backgroundColor: '#dc3545',
        }}
      />
    </div>
  );
}
