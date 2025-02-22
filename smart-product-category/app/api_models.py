from pydantic import BaseModel
from typing import List

class ProductRequest(BaseModel):
    product_id: str

class ProductResponse(BaseModel):
    type: str
    variety: List[str]