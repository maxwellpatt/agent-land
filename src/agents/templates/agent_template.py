from typing import Optional

from pydantic_ai import RunContext

from ...core.base_agent import BaseAgent
from ...core.dependencies import BaseDependencies
from ...core.models import AgentResult


class TemplateAgent(BaseAgent[BaseDependencies, AgentResult]):
    """
    Template for creating new agents. Copy this file and modify as needed.
    
    Steps to create a new agent:
    1. Copy this file with a new name
    2. Rename the class (TemplateAgent -> YourAgentName)
    3. Update the instructions to match your agent's purpose
    4. Choose appropriate dependencies and output types
    5. Implement your tools in _register_tools()
    6. Create a global instance at the bottom
    """
    
    def __init__(self, model: Optional[str] = None):
        instructions = """
        Replace this with instructions specific to your agent's role and capabilities.
        Be clear about what the agent should do, how it should behave, and what
        tools it has available.
        """
        
        super().__init__(
            name="template_agent",  # Change this to your agent's name
            model=model,
            instructions=instructions,
            deps_type=BaseDependencies,  # Change to appropriate dependency type
            output_type=AgentResult,     # Change to appropriate output type
        )
    
    def _register_tools(self) -> None:
        """Register tools specific to this agent"""
        
        @self.agent.tool
        async def example_tool(ctx: RunContext[BaseDependencies], param: str) -> str:
            """
            Example tool - replace with your actual tools.
            
            Args:
                ctx: Runtime context with dependencies
                param: Tool parameter
            
            Returns:
                Tool result as string
            """
            # Access dependencies if needed
            user_id = ctx.deps.user_id if ctx.deps else None
            
            # Implement your tool logic here
            result = f"Example tool executed with param: {param}"
            if user_id:
                result += f" for user: {user_id}"
            
            return result
        
        # Add more tools as needed
        # @self.agent.tool
        # async def another_tool(ctx: RunContext[BaseDependencies], ...):
        #     ...


# Create a global instance for easy import
# template_agent = TemplateAgent()