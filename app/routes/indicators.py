from fastapi import APIRouter
from app.schemas.indicator_schemas import IndicatorUpdateRequest
from app.services.indicator_service import calculate_indicators

router = APIRouter(prefix="/data", tags=["indicators"])

@router.post("/indicators/update")
def update_indicators(request: IndicatorUpdateRequest):
    result_msg = calculate_indicators(request.ticker, request.indicators)
    return {"ticker": request.ticker, "message": result_msg}
