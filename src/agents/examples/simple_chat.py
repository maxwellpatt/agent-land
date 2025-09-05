from typing import Optional

from pydantic_ai import RunContext

from ...core.base_agent import BaseAgent
from ...core.dependencies import ChatDependencies
from ...core.models import ChatResponse


class SimpleChatAgent(BaseAgent[ChatDependencies, ChatResponse]):
    def __init__(self, model: Optional[str] = None):
        instructions = """
        You are a helpful and friendly AI assistant. Engage in natural conversation with users.
        Be concise but informative. If you don't know something, say so honestly.
        Maintain context from the conversation history when available.
        """
        
        super().__init__(
            name="simple_chat",
            model=model,
            instructions=instructions,
            deps_type=ChatDependencies,
            output_type=ChatResponse,
        )
    
    def _register_tools(self) -> None:
        @self.agent.tool
        async def get_conversation_context(ctx: RunContext[ChatDependencies]) -> str:
            """Get recent conversation history for context"""
            history = ctx.deps.conversation_history[-5:] if ctx.deps else []
            if not history:
                return "No previous conversation history available"
            
            context = "Recent conversation:\n"
            for msg in history:
                context += f"- {msg.get('role', 'user')}: {msg.get('content', '')}\n"
            
            return context
        
        @self.agent.tool
        async def remember_message(ctx: RunContext[ChatDependencies], role: str, content: str) -> str:
            """Remember a message in the conversation history"""
            if not ctx.deps:
                return "No conversation context available"
            
            message = {"role": role, "content": content}
            ctx.deps.conversation_history.append(message)
            
            # Keep only recent messages
            if len(ctx.deps.conversation_history) > ctx.deps.max_history:
                ctx.deps.conversation_history = ctx.deps.conversation_history[-ctx.deps.max_history:]
            
            return f"Remembered {role} message in conversation history"


# Create a global instance for easy import
simple_chat_agent = SimpleChatAgent()