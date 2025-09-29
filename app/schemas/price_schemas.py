from pydantic import BaseModel
from datetime import date

class PriceFetchRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str

class PriceResponse(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int

    class Config:
        from_attributes = True
