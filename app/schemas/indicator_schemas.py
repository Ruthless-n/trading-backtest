from pydantic import BaseModel
from typing import List, Dict, Optional

class IndicatorUpdateRequest(BaseModel):
    ticker: str
    indicators: Optional[List[Dict]] = []
