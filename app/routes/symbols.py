from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db import crud
from app.schemas.symbol_schemas import SymbolCreate, SymbolResponse

router = APIRouter(prefix="/symbols", tags=["symbols"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=SymbolResponse)
def create_symbol(symbol: SymbolCreate, db: Session = Depends(get_db)):
    return crud.create_symbol(db, symbol)

@router.get("/{ticker}", response_model=SymbolResponse)
def get_symbol(ticker: str, db: Session = Depends(get_db)):
    return crud.get_symbol_by_ticker(db, ticker)
