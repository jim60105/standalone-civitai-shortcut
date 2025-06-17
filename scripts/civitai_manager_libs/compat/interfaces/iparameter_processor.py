"""
Parameter Processor Interface

Provides unified parameter processing across execution modes.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class IParameterProcessor(ABC):
    """Abstract interface for parameter processing across different execution modes."""
    
    @abstractmethod
    def parse_parameters(self, text: str) -> Dict[str, Any]:
        """
        Parse parameters string into structured data.
        
        Args:
            text (str): Raw parameters text
            
        Returns:
            Dict[str, Any]: Parsed parameters as key-value pairs
        """
        pass
    
    @abstractmethod
    def format_parameters(self, params: Dict[str, Any]) -> str:
        """
        Format parameters dictionary into text string.
        
        Args:
            params (Dict[str, Any]): Parameters dictionary
            
        Returns:
            str: Formatted parameters string
        """
        pass
    
    @abstractmethod
    def extract_prompt_and_negative(self, text: str) -> tuple[str, str]:
        """
        Extract positive and negative prompts from parameters text.
        
        Args:
            text (str): Raw parameters text containing prompts
            
        Returns:
            tuple[str, str]: (positive_prompt, negative_prompt)
        """
        pass
    
    @abstractmethod
    def validate_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize parameters.
        
        Args:
            params (Dict[str, Any]): Parameters to validate
            
        Returns:
            Dict[str, Any]: Validated parameters
        """
        pass
    
    @abstractmethod
    def merge_parameters(self, base_params: Dict[str, Any], override_params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge two parameter dictionaries with override taking precedence.
        
        Args:
            base_params (Dict[str, Any]): Base parameters
            override_params (Dict[str, Any]): Override parameters
            
        Returns:
            Dict[str, Any]: Merged parameters
        """
        pass
