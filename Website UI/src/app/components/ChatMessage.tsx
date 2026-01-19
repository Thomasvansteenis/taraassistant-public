import { ReactNode } from 'react';
import { cn } from './ui/utils';

interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: string;
  avatar?: ReactNode;
  status?: 'sending' | 'sent' | 'error';
}

export function ChatMessage({ 
  role, 
  content, 
  timestamp,
  avatar,
  status = 'sent' 
}: ChatMessageProps) {
  const isUser = role === 'user';

  return (
    <div className={cn(
      "flex gap-3 mb-6 animate-in fade-in slide-in-from-bottom-2 duration-300",
      isUser && "flex-row-reverse"
    )}>
      {/* Avatar */}
      <div className={cn(
        "flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center",
        isUser ? "bg-primary text-primary-foreground" : "bg-secondary text-secondary-foreground"
      )}
      style={{
        boxShadow: 'var(--shadow-sm)'
      }}>
        {avatar || (
          <span className="text-sm font-medium">
            {isUser ? '👤' : '🏠'}
          </span>
        )}
      </div>

      {/* Message content */}
      <div className={cn(
        "flex-1 max-w-[70%]",
        isUser && "flex flex-col items-end"
      )}>
        <div className={cn(
          "rounded-2xl px-4 py-3 shadow-sm",
          isUser 
            ? "bg-primary text-primary-foreground rounded-tr-sm" 
            : "bg-card text-card-foreground border border-border rounded-tl-sm"
        )}
        style={{
          boxShadow: 'var(--shadow-sm)'
        }}>
          <p className="whitespace-pre-wrap leading-relaxed">{content}</p>
        </div>
        
        {/* Timestamp and status */}
        <div className={cn(
          "flex items-center gap-2 mt-1 px-2",
          isUser && "flex-row-reverse"
        )}>
          {timestamp && (
            <span className="text-xs text-muted-foreground">{timestamp}</span>
          )}
          {status === 'sending' && (
            <span className="text-xs text-muted-foreground">Sending...</span>
          )}
          {status === 'error' && (
            <span className="text-xs text-error">Failed to send</span>
          )}
        </div>
      </div>
    </div>
  );
}
