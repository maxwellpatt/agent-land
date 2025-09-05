import json
from typing import Any, Dict, List, Optional

from pydantic_ai import RunContext

from ...core.base_agent import BaseAgent
from ...core.dependencies import DataDependencies
from ...core.models import AnalysisResult


class DataAnalystAgent(BaseAgent[DataDependencies, AnalysisResult]):
    def __init__(self, model: Optional[str] = None):
        instructions = """
        You are a data analyst AI assistant. You help users analyze data, identify patterns,
        generate insights, and provide actionable recommendations. Use the available tools
        to process data and perform statistical analysis. Always explain your methodology
        and assumptions clearly.
        """
        
        super().__init__(
            name="data_analyst",
            model=model,
            instructions=instructions,
            deps_type=DataDependencies,
            output_type=AnalysisResult,
        )
    
    def _register_tools(self) -> None:
        @self.agent.tool
        async def load_data(ctx: RunContext[DataDependencies], data_source: str) -> str:
            """Load data from various sources (CSV, JSON, etc.)"""
            if not ctx.deps:
                return "No data dependencies configured"
            
            if not ctx.deps.data_path:
                return "No data path specified in dependencies"
            
            # Mock data loading - in practice, this would read actual files
            mock_data = {
                "records": 1000,
                "columns": ["id", "name", "value", "category", "timestamp"],
                "sample": [
                    {"id": 1, "name": "Item A", "value": 42.5, "category": "X"},
                    {"id": 2, "name": "Item B", "value": 38.2, "category": "Y"},
                    {"id": 3, "name": "Item C", "value": 55.1, "category": "X"}
                ]
            }
            
            return f"Loaded data from {data_source}:\n{json.dumps(mock_data, indent=2)}"
        
        @self.agent.tool
        async def calculate_statistics(ctx: RunContext[DataDependencies], column: str) -> str:
            """Calculate basic statistics for a column"""
            # Mock statistics - in practice, this would calculate real stats
            stats = {
                "column": column,
                "count": 1000,
                "mean": 45.6,
                "median": 44.2,
                "std": 12.3,
                "min": 18.5,
                "max": 78.9,
                "quartiles": [33.1, 44.2, 58.7]
            }
            
            return f"Statistics for column '{column}':\n{json.dumps(stats, indent=2)}"
        
        @self.agent.tool
        async def identify_patterns(ctx: RunContext[DataDependencies], data_summary: str) -> str:
            """Identify patterns and trends in the data"""
            # Mock pattern identification
            patterns = [
                "Strong correlation between value and category X",
                "Seasonal trend with peaks in Q2 and Q4",
                "Outliers detected in 2.3% of records",
                "Missing data pattern suggests systematic collection issues"
            ]
            
            return f"Identified patterns:\n" + "\n".join(f"- {pattern}" for pattern in patterns)
        
        @self.agent.tool
        async def generate_insights(ctx: RunContext[DataDependencies], analysis_results: str) -> str:
            """Generate business insights from analysis results"""
            insights = [
                "Category X items show 23% higher values on average",
                "Peak performance periods align with marketing campaigns",
                "Data quality issues may impact accuracy of trend analysis",
                "Opportunity exists to optimize category Y performance"
            ]
            
            return f"Key insights:\n" + "\n".join(f"- {insight}" for insight in insights)
        
        @self.agent.tool
        async def recommend_actions(ctx: RunContext[DataDependencies], insights: str) -> str:
            """Generate actionable recommendations based on insights"""
            recommendations = [
                "Implement data validation checks for improved quality",
                "Focus marketing efforts during identified peak periods",
                "Investigate success factors for category X items",
                "Establish regular monitoring for outlier detection"
            ]
            
            return f"Recommendations:\n" + "\n".join(f"- {rec}" for rec in recommendations)


# Create a global instance for easy import
data_analyst_agent = DataAnalystAgent()