
from pydantic import BaseModel
from typing import Any, Dict

class ModelResponse(BaseModel):
    response: Dict[str, Any]
    raw_response: str