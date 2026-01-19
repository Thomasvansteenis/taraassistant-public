import { ReactNode } from 'react';
import { cn } from './ui/utils';

interface CozyCardProps {
  children: ReactNode;
  className?: string;
  variant?: 'default' | 'gradient' | 'outlined';
  hoverable?: boolean;
}

export function CozyCard({ 
  children, 
  className, 
  variant = 'default',
  hoverable = false 
}: CozyCardProps) {
  const variants = {
    default: 'bg-card border border-border',
    gradient: 'bg-gradient-to-br from-card to-muted border border-border',
    outlined: 'bg-transparent border-2 border-border'
  };

  return (
    <div 
      className={cn(
        "rounded-xl p-6 transition-all duration-300",
        variants[variant],
        hoverable && "hover:shadow-lg hover:-translate-y-0.5 cursor-pointer",
        !hoverable && "shadow-md",
        className
      )}
      style={{
        boxShadow: hoverable 
          ? 'var(--shadow-md)' 
          : 'var(--shadow-md)'
      }}
    >
      {children}
    </div>
  );
}
