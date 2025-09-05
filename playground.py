#!/usr/bin/env python3
"""
Interactive Agent Playground

A command-line interface for testing and observing agent interactions in real-time.
Perfect for developing and debugging custom agents.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.agents.examples.simple_chat import simple_chat_agent
from src.agents.examples.research_agent import research_agent  
from src.agents.examples.data_analyst import data_analyst_agent
from src.core.dependencies import ChatDependencies, ResearchDependencies, DataDependencies
from src.config.logging import logger
from src.utils.helpers import generate_conversation_id, generate_session_id
from src.utils.agent_builder import agent_builder


class AgentPlayground:
    """Interactive playground for testing agents"""
    
    def __init__(self):
        self.session_id = generate_session_id()
        self.conversation_id = generate_conversation_id()
        self.conversation_history = []
        self.current_agent = "chat"
        
        # Available agents (built-in)
        self.agents = {
            "chat": {
                "agent": simple_chat_agent,
                "deps_class": ChatDependencies,
                "description": "Simple conversational AI with context management",
                "type": "built-in"
            },
            "research": {
                "agent": research_agent,
                "deps_class": ResearchDependencies,
                "description": "Information gathering and research agent",
                "type": "built-in"
            },
            "analyst": {
                "agent": data_analyst_agent,
                "deps_class": DataDependencies,
                "description": "Data analysis and business insights agent",
                "type": "built-in"
            }
        }
        
        # Load any previously created agents
        self._load_created_agents()
        
        print(f"🚀 Agent Playground Started")
        print(f"Session ID: {self.session_id}")
        print(f"Conversation ID: {self.conversation_id}")
        print("=" * 60)
    
    def print_help(self):
        """Display available commands"""
        print("\n📋 Available Commands:")
        print("  /help or /h          - Show this help message")
        print("  /agents or /a        - List available agents")
        print("  /switch <agent>      - Switch to different agent")
        print("  /history or /hist    - Show conversation history")
        print("  /clear               - Clear conversation history") 
        print("  /info                - Show current agent info")
        print("  /observe or /obs     - Toggle detailed observation mode")
        print("  /profile             - Show agent performance profile")
        print("  /export              - Export conversation to JSON")
        print("")
        print("🎨 Agent Creation:")
        print("  /create              - Create a new agent interactively")
        print("  /templates           - List available agent templates")
        print("  /created             - List your created agents")
        print("  /load <name>         - Load a created agent")
        print("  /delete <name>       - Delete a created agent")
        print("  /agent-info <name>   - Show detailed info about a created agent")
        print("")
        print("  /quit or /q          - Exit playground")
        print("  <message>            - Send message to current agent")
        print("-" * 60)
    
    def list_agents(self):
        """List available agents"""
        print(f"\n🤖 Available Agents:")
        
        # Built-in agents
        built_in = {k: v for k, v in self.agents.items() if v.get("type") == "built-in"}
        if built_in:
            print("  📦 Built-in:")
            for name, info in built_in.items():
                current = "👉 " if name == self.current_agent else "   "
                print(f"  {current}{name}: {info['description']}")
        
        # Custom agents
        custom = {k: v for k, v in self.agents.items() if v.get("type") == "custom"}
        if custom:
            print("  🎨 Custom:")
            for name, info in custom.items():
                current = "👉 " if name == self.current_agent else "   "
                print(f"  {current}{name}: {info['description']}")
        
        print("-" * 60)
    
    def switch_agent(self, agent_name: str):
        """Switch to a different agent"""
        if agent_name in self.agents:
            old_agent = self.current_agent
            self.current_agent = agent_name
            print(f"🔄 Switched from {old_agent} to {agent_name}")
            self.log_interaction("system", f"Switched to {agent_name} agent")
        else:
            print(f"❌ Unknown agent: {agent_name}")
            print(f"Available agents: {', '.join(self.agents.keys())}")
    
    def show_history(self):
        """Display conversation history"""
        print(f"\n📜 Conversation History ({len(self.conversation_history)} messages):")
        if not self.conversation_history:
            print("   No messages yet.")
            return
            
        for i, msg in enumerate(self.conversation_history[-10:], 1):  # Show last 10
            timestamp = msg.get('timestamp', 'Unknown')
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')[:100] + "..." if len(msg.get('content', '')) > 100 else msg.get('content', '')
            agent = msg.get('agent', 'unknown')
            
            print(f"  {i:2d}. [{timestamp}] {role} ({agent}): {content}")
        
        if len(self.conversation_history) > 10:
            print(f"   ... and {len(self.conversation_history) - 10} more messages")
        print("-" * 60)
    
    def clear_history(self):
        """Clear conversation history"""
        count = len(self.conversation_history)
        self.conversation_history.clear()
        print(f"🗑️  Cleared {count} messages from history")
    
    def show_agent_info(self):
        """Show current agent information"""
        agent_config = self.agents[self.current_agent]
        agent_info = agent_config["agent"].get_info()
        
        print(f"\n🤖 Current Agent: {self.current_agent}")
        print(f"   Name: {agent_info['name']}")
        print(f"   Model: {agent_info['model']}")
        print(f"   Dependencies: {agent_info['deps_type']}")
        print(f"   Output Type: {agent_info['output_type']}")
        print(f"   Description: {agent_config['description']}")
        print("-" * 60)
    
    def export_conversation(self):
        """Export conversation to JSON file"""
        # Ensure conversations directory exists
        conversations_dir = Path("generated/conversations")
        conversations_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = conversations_dir / f"conversation_{timestamp}.json"
        
        export_data = {
            "session_id": self.session_id,
            "conversation_id": self.conversation_id,
            "timestamp": datetime.now().isoformat(),
            "message_count": len(self.conversation_history),
            "messages": self.conversation_history
        }
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"💾 Exported conversation to {filename}")
    
    def _load_created_agents(self):
        """Load previously created agents"""
        try:
            # Check for saved agents
            agents_dir = Path("generated/agents")
            if agents_dir.exists():
                for config_file in agents_dir.glob("*.json"):
                    agent_name = config_file.stem
                    loaded_agent = agent_builder.load_agent(agent_name)
                    
                    if loaded_agent:
                        # Add to available agents
                        self.agents[agent_name] = {
                            "agent": loaded_agent,
                            "deps_class": loaded_agent.deps_type,
                            "description": f"Custom agent: {loaded_agent.instructions[:50]}...",
                            "type": "custom"
                        }
        except Exception as e:
            logger.error(f"Error loading created agents: {e}")
    
    def create_agent_interactive(self):
        """Create a new agent interactively"""
        try:
            agent = agent_builder.create_agent_interactive()
            
            if agent:
                # Add to available agents
                self.agents[agent.name] = {
                    "agent": agent,
                    "deps_class": agent.deps_type,
                    "description": f"Custom agent: {agent.instructions[:50]}...",
                    "type": "custom"
                }
                
                # Ask if user wants to switch to the new agent
                switch = input(f"\n🔄 Switch to the new agent '{agent.name}'? (y/n): ").strip().lower()
                if switch == 'y':
                    self.switch_agent(agent.name)
                
                return True
            
        except Exception as e:
            print(f"❌ Error creating agent: {e}")
            logger.error(f"Interactive agent creation error: {e}")
        
        return False
    
    def load_agent_by_name(self, agent_name: str):
        """Load an agent by name"""
        if agent_name in self.agents:
            print(f"⚠️ Agent '{agent_name}' is already loaded")
            return
        
        loaded_agent = agent_builder.load_agent(agent_name)
        
        if loaded_agent:
            self.agents[agent_name] = {
                "agent": loaded_agent,
                "deps_class": loaded_agent.deps_type,
                "description": f"Custom agent: {loaded_agent.instructions[:50]}...",
                "type": "custom"
            }
            print(f"✅ Loaded agent '{agent_name}'")
            
            # Ask if user wants to switch to the loaded agent
            switch = input(f"🔄 Switch to '{agent_name}'? (y/n): ").strip().lower()
            if switch == 'y':
                self.switch_agent(agent_name)
        else:
            print(f"❌ Could not load agent '{agent_name}'. Make sure it exists.")
    
    def delete_agent_by_name(self, agent_name: str):
        """Delete an agent by name"""
        if agent_name not in self.agents:
            print(f"❌ Agent '{agent_name}' not found")
            return
        
        if self.agents[agent_name].get("type") == "built-in":
            print(f"❌ Cannot delete built-in agent '{agent_name}'")
            return
        
        # Confirm deletion
        confirm = input(f"⚠️ Are you sure you want to delete agent '{agent_name}'? (y/n): ").strip().lower()
        if confirm != 'y':
            print("❌ Deletion cancelled")
            return
        
        # Switch away if currently using this agent
        if self.current_agent == agent_name:
            print(f"🔄 Switching away from '{agent_name}' to 'chat'")
            self.current_agent = "chat"
        
        # Delete from playground and builder
        del self.agents[agent_name]
        agent_builder.delete_agent(agent_name)
        
        print(f"✅ Deleted agent '{agent_name}'")
    
    def show_agent_templates(self):
        """Show available agent templates"""
        print(agent_builder.list_templates())
    
    def show_created_agents(self):
        """Show all created agents"""
        print(agent_builder.list_created_agents())
    
    def show_agent_detailed_info(self, agent_name: str):
        """Show detailed information about an agent"""
        if agent_name in self.agents and self.agents[agent_name].get("type") == "custom":
            info = agent_builder.get_agent_info(agent_name)
            if info:
                print(f"\n{info}")
            else:
                print(f"❌ No detailed info available for '{agent_name}'")
        elif agent_name in self.agents:
            # Show basic info for built-in agents
            self.current_agent = agent_name
            self.show_agent_info()
        else:
            print(f"❌ Agent '{agent_name}' not found")
    
    def log_interaction(self, role: str, content: str, agent: str = None, metadata: Dict[str, Any] = None):
        """Log an interaction to conversation history"""
        message = {
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content,
            "agent": agent or self.current_agent,
            "metadata": metadata or {}
        }
        self.conversation_history.append(message)
    
    async def send_message(self, message: str, observe_mode: bool = False):
        """Send message to current agent"""
        start_time = time.time()
        
        # Log user message
        self.log_interaction("user", message)
        
        # Get current agent configuration
        agent_config = self.agents[self.current_agent]
        agent = agent_config["agent"]
        deps_class = agent_config["deps_class"]
        
        # Create dependencies based on agent type
        if deps_class == ChatDependencies:
            deps = ChatDependencies(
                user_id="playground_user",
                session_id=self.session_id,
                conversation_history=self.conversation_history[-10:],  # Last 10 messages
                context={"conversation_id": self.conversation_id}
            )
        elif deps_class == ResearchDependencies:
            deps = ResearchDependencies(
                user_id="playground_user",
                session_id=self.session_id,
                search_enabled=True,
                max_results=5,
                context={"conversation_id": self.conversation_id}
            )
        elif deps_class == DataDependencies:
            deps = DataDependencies(
                user_id="playground_user", 
                session_id=self.session_id,
                context={"conversation_id": self.conversation_id}
            )
        else:
            deps = None
        
        try:
            if observe_mode:
                print(f"🔍 [OBSERVE] Sending to {self.current_agent} agent...")
                print(f"🔍 [OBSERVE] Dependencies: {type(deps).__name__}")
                print(f"🔍 [OBSERVE] Message length: {len(message)} characters")
            
            # Send message to agent
            response = await agent.run(message, deps)
            
            execution_time = time.time() - start_time
            
            # Extract response content based on agent type
            if hasattr(response, 'message'):
                response_text = response.message
            elif hasattr(response, 'analysis'):
                response_text = f"Analysis: {response.analysis}"
                if hasattr(response, 'insights') and response.insights:
                    response_text += f"\n\nInsights:\n" + "\n".join(f"• {insight}" for insight in response.insights)
                if hasattr(response, 'recommendations') and response.recommendations:
                    response_text += f"\n\nRecommendations:\n" + "\n".join(f"• {rec}" for rec in response.recommendations)
            elif hasattr(response, 'findings'):
                response_text = f"Research Results:\n"
                for i, finding in enumerate(response.findings, 1):
                    response_text += f"{i}. {finding}\n"
                if hasattr(response, 'confidence') and response.confidence:
                    response_text += f"\nConfidence: {response.confidence:.2%}"
            else:
                response_text = str(response)
            
            # Log agent response
            self.log_interaction(
                "assistant", 
                response_text, 
                self.current_agent,
                {
                    "execution_time": execution_time,
                    "response_type": type(response).__name__
                }
            )
            
            if observe_mode:
                print(f"🔍 [OBSERVE] Response received in {execution_time:.2f}s")
                print(f"🔍 [OBSERVE] Response type: {type(response).__name__}")
                print(f"🔍 [OBSERVE] Response length: {len(response_text)} characters")
            
            print(f"\n🤖 {self.current_agent}: {response_text}")
            
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.log_interaction("system", error_msg, self.current_agent, {"error": True})
            print(f"❌ {error_msg}")
    
    async def run(self):
        """Main playground loop"""
        observe_mode = False
        
        print("🎮 Agent Playground Ready!")
        print("Type /help for commands, or start chatting with your agents.")
        print("=" * 60)
        
        while True:
            try:
                # Show current agent and prompt
                prompt = f"\n[{self.current_agent}] > "
                user_input = input(prompt).strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    parts = user_input.split()
                    command = parts[0].lower()
                    
                    if command in ['/help', '/h']:
                        self.print_help()
                    elif command in ['/agents', '/a']:
                        self.list_agents()
                    elif command == '/switch':
                        if len(parts) > 1:
                            self.switch_agent(parts[1])
                        else:
                            print("Usage: /switch <agent_name>")
                    elif command in ['/history', '/hist']:
                        self.show_history()
                    elif command == '/clear':
                        self.clear_history()
                    elif command == '/info':
                        self.show_agent_info()
                    elif command in ['/observe', '/obs']:
                        observe_mode = not observe_mode
                        print(f"🔍 Observation mode: {'ON' if observe_mode else 'OFF'}")
                    elif command == '/profile':
                        print("📊 Agent Performance Profile:")
                        agent_messages = [msg for msg in self.conversation_history if msg.get('role') == 'assistant' and msg.get('agent') == self.current_agent]
                        if agent_messages:
                            avg_time = sum(msg.get('metadata', {}).get('execution_time', 0) for msg in agent_messages) / len(agent_messages)
                            print(f"   Messages: {len(agent_messages)}")
                            print(f"   Avg Response Time: {avg_time:.2f}s")
                        else:
                            print("   No messages from current agent yet.")
                    elif command == '/export':
                        self.export_conversation()
                    elif command == '/create':
                        self.create_agent_interactive()
                    elif command == '/templates':
                        self.show_agent_templates()
                    elif command == '/created':
                        self.show_created_agents()
                    elif command == '/load':
                        if len(parts) > 1:
                            self.load_agent_by_name(parts[1])
                        else:
                            print("Usage: /load <agent_name>")
                    elif command == '/delete':
                        if len(parts) > 1:
                            self.delete_agent_by_name(parts[1])
                        else:
                            print("Usage: /delete <agent_name>")
                    elif command == '/agent-info':
                        if len(parts) > 1:
                            self.show_agent_detailed_info(parts[1])
                        else:
                            print("Usage: /agent-info <agent_name>")
                    elif command in ['/quit', '/q']:
                        print("👋 Goodbye!")
                        break
                    else:
                        print(f"Unknown command: {command}")
                        print("Type /help for available commands.")
                
                else:
                    # Send message to agent
                    await self.send_message(user_input, observe_mode)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                logger.error(f"Playground error: {e}")


async def main():
    """Run the agent playground"""
    playground = AgentPlayground()
    await playground.run()


if __name__ == "__main__":
    asyncio.run(main())