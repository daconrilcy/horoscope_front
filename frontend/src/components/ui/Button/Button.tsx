import React from 'react';
import './Button.css';
import { classNames } from '../../../utils/classNames';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  loading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      variant = 'primary',
      size = 'md',
      loading = false,
      leftIcon,
      rightIcon,
      fullWidth = false,
      className,
      children,
      disabled,
      type = 'button',
      ...props
    },
    ref
  ) => {
    const isInteractivityDisabled = disabled || loading;

    return (
      <button
        ref={ref}
        type={type}
        disabled={isInteractivityDisabled}
        aria-busy={loading ? 'true' : undefined}
        aria-disabled={disabled ? 'true' : undefined}
        className={classNames(
          'btn',
          `btn--${variant}`,
          `btn--${size}`,
          fullWidth && 'btn--full-width',
          loading && 'btn--loading',
          className
        )}
        {...props}
      >
        {loading && (
          <span className="btn__spinner-container">
            <span className="btn__spinner" aria-hidden="true" />
          </span>
        )}
        {!loading && leftIcon && <span className="btn__icon btn__icon--left">{leftIcon}</span>}
        <span className="btn__content">{children}</span>
        {!loading && rightIcon && <span className="btn__icon btn__icon--right">{rightIcon}</span>}
      </button>
    );
  }
);

Button.displayName = 'Button';
