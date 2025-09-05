"""
Agent Observer System

Advanced monitoring and observation tools for agent interactions.
Provides detailed insights into agent behavior, performance, and decision-making.
"""

import json
import time
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, AsyncIterator

from ..config.logging import logger


class AgentObserver:
    """Enhanced observer for agent interactions"""
    
    def __init__(self, output_dir: str = "generated/observations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.observations = []
        self.current_observation = None
        
    def start_observation(self, agent_name: str, prompt: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Start observing an agent interaction"""
        observation = {
            "id": f"obs_{int(time.time() * 1000)}",
            "agent_name": agent_name,
            "prompt": prompt,
            "context": context or {},
            "start_time": datetime.now().isoformat(),
            "start_timestamp": time.time(),
            "steps": [],
            "tools_used": [],
            "performance": {},
            "status": "running"
        }
        
        self.current_observation = observation
        self.observations.append(observation)
        
        logger.info(f"🔍 Started observation {observation['id']} for agent {agent_name}")
        return observation
    
    def log_step(self, step_type: str, description: str, data: Any = None):
        """Log a step in the current observation"""
        if not self.current_observation:
            return
        
        step = {
            "timestamp": datetime.now().isoformat(),
            "elapsed": time.time() - self.current_observation["start_timestamp"],
            "type": step_type,
            "description": description,
            "data": data
        }
        
        self.current_observation["steps"].append(step)
        logger.debug(f"🔍 Step [{step_type}]: {description}")
    
    def log_tool_usage(self, tool_name: str, input_data: Any, output_data: Any, execution_time: float):
        """Log tool usage during agent interaction"""
        if not self.current_observation:
            return
        
        tool_usage = {
            "timestamp": datetime.now().isoformat(),
            "tool_name": tool_name,
            "input_data": input_data,
            "output_data": output_data,
            "execution_time": execution_time
        }
        
        self.current_observation["tools_used"].append(tool_usage)
        logger.info(f"🔧 Tool used: {tool_name} ({execution_time:.3f}s)")
    
    def end_observation(self, result: Any = None, error: str = None):
        """End the current observation"""
        if not self.current_observation:
            return
        
        end_time = time.time()
        total_time = end_time - self.current_observation["start_timestamp"]
        
        self.current_observation.update({
            "end_time": datetime.now().isoformat(),
            "total_execution_time": total_time,
            "result": str(result) if result else None,
            "error": error,
            "status": "error" if error else "completed",
            "performance": {
                "total_time": total_time,
                "steps_count": len(self.current_observation["steps"]),
                "tools_used_count": len(self.current_observation["tools_used"]),
                "avg_step_time": total_time / len(self.current_observation["steps"]) if self.current_observation["steps"] else 0
            }
        })
        
        # Save observation to file
        self._save_observation(self.current_observation)
        
        logger.info(f"🔍 Completed observation {self.current_observation['id']} ({total_time:.2f}s)")
        self.current_observation = None
    
    def _save_observation(self, observation: Dict[str, Any]):
        """Save observation to JSON file"""
        filename = f"observation_{observation['id']}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(observation, f, indent=2, default=str)
            logger.debug(f"💾 Saved observation to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save observation: {e}")
    
    @asynccontextmanager
    async def observe(self, agent_name: str, prompt: str, context: Dict[str, Any] = None) -> AsyncIterator[Dict[str, Any]]:
        """Context manager for observing agent interactions"""
        observation = self.start_observation(agent_name, prompt, context)
        try:
            yield observation
        except Exception as e:
            self.end_observation(error=str(e))
            raise
        else:
            self.end_observation()
    
    def get_agent_summary(self, agent_name: str) -> Dict[str, Any]:
        """Get performance summary for a specific agent"""
        agent_observations = [obs for obs in self.observations if obs["agent_name"] == agent_name]
        
        if not agent_observations:
            return {"error": f"No observations found for agent {agent_name}"}
        
        completed_obs = [obs for obs in agent_observations if obs["status"] == "completed"]
        
        summary = {
            "agent_name": agent_name,
            "total_observations": len(agent_observations),
            "completed_observations": len(completed_obs),
            "error_rate": (len(agent_observations) - len(completed_obs)) / len(agent_observations),
            "performance": {}
        }
        
        if completed_obs:
            execution_times = [obs["total_execution_time"] for obs in completed_obs]
            tool_usage = []
            for obs in completed_obs:
                tool_usage.extend(obs["tools_used"])
            
            summary["performance"] = {
                "avg_execution_time": sum(execution_times) / len(execution_times),
                "min_execution_time": min(execution_times),
                "max_execution_time": max(execution_times),
                "total_tools_used": len(tool_usage),
                "unique_tools": len(set(tool["tool_name"] for tool in tool_usage)),
                "most_used_tools": self._get_most_used_tools(tool_usage)
            }
        
        return summary
    
    def _get_most_used_tools(self, tool_usage: List[Dict]) -> List[Dict[str, Any]]:
        """Get most frequently used tools"""
        tool_counts = {}
        for tool in tool_usage:
            tool_name = tool["tool_name"]
            if tool_name not in tool_counts:
                tool_counts[tool_name] = {"count": 0, "total_time": 0}
            tool_counts[tool_name]["count"] += 1
            tool_counts[tool_name]["total_time"] += tool["execution_time"]
        
        # Sort by usage count
        sorted_tools = sorted(
            [{"tool": name, **stats} for name, stats in tool_counts.items()],
            key=lambda x: x["count"],
            reverse=True
        )
        
        return sorted_tools[:5]  # Top 5
    
    def generate_report(self) -> str:
        """Generate a comprehensive observation report"""
        if not self.observations:
            return "No observations recorded yet."
        
        report_lines = [
            "🔍 Agent Observation Report",
            "=" * 50,
            f"Total Observations: {len(self.observations)}",
            f"Report Generated: {datetime.now().isoformat()}",
            "",
        ]
        
        # Agent summaries
        agents = set(obs["agent_name"] for obs in self.observations)
        for agent in agents:
            summary = self.get_agent_summary(agent)
            report_lines.extend([
                f"🤖 Agent: {agent}",
                f"   Observations: {summary['total_observations']}",
                f"   Completed: {summary['completed_observations']}",
                f"   Error Rate: {summary['error_rate']:.1%}",
            ])
            
            if "performance" in summary and summary["performance"]:
                perf = summary["performance"]
                report_lines.extend([
                    f"   Avg Execution Time: {perf['avg_execution_time']:.2f}s",
                    f"   Tools Used: {perf['total_tools_used']}",
                    f"   Most Used Tools: {', '.join(tool['tool'] for tool in perf['most_used_tools'][:3])}",
                ])
            
            report_lines.append("")
        
        # Recent observations
        recent_obs = sorted(self.observations, key=lambda x: x["start_timestamp"], reverse=True)[:5]
        report_lines.extend([
            "📊 Recent Observations:",
            "-" * 30,
        ])
        
        for obs in recent_obs:
            status_emoji = "✅" if obs["status"] == "completed" else "❌" if obs["status"] == "error" else "⏳"
            report_lines.append(
                f"{status_emoji} {obs['id']} | {obs['agent_name']} | "
                f"{obs.get('total_execution_time', 0):.2f}s | "
                f"{len(obs['tools_used'])} tools"
            )
        
        return "\n".join(report_lines)


# Global observer instance
observer = AgentObserver()


def observe_agent_run(agent_name: str, prompt: str, context: Dict[str, Any] = None):
    """Decorator for observing agent runs"""
    return observer.observe(agent_name, prompt, context)


def log_step(step_type: str, description: str, data: Any = None):
    """Log a step in the current observation"""
    observer.log_step(step_type, description, data)


def log_tool_usage(tool_name: str, input_data: Any, output_data: Any, execution_time: float):
    """Log tool usage"""
    observer.log_tool_usage(tool_name, input_data, output_data, execution_time)