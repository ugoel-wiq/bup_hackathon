from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from typing import Dict, Any
import json
from config import settings
from schema import ModelResponse
from templates import JSON_RESPONSE_TEMPLATE
import logging

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        try:
            self.llm = ChatGoogleGenerativeAI(
                model=settings.model_name,
                temperature=settings.temperature,
                max_output_tokens=settings.max_output_tokens,
                google_api_key=settings.google_api_key
            )
            self.json_parser = StrOutputParser()
        except Exception as e:
            logger.error(f"Error initializing Gemini client: {str(e)}")
            raise
    
    async def process_prompt(self, prompt: str, json_structure: Dict[str, Any]) -> ModelResponse:
        prompt_template = ChatPromptTemplate.from_template(JSON_RESPONSE_TEMPLATE)
        
        chain = (
            prompt_template 
            | self.llm 
            | StrOutputParser()
        )
        
        try:
            result = await chain.ainvoke({
                "prompt": prompt,
                "json_structure": json.dumps(json_structure, indent=2)
            })
            
            # Clean the response to ensure it only contains JSON
            result = result.strip()
            if result.startswith('```json'):
                result = result[7:]
            if result.endswith('```'):
                result = result[:-3]
            result = result.strip()
            
            try:
                parsed_response = json.loads(result)
            except json.JSONDecodeError as je:
                logger.error(f"JSON parsing error: {str(je)}\nResponse was: {result}")
                raise Exception(f"Failed to parse LLM response as JSON: {str(je)}")
            
            return ModelResponse(
                response=parsed_response,
                raw_response=result
            )
        except Exception as e:
            logger.error(f"Error in process_prompt: {str(e)}")
            raise