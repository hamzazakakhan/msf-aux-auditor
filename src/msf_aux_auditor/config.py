"""Configuration loading and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator
from typing import Literal


class MsfConfig(BaseModel):
    """Metasploit RPC configuration."""
    
    host: str = Field(default="127.0.0.1", description="Metasploit RPC host")
    port: int = Field(default=55553, description="Metasploit RPC port")
    username: str = Field(default="msf", description="RPC username")
    password: str = Field(default="", description="RPC password")
    ssl: bool = Field(default=False, description="Use SSL for RPC connection")


class AIConfig(BaseModel):
    """AI analysis configuration."""
    
    enabled: bool = Field(default=False, description="Enable AI-powered analysis")
    provider: Literal["openai", "anthropic"] = Field(default="openai", description="AI provider to use")
    api_key: str = Field(default="", description="API key for AI provider (can use env vars)")
    model: str = Field(default="", description="Model to use (defaults based on provider)")


class ModuleConfig(BaseModel):
    """Configuration for auxiliary modules."""
    
    allowed_modules: list[str] = Field(default_factory=list, description="List of allowed Metasploit auxiliary modules")
    msf_config: MsfConfig = Field(default_factory=MsfConfig, description="Metasploit RPC configuration")
    ai_config: AIConfig = Field(default_factory=AIConfig, description="AI analysis configuration")
    timeout: int = Field(default=300, description="Module execution timeout in seconds")
    
    @field_validator("allowed_modules")
    @classmethod
    def validate_module_paths(cls, v: list[str]) -> list[str]:
        """Validate that module paths start with auxiliary/."""
        for module in v:
            if not module.startswith("auxiliary/"):
                raise ValueError(f"Module '{module}' must start with 'auxiliary/'")
        return v


def load_config(config_path: Path | str) -> ModuleConfig:
    """Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        ModuleConfig instance
        
    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config is invalid
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")
    
    with open(path, "r") as f:
        data = json.load(f)
    
    return ModuleConfig(**data)
