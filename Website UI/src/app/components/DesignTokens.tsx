/**
 * DESIGN TOKENS & COMPONENT LIBRARY
 * Home Assistant AI Dashboard
 * 
 * This file documents the design system tokens and usage guidelines.
 */

/**
 * ═══════════════════════════════════════════════════════════════
 * COLOR PALETTE - Warm Pastels
 * ═══════════════════════════════════════════════════════════════
 * 
 * Primary (Warm Coral):
 *   - primary: #ff9b85
 *   - primary-light: #ffb5a3
 *   - primary-dark: #f48171
 *   Usage: Primary actions, branding, user messages
 * 
 * Secondary (Soft Lavender):
 *   - secondary: #d4c5f9
 *   - secondary-light: #e5dcfc
 *   - secondary-dark: #c0afe6
 *   Usage: Secondary actions, assistant branding, highlights
 * 
 * Accent (Soft Mint):
 *   - accent: #b8e6d5
 *   - accent-light: #d1f0e3
 *   - accent-dark: #a0d8c4
 *   Usage: Tertiary actions, accents, decorative elements
 * 
 * Info (Soft Sky Blue):
 *   - info: #a7d7f0
 *   Usage: Information states, processing indicators
 * 
 * Success (Soft Sage):
 *   - success: #c7e8b5
 *   Usage: Success states, positive feedback, online status
 * 
 * Warning (Soft Peach):
 *   - warning: #ffd89b
 *   Usage: Warning states, attention needed
 * 
 * Error (Soft Rose):
 *   - error: #ffb3ba
 *   Usage: Error states, critical alerts
 * 
 * Neutrals:
 *   - background: #fdfbf7 (warm off-white)
 *   - foreground: #4a4137 (warm dark brown)
 *   - muted: #f5f2ed (soft beige)
 *   - muted-foreground: #8a8378 (warm gray)
 *   - border: #e8e4dc (soft border)
 */

/**
 * ═══════════════════════════════════════════════════════════════
 * TYPOGRAPHY
 * ═══════════════════════════════════════════════════════════════
 * 
 * Font Families:
 *   - Primary (Headings): 'Outfit' - Friendly, expressive, rounded
 *   - Secondary (Body): 'DM Sans' - Clean, readable, professional
 * 
 * Font Weights:
 *   - Light: 300
 *   - Normal: 400
 *   - Medium: 500
 *   - Semibold: 600
 *   - Bold: 700
 * 
 * Type Scale:
 *   - h1: 2rem (32px) / Bold / Line-height: 1.3
 *   - h2: 1.5rem (24px) / Semibold / Line-height: 1.4
 *   - h3: 1.25rem (20px) / Semibold / Line-height: 1.4
 *   - h4: 1.125rem (18px) / Medium / Line-height: 1.5
 *   - Body: 1rem (16px) / Normal / Line-height: 1.6
 *   - Small: 0.875rem (14px) / Normal / Line-height: 1.5
 */

/**
 * ═══════════════════════════════════════════════════════════════
 * SPACING SCALE
 * ═══════════════════════════════════════════════════════════════
 * 
 * --spacing-xs: 0.25rem (4px)
 * --spacing-sm: 0.5rem (8px)
 * --spacing-md: 1rem (16px) - Base unit
 * --spacing-lg: 1.5rem (24px)
 * --spacing-xl: 2rem (32px)
 * --spacing-2xl: 3rem (48px)
 * --spacing-3xl: 4rem (64px)
 * 
 * Usage Guidelines:
 * - Use generous spacing for a calm, uncluttered feel
 * - Minimum touch target: 44px (2.75rem)
 * - Card padding: 1.5rem (24px)
 * - Section gaps: 1.5rem - 2rem
 */

/**
 * ═══════════════════════════════════════════════════════════════
 * BORDER RADIUS
 * ═══════════════════════════════════════════════════════════════
 * 
 * --radius-sm: 0.5rem (8px) - Small elements
 * --radius-md: 0.75rem (12px) - Medium elements
 * --radius-lg: 1rem (16px) - Cards, buttons (default)
 * --radius-xl: 1.5rem (24px) - Large cards
 * --radius-2xl: 2rem (32px) - Chat bubbles
 * 
 * Usage: Soft, rounded corners throughout for cozy feel
 */

/**
 * ═══════════════════════════════════════════════════════════════
 * SHADOWS - Soft Depth
 * ═══════════════════════════════════════════════════════════════
 * 
 * --shadow-xs: Subtle, barely visible
 * --shadow-sm: Small elements (badges, small buttons)
 * --shadow-md: Cards, buttons (default)
 * --shadow-lg: Elevated cards, modals
 * --shadow-xl: Floating panels, dropdowns
 * 
 * All shadows use very low opacity (3-8%) for soft, gentle depth
 */

/**
 * ═══════════════════════════════════════════════════════════════
 * COMPONENT LIBRARY
 * ═══════════════════════════════════════════════════════════════
 * 
 * COZYCARD
 * --------
 * Purpose: Primary container component with soft shadows and rounded corners
 * Variants:
 *   - default: Solid background with border
 *   - gradient: Subtle gradient background
 *   - outlined: Transparent with thicker border
 * Props:
 *   - hoverable: Adds lift effect on hover
 * 
 * Example:
 *   <CozyCard variant="gradient" hoverable>
 *     Content here
 *   </CozyCard>
 * 
 * 
 * STATUSBADGE
 * -----------
 * Purpose: Display system or device status
 * States: online, offline, error, idle, processing
 * Features:
 *   - Animated dot for active states
 *   - Color-coded backgrounds
 *   - Optional custom label
 * 
 * Example:
 *   <StatusBadge status="online" />
 *   <StatusBadge status="error" label="Connection Lost" />
 * 
 * 
 * QUICKACTION
 * -----------
 * Purpose: Large, friendly action buttons
 * Variants: primary, secondary, accent, info
 * Features:
 *   - Icon support
 *   - Optional description text
 *   - Scale animation on hover
 *   - Disabled state
 * 
 * Example:
 *   <QuickAction
 *     icon={<Lightbulb />}
 *     label="Toggle Lights"
 *     description="Living room"
 *     variant="primary"
 *     onClick={handleClick}
 *   />
 * 
 * 
 * CHATMESSAGE
 * -----------
 * Purpose: Display chat messages with visual distinction
 * Roles: user, assistant
 * Features:
 *   - Avatar display
 *   - Timestamp
 *   - Status indicators (sending, sent, error)
 *   - Smooth animations
 *   - Responsive bubble width
 * 
 * Example:
 *   <ChatMessage
 *     role="assistant"
 *     content="Hello! How can I help?"
 *     timestamp="10:30 AM"
 *     status="sent"
 *   />
 * 
 * 
 * EMPTYSTATE
 * ----------
 * Purpose: Friendly empty state displays
 * Features:
 *   - Large icon
 *   - Title and description
 *   - Optional action button
 * 
 * Example:
 *   <EmptyState
 *     icon={<MessageSquare />}
 *     title="No messages yet"
 *     description="Start a conversation"
 *     action={<button>Get Started</button>}
 *   />
 * 
 * 
 * LOADINGSPINNER
 * --------------
 * Purpose: Loading indicators
 * Sizes: sm, md, lg
 * Features:
 *   - Smooth animation
 *   - Optional label
 *   - Primary color
 * 
 * Example:
 *   <LoadingSpinner size="md" label="Loading..." />
 * 
 * 
 * INSIGHTSPANEL
 * -------------
 * Purpose: Collapsible side panel for insights and logs
 * Features:
 *   - Smooth slide animation
 *   - Mobile overlay
 *   - Activity logs
 *   - System health metrics
 *   - Statistics cards
 * 
 * Example:
 *   <InsightsPanel
 *     isOpen={isPanelOpen}
 *     onToggle={() => setIsPanelOpen(!isPanelOpen)}
 *   />
 */

/**
 * ═══════════════════════════════════════════════════════════════
 * INTERACTION PATTERNS
 * ═══════════════════════════════════════════════════════════════
 * 
 * LOADING STATES:
 * ---------------
 * - Use LoadingSpinner for async operations
 * - Show inline spinners in chat for AI responses
 * - Disable inputs during loading
 * - Display "Thinking..." or similar friendly text
 * 
 * Example:
 *   {isLoading ? (
 *     <LoadingSpinner size="md" label="Processing..." />
 *   ) : (
 *     <Content />
 *   )}
 * 
 * 
 * SUCCESS FEEDBACK:
 * -----------------
 * - Use success color (#c7e8b5)
 * - Show checkmark icon
 * - Add subtle animation
 * - Display success message in chat or toast
 * 
 * Example:
 *   <StatusBadge status="online" label="Connected" />
 *   <div className="text-success">✓ Action completed</div>
 * 
 * 
 * ERROR HANDLING:
 * ---------------
 * - Use error color (#ffb3ba)
 * - Show alert icon
 * - Provide clear error message
 * - Offer retry action when appropriate
 * - Don't hide the interface - show error state
 * 
 * Example:
 *   <EmptyState
 *     icon={<AlertCircle />}
 *     title="Connection Lost"
 *     description="Check your network connection"
 *     action={<button onClick={retry}>Retry</button>}
 *   />
 * 
 * 
 * HOVER STATES:
 * -------------
 * - Subtle scale transforms (scale-105)
 * - Background color changes
 * - Shadow elevation
 * - Smooth transitions (300ms)
 * 
 * Example CSS classes:
 *   hover:scale-105 hover:shadow-lg transition-all duration-300
 * 
 * 
 * FOCUS STATES:
 * -------------
 * - 2px ring in primary color
 * - 50% opacity for soft appearance
 * - Visible on keyboard navigation
 * 
 * Example CSS classes:
 *   focus:outline-none focus:ring-2 focus:ring-primary/50
 * 
 * 
 * DISABLED STATES:
 * ----------------
 * - 50% opacity
 * - No pointer cursor
 * - No hover effects
 * - Clear visual distinction
 * 
 * Example CSS classes:
 *   disabled:opacity-50 disabled:cursor-not-allowed
 */

/**
 * ═══════════════════════════════════════════════════════════════
 * ANIMATION GUIDELINES
 * ═══════════════════════════════════════════════════════════════
 * 
 * Duration:
 *   - Micro-interactions: 150ms (quick feedback)
 *   - Standard: 300ms (most transitions)
 *   - Complex: 500ms (page transitions)
 * 
 * Easing:
 *   - Default: ease-in-out
 *   - Entry: ease-out
 *   - Exit: ease-in
 * 
 * Types:
 *   - Fade: opacity transitions
 *   - Slide: translate transforms
 *   - Scale: size transforms for hover
 *   - Spin: loading indicators
 * 
 * Usage:
 *   - Keep animations subtle and purposeful
 *   - Don't overuse - can feel distracting
 *   - Ensure accessibility (respect prefers-reduced-motion)
 */

/**
 * ═══════════════════════════════════════════════════════════════
 * RESPONSIVE BREAKPOINTS
 * ═══════════════════════════════════════════════════════════════
 * 
 * Mobile: < 640px
 *   - Single column layout
 *   - Stacked quick actions
 *   - Full-width chat
 *   - Overlay side panel
 * 
 * Tablet: 640px - 1024px
 *   - Two column layout
 *   - Side-by-side content
 *   - Collapsible side panel
 * 
 * Desktop: > 1024px
 *   - Three column layout
 *   - Persistent side panel toggle
 *   - Maximum content width
 *   - Generous spacing
 * 
 * Tailwind Breakpoints:
 *   - sm: 640px
 *   - md: 768px
 *   - lg: 1024px
 *   - xl: 1280px
 */

/**
 * ═══════════════════════════════════════════════════════════════
 * ACCESSIBILITY NOTES
 * ═══════════════════════════════════════════════════════════════
 * 
 * - All interactive elements have min 44px touch target
 * - Color contrast meets WCAG AA standards (4.5:1)
 * - Focus indicators visible for keyboard navigation
 * - ARIA labels on icon-only buttons
 * - Semantic HTML structure
 * - Screen reader friendly
 * - Reduced motion support via CSS
 */

// This is a documentation-only file
export {};
