from sqlalchemy import (
    Column, Integer, BigInteger, String, Date, DateTime, Float, JSON, Enum, ForeignKey, Index, Numeric, UniqueConstraint, PrimaryKeyConstraint
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

class BacktestStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class TradeSide(str, enum.Enum):
    LONG = "LONG"
    SHORT = "SHORT"

class JobStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Symbol(Base):
    __tablename__ = "symbols"

    id = Column(Integer, primary_key=True)
    ticker = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    exchange = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    prices = relationship("Price", back_populates="symbol", cascade="all, delete-orphan")
    indicators = relationship("Indicator", back_populates="symbol", cascade="all, delete-orphan")


class Price(Base):
    __tablename__ = "prices"
    
    __table_args__ = (
        PrimaryKeyConstraint("id", "symbol_id"), 
        
        UniqueConstraint("symbol_id", "date", name="uq_prices_symbol_date"),

        Index("ix_prices_symbol_date", "symbol_id", "date"),

        {"postgresql_partition_by": "HASH (symbol_id)"},
    )

    id = Column(Integer)
    
    symbol_id = Column(Integer, ForeignKey("symbols.id", ondelete="CASCADE"), nullable=False)
    
    date = Column(Date, nullable=False)
    
    open = Column(Numeric(precision=10, scale=4), nullable=False)
    high = Column(Numeric(precision=10, scale=4), nullable=False)
    low = Column(Numeric(precision=10, scale=4), nullable=False)
    close = Column(Numeric(precision=10, scale=4), nullable=False)
    volume = Column(BigInteger, nullable=False) 

    symbol = relationship("Symbol", back_populates="prices")

class Indicator(Base):
    __tablename__ = "indicators"
    __table_args__ = (
        Index("ix_indicators_symbol_date_name_hash", "symbol_id", "date", "name", "params_hash", unique=True),
    )

    id = Column(Integer, primary_key=True)
    symbol_id = Column(Integer, ForeignKey("symbols.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    name = Column(String, nullable=False)
    value = Column(Float, nullable=False)
    params_hash = Column(String, nullable=False)

    symbol = relationship("Symbol", back_populates="indicators")


class Backtest(Base):
    __tablename__ = "backtests"
    __table_args__ = (
        Index("ix_backtests_ticker_created", "ticker", "created_at"),
    )

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    ticker = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    strategy_type = Column(String, nullable=False)
    strategy_params_json = Column(JSON, nullable=False)
    initial_cash = Column(Float, nullable=False)
    commission = Column(Float, nullable=False)
    timeframe = Column(String, nullable=False)
    status = Column(Enum(BacktestStatus), default=BacktestStatus.PENDING)
    message = Column(String, nullable=True)

    trades = relationship("Trade", back_populates="backtest", cascade="all, delete-orphan")
    daily_positions = relationship("DailyPosition", back_populates="backtest", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="backtest", uselist=False, cascade="all, delete-orphan")

    results = relationship("BacktestResult", back_populates="backtest")
class BacktestResult(Base):
    __tablename__ = "backtest_results"

    id = Column(Integer, primary_key=True, index=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id"), nullable=False)
    metrics = Column(JSON, nullable=True)
    trades = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    backtest = relationship("Backtest", back_populates="results")

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id", ondelete="CASCADE"), nullable=False)
    entry_date = Column(Date, nullable=False)
    exit_date = Column(Date, nullable=True)
    side = Column(Enum(TradeSide), nullable=False)
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    size = Column(Float, nullable=False)
    commission = Column(Float, nullable=False)
    pnl = Column(Float, nullable=True)

    backtest = relationship("Backtest", back_populates="trades")


class DailyPosition(Base):
    __tablename__ = "daily_positions"
    __table_args__ = (
        Index("ix_daily_positions_backtest_date", "backtest_id", "date"),
    )

    id = Column(Integer, primary_key=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    position_size = Column(Float, nullable=False)
    cash = Column(Float, nullable=False)
    equity = Column(Float, nullable=False)
    drawdown = Column(Float, nullable=False)

    backtest = relationship("Backtest", back_populates="daily_positions")


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True)
    backtest_id = Column(Integer, ForeignKey("backtests.id", ondelete="CASCADE"), nullable=False, unique=True)
    total_return = Column(Float, nullable=False)
    sharpe = Column(Float, nullable=False)
    max_drawdown = Column(Float, nullable=False)
    win_rate = Column(Float, nullable=False)
    avg_trade_return = Column(Float, nullable=False)

    backtest = relationship("Backtest", back_populates="metrics")


class JobRun(Base):
    __tablename__ = "job_runs"
    __table_args__ = (
        Index("ix_job_runs_job_name_started", "job_name", "started_at"),
    )

    id = Column(Integer, primary_key=True)
    job_name = Column(String, nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    message = Column(String, nullable=True)
    elapsed_ms = Column(Float, nullable=True)