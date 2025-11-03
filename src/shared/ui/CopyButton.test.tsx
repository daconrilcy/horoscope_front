import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { CopyButton } from './CopyButton';

describe('CopyButton', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock clipboard API
    Object.assign(navigator, {
      clipboard: {
        writeText: vi.fn().mockResolvedValue(undefined),
      },
    });
  });

  it('devrait copier du texte statique', async () => {
    render(<CopyButton text="Texte à copier" />);

    const button = screen.getByRole('button', { name: 'Copier' });
    await userEvent.click(button);

    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockWriteText = vi.mocked(navigator.clipboard.writeText);
    expect(mockWriteText).toHaveBeenCalledWith('Texte à copier');
  });

  it('devrait copier du texte depuis une fonction', async () => {
    const getText = vi.fn().mockReturnValue('Texte depuis fonction');
    render(<CopyButton text={getText} />);

    const button = screen.getByRole('button', { name: 'Copier' });
    await userEvent.click(button);

    expect(getText).toHaveBeenCalled();
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockWriteText = vi.mocked(navigator.clipboard.writeText);
    expect(mockWriteText).toHaveBeenCalledWith('Texte depuis fonction');
  });

  it('devrait copier du texte depuis une fonction async', async () => {
    const getText = vi.fn().mockResolvedValue('Texte async');
    render(<CopyButton text={getText} />);

    const button = screen.getByRole('button', { name: 'Copier' });
    await userEvent.click(button);

    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockWriteText = vi.mocked(navigator.clipboard.writeText);
    await waitFor(() => {
      expect(mockWriteText).toHaveBeenCalledWith('Texte async');
    });
  });

  it('devrait afficher "Copié !" après copie réussie', async () => {
    render(<CopyButton text="Texte" />);

    const button = screen.getByRole('button', { name: 'Copier' });
    await userEvent.click(button);

    await waitFor(() => {
      expect(screen.getByText('Copié !')).toBeInTheDocument();
      expect(screen.getByRole('button')).toHaveAttribute(
        'aria-label',
        'Copié !'
      );
    });
  });

  it('devrait appeler onCopy après copie réussie', async () => {
    const onCopy = vi.fn();
    render(<CopyButton text="Texte" onCopy={onCopy} />);

    const button = screen.getByRole('button', { name: 'Copier' });
    await userEvent.click(button);

    await waitFor(() => {
      expect(onCopy).toHaveBeenCalledTimes(1);
    });
  });

  it('devrait utiliser fallback document.execCommand si clipboard API échoue', async () => {
    // Désactiver clipboard API
    Object.assign(navigator, {
      clipboard: undefined,
    });

    const execCommand = vi.fn().mockReturnValue(true);

    document.execCommand = execCommand as typeof document.execCommand;

    render(<CopyButton text="Texte" />);

    const button = screen.getByRole('button', { name: 'Copier' });
    await userEvent.click(button);

    await waitFor(() => {
      expect(execCommand).toHaveBeenCalledWith('copy');
    });
  });

  it('devrait afficher une erreur si copie échoue', async () => {
    const error = new Error('Permission denied');
    // eslint-disable-next-line @typescript-eslint/unbound-method
    const mockWriteText = vi.mocked(navigator.clipboard?.writeText);
    if (mockWriteText !== undefined) {
      mockWriteText.mockRejectedValue(error);
    }

    render(<CopyButton text="Texte" />);

    const button = screen.getByRole('button', { name: 'Copier' });
    await userEvent.click(button);

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
    });
  });
});
