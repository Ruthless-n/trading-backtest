from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import date
from typing import List, Optional

from app.db import models
from app.schemas import symbol_schemas, price_schemas, backtest_schemas

##SYMBOL
def create_symbol(db: Session, symbol: symbol_schemas.SymbolCreate) -> models.Symbol:
    db_symbol = models.Symbol(
        ticker=symbol.ticker,
        name=symbol.name,
        exchange=symbol.exchange,
        currency=symbol.currency,
    )
    try:
        db.add(db_symbol)
        db.commit()
        db.refresh(db_symbol)
        return db_symbol
    except IntegrityError:
        db.rollback()
        return get_symbol_by_ticker(db, symbol.ticker)


def get_symbol_by_ticker(db: Session, ticker: str) -> Optional[models.Symbol]:
    return db.query(models.Symbol).filter(models.Symbol.ticker == ticker).first()


def get_symbols(db: Session, skip: int = 0, limit: int = 100) -> List[models.Symbol]:
    return db.query(models.Symbol).offset(skip).limit(limit).all()


##PRICES
def create_price(db: Session, price: models.Price) -> models.Price:
    db.add(price)
    db.commit()
    db.refresh(price)
    return price


def bulk_insert_prices(db: Session, prices: List[models.Price]):
    try:
        db.bulk_save_objects(prices)
        db.commit()
    except IntegrityError:
        db.rollback()


def get_prices_by_symbol(
    db: Session, symbol_id: int, start_date: date, end_date: date
) -> List[models.Price]:
    return (
        db.query(models.Price)
        .filter(
            models.Price.symbol_id == symbol_id,
            models.Price.date >= start_date,
            models.Price.date <= end_date,
        )
        .order_by(models.Price.date.asc())
        .all()
    )


##BACKTESTS

def create_backtest(db: Session, backtest: backtest_schemas.BacktestRunRequest) -> models.Backtest:
    db_backtest = models.Backtest(
        ticker=backtest.ticker,
        start_date=backtest.start_date,
        end_date=backtest.end_date,
        strategy_type=backtest.strategy_type,
        strategy_params=backtest.strategy_params,
        initial_cash=backtest.initial_cash,
        commission=backtest.commission,
        timeframe=backtest.timeframe,
        status="created",
    )
    db.add(db_backtest)
    db.commit()
    db.refresh(db_backtest)
    return db_backtest


def get_backtest(db: Session, backtest_id: int) -> Optional[models.Backtest]:
    return db.query(models.Backtest).filter(models.Backtest.id == backtest_id).first()


def update_backtest_status(db: Session, backtest_id: int, status: str):
    db_backtest = get_backtest(db, backtest_id)
    if db_backtest:
        db_backtest.status = status
        db.commit()
        db.refresh(db_backtest)
    return db_backtest


def save_backtest_result(
    db: Session, backtest_id: int, metrics: dict, trades: list
) -> models.BacktestResult:
    db_result = models.BacktestResult(
        backtest_id=backtest_id, metrics=metrics, trades=trades
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result


def get_backtest_results(db: Session, backtest_id: int) -> Optional[models.BacktestResult]:
    return (
        db.query(models.BacktestResult)
        .filter(models.BacktestResult.backtest_id == backtest_id)
        .first()
    )
    
def get_prices_by_ticker(db: Session, ticker: str, start_date: date, end_date: date):
    symbol = get_symbol_by_ticker(db, ticker)
    if not symbol:
        return []
    return get_prices_by_symbol(db, symbol.id, start_date, end_date)

