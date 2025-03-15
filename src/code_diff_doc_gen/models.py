"""Pydantic models for API responses."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """Token usage tracking."""
    
    input_tokens: int = Field(0, description="Input tokens used")
    output_tokens: int = Field(0, description="Output tokens generated")
    cache_creation_input_tokens: int = Field(0, description="Tokens used for cache creation")
    cache_read_input_tokens: int = Field(0, description="Tokens read from cache")


class CodeAnalysis(BaseModel):
    """Code pair showing incorrect vs correct implementation."""
    
    bad_code: str = Field(..., description="Example of problematic code pattern")
    good_code: str = Field(..., description="Example of improved code pattern")
    
    
class CodePair(BaseModel):
    """A single code comparison example."""
    
    bad_code: str = Field(..., description="The problematic generated code")
    good_code: str = Field(..., description="The correct original code implementation")


class CodeAnalysisResult(BaseModel):
    """Result of code analysis."""
    
    pairs: List[CodePair] = Field(
        default_factory=list,
        description="Pairs of bad/good code examples showing specific improvements"
    )


class FileDescription(BaseModel):
    """Description of a source file."""
    
    description: str = Field(..., description="Natural language description of the file")


class GeneratedCode(BaseModel):
    """Generated code implementation."""
    
    implementation: str = Field(..., description="Generated code implementation")