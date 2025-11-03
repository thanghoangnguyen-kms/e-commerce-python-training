"""
Service decorator for dependency injection pattern.
Replaces @staticmethod with a more testable and flexible approach.
"""
from functools import wraps
from typing import Callable, Any


def service_method(func: Callable) -> Callable:
    """
    Decorator for service methods to support dependency injection.
    
    This replaces @staticmethod and allows service methods to work with
    injected dependencies (like repositories) while maintaining a clean API.
    
    Usage:
        class MyService:
            def __init__(self, repository: MyRepository):
                self.repository = repository
            
            @service_method
            async def my_method(self, param: str):
                return await self.repository.find_by_param(param)
    """
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Any:
        return await func(*args, **kwargs)
    
    return wrapper

