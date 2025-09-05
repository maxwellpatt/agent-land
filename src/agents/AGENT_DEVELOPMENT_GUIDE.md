# Agent Development & Observation Guide 🤖

This guide covers everything you need to know about building custom agents and observing their interactions using the advanced tools we've created.

## 🚀 Quick Start: Building Your First Custom Agent

### 1. Using the Agent Template

```bash
# Copy the template
cp src/agents/templates/agent_template.py src/agents/examples/my_custom_agent.py
```

### 2. Customize Your Agent

```python
from typing import Optional
from pydantic_ai import RunContext
from ...core.base_agent import BaseAgent
from ...core.dependencies import BaseDependencies
from ...core.models import AgentResult

class MyCustomAgent(BaseAgent[BaseDependencies, AgentResult]):
    def __init__(self, model: Optional[str] = None):
        instructions = """
        You are a specialized AI assistant for [your domain].
        Your role is to [describe the agent's purpose].
        Always be [describe desired behavior traits].
        """
        
        super().__init__(
            name="my_custom_agent",
            model=model,
            instructions=instructions,
            deps_type=BaseDependencies,
            output_type=AgentResult,
        )
    
    def _register_tools(self) -> None:
        @self.agent.tool
        async def my_tool(ctx: RunContext[BaseDependencies], param: str) -> str:
            """Your custom tool description"""
            # Tool implementation
            return f"Tool result: {param}"

# Create global instance
my_custom_agent = MyCustomAgent()
```

### 3. Test Your Agent

```bash
# Quick test
python playground.py
# Then type: /switch my_custom_agent
```

## 🎮 Interactive Testing Tools

### 1. Agent Playground (`playground.py`)

**Best for:** Real-time interaction and conversation testing

```bash
python playground.py
```

**Key Features:**
- Switch between agents on the fly
- Maintain conversation context
- Observe detailed execution logs
- Export conversations to JSON
- Performance profiling

**Useful Commands:**
- `/help` - Show all commands
- `/switch <agent>` - Change agent
- `/observe` - Toggle detailed observation mode
- `/history` - View conversation history
- `/profile` - Show performance stats
- `/export` - Save conversation

### 2. Agent Debugger (`agent_debugger.py`)

**Best for:** Deep debugging and performance analysis

```bash
python agent_debugger.py
```

**Features:**
- Step-by-step execution tracing
- Performance profiling across multiple prompts
- Agent comparison on same prompts
- Detailed error analysis
- Execution time breakdown

**Commands:**
- `debug <agent> <prompt>` - Debug single interaction
- `compare <prompt>` - Compare all agents
- `profile <agent>` - Run performance tests
- `summary` - Show debug statistics

### 3. Multi-Agent Scenarios (`examples/multi_agent_scenarios.py`)

**Best for:** Observing agent collaboration and interaction

```bash
python examples/multi_agent_scenarios.py
```

**Scenarios:**
1. **Collaborative Research** - Agents work together on research
2. **Debate Discussion** - Agents argue different positions
3. **Problem-Solving Chain** - Sequential problem solving

## 🔍 Observation and Monitoring

### Advanced Logging System

The framework automatically logs all agent interactions to `logger.txt` and creates structured observation files.

#### Observation Features:
- **Step-by-step execution tracking**
- **Tool usage monitoring** 
- **Performance metrics**
- **Error analysis**
- **Conversation flow visualization**

#### Accessing Observations:

```python
from src.utils.observer import observer

# Get agent performance summary
summary = observer.get_agent_summary("my_agent")
print(summary)

# Generate comprehensive report
report = observer.generate_report()
print(report)
```

### Conversation Tracking

Track multi-agent conversations and interactions:

```python
from src.utils.conversation_tracker import conversation_tracker

# Start tracking a conversation
conv_id = conversation_tracker.start_conversation(
    "my_conversation",
    ["agent1", "agent2"], 
    "Discussion topic"
)

# Add messages as agents interact
conversation_tracker.add_message(
    conv_id,
    "agent1", 
    "Hello!",
    response_time=0.5
)

# Visualize the conversation
viz = conversation_tracker.visualize_conversation(conv_id)
print(viz)
```

## 🛠️ Advanced Agent Development Patterns

### 1. Custom Dependencies

Create specialized dependencies for your agent's needs:

```python
from src.core.dependencies import BaseDependencies

class MyAgentDependencies(BaseDependencies):
    api_key: str
    max_requests: int = 100
    custom_config: Dict[str, Any] = {}
    
    def validate_api_key(self) -> bool:
        return len(self.api_key) > 10
```

### 2. Custom Output Models

Define structured outputs for your agent:

```python
from src.core.models import BaseResponse
from typing import List

class MyAgentResponse(BaseResponse):
    result: str
    confidence: float
    suggestions: List[str] = []
    processing_steps: List[str] = []
```

### 3. Advanced Tool Integration

Create sophisticated tools with error handling and observation:

```python
@self.agent.tool
async def advanced_tool(ctx: RunContext[MyAgentDependencies], query: str) -> str:
    """Advanced tool with observation and error handling"""
    from src.utils.observer import observer
    
    start_time = time.time()
    
    try:
        # Log tool start
        observer.log_step("tool_start", f"Starting advanced_tool with query: {query}")
        
        # Tool logic here
        result = await some_async_operation(query, ctx.deps.api_key)
        
        # Log success
        execution_time = time.time() - start_time
        observer.log_tool_usage("advanced_tool", query, result, execution_time)
        
        return result
        
    except Exception as e:
        # Log error
        observer.log_step("tool_error", f"Tool failed: {str(e)}")
        raise
```

### 4. Agent Chaining and Composition

Build complex workflows by chaining agents:

```python
async def complex_workflow(initial_prompt: str):
    # Step 1: Research
    research_result = await research_agent.run(
        f"Research: {initial_prompt}",
        ResearchDependencies(search_enabled=True)
    )
    
    # Step 2: Analysis (using research results)
    analysis_result = await data_analyst_agent.run(
        f"Analyze: {research_result.findings}",
        DataDependencies()
    )
    
    # Step 3: Synthesis
    final_result = await simple_chat_agent.run(
        f"Synthesize research and analysis: {analysis_result.analysis}",
        ChatDependencies()
    )
    
    return final_result
```

## 📊 Performance Optimization Tips

### 1. Monitor Agent Performance

```python
# Use the debugger to profile your agent
python agent_debugger.py

# Run performance tests
profile <your_agent>
```

### 2. Optimize Tool Usage

- **Cache frequent operations**
- **Use async/await properly**
- **Implement timeout handling**
- **Add retry logic for unreliable operations**

### 3. Memory Management

```python
# Clear conversation history when it gets too long
if len(deps.conversation_history) > MAX_HISTORY:
    deps.conversation_history = deps.conversation_history[-MAX_KEEP:]
```

## 🧪 Testing Strategies

### 1. Unit Testing Individual Tools

```python
import pytest
from src.agents.examples.my_agent import my_custom_agent

@pytest.mark.asyncio
async def test_my_agent_basic_functionality():
    deps = MyAgentDependencies(api_key="test_key")
    result = await my_custom_agent.run("test prompt", deps)
    assert result is not None
    assert hasattr(result, 'expected_field')
```

### 2. Integration Testing

```bash
# Use the multi-agent scenarios for integration testing
python examples/multi_agent_scenarios.py
```

### 3. Performance Testing

```python
# Profile agent performance across multiple prompts
test_prompts = [
    "Simple question",
    "Complex analysis request", 
    "Multi-step task"
]

await debugger.profile_agent_performance("my_agent", test_prompts)
```

## 📈 Scaling Agent Development

### 1. Agent Factory Pattern

```python
class AgentFactory:
    @staticmethod
    def create_specialized_agent(domain: str, expertise_level: str):
        instructions = f"You are a {expertise_level} expert in {domain}..."
        
        return BaseAgent(
            name=f"{domain}_{expertise_level}_agent",
            instructions=instructions,
            # ... other config
        )

# Create agents dynamically
marketing_expert = AgentFactory.create_specialized_agent("marketing", "senior")
tech_expert = AgentFactory.create_specialized_agent("technology", "principal")
```

### 2. Configuration-Driven Agents

```python
# agents_config.yaml
agents:
  customer_support:
    instructions: "You are a helpful customer support agent..."
    tools: ["search_kb", "create_ticket"]
    model: "openai:gpt-4o"
  
  sales_assistant:
    instructions: "You are a knowledgeable sales assistant..."
    tools: ["product_lookup", "pricing_calculator"]
    model: "anthropic:claude-3-sonnet"
```

### 3. Monitoring and Analytics

```python
# Track agent usage patterns
from src.utils.observer import observer

# Generate regular reports
daily_report = observer.generate_report()
send_report_to_dashboard(daily_report)

# Monitor error rates
error_rates = calculate_agent_error_rates()
if error_rates["my_agent"] > 0.05:  # 5% threshold
    alert_dev_team("High error rate detected")
```

## 🚨 Debugging Common Issues

### Issue 1: Agent Not Responding
```bash
# Check API key configuration
python -c "from src.config.settings import settings; print('API Key set:', bool(settings.openai_api_key))"

# Test with debugger
python agent_debugger.py
debug my_agent "simple test"
```

### Issue 2: Tool Errors
```python
# Add detailed logging to your tools
@self.agent.tool
async def problematic_tool(ctx, param):
    logger.info(f"Tool called with param: {param}")
    logger.info(f"Context: {ctx.deps}")
    
    try:
        result = await operation(param)
        logger.info(f"Tool succeeded: {result}")
        return result
    except Exception as e:
        logger.error(f"Tool failed: {e}")
        raise
```

### Issue 3: Performance Issues
```bash
# Profile your agent
python agent_debugger.py
profile my_agent

# Check conversation history size
# Large histories can slow down responses
```

## 🎯 Best Practices

### 1. Agent Design
- **Single Responsibility**: Each agent should have one clear purpose
- **Clear Instructions**: Be specific about what the agent should do
- **Error Handling**: Always handle exceptions gracefully
- **Logging**: Log important steps and decisions

### 2. Tool Development
- **Async by Default**: Use async/await for all I/O operations
- **Input Validation**: Validate tool parameters
- **Timeout Handling**: Set reasonable timeouts for external calls
- **Resource Cleanup**: Clean up resources properly

### 3. Testing and Observation
- **Test Early**: Use the playground for quick iteration
- **Debug Systematically**: Use the debugger for complex issues
- **Monitor Performance**: Track execution times and error rates
- **Document Behavior**: Keep notes on what works and what doesn't

## 📚 Next Steps

1. **Start Simple**: Build a basic agent using the template
2. **Test Interactively**: Use the playground to refine behavior
3. **Add Complexity**: Gradually add tools and features
4. **Monitor Performance**: Use debugging tools to optimize
5. **Scale Up**: Build multi-agent workflows and scenarios

## 🤝 Getting Help

- **Check Logs**: Always start by checking `logger.txt`
- **Use Debugging Tools**: The debugger can reveal many issues
- **Test Incrementally**: Add one feature at a time
- **Review Examples**: Look at the existing agents for patterns

Remember: Building great agents is an iterative process. Start simple, test frequently, and gradually add complexity while monitoring performance and behavior. The observation tools will help you understand exactly what your agents are doing and how to improve them! 🎉