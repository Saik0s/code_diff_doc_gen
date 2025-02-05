"""LLM interaction module using OpenAI.

Provides a simple interface for interacting with OpenAI's language models.
"""

import os
from typing import List, Optional
from dataclasses import dataclass
from openai import OpenAI
from loguru import logger


@dataclass
class Message:
    """Represents a chat message."""

    role: str
    content: str


class LLMClient:
    """Simple wrapper for OpenAI API interactions."""

    def __init__(self, model: str = "gpt-4o"):
        """Initialize OpenAI client.

        Args:
            model: OpenAI model to use

        Raises:
            ValueError: If OPENAI_API_KEY environment variable is not set
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable must be set")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def complete(
        self,
        messages: List[Message],
        temperature: float = 0,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Complete a chat conversation.

        Args:
            messages: List of chat messages
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text response

        Raises:
            Exception: If API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
