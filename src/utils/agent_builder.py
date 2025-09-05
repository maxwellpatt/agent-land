"""
Agent Builder

Interactive agent creation and modification system.
Allows creating agents dynamically in the playground environment.
"""

import json
import re
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type

from ..config.logging import logger
from ..core.base_agent import BaseAgent
from ..core.dependencies import BaseDependencies, ChatDependencies, ResearchDependencies, DataDependencies
from ..core.models import BaseResponse, ChatResponse, ResearchResult, AnalysisResult, AgentResult


class DynamicAgent(BaseAgent):
    """Dynamically created agent that can be modified at runtime"""
    
    def __init__(
        self,
        name: str,
        instructions: str,
        model: Optional[str] = None,
        deps_type: Type = BaseDependencies,
        output_type: Type = AgentResult,
        tools: List[Dict[str, Any]] = None
    ):
        self.custom_tools = tools or []
        
        super().__init__(
            name=name,
            model=model,
            instructions=instructions,
            deps_type=deps_type,
            output_type=output_type,
        )
        
        # Store configuration for saving/loading
        self.config = {
            "name": name,
            "instructions": instructions,
            "model": model or "openai:gpt-4o",
            "deps_type": deps_type.__name__,
            "output_type": output_type.__name__,
            "tools": self.custom_tools,
            "created_at": datetime.now().isoformat()
        }
    
    def _register_tools(self):
        """Register custom tools defined at creation time"""
        for tool_config in self.custom_tools:
            self._create_dynamic_tool(tool_config)
    
    def _create_dynamic_tool(self, tool_config: Dict[str, Any]):
        """Create a tool dynamically from configuration"""
        tool_name = tool_config["name"]
        tool_description = tool_config["description"]
        tool_type = tool_config.get("type", "default")
        
        # Create a simple tool function based on type
        if tool_type == "echo":
            def create_echo_tool():
                async def echo_tool(ctx, message: str) -> str:
                    f"""Echo tool: {tool_description}"""
                    return f"Echo: {message}"
                echo_tool.__name__ = tool_name
                return echo_tool
            
            self.agent.tool(create_echo_tool())
            
        elif tool_type == "format":
            def create_format_tool():
                async def format_tool(ctx, text: str, format_type: str = "upper") -> str:
                    f"""Format tool: {tool_description}"""
                    if format_type == "upper":
                        return text.upper()
                    elif format_type == "lower":
                        return text.lower()
                    elif format_type == "title":
                        return text.title()
                    else:
                        return text
                format_tool.__name__ = tool_name
                return format_tool
            
            self.agent.tool(create_format_tool())
                
        elif tool_type == "counter":
            def create_counter_tool():
                counter_value = {"count": 0}
                
                async def counter_tool(ctx, action: str = "increment") -> str:
                    f"""Counter tool: {tool_description}"""
                    if action == "increment":
                        counter_value["count"] += 1
                    elif action == "decrement":
                        counter_value["count"] -= 1
                    elif action == "reset":
                        counter_value["count"] = 0
                    
                    return f"Counter: {counter_value['count']}"
                counter_tool.__name__ = tool_name
                return counter_tool
            
            self.agent.tool(create_counter_tool())
                
        else:
            # Default simple tool
            def create_default_tool():
                async def dynamic_tool(ctx, input_param: str) -> str:
                    f"""Dynamic tool: {tool_description}"""
                    return f"Tool '{tool_name}' processed: {input_param}"
                dynamic_tool.__name__ = tool_name
                return dynamic_tool
            
            self.agent.tool(create_default_tool())


class AgentBuilder:
    """Interactive agent builder for the playground"""
    
    def __init__(self):
        self.created_agents = {}
        self.agent_templates = {
            "chat": {
                "instructions": "You are a helpful conversational AI assistant. Be friendly, informative, and engaging.",
                "deps_type": ChatDependencies,
                "output_type": ChatResponse,
                "suggested_tools": ["echo", "format"]
            },
            "specialist": {
                "instructions": "You are a specialized AI expert in your domain. Provide detailed, accurate information.",
                "deps_type": BaseDependencies,
                "output_type": AgentResult,
                "suggested_tools": ["counter", "format"]
            },
            "researcher": {
                "instructions": "You are a research-focused AI that gathers and analyzes information systematically.",
                "deps_type": ResearchDependencies,
                "output_type": ResearchResult,
                "suggested_tools": ["echo", "counter"]
            },
            "analyst": {
                "instructions": "You are an analytical AI that provides insights and recommendations based on data.",
                "deps_type": DataDependencies,
                "output_type": AnalysisResult,
                "suggested_tools": ["format", "counter"]
            }
        }
        
        # Create agents directory if it doesn't exist
        self.agents_dir = Path("generated/agents")
        self.agents_dir.mkdir(parents=True, exist_ok=True)
    
    def list_templates(self) -> str:
        """List available agent templates"""
        output = ["🎨 Available Agent Templates:", ""]
        
        for i, (name, config) in enumerate(self.agent_templates.items(), 1):
            output.extend([
                f"{i}. {name.title()} Agent",
                f"   Instructions: {config['instructions'][:60]}...",
                f"   Dependencies: {config['deps_type'].__name__}",
                f"   Output: {config['output_type'].__name__}",
                f"   Suggested Tools: {', '.join(config['suggested_tools'])}",
                ""
            ])
        
        return "\n".join(output)
    
    def create_agent_interactive(self) -> Optional[DynamicAgent]:
        """Interactive agent creation process"""
        print("🎨 Agent Creation Wizard")
        print("=" * 40)
        
        try:
            # Step 1: Choose template or create from scratch
            print("\n1. Choose a starting point:")
            print("   0. Create from scratch")
            for i, template_name in enumerate(self.agent_templates.keys(), 1):
                print(f"   {i}. {template_name.title()} template")
            
            choice = input("\nEnter choice (0-{}): ".format(len(self.agent_templates))).strip()
            
            if choice == "0":
                # From scratch
                template_config = {
                    "instructions": "",
                    "deps_type": BaseDependencies,
                    "output_type": AgentResult,
                    "suggested_tools": []
                }
            else:
                try:
                    template_name = list(self.agent_templates.keys())[int(choice) - 1]
                    template_config = self.agent_templates[template_name].copy()
                    print(f"\n✅ Using {template_name} template")
                except (ValueError, IndexError):
                    print("❌ Invalid choice")
                    return None
            
            # Step 2: Agent name
            print("\n2. Agent Configuration")
            agent_name = input("Agent name (e.g., 'my_helper'): ").strip()
            if not agent_name or not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', agent_name):
                print("❌ Invalid agent name. Use letters, numbers, and underscores only.")
                return None
            
            if agent_name in self.created_agents:
                print(f"❌ Agent '{agent_name}' already exists")
                return None
            
            # Step 3: Instructions
            print(f"\n3. Agent Instructions")
            if template_config["instructions"]:
                print(f"Template instructions: {template_config['instructions']}")
                use_template = input("Use template instructions? (y/n): ").strip().lower()
                
                if use_template == 'y':
                    instructions = template_config["instructions"]
                else:
                    instructions = self._get_multiline_input("Enter custom instructions:")
            else:
                instructions = self._get_multiline_input("Enter agent instructions:")
            
            # Step 4: Model selection
            print(f"\n4. Model Selection")
            models = ["openai:gpt-4o", "openai:gpt-3.5-turbo", "anthropic:claude-3-sonnet"]
            for i, model in enumerate(models, 1):
                print(f"   {i}. {model}")
            
            model_choice = input(f"Choose model (1-{len(models)}) [1]: ").strip() or "1"
            try:
                model = models[int(model_choice) - 1]
            except (ValueError, IndexError):
                model = models[0]
            
            # Step 5: Dependencies type
            print(f"\n5. Dependencies Type")
            deps_types = [
                ("BaseDependencies", BaseDependencies),
                ("ChatDependencies", ChatDependencies),
                ("ResearchDependencies", ResearchDependencies),
                ("DataDependencies", DataDependencies)
            ]
            
            for i, (name, _) in enumerate(deps_types, 1):
                current = " (current)" if template_config["deps_type"] == deps_types[i-1][1] else ""
                print(f"   {i}. {name}{current}")
            
            deps_choice = input(f"Choose dependencies (1-{len(deps_types)}) [current]: ").strip()
            if deps_choice:
                try:
                    deps_type = deps_types[int(deps_choice) - 1][1]
                except (ValueError, IndexError):
                    deps_type = template_config["deps_type"]
            else:
                deps_type = template_config["deps_type"]
            
            # Step 6: Output type
            print(f"\n6. Output Type")
            output_types = [
                ("AgentResult", AgentResult),
                ("ChatResponse", ChatResponse),
                ("ResearchResult", ResearchResult),
                ("AnalysisResult", AnalysisResult)
            ]
            
            for i, (name, _) in enumerate(output_types, 1):
                current = " (current)" if template_config["output_type"] == output_types[i-1][1] else ""
                print(f"   {i}. {name}{current}")
            
            output_choice = input(f"Choose output type (1-{len(output_types)}) [current]: ").strip()
            if output_choice:
                try:
                    output_type = output_types[int(output_choice) - 1][1]
                except (ValueError, IndexError):
                    output_type = template_config["output_type"]
            else:
                output_type = template_config["output_type"]
            
            # Step 7: Add tools
            print(f"\n7. Tools (optional)")
            tools = []
            
            if template_config["suggested_tools"]:
                print(f"Suggested tools for this template: {', '.join(template_config['suggested_tools'])}")
                add_suggested = input("Add suggested tools? (y/n): ").strip().lower()
                
                if add_suggested == 'y':
                    for tool_name in template_config["suggested_tools"]:
                        tools.append(self._create_tool_config(tool_name))
            
            # Allow adding custom tools
            while True:
                add_tool = input("Add a custom tool? (y/n): ").strip().lower()
                if add_tool != 'y':
                    break
                
                tool_config = self._create_custom_tool()
                if tool_config:
                    tools.append(tool_config)
            
            # Step 8: Create the agent
            print(f"\n8. Creating Agent...")
            
            agent = DynamicAgent(
                name=agent_name,
                instructions=instructions,
                model=model,
                deps_type=deps_type,
                output_type=output_type,
                tools=tools
            )
            
            # Store the agent
            self.created_agents[agent_name] = agent
            
            # Save to file
            self._save_agent_config(agent)
            
            print(f"✅ Successfully created agent '{agent_name}'!")
            print(f"📄 Configuration saved to {self.agents_dir / f'{agent_name}.json'}")
            
            return agent
            
        except KeyboardInterrupt:
            print("\n❌ Agent creation cancelled")
            return None
        except Exception as e:
            print(f"❌ Error creating agent: {e}")
            logger.error(f"Agent creation error: {e}")
            return None
    
    def _get_multiline_input(self, prompt: str) -> str:
        """Get multiline input from user"""
        print(f"{prompt}")
        print("(Enter text, then press Enter on empty line to finish)")
        
        lines = []
        while True:
            line = input("  ")
            if not line:
                break
            lines.append(line)
        
        return "\n".join(lines)
    
    def _create_tool_config(self, tool_type: str) -> Dict[str, Any]:
        """Create a tool configuration for predefined tool types"""
        tool_configs = {
            "echo": {
                "name": "echo_tool",
                "description": "Echoes back the input message",
                "type": "echo",
                "parameters": ["message"]
            },
            "format": {
                "name": "text_formatter",
                "description": "Formats text in different ways (upper, lower, title)",
                "type": "format", 
                "parameters": ["text", "format_type"]
            },
            "counter": {
                "name": "counter",
                "description": "A simple counter that can increment, decrement, or reset",
                "type": "counter",
                "parameters": ["action"]
            }
        }
        
        return tool_configs.get(tool_type, {})
    
    def _create_custom_tool(self) -> Optional[Dict[str, Any]]:
        """Create a custom tool interactively"""
        print("\n🔧 Custom Tool Creation")
        
        tool_name = input("Tool name: ").strip()
        if not tool_name or not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', tool_name):
            print("❌ Invalid tool name")
            return None
        
        description = input("Tool description: ").strip()
        if not description:
            description = f"Custom tool: {tool_name}"
        
        print("\nTool type:")
        print("1. Echo (returns input)")
        print("2. Format (text formatting)")
        print("3. Counter (simple counter)")
        
        tool_type_choice = input("Choose type (1-3): ").strip()
        tool_type_map = {"1": "echo", "2": "format", "3": "counter"}
        tool_type = tool_type_map.get(tool_type_choice, "echo")
        
        return {
            "name": tool_name,
            "description": description,
            "type": tool_type,
            "parameters": []
        }
    
    def _save_agent_config(self, agent: DynamicAgent):
        """Save agent configuration to file"""
        config_file = self.agents_dir / f"{agent.name}.json"
        
        try:
            with open(config_file, 'w') as f:
                json.dump(agent.config, f, indent=2, default=str)
            logger.info(f"Saved agent config to {config_file}")
        except Exception as e:
            logger.error(f"Failed to save agent config: {e}")
    
    def load_agent(self, agent_name: str) -> Optional[DynamicAgent]:
        """Load an agent from saved configuration"""
        config_file = self.agents_dir / f"{agent_name}.json"
        
        if not config_file.exists():
            return None
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            
            # Map string names back to types
            deps_type_map = {
                "BaseDependencies": BaseDependencies,
                "ChatDependencies": ChatDependencies,
                "ResearchDependencies": ResearchDependencies,
                "DataDependencies": DataDependencies
            }
            
            output_type_map = {
                "AgentResult": AgentResult,
                "ChatResponse": ChatResponse,
                "ResearchResult": ResearchResult,
                "AnalysisResult": AnalysisResult
            }
            
            agent = DynamicAgent(
                name=config["name"],
                instructions=config["instructions"],
                model=config.get("model"),
                deps_type=deps_type_map.get(config["deps_type"], BaseDependencies),
                output_type=output_type_map.get(config["output_type"], AgentResult),
                tools=config.get("tools", [])
            )
            
            self.created_agents[agent_name] = agent
            logger.info(f"Loaded agent {agent_name} from config")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to load agent {agent_name}: {e}")
            return None
    
    def list_created_agents(self) -> str:
        """List all created agents"""
        if not self.created_agents:
            return "No custom agents created yet."
        
        output = ["🤖 Created Agents:", ""]
        
        for name, agent in self.created_agents.items():
            config = agent.config
            output.extend([
                f"📋 {name}",
                f"   Model: {config['model']}",
                f"   Dependencies: {config['deps_type']}",
                f"   Tools: {len(config['tools'])} tools",
                f"   Created: {config['created_at'][:19]}",
                ""
            ])
        
        return "\n".join(output)
    
    def delete_agent(self, agent_name: str) -> bool:
        """Delete a created agent"""
        if agent_name not in self.created_agents:
            return False
        
        # Remove from memory
        del self.created_agents[agent_name]
        
        # Remove config file
        config_file = self.agents_dir / f"{agent_name}.json"
        if config_file.exists():
            config_file.unlink()
        
        logger.info(f"Deleted agent {agent_name}")
        return True
    
    def get_agent_info(self, agent_name: str) -> Optional[str]:
        """Get detailed info about a created agent"""
        if agent_name not in self.created_agents:
            return None
        
        agent = self.created_agents[agent_name]
        config = agent.config
        
        info_lines = [
            f"🤖 Agent: {agent_name}",
            "=" * 40,
            f"Instructions: {config['instructions'][:100]}...",
            f"Model: {config['model']}",
            f"Dependencies: {config['deps_type']}",
            f"Output Type: {config['output_type']}",
            f"Created: {config['created_at'][:19]}",
            f"Tools: {len(config['tools'])}",
        ]
        
        if config['tools']:
            info_lines.append("\nTools:")
            for tool in config['tools']:
                info_lines.append(f"  - {tool['name']}: {tool['description']}")
        
        return "\n".join(info_lines)


# Global agent builder instance
agent_builder = AgentBuilder()