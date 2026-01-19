"""Conversation memory for maintaining chat history."""
from dataclasses import dataclass, field
from typing import Optional
from collections import deque
from datetime import datetime
import json

from app.providers.llm import Message


@dataclass
class ConversationMemory:
    """Manages conversation history with a sliding window."""
    
    max_messages: int = 20  # Keep last N messages
    messages: deque = field(default_factory=lambda: deque(maxlen=20))
    session_id: str = "default"
    created_at: datetime = field(default_factory=datetime.now)
    
    def add_user_message(self, content: str) -> None:
        """Add a user message to history."""
        self.messages.append(Message(role="user", content=content))
    
    def add_assistant_message(self, content: str) -> None:
        """Add an assistant message to history."""
        self.messages.append(Message(role="assistant", content=content))
    
    def add_tool_message(self, content: str, tool_call_id: str) -> None:
        """Add a tool result message."""
        self.messages.append(Message(
            role="tool",
            content=content,
            tool_call_id=tool_call_id
        ))
    
    def get_messages(self) -> list[Message]:
        """Get all messages in history."""
        return list(self.messages)
    
    def clear(self) -> None:
        """Clear conversation history."""
        self.messages.clear()
    
    def get_context_summary(self) -> str:
        """Get a summary of the conversation for context."""
        if not self.messages:
            return "No previous conversation."
        
        recent = list(self.messages)[-5:]  # Last 5 messages
        summary_lines = ["Recent conversation:"]
        for msg in recent:
            role = msg.role.capitalize()
            content = msg.content[:100] + "..." if len(msg.content) > 100 else msg.content
            summary_lines.append(f"  {role}: {content}")
        
        return "\n".join(summary_lines)


class MemoryStore:
    """In-memory store for multiple conversation sessions."""
    
    def __init__(self):
        self._sessions: dict[str, ConversationMemory] = {}
    
    def get_or_create(self, session_id: str = "default") -> ConversationMemory:
        """Get existing session or create new one."""
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationMemory(session_id=session_id)
        return self._sessions[session_id]
    
    def delete(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    def list_sessions(self) -> list[str]:
        """List all session IDs."""
        return list(self._sessions.keys())


# Global memory store
memory_store = MemoryStore()


def get_memory(session_id: str = "default") -> ConversationMemory:
    """Get conversation memory for a session."""
    return memory_store.get_or_create(session_id)
