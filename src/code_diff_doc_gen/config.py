"""Configuration settings for the application."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Optional

from loguru import logger


@dataclass
class AppConfig:
    """Application configuration."""

    output_dir: Path = field(default_factory=lambda: Path(".codediff"))
    model: str = "claude-3-7-sonnet-20250219"
    max_tokens: int = 20000
    thinking_budget: int = 10000

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Create config from environment variables."""
        output_dir = os.getenv("CODEDIFF_OUTPUT_DIR", ".codediff")
        model = os.getenv("CODEDIFF_MODEL", "claude-3-7-sonnet-20250219")

        return cls(
            output_dir=Path(output_dir),
            model=model,
        )


@dataclass
class AppState:
    """Application state tracking."""

    total_usage: Dict = field(
        default_factory=lambda: {
            "input_tokens": 0,
            "output_tokens": 0,
            "cache_creation_input_tokens": 0,
            "cache_read_input_tokens": 0,
            "cost": 0.0,
        }
    )


config = AppConfig.from_env()
state = AppState()


def update_usage_stats(completion_usage):
    """Update cumulative usage statistics."""
    # Update token counts
    state.total_usage["input_tokens"] += completion_usage.input_tokens
    state.total_usage["output_tokens"] += completion_usage.output_tokens
    state.total_usage["cache_creation_input_tokens"] += completion_usage.cache_creation_input_tokens
    state.total_usage["cache_read_input_tokens"] += completion_usage.cache_read_input_tokens

    # Calculate costs based on Claude 3.7 Sonnet pricing
    input_cost = completion_usage.input_tokens * 0.000003
    cache_write_cost = completion_usage.cache_creation_input_tokens * 0.00000375
    cache_hit_cost = completion_usage.cache_read_input_tokens * 0.0000003
    output_cost = completion_usage.output_tokens * 0.000015
    total_cost = input_cost + cache_write_cost + cache_hit_cost + output_cost

    # Add to total cost
    state.total_usage["cost"] += total_cost

    # Log current call usage
    logger.info(
        f"Call usage: {completion_usage.input_tokens:,} in / "
        f"{completion_usage.output_tokens:,} out / "
        f"cache: {completion_usage.cache_creation_input_tokens:,} write / "
        f"{completion_usage.cache_read_input_tokens:,} read / "
        f"${total_cost:.4f}"
    )

    # Log cumulative usage
    logger.info(
        f"Total usage: {state.total_usage['input_tokens']:,} in / "
        f"{state.total_usage['output_tokens']:,} out / "
        f"cache: {state.total_usage['cache_creation_input_tokens']:,} write / "
        f"{state.total_usage['cache_read_input_tokens']:,} read / "
        f"${state.total_usage['cost']:.4f}"
    )
