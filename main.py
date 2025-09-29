import os
import sys
from pathlib import Path
from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.routes import backtests
from app.db.session import SessionLocal
from app.db.models import Base
from app.routes import health, backtests, symbols, prices, indicators
from sqlalchemy import create_engine
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.services.data_service import fetch_ohlcv
from app.core.logging import get_logger

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/backtestdb")
engine = create_engine(DATABASE_URL, future=True)
Base.metadata.create_all(bind=engine)
sys.path.append(str(Path(__file__).parent.resolve()))

logger = get_logger()

app = FastAPI(title="Backtesting API", version="1.0")
app.include_router(health.router)
app.include_router(backtests.router)
app.include_router(symbols.router)
app.include_router(prices.router)
app.include_router(indicators.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(backtests.router)

# --- Health Check ---
@app.get("/health")
def health():
    db = SessionLocal()
    try:
        db.execute("SELECT 1")
    except Exception as e:
        return {"status": "FAIL", "db_error": str(e), "timestamp": datetime.utcnow()}
    finally:
        db.close()

    import time
    start = time.time()
    try:
        fetch_ohlcv("AAPL", "2023-01-01", "2023-01-10")
        latency = round((time.time() - start)*1000, 2)
    except Exception as e:
        return {"status": "FAIL", "yfinance_error": str(e), "timestamp": datetime.utcnow()}

    return {"status": "OK", "db": "connected", "yfinance_latency_ms": latency, "timestamp": datetime.utcnow()}

scheduler = BackgroundScheduler()

def daily_indicators_job():
    logger.info("Starting daily_indicators job")
    db = SessionLocal()
    try:
        tickers = [t.ticker for t in db.execute("SELECT ticker FROM symbols").fetchall()]
        for ticker in tickers:
            df = fetch_ohlcv(ticker, "2023-01-01", datetime.utcnow().strftime("%Y-%m-%d"))
            logger.info(f"Updated OHLCV for {ticker}")
        logger.info("Daily indicators job completed")
    finally:
        db.close()

def health_check_job():
    logger.info("Running periodic health_check job")
    try:
        health()
    except Exception as e:
        logger.error(f"Health check failed: {e}")

scheduler.add_job(daily_indicators_job, "cron", hour=21, minute=30, id="daily_indicators")
scheduler.add_job(health_check_job, "interval", minutes=60, id="health_check")

scheduler.start()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Application startup event!")
    yield
    print("Application shutdown event!")

app = FastAPI(lifespan=lifespan)