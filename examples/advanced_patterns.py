#!/usr/bin/env python3
"""
Advanced patterns and usage examples for agent-land.

This script demonstrates more sophisticated usage patterns including:
- Agent chaining and composition
- Custom tool integration
- Streaming responses
- Error handling and retry logic
"""

import asyncio
import json
from pathlib import Path
from typing import List, Dict, Any

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.examples.simple_chat import simple_chat_agent
from src.agents.examples.research_agent import research_agent
from src.agents.examples.data_analyst import data_analyst_agent
from src.core.dependencies import ChatDependencies, ResearchDependencies, DataDependencies
from src.core.base_agent import BaseAgent
from src.core.models import BaseResponse
from src.config.logging import logger
from src.utils.helpers import generate_session_id, retry_async, RetryConfig
from src.utils.logger import get_contextual_logger


async def agent_chaining_example():
    """Demonstrate chaining multiple agents together"""
    print("\n🔗 Agent Chaining Example")
    print("=" * 50)
    
    # Step 1: Research agent gathers information
    research_deps = ResearchDependencies(
        session_id=generate_session_id(),
        search_enabled=True
    )
    
    topic = "sustainable energy technologies"
    print(f"📋 Researching: {topic}")
    
    try:
        research_result = await research_agent.run(
            f"Research current trends and developments in {topic}",
            research_deps
        )
        
        print(f"✅ Research completed with {len(research_result.findings)} findings")
        
        # Step 2: Data analyst processes the research findings
        data_deps = DataDependencies(
            session_id=research_deps.session_id  # Same session
        )
        
        # Convert research findings to a format for analysis
        research_data = {
            "topic": topic,
            "findings": research_result.findings,
            "sources": research_result.sources
        }
        
        analysis_prompt = f"""
        Analyze the following research data and provide strategic insights:
        {json.dumps(research_data, indent=2)}
        
        Focus on identifying patterns, opportunities, and actionable recommendations.
        """
        
        analysis_result = await data_analyst_agent.run(analysis_prompt, data_deps)
        
        print(f"✅ Analysis completed")
        
        # Step 3: Chat agent summarizes everything for the user
        chat_deps = ChatDependencies(
            session_id=research_deps.session_id  # Same session
        )
        
        summary_prompt = f"""
        Create a comprehensive summary based on this research and analysis:
        
        Research Topic: {topic}
        Key Findings: {', '.join(research_result.findings[:3])}
        Analysis: {analysis_result.analysis}
        Top Insights: {', '.join(analysis_result.insights[:2]) if analysis_result.insights else 'None'}
        
        Provide a clear, actionable summary for business decision-makers.
        """
        
        summary_result = await simple_chat_agent.run(summary_prompt, chat_deps)
        
        print(f"\n📄 Final Summary:")
        print(f"{summary_result.message}")
        
    except Exception as e:
        print(f"❌ Error in agent chaining: {e}")


async def streaming_example():
    """Demonstrate streaming responses from agents"""
    print("\n🌊 Streaming Example")
    print("=" * 50)
    
    deps = ChatDependencies(session_id=generate_session_id())
    
    prompt = "Tell me a detailed story about the future of artificial intelligence, including potential benefits and challenges."
    
    print(f"📝 Streaming response for: {prompt[:50]}...")
    print("\n🤖 Agent response (streaming):")
    
    try:
        async for chunk in simple_chat_agent.stream(prompt, deps):
            # In a real streaming implementation, this would show incremental responses
            print(".", end="", flush=True)  # Show progress
        
        print("\n✅ Streaming completed")
        
    except Exception as e:
        print(f"\n❌ Streaming error: {e}")


async def retry_logic_example():
    """Demonstrate retry logic for agent operations"""
    print("\n🔄 Retry Logic Example")
    print("=" * 50)
    
    contextual_logger = get_contextual_logger("RetryExample")
    
    async def unreliable_agent_call():
        """Simulate an unreliable agent call"""
        import random
        if random.random() < 0.7:  # 70% chance of failure for demo
            raise Exception("Simulated API failure")
        
        return await simple_chat_agent.run(
            "What is the meaning of life?",
            ChatDependencies(session_id=generate_session_id())
        )
    
    # Configure retry behavior
    retry_config = RetryConfig(
        max_attempts=3,
        delay=1.0,
        backoff_factor=2.0
    )
    
    contextual_logger.info("Starting unreliable agent call with retry logic")
    
    try:
        result = await retry_async(unreliable_agent_call, config=retry_config)
        contextual_logger.info("Agent call succeeded!")
        print(f"✅ Success after retries: {result.message[:100]}...")
        
    except Exception as e:
        contextual_logger.error(f"Agent call failed after all retries: {e}")
        print(f"❌ Failed after all retries: {e}")


async def custom_tool_integration():
    """Demonstrate adding custom tools to existing agents"""
    print("\n🔧 Custom Tool Integration")
    print("=" * 50)
    
    # Create a custom tool function
    async def calculate_compound_interest(principal: float, rate: float, time: int) -> str:
        """Calculate compound interest"""
        amount = principal * (1 + rate) ** time
        interest = amount - principal
        return f"Principal: ${principal:.2f}, Rate: {rate:.1%}, Time: {time} years, Interest: ${interest:.2f}, Total: ${amount:.2f}"
    
    # Add the custom tool to the chat agent
    simple_chat_agent.add_tool(calculate_compound_interest, "compound_interest_calculator")
    
    # Test the agent with the new tool
    deps = ChatDependencies(session_id=generate_session_id())
    
    prompt = "Calculate the compound interest for $10,000 invested at 5% annual interest for 10 years."
    
    print(f"📝 Testing custom tool with: {prompt}")
    
    try:
        result = await simple_chat_agent.run(prompt, deps)
        print(f"🤖 Agent with custom tool: {result.message}")
        
    except Exception as e:
        print(f"❌ Custom tool error: {e}")


async def parallel_agent_execution():
    """Demonstrate running multiple agents in parallel"""
    print("\n⚡ Parallel Agent Execution")
    print("=" * 50)
    
    # Create different tasks for different agents
    tasks = [
        (simple_chat_agent, "What are the benefits of renewable energy?", ChatDependencies()),
        (research_agent, "Find information about electric vehicle adoption rates", ResearchDependencies()),
        (data_analyst_agent, "Analyze trends in green technology investment", DataDependencies())
    ]
    
    print("🚀 Starting parallel agent execution...")
    
    async def run_agent_task(agent, prompt, deps):
        """Run a single agent task"""
        task_logger = get_contextual_logger(f"Task-{agent.name}")
        task_logger.info(f"Starting: {prompt[:50]}...")
        
        try:
            result = await agent.run(prompt, deps)
            task_logger.info("Completed successfully")
            return agent.name, result, None
        except Exception as e:
            task_logger.error(f"Failed: {e}")
            return agent.name, None, e
    
    # Run all tasks concurrently
    try:
        results = await asyncio.gather(
            *[run_agent_task(agent, prompt, deps) for agent, prompt, deps in tasks],
            return_exceptions=True
        )
        
        print("\n📊 Parallel Execution Results:")
        for agent_name, result, error in results:
            if error:
                print(f"❌ {agent_name}: Failed - {error}")
            else:
                response_preview = str(result)[:100] + "..." if len(str(result)) > 100 else str(result)
                print(f"✅ {agent_name}: {response_preview}")
                
    except Exception as e:
        print(f"❌ Parallel execution error: {e}")


class MetaAgent(BaseAgent):
    """An agent that coordinates other agents"""
    
    def __init__(self):
        super().__init__(
            name="meta_agent",
            instructions="You coordinate other AI agents to solve complex tasks."
        )
        
        # Store references to other agents
        self.available_agents = {
            "chat": simple_chat_agent,
            "research": research_agent,
            "analysis": data_analyst_agent
        }
    
    def _register_tools(self):
        # Meta-agent doesn't need specific tools in this example
        pass
    
    async def coordinate_agents(self, task: str) -> Dict[str, Any]:
        """Coordinate multiple agents to solve a complex task"""
        logger.info(f"Meta-agent coordinating task: {task}")
        
        results = {}
        
        # Simple coordination logic (can be made more sophisticated)
        if "research" in task.lower():
            results["research"] = await self.available_agents["research"].run(
                task, ResearchDependencies()
            )
        
        if "analyze" in task.lower() or "analysis" in task.lower():
            results["analysis"] = await self.available_agents["analysis"].run(
                task, DataDependencies()
            )
        
        # Always provide a summary
        summary_prompt = f"Summarize the results of this multi-agent task: {task}\nResults: {results}"
        results["summary"] = await self.available_agents["chat"].run(
            summary_prompt, ChatDependencies()
        )
        
        return results


async def meta_agent_example():
    """Demonstrate meta-agent coordination"""
    print("\n🎯 Meta-Agent Coordination")
    print("=" * 50)
    
    meta_agent = MetaAgent()
    
    complex_task = "Research and analyze the impact of artificial intelligence on job markets"
    
    print(f"📋 Complex Task: {complex_task}")
    print("🤖 Meta-agent coordinating sub-agents...")
    
    try:
        results = await meta_agent.coordinate_agents(complex_task)
        
        print("\n📊 Coordination Results:")
        for agent_type, result in results.items():
            print(f"\n🎯 {agent_type.upper()} Agent Result:")
            result_preview = str(result)[:200] + "..." if len(str(result)) > 200 else str(result)
            print(f"   {result_preview}")
            
    except Exception as e:
        print(f"❌ Meta-agent coordination error: {e}")


async def main():
    """Run all advanced examples"""
    print("🚀 Agent-Land Advanced Patterns Examples")
    print("=" * 50)
    
    # Check if we have API keys configured
    from src.config.settings import settings
    
    if not any([settings.openai_api_key, settings.anthropic_api_key]):
        print("\n⚠️  Warning: No API keys configured!")
        print("Please set up your .env file with API keys to run these advanced examples.")
        print("See .env.example for the required format.")
        return
    
    try:
        # Run advanced examples
        await agent_chaining_example()
        await streaming_example()
        await retry_logic_example()
        await custom_tool_integration()
        await parallel_agent_execution()
        await meta_agent_example()
        
        print("\n✅ All advanced examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Error running advanced examples: {e}")
        print(f"\n❌ Error running advanced examples: {e}")


if __name__ == "__main__":
    asyncio.run(main())