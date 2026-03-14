import React, { useEffect, useRef, useId } from 'react';
import { createPortal } from 'react-dom';
import { X } from 'lucide-react';
import { classNames } from '@utils/classNames';
import { detectLang } from '@i18n/astrology';
import { commonTranslations } from '@i18n/common';
import './Modal.css';

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  variant?: 'default' | 'danger' | 'info';
  className?: string;
  size?: 'sm' | 'md' | 'lg';
  closeAriaLabel?: string;
}

export const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  footer,
  variant = 'default',
  className,
  size = 'md',
  closeAriaLabel,
}) => {
  const lang = detectLang();
  const t = commonTranslations(lang);
  const modalRef = useRef<HTMLDivElement>(null);
  const titleId = useId();

  const resolvedCloseAriaLabel = closeAriaLabel ?? t.actions.close;

  // Handle Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    document.addEventListener('keydown', handleEscape);
    return () => document.removeEventListener('keydown', handleEscape);
  }, [isOpen, onClose]);

  // Handle Scroll Lock
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  // Focus Trap
  useEffect(() => {
    if (!isOpen) return;
    
    const modal = modalRef.current;
    if (!modal) return;

    const focusableElements = modal.querySelectorAll(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    );
    const first = focusableElements[0] as HTMLElement;
    const last = focusableElements[focusableElements.length - 1] as HTMLElement;

    if (first) {
      // Small delay to ensure modal animation hasn't blocked focus
      setTimeout(() => first.focus(), 50);
    }

    const handleTab = (e: KeyboardEvent) => {
      if (e.key !== 'Tab') return;

      if (e.shiftKey) {
        if (document.activeElement === first) {
          e.preventDefault();
          last?.focus();
        }
      } else {
        if (document.activeElement === last) {
          e.preventDefault();
          first?.focus();
        }
      }
    };

    modal.addEventListener('keydown', handleTab);
    return () => modal.removeEventListener('keydown', handleTab);
  }, [isOpen]);

  if (!isOpen) return null;

  return createPortal(
    <div 
      className="modal-overlay" 
      onClick={onClose}
    >
      <div
        ref={modalRef}
        className={classNames(
          'modal',
          `modal--${variant}`,
          `modal--${size}`,
          className
        )}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        onClick={(e) => e.stopPropagation()}
      >
        <div className="modal__header">
          <h2 id={titleId} className="modal__title">
            {title}
          </h2>
          <button
            type="button"
            className="modal__close"
            onClick={onClose}
            aria-label={resolvedCloseAriaLabel}
          >
            <X size={20} />
          </button>
        </div>

        <div className="modal__body">{children}</div>

        {footer && <div className="modal__footer">{footer}</div>}
      </div>
    </div>,
    document.body
  );
};


