import { useState } from 'react';
import { CozyCard } from './CozyCard';
import { cn } from './ui/utils';
import { ChevronLeft, Activity, CircleAlert, CircleCheck } from 'lucide-react';

interface LogEntry {
  id: string;
  type: 'info' | 'warning' | 'error' | 'success';
  message: string;
  timestamp: string;
}

interface InsightsPanelProps {
  isOpen: boolean;
  onToggle: () => void;
}

const mockLogs: LogEntry[] = [
  { id: '1', type: 'success', message: 'Smart lights turned on in living room', timestamp: '2 min ago' },
  { id: '2', type: 'info', message: 'Temperature adjusted to 72°F', timestamp: '5 min ago' },
  { id: '3', type: 'warning', message: 'Front door unlocked', timestamp: '12 min ago' },
  { id: '4', type: 'success', message: 'Morning routine completed', timestamp: '1 hour ago' },
  { id: '5', type: 'error', message: 'Garage door sensor offline', timestamp: '2 hours ago' },
];

const typeConfig = {
  info: { color: 'text-info', bg: 'bg-info/10', icon: Activity },
  warning: { color: 'text-warning', bg: 'bg-warning/10', icon: CircleAlert },
  error: { color: 'text-error', bg: 'bg-error/10', icon: CircleAlert },
  success: { color: 'text-success', bg: 'bg-success/10', icon: CircleCheck },
};

export function InsightsPanel({ isOpen, onToggle }: InsightsPanelProps) {
  return (
    <>
      {/* Overlay for mobile */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          onClick={onToggle}
        />
      )}
      
      {/* Panel */}
      <div
        className={cn(
          "fixed lg:relative top-0 right-0 h-full bg-background border-l border-border",
          "transition-all duration-300 z-50",
          "flex flex-col overflow-visible",
          isOpen ? "w-80 md:w-96" : "w-0 border-l-0"
        )}
      >
        {/* Toggle button */}
        <button
          onClick={onToggle}
          className={cn(
            "absolute left-0 top-20 -translate-x-full",
            "bg-card border border-r-0 border-border rounded-l-lg p-2",
            "hover:bg-muted transition-colors shadow-md",
            "flex"
          )}
          style={{
            boxShadow: 'var(--shadow-md)'
          }}
        >
          <ChevronLeft 
            className={cn(
              "w-5 h-5 transition-transform duration-300",
              !isOpen && "rotate-180"
            )}
          />
        </button>

        {/* Panel content */}
        <div className={cn(
          "flex-1 overflow-hidden",
          !isOpen && "invisible"
        )}>
          <div className="h-full overflow-y-auto p-6 space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
              <h2>Insights & Logs</h2>
              <button
                onClick={onToggle}
                className="lg:hidden p-2 hover:bg-muted rounded-lg transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 gap-3">
              <CozyCard className="p-4">
                <div className="text-2xl font-bold text-primary mb-1">24</div>
                <div className="text-sm text-muted-foreground">Active Devices</div>
              </CozyCard>
              <CozyCard className="p-4">
                <div className="text-2xl font-bold text-success mb-1">98%</div>
                <div className="text-sm text-muted-foreground">Uptime</div>
              </CozyCard>
            </div>

            {/* Activity Logs */}
            <div>
              <h3 className="mb-4">Recent Activity</h3>
              <div className="space-y-3">
                {mockLogs.map((log) => {
                  const config = typeConfig[log.type];
                  const Icon = config.icon;
                  
                  return (
                    <div
                      key={log.id}
                      className={cn(
                        "flex gap-3 p-3 rounded-lg border border-border",
                        "bg-card hover:bg-muted/50 transition-colors"
                      )}
                    >
                      <div className={cn(
                        "flex-shrink-0 w-8 h-8 rounded-lg flex items-center justify-center",
                        config.bg
                      )}>
                        <Icon className={cn("w-4 h-4", config.color)} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm leading-snug mb-1">{log.message}</p>
                        <p className="text-xs text-muted-foreground">{log.timestamp}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* System Health */}
            <div>
              <h3 className="mb-4">System Health</h3>
              <CozyCard variant="gradient" className="p-4">
                <div className="space-y-3">
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>CPU Usage</span>
                      <span className="text-muted-foreground">32%</span>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-success w-[32%] rounded-full transition-all duration-300" />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Memory</span>
                      <span className="text-muted-foreground">58%</span>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-info w-[58%] rounded-full transition-all duration-300" />
                    </div>
                  </div>
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Storage</span>
                      <span className="text-muted-foreground">74%</span>
                    </div>
                    <div className="h-2 bg-muted rounded-full overflow-hidden">
                      <div className="h-full bg-warning w-[74%] rounded-full transition-all duration-300" />
                    </div>
                  </div>
                </div>
              </CozyCard>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}