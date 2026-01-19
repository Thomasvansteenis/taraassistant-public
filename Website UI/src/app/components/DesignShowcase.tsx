import { CozyCard } from './CozyCard';
import { StatusBadge } from './StatusBadge';
import { QuickAction } from './QuickAction';
import { EmptyState } from './EmptyState';
import { LoadingSpinner } from './LoadingSpinner';
import { Lightbulb, Heart, MessageSquare } from 'lucide-react';

/**
 * Design Showcase Component
 * 
 * This component demonstrates all available design tokens and components
 * Use this as a reference for implementing new features
 */
export function DesignShowcase() {
  return (
    <div className="min-h-screen p-8 space-y-12">
      <div>
        <h1 className="mb-2">Home Assistant Design System</h1>
        <p className="text-muted-foreground">
          A warm, cozy design system with pastel colors and friendly typography
        </p>
      </div>

      {/* Colors */}
      <section>
        <h2 className="mb-6">Color Palette</h2>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
          <div>
            <div className="h-24 bg-primary rounded-xl mb-2 shadow-md" />
            <p className="text-sm font-medium">Primary</p>
            <p className="text-xs text-muted-foreground">Warm Coral</p>
          </div>
          <div>
            <div className="h-24 bg-secondary rounded-xl mb-2 shadow-md" />
            <p className="text-sm font-medium">Secondary</p>
            <p className="text-xs text-muted-foreground">Soft Lavender</p>
          </div>
          <div>
            <div className="h-24 bg-accent rounded-xl mb-2 shadow-md" />
            <p className="text-sm font-medium">Accent</p>
            <p className="text-xs text-muted-foreground">Soft Mint</p>
          </div>
          <div>
            <div className="h-24 bg-info rounded-xl mb-2 shadow-md" />
            <p className="text-sm font-medium">Info</p>
            <p className="text-xs text-muted-foreground">Soft Sky</p>
          </div>
          <div>
            <div className="h-24 bg-success rounded-xl mb-2 shadow-md" />
            <p className="text-sm font-medium">Success</p>
            <p className="text-xs text-muted-foreground">Soft Sage</p>
          </div>
          <div>
            <div className="h-24 bg-warning rounded-xl mb-2 shadow-md" />
            <p className="text-sm font-medium">Warning</p>
            <p className="text-xs text-muted-foreground">Soft Peach</p>
          </div>
          <div>
            <div className="h-24 bg-error rounded-xl mb-2 shadow-md" />
            <p className="text-sm font-medium">Error</p>
            <p className="text-xs text-muted-foreground">Soft Rose</p>
          </div>
        </div>
      </section>

      {/* Typography */}
      <section>
        <h2 className="mb-6">Typography</h2>
        <CozyCard className="space-y-4">
          <div>
            <h1>Heading 1 - Outfit Bold</h1>
            <p className="text-xs text-muted-foreground mt-1">
              2rem / Bold / Line-height: 1.3
            </p>
          </div>
          <div>
            <h2>Heading 2 - Outfit Semibold</h2>
            <p className="text-xs text-muted-foreground mt-1">
              1.5rem / Semibold / Line-height: 1.4
            </p>
          </div>
          <div>
            <h3>Heading 3 - Outfit Semibold</h3>
            <p className="text-xs text-muted-foreground mt-1">
              1.25rem / Semibold / Line-height: 1.4
            </p>
          </div>
          <div>
            <h4>Heading 4 - Outfit Medium</h4>
            <p className="text-xs text-muted-foreground mt-1">
              1.125rem / Medium / Line-height: 1.5
            </p>
          </div>
          <div>
            <p>
              Body text - DM Sans Regular. This is the primary font for all body
              content and longer text passages. It's highly readable and pairs
              beautifully with Outfit.
            </p>
            <p className="text-xs text-muted-foreground mt-1">
              1rem / Normal / Line-height: 1.6
            </p>
          </div>
        </CozyCard>
      </section>

      {/* Cards */}
      <section>
        <h2 className="mb-6">Cards</h2>
        <div className="grid md:grid-cols-3 gap-6">
          <CozyCard variant="default">
            <h3 className="mb-2">Default Card</h3>
            <p className="text-sm text-muted-foreground">
              Solid background with subtle shadow and border
            </p>
          </CozyCard>
          <CozyCard variant="gradient">
            <h3 className="mb-2">Gradient Card</h3>
            <p className="text-sm text-muted-foreground">
              Soft gradient from card to muted background
            </p>
          </CozyCard>
          <CozyCard variant="outlined">
            <h3 className="mb-2">Outlined Card</h3>
            <p className="text-sm text-muted-foreground">
              Transparent background with thicker border
            </p>
          </CozyCard>
        </div>
      </section>

      {/* Status Badges */}
      <section>
        <h2 className="mb-6">Status Badges</h2>
        <CozyCard>
          <div className="flex flex-wrap gap-3">
            <StatusBadge status="online" />
            <StatusBadge status="offline" />
            <StatusBadge status="error" />
            <StatusBadge status="idle" />
            <StatusBadge status="processing" />
            <StatusBadge status="online" showDot={false} label="24/24 Online" />
          </div>
        </CozyCard>
      </section>

      {/* Quick Actions */}
      <section>
        <h2 className="mb-6">Quick Actions</h2>
        <div className="grid md:grid-cols-2 gap-4">
          <QuickAction
            icon={<Lightbulb />}
            label="Primary Action"
            description="With description text"
            variant="primary"
          />
          <QuickAction
            icon={<Heart />}
            label="Secondary Action"
            description="Soft lavender style"
            variant="secondary"
          />
          <QuickAction
            icon={<MessageSquare />}
            label="Accent Action"
            description="Soft mint style"
            variant="accent"
          />
          <QuickAction
            icon={<Lightbulb />}
            label="Info Action"
            description="Soft sky blue"
            variant="info"
          />
        </div>
      </section>

      {/* Loading States */}
      <section>
        <h2 className="mb-6">Loading States</h2>
        <CozyCard>
          <div className="flex flex-wrap gap-8 items-center justify-center py-8">
            <LoadingSpinner size="sm" label="Small" />
            <LoadingSpinner size="md" label="Medium" />
            <LoadingSpinner size="lg" label="Large" />
          </div>
        </CozyCard>
      </section>

      {/* Empty States */}
      <section>
        <h2 className="mb-6">Empty State</h2>
        <CozyCard>
          <EmptyState
            icon={<MessageSquare />}
            title="No Messages Yet"
            description="Start a conversation to see messages appear here. It's easy and friendly!"
            action={
              <button className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary-dark transition-all hover:scale-105 shadow-md">
                Get Started
              </button>
            }
          />
        </CozyCard>
      </section>

      {/* Spacing */}
      <section>
        <h2 className="mb-6">Spacing Scale</h2>
        <CozyCard className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="w-1 bg-primary" style={{ height: '0.25rem' }} />
            <span className="text-sm">xs - 0.25rem (4px)</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-2 bg-primary" style={{ height: '0.5rem' }} />
            <span className="text-sm">sm - 0.5rem (8px)</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-4 bg-primary" style={{ height: '1rem' }} />
            <span className="text-sm">md - 1rem (16px)</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-6 bg-primary" style={{ height: '1.5rem' }} />
            <span className="text-sm">lg - 1.5rem (24px)</span>
          </div>
          <div className="flex items-center gap-4">
            <div className="w-8 bg-primary" style={{ height: '2rem' }} />
            <span className="text-sm">xl - 2rem (32px)</span>
          </div>
        </CozyCard>
      </section>

      {/* Border Radius */}
      <section>
        <h2 className="mb-6">Border Radius</h2>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div>
            <div className="h-24 bg-primary rounded-sm mb-2" />
            <p className="text-sm">sm - 0.5rem</p>
          </div>
          <div>
            <div className="h-24 bg-secondary rounded-md mb-2" />
            <p className="text-sm">md - 0.75rem</p>
          </div>
          <div>
            <div className="h-24 bg-accent rounded-lg mb-2" />
            <p className="text-sm">lg - 1rem</p>
          </div>
          <div>
            <div className="h-24 bg-info rounded-xl mb-2" />
            <p className="text-sm">xl - 1.5rem</p>
          </div>
          <div>
            <div className="h-24 bg-warning rounded-2xl mb-2" />
            <p className="text-sm">2xl - 2rem</p>
          </div>
        </div>
      </section>
    </div>
  );
}
