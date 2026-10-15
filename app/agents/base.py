from abc import ABC
from app.providers.base import BaseLLMProvider
from app.utils.logging import get_logger


class BaseAgent(ABC):
    """Base class for all research agents in the system."""

    def __init__(self, llm_provider: BaseLLMProvider):
        self.llm = llm_provider
        self.logger = get_logger(self.__class__.__name__)
