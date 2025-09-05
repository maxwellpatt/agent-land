# Agent-Land 🤖

A clean, organized playground for exploring [Pydantic AI](https://ai.pydantic.dev/) agent capabilities. Build, test, and manage custom AI agents with a complete development environment.

## ✨ User Guide

**🎮 Interactive Playground (`python playground.py`)**
- Create custom agents with an interactive wizard (`/create`)
- Switch between agents on the fly (`/switch <agent>`)
- Test and chat with your agents in real-time
- Export conversations to JSON (`/export`)
- Full conversation history and performance tracking

**🎨 Agent Creation System**
- Step-by-step agent builder with templates
- Custom instructions, tools, and model selection
- Save/load agent configurations
- 4 built-in templates: Chat, Specialist, Researcher, Analyst

**🔧 Agent Management**
- List all agents (`/agents`) - built-in + custom
- Load saved agents (`/load <name>`)
- Delete agents (`/delete <name>`)
- Detailed agent info (`/agent-info <name>`)

**📊 Observation & Debugging**
- Multi-agent scenario testing (`python examples/multi_agent_scenarios.py`)
- Performance profiling and conversation tracking
- Comprehensive logging system

## 📋 What's Currently Example-Only

These are working examples but need customization for real-world use:

- **Research Agent** - Basic web search example (needs real search API)
- **Data Analyst Agent** - Sample data processing (needs real data sources)
- **Web Search Tool** - Placeholder implementation
- **File Operations Tool** - Basic file I/O examples

## 🚀 Quick Start

### Setup
```bash
# Clone and setup
git clone <repository-url>
cd agent-land
pip install -r requirements.txt

# Configure API keys
cp .env.example .env
# Edit .env with your OpenAI/Anthropic API keys
```

### Try It Out
```bash
# Start the interactive playground
python playground.py

# Create your first custom agent
[chat] > /create
# Follow the interactive wizard...

# Switch to your new agent and chat
[chat] > /switch my_agent
[my_agent] > Hello! Tell me about yourself.
```

### Test Multi-Agent Scenarios
```bash
# Run collaborative scenarios
python examples/multi_agent_scenarios.py
```

## 🏗️ Project Structure

```
agent-land/
├── playground.py               # 🎮 Main interactive environment
├── src/
│   ├── agents/examples/        # Working example agents
│   ├── agents/templates/       # Templates for new agents  
│   ├── core/                  # Base classes and models
│   ├── tools/                 # Agent tools (examples)
│   └── utils/                 # Agent builder and utilities
├── examples/                  # Usage demonstrations & scenarios
│   └── multi_agent_scenarios.py # 🎭 Multi-agent testing
└── generated/                 # 🗂️ All your created content
    ├── agents/               # Custom agent configs
    ├── conversations/        # Exported chats & scenarios
    └── observations/         # Debugging data
```

## 🎯 Core Features

### Interactive Agent Development
The playground provides a complete development environment:
- Create agents with guided prompts
- Test interactions immediately
- Iterate and refine agent behavior
- Export and share conversations

### Template-Based Creation
Start from proven patterns:
- **Chat Agent** - Conversational AI with context
- **Specialist Agent** - Domain-specific expert
- **Researcher Agent** - Information gathering
- **Analyst Agent** - Data analysis and insights

### Professional Tooling
- Type-safe with Pydantic throughout
- Comprehensive logging (`logger.txt`)
- Environment-based configuration
- Clean separation of concerns

## 🎨 Creating Your First Agent

1. **Start the playground**: `python playground.py`
2. **Create an agent**: Type `/create` and follow the wizard
3. **Choose a template** or start from scratch
4. **Customize**: Instructions, model, tools, and behavior
5. **Test immediately**: Switch to your agent and start chatting
6. **Iterate**: Modify and improve based on testing

Your agents are automatically saved and available every time you restart the playground.

## 🔍 Advanced Usage

### Multi-Agent Collaboration
Test how agents work together on complex tasks:
```bash
python examples/multi_agent_scenarios.py
# Choose from: Collaborative Research, Debate Discussion, Problem-Solving Chain
```

### Performance Analysis
Monitor agent performance through the playground's built-in profiling:
- Use `/observe` to toggle detailed execution logging
- Use `/profile` to see response time statistics
- Check `generated/observations/` for detailed debugging data

### Conversation Tracking
All interactions are logged and can be exported. Use `/export` in the playground or check `generated/conversations/` for scenario results.

## 📚 Documentation

- **`AGENT_DEVELOPMENT_GUIDE.md`** - Complete development guide
- **`CLAUDE.md`** - Architecture decisions and design thoughts
- **`examples/`** - Usage patterns and demonstrations

## 🗂️ Generated Content

Agent-Land keeps everything organized in `generated/`:
- **`agents/`** - Your custom agent configurations  
- **`conversations/`** - Exported chats and scenario results
- **`observations/`** - Debugging and performance data

This folder is gitignored to keep your repo clean while preserving your work locally.

## ⚡ What Makes This Special

- **Zero Setup Friction** - Works immediately with just API keys
- **Interactive Development** - Build and test agents in real-time
- **Professional Architecture** - Type-safe, logged, and maintainable
- **Extensible Design** - Easy to add new agents, tools, and capabilities
- **Clean Organization** - Everything has its place

## 🤝 Perfect For

- **Learning Pydantic AI** - Hands-on playground environment
- **Prototyping Agents** - Rapid iteration and testing
- **Agent Research** - Compare behaviors and performance
- **Building AI Teams** - Multi-agent coordination experiments

## 🚨 Requirements

- Python 3.8+
- OpenAI API key (for GPT models)
- Anthropic API key (optional, for Claude models)

## 🔗 Links

- [Pydantic AI Documentation](https://ai.pydantic.dev/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

**Ready to build your AI agent team?** 🚀  
`python playground.py` and type `/create` to get started!