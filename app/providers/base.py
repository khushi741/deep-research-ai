from abc import ABC, abstractmethod
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseLLMProvider(ABC):
    """Abstract interface for LLM operations used by agents."""

    @abstractmethod
    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """Generate plain text output from prompt."""
        pass

    @abstractmethod
    def generate_structured(
        self, 
        prompt: str, 
        response_schema: Type[T], 
        system_instruction: Optional[str] = None
    ) -> T:
        """Generate validated Pydantic object from prompt using schema."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Return True if the LLM provider is properly configured and accessible."""
        pass
