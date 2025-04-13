from pydantic import BaseModel, Field
from typing import List, Optional

class ProductRequest(BaseModel):
    """Request model for product categorization."""
    product_id: str = Field(..., description="The Woolworths product ID")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "product_id": "123456"
            }
        }
    }

class ProductResponse(BaseModel):
    """Response model for product categorization."""
    type: str = Field(..., description="The main product type")
    variety: List[str] = Field(..., description="List of product varieties")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "fruit",
                "variety": ["apple", "red delicious"]
            }
        }
    }

class HealthResponse(BaseModel):
    """Response model for health check endpoint."""
    status: str = Field(..., description="Health status of the service")
    version: str = Field(..., description="API version")
    timestamp: int = Field(..., description="Current timestamp")

class EnhancedProductResponse(BaseModel):
    """Enhanced response model for detailed product categorization."""
    type: str = Field(..., description="The main product type")
    variety: List[str] = Field(..., description="List of product varieties")
    dietary_attributes: List[str] = Field(default_factory=list, description="Dietary attributes (vegan, gluten-free, etc.)")
    flavor_profile: List[str] = Field(default_factory=list, description="Flavor characteristics")
    usage_occasions: List[str] = Field(default_factory=list, description="Suitable usage occasions")
    health_benefits: List[str] = Field(default_factory=list, description="Health benefits associated with product")
    certifications: List[str] = Field(default_factory=list, description="Product certifications")
    texture: List[str] = Field(default_factory=list, description="Texture attributes")
    ingredients_highlight: List[str] = Field(default_factory=list, description="Key ingredients")
    serving_suggestions: List[str] = Field(default_factory=list, description="Serving suggestions")
    pairings: List[str] = Field(default_factory=list, description="Food/drink pairing suggestions")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "type": "plant-based milk",
                "variety": ["almond milk", "unsweetened"],
                "dietary_attributes": ["vegan", "gluten-free", "dairy-free"],
                "flavor_profile": ["nutty", "mild", "subtle"],
                "usage_occasions": ["breakfast", "baking", "smoothies"],
                "health_benefits": ["low-calorie", "vitamin E source"],
                "certifications": ["non-GMO"],
                "texture": ["smooth", "light"],
                "ingredients_highlight": ["almonds", "filtered water"],
                "serving_suggestions": ["chilled", "in coffee"],
                "pairings": ["cereal", "coffee", "smoothies"]
            }
        }
    }