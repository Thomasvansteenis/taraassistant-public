# Home Assistant AI Dashboard - Design System

A warm, cozy home assistant interface with a homely pastel palette, expressive typography, and comprehensive component library.

## 🎨 Design Principles

- **Warm & Cozy**: Soft pastel colors that feel welcoming and homely
- **Minimal Chrome**: Clean interface with generous spacing and clear hierarchy
- **Soft Depth**: Subtle shadows and rounded corners for gentle visual depth
- **Expressive Typography**: Friendly Outfit font paired with readable DM Sans
- **Responsive**: Seamlessly adapts from mobile to desktop

## 🎯 Key Features

### Chat Panel
- Interactive AI assistant chat interface
- Message history with timestamps
- Loading states for AI responses
- User and assistant message distinction
- Empty state guidance

### Quick Actions
- Large, friendly action buttons
- Four color variants (primary, secondary, accent, info)
- Icon support with descriptions
- Hover animations and feedback
- Disabled states

### Status Bar
- System status indicators
- Animated status badges
- User greeting
- Mobile-responsive navigation

### Insights Panel
- Collapsible side panel
- Activity logs with type indicators (info, warning, error, success)
- System health metrics (CPU, Memory, Storage)
- Device statistics
- Mobile overlay with smooth animations

### State Demonstrations
- **Empty State**: Guidance for new users
- **Active State**: Fully functioning dashboard
- **Error State**: Connection error handling

## 📦 Component Library

### CozyCard
Primary container component with soft shadows and rounded corners.

```tsx
<CozyCard variant="default" hoverable>
  Content here
</CozyCard>
```

**Variants:**
- `default` - Solid background with border
- `gradient` - Subtle gradient background
- `outlined` - Transparent with thicker border

**Props:**
- `hoverable` - Adds lift effect on hover

### StatusBadge
Display system or device status with color coding.

```tsx
<StatusBadge status="online" />
<StatusBadge status="error" label="Connection Lost" />
```

**States:** online, offline, error, idle, processing

### QuickAction
Large, friendly action buttons for common tasks.

```tsx
<QuickAction
  icon={<Lightbulb />}
  label="Toggle Lights"
  description="Living room"
  variant="primary"
  onClick={handleClick}
/>
```

**Variants:** primary, secondary, accent, info

### ChatMessage
Display chat messages with visual distinction.

```tsx
<ChatMessage
  role="assistant"
  content="Hello! How can I help?"
  timestamp="10:30 AM"
  status="sent"
/>
```

**Roles:** user, assistant
**Status:** sending, sent, error

### EmptyState
Friendly empty state displays.

```tsx
<EmptyState
  icon={<MessageSquare />}
  title="No messages yet"
  description="Start a conversation"
  action={<button>Get Started</button>}
/>
```

### LoadingSpinner
Loading indicators with size variants.

```tsx
<LoadingSpinner size="md" label="Loading..." />
```

**Sizes:** sm, md, lg

### InsightsPanel
Collapsible side panel for insights and logs.

```tsx
<InsightsPanel
  isOpen={isPanelOpen}
  onToggle={() => setIsPanelOpen(!isPanelOpen)}
/>
```

## 🎨 Color Palette

### Primary - Warm Coral
- Base: `#ff9b85`
- Light: `#ffb5a3`
- Dark: `#f48171`
- Usage: Primary actions, branding, user messages

### Secondary - Soft Lavender
- Base: `#d4c5f9`
- Light: `#e5dcfc`
- Dark: `#c0afe6`
- Usage: Secondary actions, assistant branding

### Accent - Soft Mint
- Base: `#b8e6d5`
- Light: `#d1f0e3`
- Dark: `#a0d8c4`
- Usage: Tertiary actions, accents

### Info - Soft Sky Blue
- Base: `#a7d7f0`
- Usage: Information states, processing

### Success - Soft Sage
- Base: `#c7e8b5`
- Usage: Success states, online status

### Warning - Soft Peach
- Base: `#ffd89b`
- Usage: Warning states, attention needed

### Error - Soft Rose
- Base: `#ffb3ba`
- Usage: Error states, critical alerts

### Neutrals
- Background: `#fdfbf7` (warm off-white)
- Foreground: `#4a4137` (warm dark brown)
- Muted: `#f5f2ed` (soft beige)
- Border: `#e8e4dc` (soft border)

## 📝 Typography

### Font Families
- **Primary (Headings)**: 'Outfit' - Friendly, expressive, rounded
- **Secondary (Body)**: 'DM Sans' - Clean, readable, professional

### Type Scale
- **h1**: 2rem (32px) / Bold / 1.3 line-height
- **h2**: 1.5rem (24px) / Semibold / 1.4 line-height
- **h3**: 1.25rem (20px) / Semibold / 1.4 line-height
- **h4**: 1.125rem (18px) / Medium / 1.5 line-height
- **Body**: 1rem (16px) / Normal / 1.6 line-height
- **Small**: 0.875rem (14px) / Normal / 1.5 line-height

## 📏 Spacing Scale

- **xs**: 0.25rem (4px)
- **sm**: 0.5rem (8px)
- **md**: 1rem (16px) - Base unit
- **lg**: 1.5rem (24px)
- **xl**: 2rem (32px)
- **2xl**: 3rem (48px)
- **3xl**: 4rem (64px)

**Guidelines:**
- Use generous spacing for calm, uncluttered feel
- Minimum touch target: 44px
- Card padding: 1.5rem (24px)
- Section gaps: 1.5-2rem

## 🔄 Border Radius

- **sm**: 0.5rem (8px) - Small elements
- **md**: 0.75rem (12px) - Medium elements
- **lg**: 1rem (16px) - Cards, buttons (default)
- **xl**: 1.5rem (24px) - Large cards
- **2xl**: 2rem (32px) - Chat bubbles

## 🌑 Shadows (Soft Depth)

- **xs**: Subtle, barely visible
- **sm**: Small elements (badges, buttons)
- **md**: Cards, buttons (default)
- **lg**: Elevated cards, modals
- **xl**: Floating panels, dropdowns

All shadows use very low opacity (3-8%) for soft, gentle depth.

## 🎬 Interaction Patterns

### Loading States
- Use LoadingSpinner for async operations
- Show inline spinners for AI responses
- Disable inputs during loading
- Display friendly loading text

### Success Feedback
- Use success color (#c7e8b5)
- Show checkmark icon
- Add subtle animation
- Display success message

### Error Handling
- Use error color (#ffb3ba)
- Show alert icon
- Provide clear error message
- Offer retry action
- Don't hide interface - show error state

### Hover States
- Subtle scale transforms (scale-105)
- Background color changes
- Shadow elevation
- Smooth transitions (300ms)

### Focus States
- 2px ring in primary color
- 50% opacity for soft appearance
- Visible on keyboard navigation

### Disabled States
- 50% opacity
- No pointer cursor
- No hover effects
- Clear visual distinction

## 📱 Responsive Breakpoints

### Mobile (< 640px)
- Single column layout
- Stacked quick actions
- Full-width chat
- Overlay side panel

### Tablet (640px - 1024px)
- Two column layout
- Side-by-side content
- Collapsible side panel

### Desktop (> 1024px)
- Three column layout
- Persistent side panel toggle
- Maximum content width
- Generous spacing

## 🎨 Animation Guidelines

### Duration
- Micro-interactions: 150ms (quick feedback)
- Standard: 300ms (most transitions)
- Complex: 500ms (page transitions)

### Easing
- Default: ease-in-out
- Entry: ease-out
- Exit: ease-in

### Types
- Fade: opacity transitions
- Slide: translate transforms
- Scale: size transforms for hover
- Spin: loading indicators

**Guidelines:**
- Keep animations subtle and purposeful
- Don't overuse
- Ensure accessibility (respect prefers-reduced-motion)

## ♿ Accessibility

- All interactive elements have min 44px touch target
- Color contrast meets WCAG AA standards (4.5:1)
- Focus indicators visible for keyboard navigation
- ARIA labels on icon-only buttons
- Semantic HTML structure
- Screen reader friendly
- Reduced motion support

## 📁 File Structure

```
/src/app/
  App.tsx - Main dashboard component
  /components/
    CozyCard.tsx - Primary container component
    StatusBadge.tsx - Status indicators
    QuickAction.tsx - Action buttons
    ChatMessage.tsx - Chat message display
    EmptyState.tsx - Empty state displays
    LoadingSpinner.tsx - Loading indicators
    InsightsPanel.tsx - Collapsible side panel
    DesignShowcase.tsx - Component showcase
    DesignTokens.tsx - Token documentation
    
/src/styles/
  theme.css - Design tokens and CSS variables
  fonts.css - Typography imports
```

## 🚀 Usage Example

```tsx
import { CozyCard } from './components/CozyCard';
import { StatusBadge } from './components/StatusBadge';
import { QuickAction } from './components/QuickAction';
import { Lightbulb } from 'lucide-react';

function MyComponent() {
  return (
    <div className="p-6 space-y-6">
      <CozyCard variant="gradient">
        <h2 className="mb-4">Welcome Home</h2>
        <StatusBadge status="online" />
      </CozyCard>
      
      <QuickAction
        icon={<Lightbulb />}
        label="Toggle Lights"
        description="Living room"
        variant="primary"
        onClick={handleAction}
      />
    </div>
  );
}
```

## 🎯 Demo Modes

The dashboard includes three demo modes to showcase different states:

1. **Empty State**: Shows guidance for new users
2. **Active State**: Fully functioning dashboard with interactions
3. **Error State**: Demonstrates error handling and recovery

Switch between modes using the demo mode buttons in the dashboard.

---

Built with React, TypeScript, Tailwind CSS, and Lucide Icons
