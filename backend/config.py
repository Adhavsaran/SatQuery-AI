"""SatQuery Backend Configuration

Loads settings from environment variables with sensible defaults.
"""

from pydantic_settings import BaseSettings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application configuration from .env or environment variables."""

    # Backend
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    environment: str = "development"
    debug: bool = True

    # LLM Configuration
    llm_provider: str = "openai"
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4o"
    deepseek_api_key: Optional[str] = None
    deepseek_model: str = "deepseek-chat"
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-3-5-sonnet-20241022"
    google_api_key: Optional[str] = None
    google_model: str = "gemini-1.5-pro"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "mistral"

    # VLM Configuration
    vlm_provider: str = "huggingface"
    vlm_model: str = "google/flan-t5-base"  # Placeholder - will use proper VLM

    # Data Directories
    data_dir: str = "./data/input"
    output_dir: str = "./data/output"
    temp_dir: str = "./data/temp"

    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = "./logs/satquery.log"

    # Features
    enable_cache: bool = True
    enable_profiling: bool = False
    enable_execution_trace: bool = True

    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"  # Allow extra fields from env

    def get_llm_config(self) -> dict:
        """Get LLM provider configuration."""
        if self.llm_provider == "openai":
            return {
                "provider": "openai",
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "base_url": "https://api.openai.com/v1",
            }
        elif self.llm_provider == "deepseek":
            return {
                "provider": "deepseek",
                "api_key": self.deepseek_api_key,
                "model": self.deepseek_model,
                "base_url": "https://api.deepseek.com/v1",
            }
        elif self.llm_provider == "anthropic":
            return {
                "provider": "anthropic",
                "api_key": self.anthropic_api_key,
                "model": self.anthropic_model,
            }
        elif self.llm_provider == "google":
            return {
                "provider": "google",
                "api_key": self.google_api_key,
                "model": self.google_model,
            }
        elif self.llm_provider == "ollama":
            return {
                "provider": "ollama",
                "base_url": self.ollama_base_url,
                "model": self.ollama_model,
            }
        else:
            raise ValueError(f"Unknown LLM provider: {self.llm_provider}")

    def validate(self) -> None:
        """Validate configuration."""
        if self.llm_provider != "ollama":
            api_key_field = f"{self.llm_provider}_api_key"
            api_key = getattr(self, api_key_field, None)
            if not api_key:
                logger.warning(
                    f"API key not set for {self.llm_provider}. "
                    f"Set {api_key_field.upper()} environment variable."
                )


# Global settings instance
settings = Settings()
