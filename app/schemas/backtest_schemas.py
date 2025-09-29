from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict
from datetime import date

class BacktestRunRequest(BaseModel):
    ticker: str
    start_date: date
    end_date: date
    strategy_type: str
    strategy_params: Optional[Dict] = {}
    initial_cash: Optional[float] = 100000
    commission: Optional[float] = 0.0
    timeframe: Optional[str] = "1d"

    @field_validator("end_date")
    def check_dates(cls, v, values):
        if "start_date" in values and v <= values["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class BacktestRunResponse(BaseModel):
    id: int
    status: str
    message: Optional[str] = None
