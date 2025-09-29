import yfinance as yf
import pandas as pd
import os
import pickle
from app.db.session import SessionLocal
from app.db.models import Price, Symbol
from sqlalchemy.exc import IntegrityError

CACHE_DIR = os.getenv("YFINANCE_CACHE_DIR", "./cache")
os.makedirs(CACHE_DIR, exist_ok=True)

def fetch_ohlcv(ticker: str, start: str, end: str) -> pd.DataFrame:
    cache_file = os.path.join(CACHE_DIR, f"{ticker}_{start}_{end}.pkl")
    if os.path.exists(cache_file):
        with open(cache_file, "rb") as f:
            df = pickle.load(f)
            return df

    df = yf.download(ticker, start=start, end=end)
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [c[0].lower() for c in df.columns] 
    if df.empty:
        return df

    df.reset_index(inplace=True)
    df.rename(columns={"Date": "date", "Open":"open","High":"high","Low":"low","Close":"close","Volume":"volume"}, inplace=True)
    with open(cache_file, "wb") as f:
        pickle.dump(df, f)

    return df

def persist_prices(symbol_id: int, df: pd.DataFrame):
    print(df.columns)

    db = SessionLocal()
    prices = []
    
    for row in df.itertuples():
        prices.append(
            Price(
                symbol_id=symbol_id,
                date=pd.to_datetime(row[1]).date(),
                open=float(row[5]),
                high=float(row[3]),
                low=float(row[4]),
                close=float(row[2]),
                volume=int(row[6])
            )
        )
    try:
        db.bulk_save_objects(prices)
        db.commit()
    except IntegrityError:
        db.rollback()
    finally:
        db.close()
