import asyncio
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union


def generate_session_id() -> str:
    """Generate a unique session ID"""
    return str(uuid.uuid4())


def generate_conversation_id() -> str:
    """Generate a unique conversation ID"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    short_uuid = str(uuid.uuid4())[:8]
    return f"conv_{timestamp}_{short_uuid}"


def safe_get_nested(data: Dict[str, Any], keys: List[str], default: Any = None) -> Any:
    """Safely get a nested value from a dictionary"""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def flatten_dict(data: Dict[str, Any], parent_key: str = "", separator: str = ".") -> Dict[str, Any]:
    """Flatten a nested dictionary"""
    items = []
    for key, value in data.items():
        new_key = f"{parent_key}{separator}{key}" if parent_key else key
        
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, separator).items())
        else:
            items.append((new_key, value))
    
    return dict(items)


def chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
    """Split a list into chunks of specified size"""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def sanitize_string(text: str, max_length: Optional[int] = None, allowed_chars: Optional[str] = None) -> str:
    """Sanitize a string for safe use"""
    if not isinstance(text, str):
        text = str(text)
    
    # Remove or replace problematic characters
    sanitized = text.strip()
    
    if allowed_chars:
        # Keep only allowed characters
        sanitized = "".join(c for c in sanitized if c in allowed_chars)
    
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def format_timestamp(dt: Optional[datetime] = None, format_string: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a timestamp"""
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_string)


def parse_model_string(model_string: str) -> Dict[str, str]:
    """Parse a model string like 'openai:gpt-4o' into provider and model"""
    if ":" in model_string:
        provider, model = model_string.split(":", 1)
        return {"provider": provider, "model": model}
    else:
        return {"provider": "unknown", "model": model_string}


def merge_dicts(*dicts: Dict[str, Any], deep: bool = True) -> Dict[str, Any]:
    """Merge multiple dictionaries"""
    result = {}
    
    for d in dicts:
        if not isinstance(d, dict):
            continue
            
        for key, value in d.items():
            if key in result and deep and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = merge_dicts(result[key], value, deep=True)
            else:
                result[key] = value
    
    return result


def validate_api_key(api_key: Optional[str], min_length: int = 10) -> bool:
    """Validate that an API key looks reasonable"""
    if not api_key or not isinstance(api_key, str):
        return False
    
    # Basic validation
    api_key = api_key.strip()
    if len(api_key) < min_length:
        return False
    
    # Check for placeholder values
    placeholder_values = [
        "your_api_key_here",
        "your_openai_api_key_here",
        "your_anthropic_api_key_here",
        "sk-placeholder",
        "api_key_placeholder"
    ]
    
    if api_key.lower() in [p.lower() for p in placeholder_values]:
        return False
    
    return True


async def run_with_timeout(coro, timeout_seconds: float, default_result: Any = None) -> Any:
    """Run a coroutine with a timeout"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout_seconds)
    except asyncio.TimeoutError:
        return default_result


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to a maximum length"""
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Try to extract JSON from a text string"""
    import json
    import re
    
    # Look for JSON-like patterns
    json_patterns = [
        r'\{[^{}]*\}',  # Simple object
        r'\{.*\}',      # Complex object (greedy)
    ]
    
    for pattern in json_patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
    
    return None


def calculate_text_similarity(text1: str, text2: str) -> float:
    """Calculate simple text similarity (Jaccard similarity)"""
    if not text1 or not text2:
        return 0.0
    
    # Simple word-based similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 and not words2:
        return 1.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


class RetryConfig:
    """Configuration for retry logic"""
    def __init__(self, max_attempts: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
        self.max_attempts = max_attempts
        self.delay = delay
        self.backoff_factor = backoff_factor


async def retry_async(func, *args, config: Optional[RetryConfig] = None, **kwargs) -> Any:
    """Retry an async function with exponential backoff"""
    if config is None:
        config = RetryConfig()
    
    last_exception = None
    current_delay = config.delay
    
    for attempt in range(config.max_attempts):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            last_exception = e
            if attempt < config.max_attempts - 1:
                await asyncio.sleep(current_delay)
                current_delay *= config.backoff_factor
            else:
                break
    
    if last_exception:
        raise last_exception