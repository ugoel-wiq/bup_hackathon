from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any, Optional
import json
import backoff
import logging
from config import settings
from schema import ModelResponse
from templates import ENHANCED_JSON_RESPONSE_TEMPLATE

logger = logging.getLogger(__name__)

class GeminiClient:
    """Client for interacting with Google's Gemini AI model."""
    
    def __init__(self, 
                 model_name: Optional[str] = None, 
                 temperature: Optional[float] = None,
                 max_output_tokens: Optional[int] = None,
                 api_key: Optional[str] = None):
        """Initialize the Gemini client.
        
        Args:
            model_name: Name of the Gemini model to use (defaults to config setting)
            temperature: Temperature setting for generation (defaults to config setting)
            max_output_tokens: Max tokens to generate (defaults to config setting)
            api_key: Google API key (defaults to config setting)
        
        Raises:
            ValueError: If API key is not provided and not in settings
        """
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=model_name or settings.model_name,
                temperature=temperature or settings.temperature,
                max_output_tokens=max_output_tokens or settings.max_output_tokens,
                google_api_key=api_key or settings.google_api_key
            )
            self.json_parser = StrOutputParser()
        except Exception as e:
            logger.error(f"Error initializing Gemini client: {str(e)}")
            raise ValueError(f"Failed to initialize Gemini client: {str(e)}")
    
    @staticmethod
    def _clean_json_response(result: str) -> str:
        """Clean the model response to ensure it's valid JSON.
        
        Args:
            result: Raw string response from the model
            
        Returns:
            Cleaned JSON string
        """
        result = result.strip()
        
        # Remove markdown code block markers if present
        if result.startswith('```json'):
            result = result[7:]
        elif result.startswith('```'):
            result = result[3:]
            
        if result.endswith('```'):
            result = result[:-3]
            
        return result.strip()
    
    @backoff.on_exception(
        backoff.expo,
        (ValueError, ConnectionError, TimeoutError),
        max_tries=3
    )
    async def process_prompt(self, prompt: str, json_structure: Dict[str, Any]) -> ModelResponse:
        """Process a prompt with the Gemini model and return structured response.
        
        Args:
            prompt: The input prompt to process
            json_structure: Expected JSON structure for the response
            
        Returns:
            ModelResponse containing parsed response and raw response
            
        Raises:
            ValueError: If the model fails to generate a valid JSON response
        """
        prompt_template = ChatPromptTemplate.from_template(ENHANCED_JSON_RESPONSE_TEMPLATE)
        
        chain = (
            prompt_template 
            | self.llm 
            | StrOutputParser()
        )
        
        try:
            logger.debug(f"Sending prompt to Gemini: {prompt[:100]}...")
            result = await chain.ainvoke({
                "prompt": prompt,
                "json_structure": json.dumps(json_structure, indent=2)
            })
            
            # Clean the response to ensure it only contains JSON
            cleaned_result = self._clean_json_response(result)
            
            try:
                parsed_response = json.loads(cleaned_result)
                logger.debug("Successfully parsed JSON response from Gemini")
            except json.JSONDecodeError as je:
                logger.error(f"JSON parsing error: {str(je)}\nCleaned response: {cleaned_result}")
                raise ValueError(f"Failed to parse LLM response as JSON: {str(je)}")
            
            return ModelResponse(
                response=parsed_response,
                raw_response=cleaned_result
            )
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            logger.error(f"Error in process_prompt: {str(e)}")
            raise ValueError(f"Failed to process prompt: {str(e)}")