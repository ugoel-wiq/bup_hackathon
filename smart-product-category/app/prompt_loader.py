from pathlib import Path
import logging
from typing import Dict, Any, Optional
import os

logger = logging.getLogger(__name__)

class PromptLoader:
    """Utility class to load prompts from text files."""
    
    def __init__(self, prompts_dir: str = "prompts"):
        """Initialize the prompt loader.
        
        Args:
            prompts_dir: Directory containing prompt files
        """
        base_path = Path(__file__).parent
        self.prompts_dir = base_path / prompts_dir
        
        # Ensure the prompts directory exists
        if not self.prompts_dir.exists():
            logger.warning(f"Prompts directory not found: {self.prompts_dir}")
            self.prompts_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created prompts directory: {self.prompts_dir}")
    
    def load_prompt(self, prompt_name: str, variables: Optional[Dict[str, Any]] = None) -> str:
        """Load a prompt from file and inject variables if provided.
        
        Args:
            prompt_name: Name of the prompt file (without extension)
            variables: Dictionary of variables to format into the prompt
            
        Returns:
            Formatted prompt string
            
        Raises:
            FileNotFoundError: If prompt file is not found
            KeyError: If a required variable is missing
        """
        try:
            prompt_path = self.prompts_dir / f"{prompt_name}.txt"
            
            if not prompt_path.exists():
                logger.error(f"Prompt file not found: {prompt_path}")
                raise FileNotFoundError(f"Prompt '{prompt_name}' not found at {prompt_path}")
                
            with open(prompt_path, 'r') as f:
                prompt_template = f.read()
            
            if variables:
                try:
                    return prompt_template.format(**variables)
                except KeyError as e:
                    logger.error(f"Missing required variable in prompt '{prompt_name}': {e}")
                    raise KeyError(f"Missing required variable in prompt '{prompt_name}': {e}")
            
            return prompt_template
            
        except Exception as e:
            if isinstance(e, (FileNotFoundError, KeyError)):
                raise
            logger.error(f"Error loading prompt '{prompt_name}': {str(e)}")
            raise ValueError(f"Failed to load prompt '{prompt_name}': {str(e)}")