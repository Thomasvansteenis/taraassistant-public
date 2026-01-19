import { useState } from 'react';
import { CozyCard } from './components/CozyCard';
import { StatusBadge } from './components/StatusBadge';
import { QuickAction } from './components/QuickAction';
import { ChatMessage } from './components/ChatMessage';
import { EmptyState } from './components/EmptyState';
import { LoadingSpinner } from './components/LoadingSpinner';
import { InsightsPanel } from './components/InsightsPanel';
import { 
  House, 
  Lightbulb, 
  Thermometer, 
  Lock, 
  Music, 
  Send, 
  Menu,
  MessageSquare,
  Sparkles,
  CircleAlert
} from 'lucide-react';

type ViewMode = 'empty' | 'active' | 'error';
type ChatState = 'idle' | 'loading' | 'error';

export default function App() {
  const [viewMode, setViewMode] = useState<ViewMode>('active');
  const [chatState, setChatState] = useState<ChatState>('idle');
  const [isPanelOpen, setIsPanelOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: '1',
      role: 'assistant' as const,
      content: "Hello! I'm your home assistant. How can I help you today?",
      timestamp: '10:30 AM'
    }
  ]);
  const [inputValue, setInputValue] = useState('');

  const handleSendMessage = () => {
    if (!inputValue.trim()) return;

    // Add user message
    const userMessage = {
      id: Date.now().toString(),
      role: 'user' as const,
      content: inputValue,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages([...messages, userMessage]);
    setInputValue('');
    setChatState('loading');

    // Simulate AI response
    setTimeout(() => {
      const responses = [
        "I've adjusted the temperature to your preferred setting.",
        "The lights in the living room have been turned on.",
        "I've started playing your favorite playlist.",
        "Your front door is now locked.",
        "The coffee maker will start brewing in 5 minutes."
      ];
      const response = {
        id: (Date.now() + 1).toString(),
        role: 'assistant' as const,
        content: responses[Math.floor(Math.random() * responses.length)],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages(prev => [...prev, response]);
      setChatState('idle');
    }, 1500);
  };

  const handleQuickAction = (action: string) => {
    const actionMessage = {
      id: Date.now().toString(),
      role: 'assistant' as const,
      content: `${action} completed successfully!`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };
    setMessages([...messages, actionMessage]);
  };

  return (
    <div className="min-h-screen flex flex-col lg:flex-row">
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Status Bar */}
        <header className="sticky top-0 z-30 bg-background/80 backdrop-blur-lg border-b border-border">
          <div className="px-4 md:px-8 py-4 flex items-center justify-between gap-4">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-xl flex items-center justify-center shadow-md">
                  <House className="w-5 h-5 text-white" />
                </div>
                <div className="hidden sm:block">
                  <h1 className="leading-none mb-0.5">Home Assistant</h1>
                  <p className="text-sm text-muted-foreground">Welcome back, Alex</p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <StatusBadge status={viewMode === 'error' ? 'error' : 'online'} />
              <button
                onClick={() => setIsPanelOpen(!isPanelOpen)}
                className="lg:hidden p-2 hover:bg-muted rounded-lg transition-colors"
              >
                <Menu className="w-5 h-5" />
              </button>
            </div>
          </div>
        </header>

        {/* Demo Mode Switcher */}
        <div className="px-4 md:px-8 py-4 bg-muted/30">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-sm text-muted-foreground">Demo Mode:</span>
            <button
              onClick={() => setViewMode('empty')}
              className={`px-3 py-1 rounded-lg text-sm transition-all ${
                viewMode === 'empty' 
                  ? 'bg-primary text-primary-foreground shadow-sm' 
                  : 'bg-card hover:bg-muted border border-border'
              }`}
            >
              Empty State
            </button>
            <button
              onClick={() => setViewMode('active')}
              className={`px-3 py-1 rounded-lg text-sm transition-all ${
                viewMode === 'active' 
                  ? 'bg-primary text-primary-foreground shadow-sm' 
                  : 'bg-card hover:bg-muted border border-border'
              }`}
            >
              Active State
            </button>
            <button
              onClick={() => setViewMode('error')}
              className={`px-3 py-1 rounded-lg text-sm transition-all ${
                viewMode === 'error' 
                  ? 'bg-primary text-primary-foreground shadow-sm' 
                  : 'bg-card hover:bg-muted border border-border'
              }`}
            >
              Error State
            </button>
          </div>
        </div>

        {/* Main Content */}
        <main className="flex-1 overflow-hidden">
          <div className="h-full flex flex-col gap-6 p-4 md:p-8">
            {/* Chat Panel - Now First */}
            <div className="w-full">
              <CozyCard className="flex flex-col p-6">
                <div className="flex items-center gap-3 mb-4 pb-4 border-b border-border">
                  <div className="w-10 h-10 bg-gradient-to-br from-secondary to-accent rounded-full flex items-center justify-center">
                    <Sparkles className="w-5 h-5 text-secondary-foreground" />
                  </div>
                  <div>
                    <h3 className="leading-none mb-1">AI Assistant</h3>
                    <p className="text-sm text-muted-foreground">
                      {chatState === 'loading' ? 'Thinking...' : 'Ready to help'}
                    </p>
                  </div>
                </div>

                {/* Input Area - Now at Top */}
                {viewMode !== 'error' && (
                  <div className="flex gap-3 mb-4">
                    <input
                      type="text"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                      placeholder="Ask me anything..."
                      disabled={chatState === 'loading'}
                      className="flex-1 px-4 py-3 bg-input-background rounded-xl border border-border focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all disabled:opacity-50"
                    />
                    <button
                      onClick={handleSendMessage}
                      disabled={!inputValue.trim() || chatState === 'loading'}
                      className="px-6 py-3 bg-primary text-primary-foreground rounded-xl hover:bg-primary-dark disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:scale-105 active:scale-95 shadow-md"
                    >
                      <Send className="w-5 h-5" />
                    </button>
                  </div>
                )}

                {/* Messages Area - Below Input */}
                <div className="overflow-y-auto max-h-[300px] -mx-2 px-2 pt-4 border-t border-border">
                  {viewMode === 'empty' ? (
                    <EmptyState
                      icon={<MessageSquare />}
                      title="Start a Conversation"
                      description="Ask me to control your devices, check status, or answer questions about your home."
                      action={
                        <button 
                          className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary-dark transition-all hover:scale-105 shadow-md"
                          onClick={() => {
                            setInputValue('Turn on the living room lights');
                            setViewMode('active');
                          }}
                        >
                          Try an example
                        </button>
                      }
                    />
                  ) : viewMode === 'error' ? (
                    <EmptyState
                      icon={<CircleAlert />}
                      title="Connection Lost"
                      description="We're having trouble connecting to the AI assistant. Your devices are still controllable via quick actions."
                      action={
                        <button 
                          className="px-6 py-3 bg-primary text-primary-foreground rounded-lg hover:bg-primary-dark transition-all hover:scale-105 shadow-md"
                          onClick={() => setChatState('idle')}
                        >
                          Retry Connection
                        </button>
                      }
                    />
                  ) : (
                    <>
                      {messages.map((message) => (
                        <ChatMessage
                          key={message.id}
                          role={message.role}
                          content={message.content}
                          timestamp={message.timestamp}
                        />
                      ))}
                      {chatState === 'loading' && (
                        <div className="flex justify-center py-4">
                          <LoadingSpinner size="md" />
                        </div>
                      )}
                    </>
                  )}
                </div>
              </CozyCard>
            </div>

            {/* Quick Actions & Device Status - Now Below Chat */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="md:col-span-2 lg:col-span-3 space-y-3">
                <h2>Quick Actions</h2>
                
                {viewMode === 'error' ? (
                  <CozyCard className="p-6">
                    <div className="flex flex-col items-center text-center gap-3">
                      <div className="w-12 h-12 bg-error/10 rounded-full flex items-center justify-center">
                        <CircleAlert className="w-6 h-6 text-error" />
                      </div>
                      <div>
                        <h4 className="mb-1">Connection Error</h4>
                        <p className="text-sm text-muted-foreground">
                          Unable to connect to home devices. Check your network connection.
                        </p>
                      </div>
                      <button className="mt-2 px-4 py-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary-dark transition-colors">
                        Retry Connection
                      </button>
                    </div>
                  </CozyCard>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <QuickAction
                      icon={<Lightbulb />}
                      label="Toggle Lights"
                      description="Living room"
                      variant="primary"
                      onClick={() => handleQuickAction('Toggle lights')}
                    />
                    <QuickAction
                      icon={<Thermometer />}
                      label="Adjust Temperature"
                      description="Currently 72°F"
                      variant="secondary"
                      onClick={() => handleQuickAction('Temperature adjusted')}
                    />
                    <QuickAction
                      icon={<Lock />}
                      label="Lock Doors"
                      description="Secure all entries"
                      variant="accent"
                      onClick={() => handleQuickAction('All doors locked')}
                    />
                    <QuickAction
                      icon={<Music />}
                      label="Play Music"
                      description="Your favorites"
                      variant="info"
                      onClick={() => handleQuickAction('Music playing')}
                    />
                  </div>
                )}
              </div>

              {/* Device Status Cards */}
              <div className="space-y-3">
                <h3>Device Status</h3>
                <CozyCard variant="gradient" className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">Smart Devices</span>
                    <StatusBadge status="online" showDot={false} label="24/24" />
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div className="h-full bg-success w-full rounded-full" />
                  </div>
                </CozyCard>
                
                <CozyCard variant="gradient" className="p-4">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm">Energy Usage</span>
                    <span className="text-sm text-muted-foreground">2.4 kW</span>
                  </div>
                  <div className="h-2 bg-muted rounded-full overflow-hidden">
                    <div className="h-full bg-warning w-[60%] rounded-full" />
                  </div>
                </CozyCard>
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* Insights Panel */}
      <InsightsPanel isOpen={isPanelOpen} onToggle={() => setIsPanelOpen(!isPanelOpen)} />
    </div>
  );
}