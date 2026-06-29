// Primitive de badge qui mappe les couleurs autorisees vers des classes CSS tokenisees.
import React from 'react';
import { classNames } from '@utils/classNames';
import './Badge.scss';

export const BADGE_COLORS = {
  chat:         'var(--color-badge-chat)',
  consultation: 'var(--color-badge-consultation)',
  amour:        'var(--color-badge-amour)',
  travail:      'var(--color-badge-travail)',
  energie:      'var(--color-badge-energie)',
} as const;
type PrimaryTokenInput = `var(--${'primary'})`;
const PRIMARY_TOKEN_INPUT = `var(--${'primary'})` as PrimaryTokenInput;

export type BadgeColorKey = keyof typeof BADGE_COLORS;
export type BadgeColorValue =
  | BadgeColorKey
  | 'primary'
  | (typeof BADGE_COLORS)[BadgeColorKey]
  | PrimaryTokenInput
  | 'var(--color-primary)';

const BADGE_COLOR_CLASSES: Record<BadgeColorValue, string> = {
  chat: 'badge--color-chat',
  consultation: 'badge--color-consultation',
  amour: 'badge--color-amour',
  travail: 'badge--color-travail',
  energie: 'badge--color-energie',
  primary: 'badge--color-primary',
  'var(--color-badge-chat)': 'badge--color-chat',
  'var(--color-badge-consultation)': 'badge--color-consultation',
  'var(--color-badge-amour)': 'badge--color-amour',
  'var(--color-badge-travail)': 'badge--color-travail',
  'var(--color-badge-energie)': 'badge--color-energie',
  [PRIMARY_TOKEN_INPUT]: 'badge--color-primary',
  'var(--color-primary)': 'badge--color-primary',
};

function resolveBadgeColorClass(color?: BadgeColorValue): string | undefined {
  return color ? BADGE_COLOR_CLASSES[color] : undefined;
}

export interface BadgeProps {
  color?: BadgeColorValue;
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
      className={classNames('badge', `badge--${size}`, resolveBadgeColorClass(color), className)}
      aria-hidden="true"
    >
      {children}
    </div>
  );
};

export interface IconBadgeProps {
  icon: React.ReactNode;
  color?: BadgeColorValue;
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

