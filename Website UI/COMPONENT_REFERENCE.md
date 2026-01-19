# Component Reference Guide

Quick reference for all components in the Home Assistant design system.

## 🎴 CozyCard

The primary container component with soft shadows and rounded corners.

### Import
```tsx
import { CozyCard } from './components/CozyCard';
```

### Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| children | ReactNode | required | Content to display inside card |
| className | string | - | Additional CSS classes |
| variant | 'default' \| 'gradient' \| 'outlined' | 'default' | Visual style variant |
| hoverable | boolean | false | Adds lift effect on hover |

### Examples
```tsx
// Default card
<CozyCard>
  <h3>Card Title</h3>
  <p>Card content here</p>
</CozyCard>

// Gradient card with hover effect
<CozyCard variant="gradient" hoverable>
  <h3>Hoverable Card</h3>
</CozyCard>

// Outlined card with custom class
<CozyCard variant="outlined" className="bg-muted">
  <h3>Custom Styled Card</h3>
</CozyCard>
```

---

## 🏷️ StatusBadge

Display system or device status with color coding and animation.

### Import
```tsx
import { StatusBadge } from './components/StatusBadge';
```

### Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| status | 'online' \| 'offline' \| 'error' \| 'idle' \| 'processing' | required | Current status |
| label | string | - | Custom label text |
| showDot | boolean | true | Show animated dot indicator |
| className | string | - | Additional CSS classes |

### Examples
```tsx
// Online status with default label
<StatusBadge status="online" />

// Error status with custom label
<StatusBadge status="error" label="Connection Lost" />

// Status without animated dot
<StatusBadge status="online" showDot={false} label="24/24" />
```

---

## ⚡ QuickAction

Large, friendly action buttons for common tasks.

### Import
```tsx
import { QuickAction } from './components/QuickAction';
```

### Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| icon | ReactNode | required | Icon element (from lucide-react) |
| label | string | required | Action label text |
| description | string | - | Optional description text |
| onClick | () => void | - | Click handler function |
| variant | 'primary' \| 'secondary' \| 'accent' \| 'info' | 'primary' | Color variant |
| disabled | boolean | false | Disable the action |

### Examples
```tsx
import { Lightbulb, Thermometer } from 'lucide-react';

// Primary action
<QuickAction
  icon={<Lightbulb />}
  label="Toggle Lights"
  description="Living room"
  variant="primary"
  onClick={() => console.log('Lights toggled')}
/>

// Secondary action with no description
<QuickAction
  icon={<Thermometer />}
  label="Adjust Temperature"
  variant="secondary"
  onClick={handleTempChange}
/>

// Disabled action
<QuickAction
  icon={<Lightbulb />}
  label="Toggle Lights"
  variant="primary"
  disabled={true}
/>
```

---

## 💬 ChatMessage

Display chat messages with visual distinction between user and assistant.

### Import
```tsx
import { ChatMessage } from './components/ChatMessage';
```

### Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| role | 'user' \| 'assistant' | required | Message sender role |
| content | string | required | Message text content |
| timestamp | string | - | Optional timestamp |
| avatar | ReactNode | - | Custom avatar element |
| status | 'sending' \| 'sent' \| 'error' | 'sent' | Message status |

### Examples
```tsx
// Assistant message
<ChatMessage
  role="assistant"
  content="Hello! How can I help you today?"
  timestamp="10:30 AM"
/>

// User message with status
<ChatMessage
  role="user"
  content="Turn on the lights"
  timestamp="10:31 AM"
  status="sent"
/>

// Message with custom avatar
<ChatMessage
  role="assistant"
  content="Done!"
  avatar={<CustomIcon />}
/>
```

---

## 📭 EmptyState

Friendly empty state displays with guidance.

### Import
```tsx
import { EmptyState } from './components/EmptyState';
```

### Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| icon | ReactNode | required | Large icon element |
| title | string | required | Empty state title |
| description | string | - | Optional description text |
| action | ReactNode | - | Optional action button/element |
| className | string | - | Additional CSS classes |

### Examples
```tsx
import { MessageSquare } from 'lucide-react';

// Basic empty state
<EmptyState
  icon={<MessageSquare />}
  title="No Messages Yet"
  description="Start a conversation to see messages appear here"
/>

// Empty state with action
<EmptyState
  icon={<MessageSquare />}
  title="No Messages Yet"
  description="Get started by asking a question"
  action={
    <button className="px-6 py-3 bg-primary text-primary-foreground rounded-lg">
      Start Chatting
    </button>
  }
/>
```

---

## ⏳ LoadingSpinner

Loading indicators with size variants.

### Import
```tsx
import { LoadingSpinner } from './components/LoadingSpinner';
```

### Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| size | 'sm' \| 'md' \| 'lg' | 'md' | Spinner size |
| className | string | - | Additional CSS classes |
| label | string | - | Optional loading label text |

### Examples
```tsx
// Medium spinner (default)
<LoadingSpinner />

// Large spinner with label
<LoadingSpinner size="lg" label="Loading data..." />

// Small spinner without label
<LoadingSpinner size="sm" />

// Centered in a container
<div className="flex justify-center py-8">
  <LoadingSpinner size="md" label="Processing..." />
</div>
```

---

## 📊 InsightsPanel

Collapsible side panel for insights, logs, and system metrics.

### Import
```tsx
import { InsightsPanel } from './components/InsightsPanel';
```

### Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| isOpen | boolean | required | Panel open/closed state |
| onToggle | () => void | required | Toggle handler function |

### Examples
```tsx
import { useState } from 'react';

function MyComponent() {
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  
  return (
    <>
      {/* Your main content */}
      
      {/* Insights panel */}
      <InsightsPanel
        isOpen={isPanelOpen}
        onToggle={() => setIsPanelOpen(!isPanelOpen)}
      />
    </>
  );
}
```

---

## 🎨 Using Design Tokens

All design tokens are available as CSS variables and Tailwind classes.

### Colors
```tsx
// Using Tailwind classes
<div className="bg-primary text-primary-foreground">
<div className="bg-secondary text-secondary-foreground">
<div className="bg-accent text-accent-foreground">
<div className="bg-info text-info-foreground">
<div className="bg-success text-success-foreground">
<div className="bg-warning text-warning-foreground">
<div className="bg-error text-error-foreground">

// Using CSS variables
<div style={{ backgroundColor: 'var(--primary)' }}>
```

### Spacing
```tsx
// Using Tailwind spacing
<div className="p-6">        {/* 1.5rem / 24px */}
<div className="gap-4">      {/* 1rem / 16px */}
<div className="mb-8">       {/* 2rem / 32px */}

// Using CSS variables
<div style={{ padding: 'var(--spacing-lg)' }}>
```

### Border Radius
```tsx
// Using Tailwind
<div className="rounded-lg">   {/* 1rem */}
<div className="rounded-xl">   {/* 1.5rem */}
<div className="rounded-2xl">  {/* 2rem */}

// Using CSS variables
<div style={{ borderRadius: 'var(--radius-lg)' }}>
```

### Shadows
```tsx
// Using inline styles
<div style={{ boxShadow: 'var(--shadow-md)' }}>
<div style={{ boxShadow: 'var(--shadow-lg)' }}>

// Common pattern in components
className="shadow-md"  // Tailwind equivalent
```

---

## 🎯 Common Patterns

### Interactive Card
```tsx
<CozyCard variant="gradient" hoverable>
  <div className="flex items-center gap-3">
    <Lightbulb className="w-6 h-6 text-primary" />
    <div>
      <h4>Smart Lights</h4>
      <p className="text-sm text-muted-foreground">24 devices</p>
    </div>
  </div>
</CozyCard>
```

### Status Display
```tsx
<div className="flex items-center justify-between">
  <span>System Status</span>
  <StatusBadge status="online" />
</div>
```

### Loading State
```tsx
{isLoading ? (
  <LoadingSpinner size="md" label="Loading..." />
) : (
  <Content />
)}
```

### Error State
```tsx
{hasError ? (
  <EmptyState
    icon={<CircleAlert />}
    title="Something went wrong"
    description="We couldn't load the data. Please try again."
    action={
      <button onClick={retry} className="...">
        Retry
      </button>
    }
  />
) : (
  <Content />
)}
```

### Chat Interface
```tsx
<div className="space-y-4">
  {messages.map(msg => (
    <ChatMessage
      key={msg.id}
      role={msg.role}
      content={msg.content}
      timestamp={msg.timestamp}
    />
  ))}
</div>
```

---

## 🔧 Customization Tips

### Extending Components
```tsx
// Add custom styles to components
<CozyCard className="bg-gradient-to-br from-primary/10 to-secondary/10">
  Custom gradient background
</CozyCard>

// Compose components
<CozyCard>
  <div className="flex items-center justify-between mb-4">
    <h3>Device Status</h3>
    <StatusBadge status="online" />
  </div>
  <QuickAction
    icon={<Lightbulb />}
    label="Toggle"
    variant="primary"
  />
</CozyCard>
```

### Creating Variants
```tsx
// Create your own button variants using design tokens
<button className="
  px-6 py-3
  bg-primary hover:bg-primary-dark
  text-primary-foreground
  rounded-xl
  transition-all duration-300
  hover:scale-105
  shadow-md
">
  Custom Button
</button>
```

### Responsive Design
```tsx
// Use Tailwind responsive prefixes
<div className="
  grid 
  grid-cols-1 md:grid-cols-2 lg:grid-cols-3
  gap-4 md:gap-6
  p-4 md:p-8
">
  {/* Content adapts to screen size */}
</div>
```

---

## 📋 Checklist for New Features

When building new features:

- [ ] Use existing components when possible
- [ ] Follow color palette for consistency
- [ ] Use design tokens for spacing, radius, shadows
- [ ] Include hover states for interactive elements
- [ ] Add loading states for async operations
- [ ] Handle error states gracefully
- [ ] Test on mobile, tablet, and desktop
- [ ] Ensure 44px minimum touch targets
- [ ] Add keyboard navigation support
- [ ] Use semantic HTML
- [ ] Test with screen readers

---

## 💡 Examples from Dashboard

See `/src/app/App.tsx` for a complete implementation example including:
- Full layout structure
- State management
- Interactive chat interface
- Quick actions integration
- Collapsible side panel
- Multiple view modes
- Error handling
- Loading states

For a visual showcase of all components, see `/src/app/components/DesignShowcase.tsx`.

---

Built with ❤️ using React, TypeScript, and Tailwind CSS
