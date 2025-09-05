import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from ..config.logging import logger
from ..config.settings import settings
from .dependencies import BaseDependencies
from .models import AgentResult, ToolResult

T = TypeVar("T", bound=BaseDependencies)
R = TypeVar("R", bound=BaseModel)


class BaseAgent(Generic[T, R], ABC):
    def __init__(
        self,
        name: str,
        model: Optional[str] = None,
        instructions: Optional[str] = None,
        deps_type: Optional[Type[T]] = None,
        output_type: Optional[Type[R]] = None,
        **kwargs,
    ):
        self.name = name
        self.model = model or settings.default_model
        self.instructions = instructions
        self.deps_type = deps_type
        self.output_type = output_type

        # Initialize Pydantic AI agent
        self.agent = Agent(
            self.model,
            deps_type=self.deps_type,
            output_type=self.output_type,
            instructions=self.instructions,
            **kwargs,
        )

        self._register_tools()

        logger.info(f"Initialized agent '{self.name}' with model '{self.model}'")

    @abstractmethod
    def _register_tools(self) -> None:
        """Register tools specific to this agent"""
        pass

    async def run(
        self,
        prompt: str,
        dependencies: Optional[T] = None,
        **kwargs,
    ) -> Union[R, AgentResult]:
        """Run the agent with the given prompt and dependencies"""
        logger.info(f"Running agent '{self.name}' with prompt: {prompt[:100]}...")

        try:
            if dependencies:
                result = await self.agent.run(prompt, deps=dependencies, **kwargs)
            else:
                result = await self.agent.run(prompt, **kwargs)

            logger.info(f"Agent '{self.name}' completed successfully")
            return result.output if hasattr(result, "output") else result

        except Exception as e:
            logger.error(f"Agent '{self.name}' failed: {str(e)}")
            if self.output_type:
                return self.output_type()
            raise

    def run_sync(
        self,
        prompt: str,
        dependencies: Optional[T] = None,
        **kwargs,
    ) -> Union[R, AgentResult]:
        """Synchronous wrapper for run method"""
        return asyncio.run(self.run(prompt, dependencies, **kwargs))

    async def stream(
        self,
        prompt: str,
        dependencies: Optional[T] = None,
        **kwargs,
    ):
        """Stream responses from the agent"""
        logger.info(f"Streaming from agent '{self.name}'")

        try:
            if dependencies:
                async with self.agent.run_stream(
                    prompt, deps=dependencies, **kwargs
                ) as stream:
                    async for message in stream:
                        yield message
            else:
                async with self.agent.run_stream(prompt, **kwargs) as stream:
                    async for message in stream:
                        yield message

        except Exception as e:
            logger.error(f"Streaming failed for agent '{self.name}': {str(e)}")
            raise

    def add_tool(self, func: callable, name: Optional[str] = None):
        """Add a tool to the agent"""
        tool_name = name or func.__name__
        self.agent.tool(func)
        logger.info(f"Added tool '{tool_name}' to agent '{self.name}'")

    def get_info(self) -> Dict[str, Any]:
        """Get information about the agent"""
        return {
            "name": self.name,
            "model": self.model,
            "instructions": self.instructions,
            "deps_type": self.deps_type.__name__ if self.deps_type else None,
            "output_type": self.output_type.__name__ if self.output_type else None,
        }
