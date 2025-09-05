#!/usr/bin/env python3
"""
Basic usage examples for agent-land.

This script demonstrates the core functionality of the Pydantic AI agents
and shows how to use them in simple scenarios.
"""

import asyncio
import os
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.examples.simple_chat import simple_chat_agent
from src.agents.examples.research_agent import research_agent
from src.agents.examples.data_analyst import data_analyst_agent
from src.core.dependencies import ChatDependencies, ResearchDependencies, DataDependencies
from src.config.logging import logger
from src.utils.helpers import generate_session_id


async def basic_chat_example():
    """Demonstrate basic chat functionality"""
    print("\n🤖 Basic Chat Example")
    print("=" * 50)
    
    # Create dependencies with conversation history
    deps = ChatDependencies(
        user_id="demo_user",
        session_id=generate_session_id(),
        conversation_history=[]
    )
    
    # Simple conversation
    questions = [
        "Hello! What can you help me with?",
        "What's the weather like in general?",
        "Can you tell me a fun fact about artificial intelligence?"
    ]
    
    for question in questions:
        print(f"\n👤 User: {question}")
        try:
            response = await simple_chat_agent.run(question, deps)
            print(f"🤖 Agent: {response.message}")
            
            # Add to conversation history for context
            deps.conversation_history.append({"role": "user", "content": question})
            deps.conversation_history.append({"role": "assistant", "content": response.message})
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n📊 Conversation history has {len(deps.conversation_history)} messages")


async def research_example():
    """Demonstrate research agent functionality"""
    print("\n🔍 Research Agent Example")
    print("=" * 50)
    
    # Create research dependencies
    deps = ResearchDependencies(
        user_id="demo_user",
        session_id=generate_session_id(),
        search_enabled=True,
        max_results=5
    )
    
    research_query = "What are the latest trends in artificial intelligence?"
    
    print(f"\n📝 Research Query: {research_query}")
    
    try:
        result = await research_agent.run(
            f"Research the following topic and provide a comprehensive summary: {research_query}",
            deps
        )
        
        print(f"\n📋 Research Results:")
        print(f"Query: {result.query}")
        print(f"\nFindings:")
        for i, finding in enumerate(result.findings, 1):
            print(f"  {i}. {finding}")
        
        if result.sources:
            print(f"\nSources:")
            for i, source in enumerate(result.sources, 1):
                print(f"  {i}. {source}")
        
        if result.confidence:
            print(f"\nConfidence Level: {result.confidence:.2f}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def data_analysis_example():
    """Demonstrate data analyst agent functionality"""
    print("\n📊 Data Analyst Example")
    print("=" * 50)
    
    # Create data dependencies
    deps = DataDependencies(
        user_id="demo_user",
        session_id=generate_session_id(),
        data_path="/path/to/data",  # Mock path
        allowed_formats=["csv", "json"]
    )
    
    analysis_request = """
    Analyze sales data to identify trends and provide business insights.
    Focus on seasonal patterns, product performance, and growth opportunities.
    """
    
    print(f"📝 Analysis Request: {analysis_request.strip()}")
    
    try:
        result = await data_analyst_agent.run(analysis_request, deps)
        
        print(f"\n📈 Analysis Results:")
        print(f"Analysis: {result.analysis}")
        
        if result.insights:
            print(f"\n💡 Key Insights:")
            for i, insight in enumerate(result.insights, 1):
                print(f"  {i}. {insight}")
        
        if result.recommendations:
            print(f"\n🎯 Recommendations:")
            for i, rec in enumerate(result.recommendations, 1):
                print(f"  {i}. {rec}")
        
        if result.data_summary:
            print(f"\n📊 Data Summary: {result.data_summary}")
            
    except Exception as e:
        print(f"❌ Error: {e}")


async def agent_info_example():
    """Display information about all agents"""
    print("\n📋 Agent Information")
    print("=" * 50)
    
    agents = [
        ("Simple Chat", simple_chat_agent),
        ("Research", research_agent),
        ("Data Analyst", data_analyst_agent)
    ]
    
    for name, agent in agents:
        info = agent.get_info()
        print(f"\n🤖 {name} Agent:")
        print(f"  Name: {info['name']}")
        print(f"  Model: {info['model']}")
        print(f"  Dependencies: {info['deps_type']}")
        print(f"  Output Type: {info['output_type']}")


async def main():
    """Run all examples"""
    print("🚀 Agent-Land Basic Usage Examples")
    print("=" * 50)
    
    # Check if we have API keys configured
    from src.config.settings import settings
    
    if not any([settings.openai_api_key, settings.anthropic_api_key]):
        print("\n⚠️  Warning: No API keys configured!")
        print("Please set up your .env file with API keys to run the agents.")
        print("See .env.example for the required format.")
        print("\nFor now, we'll show the agent information and structure:")
        
        await agent_info_example()
        return
    
    try:
        # Run all examples
        await agent_info_example()
        await basic_chat_example()
        await research_example()
        await data_analysis_example()
        
        print("\n✅ All examples completed successfully!")
        
    except Exception as e:
        logger.error(f"Error running examples: {e}")
        print(f"\n❌ Error running examples: {e}")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())