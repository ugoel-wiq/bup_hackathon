
from pathlib import Path
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class PromptLoader:
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = Path(__file__).parent / prompts_dir
    
    def load_prompt(self, prompt_name: str, variables: Dict[str, Any] = None) -> str:
        """Load a prompt from file and inject variables if provided"""
        try:
            prompt_path = self.prompts_dir / f"{prompt_name}.txt"
            with open(prompt_path, 'r') as f:
                prompt_template = f.read()
            
            if variables:
                return prompt_template.format(**variables)
            return prompt_template
            
        except FileNotFoundError:
            logger.error(f"Prompt file not found: {prompt_name}")
            raise
        except KeyError as e:
            logger.error(f"Missing required variable in prompt: {e}")
            raise