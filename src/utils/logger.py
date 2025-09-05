import asyncio
import functools
import time
from typing import Any, Callable, Optional

from ..config.logging import logger as base_logger


def log_execution_time(func_name: Optional[str] = None):
    """Decorator to log function execution time"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            name = func_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                base_logger.debug(f"{name} completed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                base_logger.error(f"{name} failed after {execution_time:.3f}s: {e}")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            name = func_name or f"{func.__module__}.{func.__name__}"
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                base_logger.debug(f"{name} completed in {execution_time:.3f}s")
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                base_logger.error(f"{name} failed after {execution_time:.3f}s: {e}")
                raise

        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def log_agent_interaction(agent_name: str, action: str):
    """Log agent interactions with structured format"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            base_logger.info(f"[{agent_name}] Starting {action}")
            try:
                result = await func(*args, **kwargs)
                base_logger.info(f"[{agent_name}] {action} completed successfully")
                return result
            except Exception as e:
                base_logger.error(f"[{agent_name}] {action} failed: {e}")
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            base_logger.info(f"[{agent_name}] Starting {action}")
            try:
                result = func(*args, **kwargs)
                base_logger.info(f"[{agent_name}] {action} completed successfully")
                return result
            except Exception as e:
                base_logger.error(f"[{agent_name}] {action} failed: {e}")
                raise

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def log_tool_usage(tool_name: str):
    """Log tool usage with parameters and results"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            base_logger.debug(
                f"[TOOL:{tool_name}] Called with args: {args}, kwargs: {kwargs}"
            )
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
                execution_time = time.time() - start_time
                base_logger.debug(
                    f"[TOOL:{tool_name}] Completed in {execution_time:.3f}s"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                base_logger.error(
                    f"[TOOL:{tool_name}] Failed after {execution_time:.3f}s: {e}"
                )
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            base_logger.debug(
                f"[TOOL:{tool_name}] Called with args: {args}, kwargs: {kwargs}"
            )
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                base_logger.debug(
                    f"[TOOL:{tool_name}] Completed in {execution_time:.3f}s"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                base_logger.error(
                    f"[TOOL:{tool_name}] Failed after {execution_time:.3f}s: {e}"
                )
                raise

        import asyncio

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class ContextualLogger:
    """Logger with contextual information"""

    def __init__(self, context: str):
        self.context = context
        self.logger = base_logger

    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self.logger.info(f"[{self.context}] {message}", **kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message with context"""
        self.logger.debug(f"[{self.context}] {message}", **kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message with context"""
        self.logger.warning(f"[{self.context}] {message}", **kwargs)

    def error(self, message: str, **kwargs):
        """Log error message with context"""
        self.logger.error(f"[{self.context}] {message}", **kwargs)

    def critical(self, message: str, **kwargs):
        """Log critical message with context"""
        self.logger.critical(f"[{self.context}] {message}", **kwargs)


def get_contextual_logger(context: str) -> ContextualLogger:
    """Get a logger with specific context"""
    return ContextualLogger(context)
