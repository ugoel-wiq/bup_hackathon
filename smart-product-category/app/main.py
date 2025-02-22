from fastapi import FastAPI, HTTPException
from api_models import ProductRequest, ProductResponse
from gemini_client import GeminiClient
from prompt_loader import PromptLoader
from woolworths_client import WoolworthsClient
import logging
import uvicorn

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Product Categorization API",
    description="API for categorizing Woolworths products using Gemini AI",
    version="1.0.0"
)

# Initialize shared components
prompt_loader = PromptLoader()
gemini_client = GeminiClient()
woolworths_client = WoolworthsClient()

json_structure = {
    "type": "string",
    "variety": ["string"]
}

@app.post("/categorize", response_model=ProductResponse)
async def categorize_product(request: ProductRequest):
    try:
        # Fetch product details from Woolworths
        product_details = await woolworths_client.get_product_details(request.product_id)
        logger.debug(f"Raw product details: {product_details}")
        
        # Handle the Product wrapper
        if isinstance(product_details, dict):
            product_data = product_details.get("Product", {})
            display_name = product_data.get("DisplayName")
            
            if not display_name:
                logger.error(f"Missing DisplayName in product data: {product_data}")
                raise HTTPException(
                    status_code=404,
                    detail="Product not found or missing display name"
                )
            
            # Load and format prompt
            prompt = prompt_loader.load_prompt(
                "category_prompt",
                variables={"product_name": display_name}
            )
            
            # Process with Gemini
            response = await gemini_client.process_prompt(prompt, json_structure)
            return ProductResponse(**response.response)
        else:
            raise HTTPException(
                status_code=500,
                detail="Unexpected response format from Woolworths API"
            )
    
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
