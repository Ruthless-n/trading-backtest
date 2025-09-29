from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.db.session import SessionLocal
from app.db.models import Backtest, Trade, DailyPosition, Metric
from app.db import crud
from app.services.backtest_runner import run_backtest
from app.services.data_service import fetch_ohlcv, persist_prices
from app.services.indicator_service import calculate_indicators
import json

router = APIRouter(prefix="/backtests", tags=["backtests"])

class BacktestRunRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    strategy_type: str
    strategy_params: Optional[dict] = {}
    initial_cash: Optional[float] = 100000
    commission: Optional[float] = 0.0
    timeframe: Optional[str] = "1d"

class BacktestCreatedResponse(BaseModel):
    id: int
    status: str

@router.post("/run", response_model=BacktestCreatedResponse)
def create_backtest(request: BacktestRunRequest, background_tasks: BackgroundTasks):
    db = SessionLocal()
    try:
        start = datetime.fromisoformat(request.start_date)
        end = datetime.fromisoformat(request.end_date)
        if start >= end:
            raise HTTPException(400, "start_date deve ser menor que end_date")

        backtest = Backtest(
            ticker=request.ticker,
            start_date=start,
            end_date=end,
            strategy_type=request.strategy_type,
            strategy_params_json=json.dumps(request.strategy_params),
            initial_cash=request.initial_cash,
            commission=request.commission,
            timeframe=request.timeframe,
            status="PENDING"
        )
        db.add(backtest)
        db.commit()
        db.refresh(backtest)

        # Garantir dados
        df = fetch_ohlcv(request.ticker, request.start_date, request.end_date)
        if df.empty:
            raise HTTPException(400, f"Sem dados de preços para {request.ticker}")
        persist_prices(1, df) 

        indicators = request.strategy_params.get("indicators", [])
        if indicators:
            calculate_indicators(request.ticker, indicators)

        background_tasks.add_task(run_backtest, backtest.id)

        return {"id": backtest.id, "status": backtest.status}
    finally:
        db.close()

@router.get("/{backtest_id}/results")
def get_backtest_results(backtest_id: int):
    db = SessionLocal()
    try:
        results = crud.get_backtest_results(db, backtest_id)
        if not results:
            raise HTTPException(status_code=404, detail="Backtest results not found")
        return results
    finally:
        db.close()
        
        