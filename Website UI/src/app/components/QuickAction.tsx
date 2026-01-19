import { ReactNode } from 'react';
import { cn } from './ui/utils';

interface QuickActionProps {
  icon: ReactNode;
  label: string;
  description?: string;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'accent' | 'info';
  disabled?: boolean;
}

const variantStyles = {
  primary: 'bg-primary hover:bg-primary-dark text-primary-foreground',
  secondary: 'bg-secondary hover:bg-secondary-dark text-secondary-foreground',
  accent: 'bg-accent hover:bg-accent-dark text-accent-foreground',
  info: 'bg-info hover:bg-info-dark text-info-foreground',
};

export function QuickAction({ 
  icon, 
  label, 
  description,
  onClick, 
  variant = 'primary',
  disabled = false 
}: QuickActionProps) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={cn(
        "flex items-center gap-4 w-full p-4 rounded-xl transition-all duration-300",
        "hover:scale-105 hover:shadow-lg active:scale-95",
        "disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100",
        variantStyles[variant]
      )}
      style={{
        boxShadow: 'var(--shadow-sm)'
      }}
    >
      <div className="flex-shrink-0 text-2xl">
        {icon}
      </div>
      <div className="flex-1 text-left">
        <div className="font-medium">{label}</div>
        {description && (
          <div className="text-sm opacity-80 mt-0.5">{description}</div>
        )}
      </div>
    </button>
  );
}
