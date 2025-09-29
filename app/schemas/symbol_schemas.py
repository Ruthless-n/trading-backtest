from pydantic import BaseModel

class SymbolCreate(BaseModel):
    ticker: str
    name: str | None = None
    exchange: str | None = None
    currency: str | None = None

class SymbolResponse(SymbolCreate):
    id: int

    class Config:
       from_attributes = True
