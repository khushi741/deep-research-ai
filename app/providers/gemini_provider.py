import os
import json
import re
from typing import Type, TypeVar, Optional, Any
from pydantic import BaseModel, ValidationError

from app.config import settings
from app.providers.base import BaseLLMProvider
from app.utils.logging import get_logger

logger = get_logger("gemini_provider")

T = TypeVar("T", bound=BaseModel)


class GeminiLLMProvider(BaseLLMProvider):
    """
    Google Gemini Provider implementation using Google GenAI SDK.
    Supports structured output validation with fallback JSON cleaning.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        self.model_name = model_name or settings.GEMINI_MODEL or "gemini-2.5-flash"
        self._client = None
        
        if self.api_key:
            try:
                # Try official new google-genai SDK first
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                self._sdk_type = "genai"
                logger.info(f"Initialized Google GenAI client with model: {self.model_name}")
            except ImportError:
                try:
                    # Fallback to google.generativeai
                    import google.generativeai as genai_legacy
                    genai_legacy.configure(api_key=self.api_key)
                    self._client = genai_legacy
                    self._sdk_type = "legacy"
                    logger.info(f"Initialized legacy google.generativeai client with model: {self.model_name}")
                except Exception as e:
                    logger.warning(f"Failed to initialize Gemini SDK: {str(e)}")
                    self._client = None

    def is_available(self) -> bool:
        return self.api_key is not None and self._client is not None

    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        if not self.is_available():
            raise RuntimeError(
                "Gemini API Key is not configured. Please set GEMINI_API_KEY in your environment or .env file."
            )

        try:
            if self._sdk_type == "genai":
                config = {}
                if system_instruction:
                    config["system_instruction"] = system_instruction
                
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=prompt,
                    config=config if config else None
                )
                return response.text or ""
            else:
                # Legacy SDK fallback
                full_prompt = f"{system_instruction}\n\n{prompt}" if system_instruction else prompt
                model = self._client.GenerativeModel(self.model_name)
                response = model.generate_content(full_prompt)
                return response.text or ""
        except Exception as e:
            logger.error(f"Gemini API text generation error: {str(e)}")
            raise RuntimeError(f"Gemini LLM error: {str(e)}") from e

    def generate_structured(
        self, 
        prompt: str, 
        response_schema: Type[T], 
        system_instruction: Optional[str] = None
    ) -> T:
        if not self.is_available():
            raise RuntimeError(
                "Gemini API Key is not configured. Please set GEMINI_API_KEY in your environment or .env file."
            )

        schema_json = json.dumps(response_schema.model_json_schema(), indent=2)
        structured_prompt = (
            f"{prompt}\n\n"
            f"CRITICAL REQUIREMENT: Return ONLY a valid JSON object matching this exact Pydantic JSON Schema.\n"
            f"Do not include any extra text, preamble, markdown formatting outside of JSON code blocks, or commentary.\n\n"
            f"Target JSON Schema:\n{schema_json}"
        )

        sys_inst = system_instruction or "You are a precise data extractor returning valid JSON adhering strictly to schemas."

        try:
            if self._sdk_type == "genai":
                response = self._client.models.generate_content(
                    model=self.model_name,
                    contents=structured_prompt,
                    config={
                        "system_instruction": sys_inst,
                        "response_mime_type": "application/json",
                    }
                )
                raw_text = response.text or "{}"
            else:
                model = self._client.GenerativeModel(self.model_name)
                full_prompt = f"{sys_inst}\n\n{structured_prompt}"
                response = model.generate_content(
                    full_prompt,
                    generation_config={"response_mime_type": "application/json"}
                )
                raw_text = response.text or "{}"

            # Parse and validate JSON
            cleaned_json = self._clean_json_string(raw_text)
            data = json.loads(cleaned_json)
            return response_schema.model_validate(data)
            
        except ValidationError as ve:
            logger.error(f"Pydantic schema validation error: {str(ve)}")
            # Retry parsing attempt with extra cleanup if possible
            raise ValueError(f"Failed to validate response against schema {response_schema.__name__}: {str(ve)}") from ve
        except Exception as e:
            logger.error(f"Error during structured generation: {str(e)}")
            raise RuntimeError(f"Structured LLM generation failed: {str(e)}") from e

    @staticmethod
    def _clean_json_string(raw_text: str) -> str:
        """Strips markdown ```json wrapper if returned."""
        text = raw_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\n?", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\n?```$", "", text)
        return text.strip()
