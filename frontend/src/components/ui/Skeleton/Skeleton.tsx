import React from 'react';
import { classNames } from '@utils/classNames';
import './Skeleton.css';

export interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  variant?: 'text' | 'rect' | 'circle';
  className?: string;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width,
  height,
  variant = 'text',
  className,
}) => {
  const style: React.CSSProperties = {
    width: width,
    height: height,
  };

  return (
    <div
      className={classNames('skeleton', `skeleton--${variant}`, className)}
      style={style}
      aria-hidden="true"
    />
  );
};

export interface SkeletonGroupProps {
  count?: number;
  widths?: string[];
  height?: string | number;
  className?: string;
  gap?: string | number;
}

export const SkeletonGroup: React.FC<SkeletonGroupProps> = ({
  count = 3,
  widths,
  height = '1rem',
  className,
  gap = 'var(--space-2, 0.5rem)',
}) => {
  const defaultWidths = ['80%', '60%', '75%', '50%', '70%'];
  
  return (
    <div 
      className={classNames('skeleton-group', className)}
      style={{ display: 'flex', flexDirection: 'column', gap }}
    >
      {Array.from({ length: count }, (_, i) => (
        <Skeleton
          key={i}
          variant="text"
          height={height}
          width={widths?.[i] ?? defaultWidths[i % defaultWidths.length]}
        />
      ))}
    </div>
  );
};

