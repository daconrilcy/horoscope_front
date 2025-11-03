import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ConfirmModal } from './ConfirmModal';
import React from 'react';

describe('ConfirmModal', () => {
  const defaultProps = {
    isOpen: true,
    onClose: vi.fn(),
    onConfirm: vi.fn(),
    title: 'Confirmer la suppression',
    message: 'Cette action est irréversible.',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("ne devrait pas s'afficher si isOpen est false", () => {
    render(<ConfirmModal {...defaultProps} isOpen={false} />);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });

  it("devrait s'afficher avec le titre et le message", () => {
    render(<ConfirmModal {...defaultProps} />);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByText('Confirmer la suppression')).toBeInTheDocument();
    expect(
      screen.getByText('Cette action est irréversible.')
    ).toBeInTheDocument();
  });

  it('devrait avoir les attributs aria corrects', () => {
    render(<ConfirmModal {...defaultProps} />);
    const dialog = screen.getByRole('dialog');
    expect(dialog).toHaveAttribute('aria-modal', 'true');
    expect(dialog).toHaveAttribute('aria-labelledby', 'confirm-modal-title');
    expect(dialog).toHaveAttribute('aria-describedby', 'confirm-modal-message');
  });

  it('devrait fermer au clic sur overlay', async () => {
    const onClose = vi.fn();
    render(<ConfirmModal {...defaultProps} onClose={onClose} />);

    const overlay = screen.getByRole('presentation');
    await userEvent.click(overlay);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('devrait fermer avec Escape', async () => {
    const onClose = vi.fn();
    render(<ConfirmModal {...defaultProps} onClose={onClose} />);

    await userEvent.keyboard('{Escape}');

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('devrait désactiver le bouton de confirmation si le texte ne correspond pas', async () => {
    render(<ConfirmModal {...defaultProps} confirmText="SUPPRIMER" />);

    const input = screen.getByPlaceholderText('SUPPRIMER');
    const confirmButton = screen.getByRole('button', { name: 'Confirmer' });

    expect(confirmButton).toBeDisabled();

    // Taper un texte incorrect
    await userEvent.type(input, 'supprimer'); // minuscule

    await waitFor(() => {
      expect(confirmButton).toBeDisabled();
    });
  });

  it('devrait activer le bouton de confirmation si le texte correspond exactement', async () => {
    render(<ConfirmModal {...defaultProps} confirmText="SUPPRIMER" />);

    const input = screen.getByPlaceholderText('SUPPRIMER');
    const confirmButton = screen.getByRole('button', { name: 'Confirmer' });

    await userEvent.type(input, 'SUPPRIMER');

    await waitFor(() => {
      expect(confirmButton).not.toBeDisabled();
      expect(confirmButton).toHaveStyle({ backgroundColor: '#dc3545' });
    });
  });

  it('devrait être case-sensitive', async () => {
    render(<ConfirmModal {...defaultProps} confirmText="SUPPRIMER" />);

    const input = screen.getByPlaceholderText('SUPPRIMER');
    const confirmButton = screen.getByRole('button', { name: 'Confirmer' });

    await userEvent.type(input, 'supprimer'); // minuscule

    await waitFor(() => {
      expect(confirmButton).toBeDisabled();
    });
  });

  it('devrait prendre en compte trim() pour la validation', async () => {
    render(<ConfirmModal {...defaultProps} confirmText="SUPPRIMER" />);

    const input = screen.getByPlaceholderText('SUPPRIMER');
    const confirmButton = screen.getByRole('button', { name: 'Confirmer' });

    // Vérifier que le bouton est désactivé initialement
    expect(confirmButton).toBeDisabled();

    // Taper avec espaces directement dans l'input vide
    await userEvent.type(input, '  SUPPRIMER  '); // avec espaces

    // Le bouton devrait rester désactivé car trim('  SUPPRIMER  ') !== 'SUPPRIMER'
    await waitFor(
      () => {
        expect(confirmButton).toBeDisabled();
      },
      { timeout: 2000 }
    );
  });

  it('devrait appeler onConfirm quand le formulaire est soumis avec texte valide', async () => {
    const onConfirm = vi.fn();
    render(
      <ConfirmModal
        {...defaultProps}
        onConfirm={onConfirm}
        confirmText="SUPPRIMER"
      />
    );

    const input = screen.getByPlaceholderText('SUPPRIMER');
    const confirmButton = screen.getByRole('button', { name: 'Confirmer' });

    await userEvent.type(input, 'SUPPRIMER');
    await userEvent.click(confirmButton);

    expect(onConfirm).toHaveBeenCalledTimes(1);
  });

  it('devrait appeler onClose quand le bouton Annuler est cliqué', async () => {
    const onClose = vi.fn();
    render(<ConfirmModal {...defaultProps} onClose={onClose} />);

    const cancelButton = screen.getByRole('button', { name: 'Annuler' });
    await userEvent.click(cancelButton);

    expect(onClose).toHaveBeenCalledTimes(1);
  });

  it('devrait utiliser confirmText personnalisé', () => {
    render(<ConfirmModal {...defaultProps} confirmText="DELETE" />);

    // Vérifier que DELETE est dans le label
    expect(screen.getByText('DELETE')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('DELETE')).toBeInTheDocument();

    // Vérifier que le texte de confirmation est présent
    const label = screen.getByText(/Tapez/);
    expect(label).toBeInTheDocument();
    expect(label.textContent).toContain('DELETE');
  });

  it('devrait utiliser confirmButtonLabel personnalisé', () => {
    render(
      <ConfirmModal
        {...defaultProps}
        confirmButtonLabel="Supprimer définitivement"
      />
    );

    expect(
      screen.getByRole('button', { name: 'Supprimer définitivement' })
    ).toBeInTheDocument();
  });

  it("devrait avoir le focus sur l'input au montage", async () => {
    render(<ConfirmModal {...defaultProps} />);

    const input = screen.getByPlaceholderText('SUPPRIMER');

    await waitFor(() => {
      expect(input).toHaveFocus();
    });
  });

  it('devrait gérer le focus trap (Tab reste dans le modal)', async () => {
    render(<ConfirmModal {...defaultProps} />);

    const input = screen.getByPlaceholderText('SUPPRIMER');
    const cancelButton = screen.getByRole('button', { name: 'Annuler' });

    // Attendre que le focus soit sur l'input au montage
    await waitFor(() => {
      expect(input).toHaveFocus();
    });

    // Tab devrait aller au bouton Annuler (le bouton Confirmer est désactivé donc non focusable)
    await userEvent.keyboard('{Tab}');
    await waitFor(() => {
      expect(cancelButton).toHaveFocus();
    });

    // Vérifier que le focus est bien dans le modal (pas sur un élément externe)
    const modal = screen.getByRole('dialog');
    expect(modal).toContainElement(document.activeElement as HTMLElement);
  });

  it('devrait gérer le focus trap (Shift+Tab)', async () => {
    render(<ConfirmModal {...defaultProps} />);

    const input = screen.getByPlaceholderText('SUPPRIMER');
    const cancelButton = screen.getByRole('button', { name: 'Annuler' });

    // Attendre que le focus soit sur l'input au montage
    await waitFor(() => {
      expect(input).toHaveFocus();
    });

    // Aller au bouton Annuler d'abord
    await userEvent.keyboard('{Tab}');
    await waitFor(() => {
      expect(cancelButton).toHaveFocus();
    });

    // Shift+Tab depuis le bouton Annuler devrait revenir au premier élément (input)
    // car le confirmButton est désactivé et non focusable
    await userEvent.keyboard('{Shift>}{Tab}{/Shift}');
    await waitFor(() => {
      expect(input).toHaveFocus();
    });
  });

  it("devrait réinitialiser l'input après confirmation", async () => {
    const onConfirm = vi.fn();
    render(
      <ConfirmModal
        {...defaultProps}
        onConfirm={onConfirm}
        confirmText="SUPPRIMER"
      />
    );

    const input = screen.getByPlaceholderText('SUPPRIMER');

    await userEvent.type(input, 'SUPPRIMER');
    expect(input.value).toBe('SUPPRIMER');

    const confirmButton = screen.getByRole('button', { name: 'Confirmer' });
    await userEvent.click(confirmButton);

    // L'input devrait être réinitialisé après confirmation
    await waitFor(() => {
      expect(input.value).toBe('');
    });
  });
});
