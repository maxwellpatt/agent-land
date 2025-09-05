from typing import List, Optional

from pydantic_ai import RunContext

from ...core.base_agent import BaseAgent
from ...core.dependencies import ResearchDependencies
from ...core.models import ResearchResult


class ResearchAgent(BaseAgent[ResearchDependencies, ResearchResult]):
    def __init__(self, model: Optional[str] = None):
        instructions = """
        You are a research assistant specialized in gathering and analyzing information.
        Use available tools to search for relevant information and provide comprehensive,
        well-sourced answers. Always cite your sources and indicate the confidence level
        of your findings.
        """
        
        super().__init__(
            name="research_agent",
            model=model,
            instructions=instructions,
            deps_type=ResearchDependencies,
            output_type=ResearchResult,
        )
    
    def _register_tools(self) -> None:
        @self.agent.tool
        async def search_information(ctx: RunContext[ResearchDependencies], query: str) -> str:
            """Search for information using available sources"""
            if not ctx.deps or not ctx.deps.search_enabled:
                return "Search is not enabled for this session"
            
            # Placeholder for actual search implementation
            # In a real implementation, this would call external APIs
            results = [
                f"Mock search result 1 for '{query}'",
                f"Mock search result 2 for '{query}'",
                f"Mock search result 3 for '{query}'"
            ]
            
            return f"Found {len(results)} results for '{query}':\n" + "\n".join(f"- {result}" for result in results)
        
        @self.agent.tool
        async def analyze_sources(ctx: RunContext[ResearchDependencies], sources: List[str]) -> str:
            """Analyze and evaluate the credibility of sources"""
            if not sources:
                return "No sources provided for analysis"
            
            analysis = f"Analyzed {len(sources)} sources:\n"
            for i, source in enumerate(sources, 1):
                # Mock analysis - in practice, this would be more sophisticated
                credibility = "High" if "edu" in source or "gov" in source else "Medium"
                analysis += f"{i}. {source} - Credibility: {credibility}\n"
            
            return analysis
        
        @self.agent.tool
        async def synthesize_findings(ctx: RunContext[ResearchDependencies], findings: List[str]) -> str:
            """Synthesize multiple findings into a coherent summary"""
            if not findings:
                return "No findings to synthesize"
            
            summary = f"Synthesis of {len(findings)} findings:\n"
            
            # Group similar findings (mock implementation)
            themes = {}
            for finding in findings:
                theme = finding.split()[0] if finding.split() else "General"
                if theme not in themes:
                    themes[theme] = []
                themes[theme].append(finding)
            
            for theme, theme_findings in themes.items():
                summary += f"\n{theme.title()} theme:\n"
                for finding in theme_findings:
                    summary += f"- {finding}\n"
            
            return summary


# Create a global instance for easy import
research_agent = ResearchAgent()