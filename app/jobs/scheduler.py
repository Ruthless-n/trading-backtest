from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import os
from dotenv import load_dotenv
from db.session import SessionLocal
from db.models import JobRun
from services.data_service import fetch_ohlcv
from services.indicator_service import calculate_indicators

load_dotenv(dotenv_path="../.env")

scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")

def log_job_run(job_name, status, message="", elapsed_ms=0):
    db = SessionLocal()
    try:
        jr = JobRun(
            job_name=job_name,
            started_at=datetime.now(),
            finished_at=datetime.now(),
            status=status,
            message=message,
            elapsed_ms=elapsed_ms
        )
        db.add(jr)
        db.commit()
    finally:
        db.close()

def daily_indicators_job():
    import time
    start_time = time.time()
    job_name = "daily_indicators"
    try:
        db = SessionLocal()
        tickers = [t[0] for t in db.execute("SELECT ticker FROM symbols").fetchall()]
        db.close()

        for ticker in tickers:
            df = fetch_ohlcv(ticker, "2020-01-01", datetime.today().strftime("%Y-%m-%d"))
            calculate_indicators(ticker, ["SMA","EMA","ATR","RSI","Momentum"])
        
        log_job_run(job_name, status="COMPLETED", elapsed_ms=int((time.time()-start_time)*1000))
    except Exception as e:
        log_job_run(job_name, status="FAILED", message=str(e))

scheduler.add_job(daily_indicators_job, CronTrigger(hour=21, minute=30))

def health_check_job():
    import time
    start_time = time.time()
    job_name = "health_check"
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        fetch_ohlcv("AAPL", "2020-01-01", "2020-01-10")
        log_job_run(job_name, status="COMPLETED", elapsed_ms=int((time.time()-start_time)*1000))
    except Exception as e:
        log_job_run(job_name, status="FAILED", message=str(e))

scheduler.add_job(health_check_job, CronTrigger(minute=0))

def maintenance_job():
    import time
    start_time = time.time()
    job_name = "maintenance"
    try:
        log_job_run(job_name, status="COMPLETED", elapsed_ms=int((time.time()-start_time)*1000))
    except Exception as e:
        log_job_run(job_name, status="FAILED", message=str(e))

scheduler.add_job(maintenance_job, CronTrigger(day_of_week="sun", hour=3, minute=0))

def start_scheduler():
    scheduler.start()
    print("Scheduler started with jobs: ", scheduler.get_jobs())
