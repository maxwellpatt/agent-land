"""
Conversation Tracker and Visualizer

Tools for tracking and visualizing multi-agent conversations and interactions.
Perfect for observing how agents communicate and collaborate.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from ..config.logging import logger


class ConversationTracker:
    """Track and visualize multi-agent conversations"""
    
    def __init__(self, session_name: str = None):
        self.session_name = session_name or f"session_{int(time.time())}"
        self.conversations = {}  # conversation_id -> conversation data
        self.agents = {}  # agent_id -> agent info
        self.interactions = []  # list of all interactions
        self.active_conversation = None
        
        # Create output directory
        self.output_dir = Path("generated/conversations")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📊 Started conversation tracking session: {self.session_name}")
    
    def register_agent(self, agent_id: str, agent_info: Dict[str, Any]):
        """Register an agent in the tracking system"""
        self.agents[agent_id] = {
            **agent_info,
            "registered_at": datetime.now().isoformat(),
            "message_count": 0,
            "total_response_time": 0
        }
        logger.info(f"🤖 Registered agent: {agent_id}")
    
    def start_conversation(self, conversation_id: str, participants: List[str], topic: str = None) -> str:
        """Start tracking a new conversation"""
        conversation = {
            "id": conversation_id,
            "participants": participants,
            "topic": topic,
            "started_at": datetime.now().isoformat(),
            "messages": [],
            "status": "active",
            "statistics": {
                "total_messages": 0,
                "participant_stats": {p: {"message_count": 0, "avg_response_time": 0} for p in participants}
            }
        }
        
        self.conversations[conversation_id] = conversation
        self.active_conversation = conversation_id
        
        logger.info(f"💬 Started conversation {conversation_id} with {len(participants)} participants")
        return conversation_id
    
    def add_message(
        self,
        conversation_id: str,
        sender: str,
        content: str,
        message_type: str = "text",
        metadata: Dict[str, Any] = None,
        response_time: float = None
    ):
        """Add a message to a conversation"""
        if conversation_id not in self.conversations:
            raise ValueError(f"Conversation {conversation_id} not found")
        
        conversation = self.conversations[conversation_id]
        
        message = {
            "id": f"msg_{len(conversation['messages']) + 1}",
            "timestamp": datetime.now().isoformat(),
            "sender": sender,
            "content": content,
            "type": message_type,
            "metadata": metadata or {},
            "response_time": response_time
        }
        
        conversation["messages"].append(message)
        conversation["statistics"]["total_messages"] += 1
        
        # Update participant stats
        if sender in conversation["statistics"]["participant_stats"]:
            stats = conversation["statistics"]["participant_stats"][sender]
            stats["message_count"] += 1
            
            if response_time:
                current_avg = stats["avg_response_time"]
                count = stats["message_count"]
                stats["avg_response_time"] = ((current_avg * (count - 1)) + response_time) / count
        
        # Update agent stats
        if sender in self.agents:
            self.agents[sender]["message_count"] += 1
            if response_time:
                self.agents[sender]["total_response_time"] += response_time
        
        # Log interaction
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "conversation_id": conversation_id,
            "sender": sender,
            "message_type": message_type,
            "content_length": len(content),
            "response_time": response_time
        }
        self.interactions.append(interaction)
        
        logger.debug(f"💬 [{conversation_id}] {sender}: {content[:50]}...")
    
    def end_conversation(self, conversation_id: str, summary: str = None):
        """End a conversation"""
        if conversation_id not in self.conversations:
            return
        
        conversation = self.conversations[conversation_id]
        conversation["status"] = "ended"
        conversation["ended_at"] = datetime.now().isoformat()
        conversation["summary"] = summary
        
        # Calculate conversation duration
        start_time = datetime.fromisoformat(conversation["started_at"])
        end_time = datetime.fromisoformat(conversation["ended_at"])
        duration = (end_time - start_time).total_seconds()
        conversation["duration_seconds"] = duration
        
        # Save conversation to file
        self._save_conversation(conversation)
        
        if self.active_conversation == conversation_id:
            self.active_conversation = None
        
        logger.info(f"💬 Ended conversation {conversation_id} ({duration:.1f}s)")
    
    def get_conversation_summary(self, conversation_id: str) -> Dict[str, Any]:
        """Get a summary of a conversation"""
        if conversation_id not in self.conversations:
            return {"error": "Conversation not found"}
        
        conversation = self.conversations[conversation_id]
        messages = conversation["messages"]
        
        if not messages:
            return {"error": "No messages in conversation"}
        
        # Calculate summary statistics
        total_words = sum(len(msg["content"].split()) for msg in messages)
        response_times = [msg["response_time"] for msg in messages if msg["response_time"]]
        
        summary = {
            "conversation_id": conversation_id,
            "participants": conversation["participants"],
            "topic": conversation.get("topic"),
            "status": conversation["status"],
            "duration": conversation.get("duration_seconds"),
            "message_count": len(messages),
            "total_words": total_words,
            "avg_words_per_message": total_words / len(messages),
            "avg_response_time": sum(response_times) / len(response_times) if response_times else None,
            "participant_contribution": {}
        }
        
        # Calculate each participant's contribution
        for participant in conversation["participants"]:
            participant_messages = [msg for msg in messages if msg["sender"] == participant]
            participant_words = sum(len(msg["content"].split()) for msg in participant_messages)
            
            summary["participant_contribution"][participant] = {
                "message_count": len(participant_messages),
                "word_count": participant_words,
                "percentage": (len(participant_messages) / len(messages)) * 100 if messages else 0
            }
        
        return summary
    
    def visualize_conversation(self, conversation_id: str) -> str:
        """Generate a text-based visualization of a conversation"""
        if conversation_id not in self.conversations:
            return "Conversation not found"
        
        conversation = self.conversations[conversation_id]
        messages = conversation["messages"]
        
        if not messages:
            return "No messages in conversation"
        
        # Generate visualization
        viz_lines = [
            f"💬 Conversation: {conversation_id}",
            f"🏷️  Topic: {conversation.get('topic', 'N/A')}",
            f"👥 Participants: {', '.join(conversation['participants'])}",
            f"📅 Started: {conversation['started_at']}",
            f"📊 Messages: {len(messages)}",
            "=" * 60,
            ""
        ]
        
        # Message timeline
        for i, msg in enumerate(messages, 1):
            timestamp = datetime.fromisoformat(msg["timestamp"]).strftime("%H:%M:%S")
            sender_emoji = self._get_sender_emoji(msg["sender"])
            response_time_str = f" ({msg['response_time']:.2f}s)" if msg.get("response_time") else ""
            
            viz_lines.extend([
                f"{i:2d}. [{timestamp}] {sender_emoji} {msg['sender']}{response_time_str}:",
                f"    {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}",
                ""
            ])
        
        # Add summary
        summary = self.get_conversation_summary(conversation_id)
        viz_lines.extend([
            "📊 Summary:",
            f"   Duration: {summary.get('duration', 0):.1f}s",
            f"   Avg Response Time: {summary.get('avg_response_time', 0):.2f}s" if summary.get('avg_response_time') else "   No response times recorded",
            f"   Total Words: {summary['total_words']}",
            "",
            "👥 Participation:",
        ])
        
        for participant, contrib in summary["participant_contribution"].items():
            viz_lines.append(f"   {participant}: {contrib['message_count']} messages ({contrib['percentage']:.1f}%)")
        
        return "\n".join(viz_lines)
    
    def _get_sender_emoji(self, sender: str) -> str:
        """Get emoji for sender based on agent type"""
        emoji_map = {
            "chat": "💬",
            "research": "🔍", 
            "analyst": "📊",
            "user": "👤",
            "system": "⚙️"
        }
        
        # Try to find matching emoji
        for key, emoji in emoji_map.items():
            if key in sender.lower():
                return emoji
        
        return "🤖"  # Default for agents
    
    def _save_conversation(self, conversation: Dict[str, Any]):
        """Save conversation to JSON file"""
        filename = f"conversation_{conversation['id']}.json"
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(conversation, f, indent=2, default=str)
            logger.debug(f"💾 Saved conversation to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")
    
    def get_session_report(self) -> str:
        """Generate a comprehensive session report"""
        report_lines = [
            f"📊 Conversation Tracking Report",
            f"Session: {self.session_name}",
            f"Generated: {datetime.now().isoformat()}",
            "=" * 60,
            "",
            f"📈 Overview:",
            f"   Conversations: {len(self.conversations)}",
            f"   Registered Agents: {len(self.agents)}",
            f"   Total Interactions: {len(self.interactions)}",
            ""
        ]
        
        # Agent statistics
        if self.agents:
            report_lines.extend([
                "🤖 Agent Statistics:",
                "-" * 30,
            ])
            
            for agent_id, agent_info in self.agents.items():
                avg_response = (agent_info["total_response_time"] / agent_info["message_count"]) if agent_info["message_count"] > 0 else 0
                report_lines.append(
                    f"   {agent_id}: {agent_info['message_count']} messages, "
                    f"avg {avg_response:.2f}s response"
                )
            
            report_lines.append("")
        
        # Conversation summaries
        if self.conversations:
            report_lines.extend([
                "💬 Conversation Summaries:",
                "-" * 30,
            ])
            
            for conv_id, conversation in self.conversations.items():
                status_emoji = "✅" if conversation["status"] == "ended" else "⏳"
                duration = conversation.get("duration_seconds", 0)
                report_lines.append(
                    f"{status_emoji} {conv_id}: {len(conversation['messages'])} messages, "
                    f"{duration:.1f}s duration"
                )
        
        return "\n".join(report_lines)
    
    def export_session(self) -> str:
        """Export entire session to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_export_{self.session_name}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        session_data = {
            "session_name": self.session_name,
            "export_timestamp": datetime.now().isoformat(),
            "agents": self.agents,
            "conversations": self.conversations,
            "interactions": self.interactions,
            "summary": {
                "total_conversations": len(self.conversations),
                "total_agents": len(self.agents),
                "total_interactions": len(self.interactions)
            }
        }
        
        try:
            with open(filepath, 'w') as f:
                json.dump(session_data, f, indent=2, default=str)
            logger.info(f"💾 Exported session to {filepath}")
            return str(filepath)
        except Exception as e:
            logger.error(f"Failed to export session: {e}")
            return None


# Global tracker instance
conversation_tracker = ConversationTracker()