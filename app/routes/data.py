from fastapi import APIRouter
from schemas.indicator_schemas import IndicatorUpdateRequest
from services.indicator_service import calculate_indicators

router = APIRouter(prefix="/data", tags=["data"])

@router.post("/indicators/update")
def update_indicators(request: IndicatorUpdateRequest):
    result_msg = calculate_indicators(request.ticker, request.indicators)
    return {"ticker": request.ticker, "message": result_msg}
