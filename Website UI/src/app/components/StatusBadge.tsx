import { cn } from "./ui/utils";

type Status = 'online' | 'offline' | 'error' | 'idle' | 'processing';

interface StatusBadgeProps {
  status: Status;
  label?: string;
  showDot?: boolean;
  className?: string;
}

const statusConfig = {
  online: {
    color: 'bg-success',
    textColor: 'text-success-foreground',
    label: 'Online'
  },
  offline: {
    color: 'bg-muted-foreground',
    textColor: 'text-muted-foreground',
    label: 'Offline'
  },
  error: {
    color: 'bg-error',
    textColor: 'text-error-foreground',
    label: 'Error'
  },
  idle: {
    color: 'bg-warning',
    textColor: 'text-warning-foreground',
    label: 'Idle'
  },
  processing: {
    color: 'bg-info',
    textColor: 'text-info-foreground',
    label: 'Processing'
  }
};

export function StatusBadge({ status, label, showDot = true, className }: StatusBadgeProps) {
  const config = statusConfig[status];
  const displayLabel = label || config.label;

  return (
    <div className={cn("inline-flex items-center gap-2 px-3 py-1.5 rounded-full", config.color, className)}>
      {showDot && (
        <span className="relative flex h-2 w-2">
          <span className={cn(
            "animate-ping absolute inline-flex h-full w-full rounded-full opacity-75",
            status === 'online' || status === 'processing' ? 'bg-white' : ''
          )}></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-white"></span>
        </span>
      )}
      <span className={cn("text-sm font-medium", config.textColor)}>{displayLabel}</span>
    </div>
  );
}
