from typing import Any, Dict, Optional

from pydantic import BaseModel

from ..config.settings import settings


class BaseDependencies(BaseModel):
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    context: Dict[str, Any] = {}


class ChatDependencies(BaseDependencies):
    conversation_history: list = []
    max_history: int = 50


class ResearchDependencies(BaseDependencies):
    search_enabled: bool = True
    max_results: int = 10
    search_sources: list = ["web", "documents"]


class DataDependencies(BaseDependencies):
    data_path: Optional[str] = None
    allowed_formats: list = ["csv", "json", "xlsx"]
    max_file_size: int = 100 * 1024 * 1024  # 100MB


class ToolDependencies(BaseDependencies):
    api_keys: Dict[str, str] = {}
    rate_limits: Dict[str, int] = {}
    timeout: int = 30

    def __init__(self, **data):
        super().__init__(**data)
        # Auto-populate API keys from settings
        if settings.openai_api_key:
            self.api_keys["openai"] = settings.openai_api_key
        if settings.anthropic_api_key:
            self.api_keys["anthropic"] = settings.anthropic_api_key
