import React from 'react';
import { classNames } from '../../../utils/classNames';
import './Badge.css';

export const BADGE_COLORS = {
  chat:         'var(--color-badge-chat)',
  consultation: 'var(--color-badge-consultation)',
  amour:        'var(--color-badge-amour)',
  travail:      'var(--color-badge-travail)',
  energie:      'var(--color-badge-energie)',
} as const;

export type BadgeColorKey = keyof typeof BADGE_COLORS;

export interface BadgeProps {
  color?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
  children?: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({
  color,
  size = 'md',
  className,
  children,
}) => {
  return (
    <div
      className={classNames('badge', `badge--${size}`, className)}
      style={{ background: color }}
      aria-hidden="true"
    >
      {children}
    </div>
  );
};

export interface IconBadgeProps {
  icon: React.ReactNode;
  color?: string;
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}

export const IconBadge: React.FC<IconBadgeProps> = ({
  icon,
  color,
  size = 'md',
  className,
}) => {
  return (
    <Badge color={color} size={size} className={classNames('badge--icon', className)}>
      {icon}
    </Badge>
  );
};
