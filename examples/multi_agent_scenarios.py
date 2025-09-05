#!/usr/bin/env python3
"""
Multi-Agent Interaction Scenarios

Demonstrates how different agents can work together, collaborate, and build upon each other's work.
Perfect for observing agent interactions and testing complex workflows.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.agents.examples.simple_chat import simple_chat_agent
from src.agents.examples.research_agent import research_agent
from src.agents.examples.data_analyst import data_analyst_agent
from src.core.dependencies import ChatDependencies, ResearchDependencies, DataDependencies
from src.utils.conversation_tracker import conversation_tracker
from src.utils.observer import observer
from src.config.logging import logger


class MultiAgentScenarios:
    """Orchestrates multi-agent interaction scenarios"""
    
    def __init__(self):
        self.agents = {
            "chat": {
                "agent": simple_chat_agent,
                "deps_class": ChatDependencies,
                "emoji": "💬",
                "role": "facilitator"
            },
            "research": {
                "agent": research_agent, 
                "deps_class": ResearchDependencies,
                "emoji": "🔍",
                "role": "researcher"
            },
            "analyst": {
                "agent": data_analyst_agent,
                "deps_class": DataDependencies,
                "emoji": "📊", 
                "role": "analyst"
            }
        }
        
        # Register agents with conversation tracker
        for agent_id, config in self.agents.items():
            conversation_tracker.register_agent(agent_id, {
                "name": agent_id,
                "role": config["role"],
                "emoji": config["emoji"]
            })
    
    async def scenario_collaborative_research(self, topic: str) -> Dict[str, Any]:
        """Scenario: Multiple agents collaborate on a research topic"""
        print(f"🤝 Collaborative Research Scenario")
        print(f"📋 Topic: {topic}")
        print("=" * 60)
        
        conversation_id = f"collab_research_{int(time.time())}"
        participants = ["chat", "research", "analyst"]
        
        # Start conversation tracking
        conversation_tracker.start_conversation(
            conversation_id,
            participants,
            f"Collaborative research on: {topic}"
        )
        
        results = {
            "scenario": "collaborative_research",
            "topic": topic,
            "conversation_id": conversation_id,
            "agents_involved": participants,
            "timeline": []
        }
        
        try:
            # Step 1: Chat agent introduces the topic and plans approach
            print(f"\n💬 Step 1: Planning the research approach")
            planning_prompt = f"""
            We need to conduct comprehensive research on '{topic}'. 
            Please outline a structured approach for researching this topic, 
            including what aspects should be investigated and how the research should be organized.
            """
            
            start_time = time.time()
            chat_deps = ChatDependencies(
                user_id="scenario_user",
                session_id="collab_session", 
                context={"scenario": "collaborative_research", "topic": topic}
            )
            
            planning_result = await simple_chat_agent.run(planning_prompt, chat_deps)
            planning_time = time.time() - start_time
            
            conversation_tracker.add_message(
                conversation_id,
                "chat",
                planning_result.message,
                "planning",
                {"step": 1},
                planning_time
            )
            
            results["timeline"].append({
                "step": 1,
                "agent": "chat",
                "action": "research_planning",
                "duration": planning_time,
                "output": planning_result.message
            })
            
            print(f"💬 Chat Agent Plan:\n{planning_result.message}\n")
            
            # Step 2: Research agent gathers information
            print(f"🔍 Step 2: Gathering research information")
            research_prompt = f"""
            Based on the research plan, conduct detailed research on '{topic}'.
            Focus on current trends, key developments, and important findings.
            Provide comprehensive research results with sources.
            """
            
            start_time = time.time()
            research_deps = ResearchDependencies(
                user_id="scenario_user",
                session_id="collab_session",
                search_enabled=True,
                max_results=5,
                context={
                    "scenario": "collaborative_research", 
                    "topic": topic,
                    "previous_step": "planning"
                }
            )
            
            research_result = await research_agent.run(research_prompt, research_deps)
            research_time = time.time() - start_time
            
            # Format research findings for display
            research_summary = f"Query: {research_result.query}\n\nFindings:\n"
            for i, finding in enumerate(research_result.findings, 1):
                research_summary += f"{i}. {finding}\n"
            
            if research_result.confidence:
                research_summary += f"\nConfidence: {research_result.confidence:.1%}"
            
            conversation_tracker.add_message(
                conversation_id,
                "research",
                research_summary,
                "research",
                {"step": 2, "findings_count": len(research_result.findings)},
                research_time
            )
            
            results["timeline"].append({
                "step": 2,
                "agent": "research",
                "action": "information_gathering",
                "duration": research_time,
                "findings_count": len(research_result.findings),
                "output": research_summary
            })
            
            print(f"🔍 Research Results:\n{research_summary}\n")
            
            # Step 3: Analyst agent analyzes the research
            print(f"📊 Step 3: Analyzing research findings")
            analysis_prompt = f"""
            Analyze the following research findings on '{topic}' and provide strategic insights:
            
            {research_summary}
            
            Focus on identifying patterns, opportunities, implications, and actionable recommendations.
            """
            
            start_time = time.time()
            analyst_deps = DataDependencies(
                user_id="scenario_user",
                session_id="collab_session",
                context={
                    "scenario": "collaborative_research",
                    "topic": topic,
                    "previous_steps": ["planning", "research"]
                }
            )
            
            analysis_result = await data_analyst_agent.run(analysis_prompt, analyst_deps)
            analysis_time = time.time() - start_time
            
            # Format analysis for display
            analysis_summary = f"Analysis: {analysis_result.analysis}\n"
            
            if analysis_result.insights:
                analysis_summary += f"\nKey Insights:\n"
                for i, insight in enumerate(analysis_result.insights, 1):
                    analysis_summary += f"{i}. {insight}\n"
            
            if analysis_result.recommendations:
                analysis_summary += f"\nRecommendations:\n"
                for i, rec in enumerate(analysis_result.recommendations, 1):
                    analysis_summary += f"{i}. {rec}\n"
            
            conversation_tracker.add_message(
                conversation_id,
                "analyst",
                analysis_summary,
                "analysis",
                {
                    "step": 3,
                    "insights_count": len(analysis_result.insights) if analysis_result.insights else 0,
                    "recommendations_count": len(analysis_result.recommendations) if analysis_result.recommendations else 0
                },
                analysis_time
            )
            
            results["timeline"].append({
                "step": 3,
                "agent": "analyst",
                "action": "data_analysis",
                "duration": analysis_time,
                "insights_count": len(analysis_result.insights) if analysis_result.insights else 0,
                "recommendations_count": len(analysis_result.recommendations) if analysis_result.recommendations else 0,
                "output": analysis_summary
            })
            
            print(f"📊 Analysis Results:\n{analysis_summary}\n")
            
            # Step 4: Chat agent synthesizes final report
            print(f"💬 Step 4: Synthesizing final report")
            synthesis_prompt = f"""
            Create a comprehensive final report synthesizing all the collaborative research on '{topic}'.
            
            Research Plan: {planning_result.message}
            
            Research Findings: {research_summary}
            
            Analysis: {analysis_summary}
            
            Provide a clear, actionable executive summary that combines all insights.
            """
            
            start_time = time.time()
            final_result = await simple_chat_agent.run(synthesis_prompt, chat_deps)
            synthesis_time = time.time() - start_time
            
            conversation_tracker.add_message(
                conversation_id,
                "chat",
                final_result.message,
                "synthesis",
                {"step": 4, "is_final": True},
                synthesis_time
            )
            
            results["timeline"].append({
                "step": 4,
                "agent": "chat",
                "action": "synthesis",
                "duration": synthesis_time,
                "output": final_result.message
            })
            
            print(f"💬 Final Report:\n{final_result.message}\n")
            
            # Calculate totals
            total_time = sum(step["duration"] for step in results["timeline"])
            results["total_duration"] = total_time
            results["success"] = True
            
            print(f"✅ Collaborative research completed in {total_time:.2f}s")
            
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
            print(f"❌ Scenario failed: {e}")
        
        finally:
            # End conversation tracking
            conversation_tracker.end_conversation(
                conversation_id,
                "Collaborative research scenario completed"
            )
        
        return results
    
    async def scenario_debate_discussion(self, topic: str, position_a: str, position_b: str) -> Dict[str, Any]:
        """Scenario: Two agents debate different positions, moderated by a third"""
        print(f"🗣️ Debate Discussion Scenario")
        print(f"📋 Topic: {topic}")
        print(f"🔵 Position A: {position_a}")
        print(f"🔴 Position B: {position_b}")
        print("=" * 60)
        
        conversation_id = f"debate_{int(time.time())}"
        participants = ["chat", "research", "analyst"]
        
        conversation_tracker.start_conversation(
            conversation_id,
            participants,
            f"Debate on: {topic}"
        )
        
        results = {
            "scenario": "debate_discussion",
            "topic": topic,
            "positions": {"a": position_a, "b": position_b},
            "conversation_id": conversation_id,
            "debate_rounds": []
        }
        
        try:
            # Chat agent moderates, Research takes position A, Analyst takes position B
            print(f"\n💬 Moderator: Starting the debate")
            
            moderation_prompt = f"""
            You are moderating a debate on '{topic}'.
            Position A: {position_a}
            Position B: {position_b}
            
            Please introduce the topic and set ground rules for a constructive debate.
            """
            
            start_time = time.time()
            chat_deps = ChatDependencies(
                user_id="scenario_user",
                session_id="debate_session",
                context={"scenario": "debate", "role": "moderator"}
            )
            
            moderation_result = await simple_chat_agent.run(moderation_prompt, chat_deps)
            mod_time = time.time() - start_time
            
            conversation_tracker.add_message(
                conversation_id,
                "chat",
                moderation_result.message,
                "moderation",
                {"role": "moderator"},
                mod_time
            )
            
            print(f"💬 Moderator:\n{moderation_result.message}\n")
            
            # Round 1: Research agent argues for position A
            print(f"🔍 Round 1: Research Agent (Position A)")
            
            research_prompt = f"""
            In this debate on '{topic}', argue strongly for this position: {position_a}
            
            Provide evidence, research findings, and logical arguments to support this viewpoint.
            Be persuasive but respectful.
            """
            
            start_time = time.time()
            research_deps = ResearchDependencies(
                user_id="scenario_user",
                session_id="debate_session",
                context={"scenario": "debate", "role": "position_a", "position": position_a}
            )
            
            research_debate = await research_agent.run(research_prompt, research_deps)
            research_time = time.time() - start_time
            
            # Format research argument
            research_argument = f"Position A Argument:\n{research_debate.query}\n\nKey Points:\n"
            for i, finding in enumerate(research_debate.findings, 1):
                research_argument += f"{i}. {finding}\n"
            
            conversation_tracker.add_message(
                conversation_id,
                "research",
                research_argument,
                "argument",
                {"position": "A", "round": 1},
                research_time
            )
            
            print(f"🔍 Research Agent (Position A):\n{research_argument}\n")
            
            # Round 1: Analyst agent argues for position B
            print(f"📊 Round 1: Analyst Agent (Position B)")
            
            analysis_prompt = f"""
            In this debate on '{topic}', argue strongly for this position: {position_b}
            
            Counter the previous arguments and provide data-driven insights, statistical evidence,
            and analytical reasoning to support your viewpoint. Address the opposing position directly.
            """
            
            start_time = time.time()
            analyst_deps = DataDependencies(
                user_id="scenario_user",
                session_id="debate_session",
                context={
                    "scenario": "debate", 
                    "role": "position_b", 
                    "position": position_b,
                    "opposing_argument": research_argument
                }
            )
            
            analyst_debate = await data_analyst_agent.run(analysis_prompt, analyst_deps)
            analyst_time = time.time() - start_time
            
            # Format analyst argument
            analyst_argument = f"Position B Analysis: {analyst_debate.analysis}\n"
            
            if analyst_debate.insights:
                analyst_argument += f"\nKey Insights:\n"
                for i, insight in enumerate(analyst_debate.insights, 1):
                    analyst_argument += f"{i}. {insight}\n"
            
            conversation_tracker.add_message(
                conversation_id,
                "analyst", 
                analyst_argument,
                "argument",
                {"position": "B", "round": 1},
                analyst_time
            )
            
            print(f"📊 Analyst Agent (Position B):\n{analyst_argument}\n")
            
            # Moderator summary
            print(f"💬 Moderator: Concluding the debate")
            
            conclusion_prompt = f"""
            As the moderator of this debate on '{topic}', provide a balanced summary:
            
            Position A ({position_a}) presented:
            {research_argument}
            
            Position B ({position_b}) presented:
            {analyst_argument}
            
            Summarize the key points from both sides and identify areas of agreement/disagreement.
            """
            
            start_time = time.time()
            conclusion_result = await simple_chat_agent.run(conclusion_prompt, chat_deps)
            conclusion_time = time.time() - start_time
            
            conversation_tracker.add_message(
                conversation_id,
                "chat",
                conclusion_result.message,
                "conclusion",
                {"role": "moderator"},
                conclusion_time
            )
            
            print(f"💬 Moderator Summary:\n{conclusion_result.message}\n")
            
            results["debate_rounds"] = [
                {
                    "round": 1,
                    "position_a": research_argument,
                    "position_b": analyst_argument,
                    "moderation": conclusion_result.message
                }
            ]
            
            total_time = mod_time + research_time + analyst_time + conclusion_time
            results["total_duration"] = total_time
            results["success"] = True
            
            print(f"✅ Debate completed in {total_time:.2f}s")
            
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
            print(f"❌ Debate failed: {e}")
        
        finally:
            conversation_tracker.end_conversation(
                conversation_id,
                "Debate discussion scenario completed"
            )
        
        return results
    
    async def scenario_problem_solving_chain(self, problem: str) -> Dict[str, Any]:
        """Scenario: Agents work in sequence to solve a complex problem"""
        print(f"🧩 Problem-Solving Chain Scenario")
        print(f"❓ Problem: {problem}")
        print("=" * 60)
        
        conversation_id = f"problem_solving_{int(time.time())}"
        participants = ["chat", "research", "analyst"]
        
        conversation_tracker.start_conversation(
            conversation_id,
            participants,
            f"Problem-solving chain for: {problem}"
        )
        
        results = {
            "scenario": "problem_solving_chain",
            "problem": problem,
            "conversation_id": conversation_id,
            "solution_chain": []
        }
        
        try:
            # Step 1: Chat agent breaks down the problem
            print(f"\n💬 Step 1: Problem breakdown and analysis")
            
            breakdown_prompt = f"""
            We need to solve this problem: '{problem}'
            
            Please break down this problem into smaller, manageable components.
            Identify what information we need, what research should be done,
            and what analysis would be helpful.
            """
            
            start_time = time.time()
            chat_deps = ChatDependencies(
                user_id="scenario_user",
                session_id="problem_session",
                context={"scenario": "problem_solving", "problem": problem}
            )
            
            breakdown_result = await simple_chat_agent.run(breakdown_prompt, chat_deps)
            breakdown_time = time.time() - start_time
            
            conversation_tracker.add_message(
                conversation_id,
                "chat",
                breakdown_result.message,
                "problem_breakdown",
                {"step": 1},
                breakdown_time
            )
            
            print(f"💬 Problem Breakdown:\n{breakdown_result.message}\n")
            
            # Step 2: Research agent gathers relevant information
            print(f"🔍 Step 2: Information gathering")
            
            research_prompt = f"""
            Based on the problem breakdown, research information relevant to solving: '{problem}'
            
            Problem analysis: {breakdown_result.message}
            
            Find relevant data, examples, best practices, and approaches that could help solve this problem.
            """
            
            start_time = time.time()
            research_deps = ResearchDependencies(
                user_id="scenario_user",
                session_id="problem_session",
                context={
                    "scenario": "problem_solving",
                    "problem": problem,
                    "breakdown": breakdown_result.message
                }
            )
            
            research_result = await research_agent.run(research_prompt, research_deps)
            research_time = time.time() - start_time
            
            research_info = f"Research Query: {research_result.query}\n\nInformation Found:\n"
            for i, finding in enumerate(research_result.findings, 1):
                research_info += f"{i}. {finding}\n"
            
            conversation_tracker.add_message(
                conversation_id,
                "research",
                research_info,
                "information_gathering",
                {"step": 2},
                research_time
            )
            
            print(f"🔍 Research Information:\n{research_info}\n")
            
            # Step 3: Analyst provides solution recommendations
            print(f"📊 Step 3: Solution analysis and recommendations")
            
            solution_prompt = f"""
            Based on the problem breakdown and research information, provide concrete solutions for: '{problem}'
            
            Problem breakdown: {breakdown_result.message}
            
            Research information: {research_info}
            
            Analyze the options and provide specific, actionable recommendations with implementation steps.
            """
            
            start_time = time.time()
            analyst_deps = DataDependencies(
                user_id="scenario_user",
                session_id="problem_session",
                context={
                    "scenario": "problem_solving",
                    "problem": problem,
                    "breakdown": breakdown_result.message,
                    "research": research_info
                }
            )
            
            solution_result = await data_analyst_agent.run(solution_prompt, analyst_deps)
            solution_time = time.time() - start_time
            
            solution_analysis = f"Solution Analysis: {solution_result.analysis}\n"
            
            if solution_result.recommendations:
                solution_analysis += f"\nRecommendations:\n"
                for i, rec in enumerate(solution_result.recommendations, 1):
                    solution_analysis += f"{i}. {rec}\n"
            
            conversation_tracker.add_message(
                conversation_id,
                "analyst",
                solution_analysis,
                "solution_analysis",
                {"step": 3},
                solution_time
            )
            
            print(f"📊 Solution Analysis:\n{solution_analysis}\n")
            
            # Step 4: Chat agent creates final implementation plan
            print(f"💬 Step 4: Implementation planning")
            
            implementation_prompt = f"""
            Create a comprehensive implementation plan for solving: '{problem}'
            
            Problem breakdown: {breakdown_result.message}
            Research findings: {research_info}
            Solution analysis: {solution_analysis}
            
            Provide a clear, step-by-step implementation plan that integrates all the insights.
            """
            
            start_time = time.time()
            implementation_result = await simple_chat_agent.run(implementation_prompt, chat_deps)
            implementation_time = time.time() - start_time
            
            conversation_tracker.add_message(
                conversation_id,
                "chat",
                implementation_result.message,
                "implementation_plan",
                {"step": 4, "is_final": True},
                implementation_time
            )
            
            print(f"💬 Implementation Plan:\n{implementation_result.message}\n")
            
            results["solution_chain"] = [
                {
                    "step": 1,
                    "agent": "chat",
                    "action": "problem_breakdown",
                    "output": breakdown_result.message,
                    "duration": breakdown_time
                },
                {
                    "step": 2,
                    "agent": "research", 
                    "action": "information_gathering",
                    "output": research_info,
                    "duration": research_time
                },
                {
                    "step": 3,
                    "agent": "analyst",
                    "action": "solution_analysis",
                    "output": solution_analysis,
                    "duration": solution_time
                },
                {
                    "step": 4,
                    "agent": "chat",
                    "action": "implementation_planning",
                    "output": implementation_result.message,
                    "duration": implementation_time
                }
            ]
            
            total_time = breakdown_time + research_time + solution_time + implementation_time
            results["total_duration"] = total_time
            results["success"] = True
            
            print(f"✅ Problem-solving chain completed in {total_time:.2f}s")
            
        except Exception as e:
            results["success"] = False
            results["error"] = str(e)
            print(f"❌ Problem-solving failed: {e}")
        
        finally:
            conversation_tracker.end_conversation(
                conversation_id,
                "Problem-solving chain scenario completed"
            )
        
        return results
    
    def save_scenario_results(self, results: Dict[str, Any]) -> str:
        """Save scenario results to file"""
        # Ensure conversations directory exists
        conversations_dir = Path("generated/conversations")
        conversations_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = conversations_dir / f"scenario_{results['scenario']}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"💾 Scenario results saved to {filename}")
        return str(filename)


async def main():
    """Interactive scenario runner"""
    scenarios = MultiAgentScenarios()
    
    print("🎭 Multi-Agent Scenarios")
    print("=" * 40)
    print("Choose a scenario:")
    print("1. Collaborative Research")
    print("2. Debate Discussion") 
    print("3. Problem-Solving Chain")
    print("4. Run All Scenarios")
    print("-" * 40)
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        topic = input("Enter research topic: ").strip()
        results = await scenarios.scenario_collaborative_research(topic)
        scenarios.save_scenario_results(results)
        
    elif choice == "2":
        topic = input("Enter debate topic: ").strip()
        position_a = input("Enter position A: ").strip()
        position_b = input("Enter position B: ").strip()
        results = await scenarios.scenario_debate_discussion(topic, position_a, position_b)
        scenarios.save_scenario_results(results)
        
    elif choice == "3":
        problem = input("Enter problem to solve: ").strip()
        results = await scenarios.scenario_problem_solving_chain(problem)
        scenarios.save_scenario_results(results)
        
    elif choice == "4":
        print("\n🚀 Running all scenarios...\n")
        
        # Run all scenarios with example inputs
        scenarios_to_run = [
            ("collaborative_research", "artificial intelligence in healthcare"),
            ("debate_discussion", "remote work vs office work", "Remote work increases productivity", "Office work promotes collaboration"),
            ("problem_solving_chain", "How to reduce customer churn in a SaaS business")
        ]
        
        for scenario_type, *args in scenarios_to_run:
            print(f"\n{'='*60}")
            if scenario_type == "collaborative_research":
                results = await scenarios.scenario_collaborative_research(args[0])
            elif scenario_type == "debate_discussion": 
                results = await scenarios.scenario_debate_discussion(args[0], args[1], args[2])
            elif scenario_type == "problem_solving_chain":
                results = await scenarios.scenario_problem_solving_chain(args[0])
            
            scenarios.save_scenario_results(results)
    
    else:
        print("Invalid choice")
    
    # Show session report
    print(f"\n📊 Session Report:")
    print(conversation_tracker.get_session_report())


if __name__ == "__main__":
    asyncio.run(main())