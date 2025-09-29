from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import crud
from app.services.data_service import fetch_ohlcv, persist_prices
from app.schemas.price_schemas import PriceFetchRequest, PriceResponse
from datetime import date


router = APIRouter(prefix="/prices", tags=["prices"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/fetch")
def fetch_and_save_prices(request: PriceFetchRequest, db: Session = Depends(get_db)):
    df = fetch_ohlcv(request.ticker, request.start_date, request.end_date)
    if df.empty:
        raise HTTPException(status_code=404, detail="Nenhum dado encontrado")

    persist_prices(1, df)
    return {"ticker": request.ticker, "rows_saved": len(df)}

@router.get("/{ticker}", response_model=list[PriceResponse])
def get_prices(ticker: str, db: Session = Depends(get_db)):
    return crud.get_prices_by_ticker(db, ticker, start_date=date(2000,1,1), end_date=date.today())
