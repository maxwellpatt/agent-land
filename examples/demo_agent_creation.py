#!/usr/bin/env python3
"""
Demo: Agent Creation in Playground

This script demonstrates how to create agents programmatically and shows
what the interactive creation process looks like.
"""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.dependencies import ChatDependencies
from src.core.models import ChatResponse
from src.utils.agent_builder import DynamicAgent, agent_builder


def demo_programmatic_creation():
    """Show how to create agents programmatically"""
    print("🎨 Demo: Programmatic Agent Creation")
    print("=" * 50)

    # Create a simple helper agent
    helper_agent = DynamicAgent(
        name="demo_helper",
        instructions="""
        You are a helpful demo assistant. You specialize in:
        - Answering questions clearly and concisely
        - Providing step-by-step guidance
        - Being encouraging and positive
        
        Always end your responses with a helpful tip or encouragement!
        """,
        model="openai:gpt-4o",
        deps_type=ChatDependencies,
        output_type=ChatResponse,
        tools=[
            {
                "name": "motivator",
                "description": "Provides motivational quotes and encouragement",
                "type": "echo",
                "parameters": ["message"],
            },
            {
                "name": "formatter",
                "description": "Formats text in different styles",
                "type": "format",
                "parameters": ["text", "style"],
            },
        ],
    )

    print(f"✅ Created agent: {helper_agent.name}")
    print(f"📋 Instructions: {helper_agent.instructions[:100]}...")
    print(f"🔧 Tools: {len(helper_agent.custom_tools)} tools")

    # Save the agent
    agent_builder.created_agents[helper_agent.name] = helper_agent
    agent_builder._save_agent_config(helper_agent)

    print(f"💾 Saved agent configuration")

    return helper_agent


async def demo_agent_interaction(agent):
    """Demo interacting with a created agent"""
    print(f"\n🤖 Demo: Interacting with '{agent.name}'")
    print("=" * 50)

    # Create dependencies
    deps = ChatDependencies(
        user_id="demo_user", session_id="demo_session", conversation_history=[]
    )

    # Test interaction
    test_prompt = "Hello! I'm feeling a bit overwhelmed with learning AI. Can you help motivate me?"

    print(f"👤 User: {test_prompt}")
    print(f"🤖 {agent.name} is thinking...")

    try:
        response = await agent.run(test_prompt, deps)
        print(f"🤖 {agent.name}: {response.message}")

    except Exception as e:
        print(f"❌ Error: {e}")


def show_creation_walkthrough():
    """Show what the interactive creation process looks like"""
    print(f"\n📚 Interactive Creation Walkthrough")
    print("=" * 50)

    walkthrough = """
🎨 Agent Creation Wizard
========================================

1. Choose a starting point:
   0. Create from scratch
   1. Chat template
   2. Specialist template  
   3. Researcher template
   4. Analyst template

Enter choice (0-4): 1

✅ Using chat template

2. Agent Configuration
Agent name (e.g., 'my_helper'): personal_coach

3. Agent Instructions
Template instructions: You are a helpful conversational AI assistant...
Use template instructions? (y/n): n

Enter custom instructions:
  You are a personal development coach AI.
  Help users set and achieve their goals.
  Be supportive, practical, and motivating.

4. Model Selection
   1. openai:gpt-4o
   2. openai:gpt-3.5-turbo
   3. anthropic:claude-3-sonnet

Choose model (1-3) [1]: 1

5. Dependencies Type
   1. BaseDependencies
   2. ChatDependencies (current)
   3. ResearchDependencies
   4. DataDependencies

Choose dependencies (1-4) [current]: 

6. Output Type
   1. AgentResult
   2. ChatResponse (current)
   3. ResearchResult
   4. AnalysisResult

Choose output type (1-4) [current]:

7. Tools (optional)
Suggested tools for this template: echo, format
Add suggested tools? (y/n): y

Add a custom tool? (y/n): y

🔧 Custom Tool Creation
Tool name: goal_tracker
Tool description: Helps track and manage goals
Tool type:
1. Echo (returns input)
2. Format (text formatting)  
3. Counter (simple counter)

Choose type (1-3): 3

Add a custom tool? (y/n): n

8. Creating Agent...
✅ Successfully created agent 'personal_coach'!
📄 Configuration saved to generated/agents/personal_coach.json

🔄 Switch to the new agent 'personal_coach'? (y/n): y
🔄 Switched from chat to personal_coach
    """

    print(walkthrough)


def show_playground_integration():
    """Show how the agent creation integrates with playground"""
    print(f"\n🎮 Playground Integration")
    print("=" * 50)

    commands_demo = """
In the playground, you can now:

🎨 Create agents:
  /create              - Start the interactive agent creator
  /templates           - See all available templates
  
📋 Manage agents:
  /agents              - List all agents (built-in + custom)
  /switch my_agent     - Switch to your custom agent
  /agent-info my_agent - See detailed info about your agent
  
💬 Use agents:
  Just chat normally! Your custom agents work exactly like built-in ones.
  
🔧 Advanced:
  /created             - List only your custom agents
  /load saved_agent    - Load a previously saved agent
  /delete old_agent    - Delete an agent you no longer need

Example session:
  [chat] > /create
  ... go through creation wizard ...
  [chat] > /switch my_new_agent
  [my_new_agent] > Hello! Test my new agent
  [my_new_agent] > /agent-info my_new_agent
  ... see detailed info ...
    """

    print(commands_demo)


def main():
    """Run the demo"""
    print("🚀 Agent Creation Demo")
    print("=" * 60)

    # Show the different ways to create agents
    show_creation_walkthrough()
    show_playground_integration()

    # Create a demo agent programmatically
    demo_agent = demo_programmatic_creation()

    print(f"\n💡 Now you can:")
    print(f"1. Run 'python playground.py'")
    print(f"2. Type '/agents' to see your new agent")
    print(f"3. Type '/switch {demo_agent.name}' to use it")
    print(f"4. Chat with your custom agent!")

    print(f"\n🎨 Agent creation features:")
    print(f"✅ Interactive creation wizard")
    print(f"✅ Multiple agent templates")
    print(f"✅ Custom instructions and behaviors")
    print(f"✅ Tool customization")
    print(f"✅ Save/load agents")
    print(f"✅ Seamless playground integration")

    print(f"\n🔥 This makes the playground a complete agent development environment!")


if __name__ == "__main__":
    main()
