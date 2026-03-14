import React from 'react';
import { classNames } from '@utils/classNames';
import './Card.css';

export interface CardProps {
  as?: any;
  variant?: 'glass' | 'solid' | 'elevated';
  padding?: 'none' | 'sm' | 'md' | 'lg';
  clickable?: boolean;
  className?: string;
  children?: React.ReactNode;
  onClick?: () => void;
}

const CardHeader: React.FC<{ children: React.ReactNode; className?: string }> = ({ 
  children, 
  className 
}) => (
  <div className={classNames('card__header', className)}>{children}</div>
);

const CardBody: React.FC<{ children: React.ReactNode; className?: string }> = ({ 
  children, 
  className 
}) => (
  <div className={classNames('card__body', className)}>{children}</div>
);

const CardFooter: React.FC<{ children: React.ReactNode; className?: string }> = ({ 
  children, 
  className 
}) => (
  <div className={classNames('card__footer', className)}>{children}</div>
);

export const Card: React.FC<CardProps> & {
  Header: typeof CardHeader;
  Body: typeof CardBody;
  Footer: typeof CardFooter;
} = ({
  as: Tag = 'div',
  variant = 'glass',
  padding = 'md',
  clickable = false,
  className,
  children,
  ...props
}) => {
  return (
    <Tag
      className={classNames(
        'card',
        `card--${variant}`,
        variant === 'glass' && 'glass-card',
        `card--padding-${padding}`,
        clickable && 'card--clickable',
        className
      )}
      {...props}
    >
      {children}
    </Tag>
  );
};

Card.Header = CardHeader;
Card.Body = CardBody;
Card.Footer = CardFooter;

