import httpx
from typing import Dict, Any, Callable, TypeVar, Awaitable
from fastapi import status
import time
from functools import wraps

from app.core.config import settings
from app.exception.http_exception import UserNotFoundException, BookNotFoundException, NoAvailableCopiesException, ServiceUnavailableException

T = TypeVar('T')

class CircuitBreaker:
    def __init__(self, name: str, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
    
    def record_success(self):
        self.failure_count = 0
        self.state = "CLOSED"
    
    def is_circuit_open(self) -> bool:
        if self.state == "CLOSED":
            return False
        
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF-OPEN"
                return False
            return True
        
        return False

user_service_breaker = CircuitBreaker("UserService")
book_service_breaker = CircuitBreaker("BookService")

def circuit_breaker(breaker: CircuitBreaker, fallback_value=None, excluded_exceptions=None):
    if excluded_exceptions is None:
        excluded_exceptions = []
    
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            if breaker.is_circuit_open():
                print(f"Circuit {breaker.name} is OPEN - failing fast")
                raise ServiceUnavailableException(breaker.name)
            
            try:
                result = await func(*args, **kwargs)
                if breaker.state == "HALF-OPEN":
                    breaker.record_success()
                return result
            except tuple(excluded_exceptions) as e:
                raise e
            except Exception as e:
                breaker.record_failure()
                print(f"Circuit {breaker.name} failure: {str(e)}")
                raise e
        
        return wrapper
    
    return decorator

class ExternalServiceClient:
    @staticmethod
    @circuit_breaker(user_service_breaker, excluded_exceptions=[UserNotFoundException])
    async def get_user(user_id: int) -> Dict[str, Any]:
        url = f"{settings.USER_SERVICE_URL}/api/users/{user_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    raise UserNotFoundException()
                elif response.status_code != status.HTTP_200_OK:
                    raise ServiceUnavailableException("User")
                
                return response.json()
        except httpx.RequestError:
            raise ServiceUnavailableException("User")
    
    @staticmethod
    @circuit_breaker(book_service_breaker, excluded_exceptions=[BookNotFoundException])
    async def get_book(book_id: int) -> Dict[str, Any]:
        url = f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}"
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=5.0)
                
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    raise BookNotFoundException()
                elif response.status_code != status.HTTP_200_OK:
                    raise ServiceUnavailableException("Book")
                
                return response.json()
        except httpx.RequestError:
            raise ServiceUnavailableException("Book")
    
    @staticmethod
    @circuit_breaker(book_service_breaker, excluded_exceptions=[BookNotFoundException, NoAvailableCopiesException])
    async def update_book_availability(book_id: int, operation: str, copies: int = 1) -> Dict[str, Any]:
        url = f"{settings.BOOK_SERVICE_URL}/api/books/{book_id}/availability"
        data = {
            "available_copies": copies,
            "operation": operation
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(url, json=data, timeout=5.0)
                
                if response.status_code == status.HTTP_404_NOT_FOUND:
                    raise BookNotFoundException()
                elif response.status_code == status.HTTP_400_BAD_REQUEST:
                    raise NoAvailableCopiesException()
                elif response.status_code != status.HTTP_200_OK:
                    raise ServiceUnavailableException("Book")
                
                return response.json()
        except httpx.RequestError:
            raise ServiceUnavailableException("Book")
