from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None


class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)


class ChatResponse(BaseResponse):
    message: str
    conversation_id: Optional[str] = None


class ToolResult(BaseModel):
    tool_name: str
    result: Any
    success: bool = True
    error: Optional[str] = None
    execution_time: Optional[float] = None


class AgentResult(BaseResponse):
    result: Any
    tools_used: List[ToolResult] = Field(default_factory=list)
    reasoning: Optional[str] = None


class ResearchResult(BaseResponse):
    query: str
    findings: List[str]
    sources: List[str] = Field(default_factory=list)
    confidence: Optional[float] = None


class AnalysisResult(BaseResponse):
    analysis: str
    insights: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    data_summary: Optional[Dict[str, Any]] = None