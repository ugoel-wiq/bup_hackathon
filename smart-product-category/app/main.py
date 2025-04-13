from fastapi import FastAPI, HTTPException, Depends, Response, status
from fastapi.middleware.cors import CORSMiddleware
from api_models import ProductRequest, ProductResponse, HealthResponse, EnhancedProductResponse
from gemini_client import GeminiClient
from prompt_loader import PromptLoader
from woolworths_client import WoolworthsClient
from product_utils import ProductDataExtractor
import logging
from functools import lru_cache
import uvicorn
import time
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Product Categorization API",
    description="API for categorizing Woolworths products using Gemini AI",
    version="1.0.0"
)

# Add CORS middleware for API access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JSON structure for the response
JSON_STRUCTURE = {
    "type": "string",
    "variety": ["string"]
}

# JSON structure for enhanced response
ENHANCED_JSON_STRUCTURE = {
    "type": "string",
    "variety": ["string"],
    "dietary_attributes": ["string"],
    "flavor_profile": ["string"],
    "usage_occasions": ["string"],
    "health_benefits": ["string"],
    "certifications": ["string"],
    "texture": ["string"],
    "ingredients_highlight": ["string"],
    "serving_suggestions": ["string"],
    "pairings": ["string"]
}

# Dependency injection for shared components
@lru_cache(maxsize=1)
def get_prompt_loader():
    return PromptLoader()

@lru_cache(maxsize=1)
def get_gemini_client():
    return GeminiClient()

@lru_cache(maxsize=1)
def get_woolworths_client():
    return WoolworthsClient()

# Additional dependency for product data extractor
@lru_cache(maxsize=1)
def get_product_data_extractor():
    return ProductDataExtractor()

@app.post("/categorize", response_model=ProductResponse)
async def categorize_product(
    request: ProductRequest,
    response: Response,
    woolworths_client: WoolworthsClient = Depends(get_woolworths_client),
    gemini_client: GeminiClient = Depends(get_gemini_client),
    prompt_loader: PromptLoader = Depends(get_prompt_loader)
):
    """Categorize a Woolworths product using Gemini AI.
    
    Args:
        request: Product request containing product_id
        response: FastAPI response object
        woolworths_client: Injected Woolworths client
        gemini_client: Injected Gemini client
        prompt_loader: Injected prompt loader
        
    Returns:
        ProductResponse with categorization information
        
    Raises:
        HTTPException: For various error conditions
    """
    start_time = time.time()
    logger.info(f"Received categorization request for product ID: {request.product_id}")
    
    try:
        # Fetch product details from Woolworths
        product_details = await woolworths_client.get_product_details(request.product_id)
        
        # Handle the Product wrapper
        if isinstance(product_details, dict):
            product_data = product_details.get("Product", {})
            display_name = product_data.get("DisplayName")
            
            if not display_name:
                logger.error(f"Missing DisplayName in product data: {product_data}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Product not found or missing display name"
                )
            
            # Load and format prompt
            prompt = prompt_loader.load_prompt(
                "category_prompt",
                variables={"product_name": display_name}
            )
            
            # Process with Gemini
            model_response = await gemini_client.process_prompt(prompt, JSON_STRUCTURE)
            
            # Add processing time header
            processing_time = time.time() - start_time
            response.headers["X-Processing-Time"] = f"{processing_time:.3f}"
            logger.info(f"Request completed in {processing_time:.3f}s")
            
            return ProductResponse(**model_response.response)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Unexpected response format from Woolworths API"
            )
    
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Internal server error: {str(e)}"
        )

@app.post("/categorize/enhanced", response_model=EnhancedProductResponse, 
          summary="Enhanced product categorization",
          description="Categorize a product with rich attributes for improved search relevance")
async def enhanced_categorize_product(
    request: ProductRequest,
    response: Response,
    woolworths_client: WoolworthsClient = Depends(get_woolworths_client),
    gemini_client: GeminiClient = Depends(get_gemini_client),
    prompt_loader: PromptLoader = Depends(get_prompt_loader),
    product_extractor: ProductDataExtractor = Depends(get_product_data_extractor)
):
    """Enhanced categorization of a Woolworths product using Gemini AI.
    
    Returns rich product attributes including type, variety, dietary attributes,
    flavor profile, usage occasions, health benefits, certifications, texture,
    ingredients highlight, serving suggestions, and food/drink pairings.
    """
    start_time = time.time()
    logger.info(f"Received enhanced categorization request for product ID: {request.product_id}")
    
    try:
        # Fetch product details from Woolworths
        product_details = await woolworths_client.get_product_details(request.product_id)
        
        # Extract product data for enhanced prompt
        extracted_data = product_extractor.extract_product_data(product_details)
        
        if not extracted_data:
            raise ValueError(f"Could not extract data for product ID: {request.product_id}")
            
        logger.debug(f"Extracted product data: {extracted_data}")
        
        # Load and format prompt with extracted data
        prompt = prompt_loader.load_prompt(
            "enhanced_category_prompt",
            variables=extracted_data
        )
        
        # Process with Gemini
        model_response = await gemini_client.process_prompt(prompt, ENHANCED_JSON_STRUCTURE)
        
        # Add processing time header
        processing_time = time.time() - start_time
        response.headers["X-Processing-Time"] = f"{processing_time:.3f}"
        logger.info(f"Enhanced categorization completed in {processing_time:.3f}s")
        
        return EnhancedProductResponse(**model_response.response)
    
    except ValueError as e:
        logger.error(f"Validation error in enhanced categorization: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error in enhanced categorization: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for the service."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        timestamp=int(time.time())
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
