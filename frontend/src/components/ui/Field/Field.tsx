import React, { useId, useState, forwardRef } from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { classNames } from '../../../utils/classNames';
import './Field.css';

export interface FieldProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'id'> {
  label?: string;
  hint?: string;
  error?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  id?: string;
}

export const Field = forwardRef<HTMLInputElement, FieldProps>(
  (
    {
      label,
      hint,
      error,
      leftIcon,
      rightIcon,
      id: providedId,
      type = 'text',
      className,
      disabled,
      ...props
    },
    ref
  ) => {
    const generatedId = useId();
    const id = providedId ?? generatedId;
    const errorId = `${id}-error`;
    const hintId = `${id}-hint`;

    const [showPassword, setShowPassword] = useState(false);

    const isPassword = type === 'password';
    const inputType = isPassword ? (showPassword ? 'text' : 'password') : type;

    const togglePassword = () => {
      setShowPassword((prev) => !prev);
    };

    const hasLeftIcon = !!leftIcon;
    const hasRightIcon = !!rightIcon || isPassword;

    return (
      <div className={classNames('field', className)}>
        {label && (
          <label htmlFor={id} className="field__label">
            {label}
          </label>
        )}

        <div className="field__input-wrapper">
          {leftIcon && <span className="field__icon field__icon-left">{leftIcon}</span>}

          <input
            {...props}
            ref={ref}
            id={id}
            type={inputType}
            disabled={disabled}
            aria-invalid={!!error ? 'true' : undefined}
            aria-describedby={
              classNames(!!error && errorId, !!hint && hintId) || undefined
            }
            className={classNames(
              'field__input',
              error && 'field__input--error',
              hasLeftIcon && 'field__input--has-left-icon',
              hasRightIcon && 'field__input--has-right-icon',
              disabled && 'field__input--disabled'
            )}
          />

          {isPassword ? (
            <button
              type="button"
              onClick={togglePassword}
              className="field__icon field__icon-right field__password-toggle"
              aria-label={showPassword ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
              disabled={disabled}
            >
              {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
            </button>
          ) : (
            rightIcon && <span className="field__icon field__icon-right">{rightIcon}</span>
          )}
        </div>

        {error && (
          <span id={errorId} className="field__error" role="alert">
            {error}
          </span>
        )}

        {hint && !error && (
          <span id={hintId} className="field__hint">
            {hint}
          </span>
        )}
      </div>
    );
  }
);

Field.displayName = 'Field';
