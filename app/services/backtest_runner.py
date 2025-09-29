import backtrader as bt
import pandas as pd
import json
import os
from app.db.session import SessionLocal
from app.db.models import Backtest, Trade, DailyPosition, Metric
from app.strategies.trend_following import TrendFollowingStrategy

RESULTS_DIR = "./results"
os.makedirs(RESULTS_DIR, exist_ok=True)

def run_backtest(backtest_id: int):
    db = SessionLocal()
    try:
        bt_obj = db.query(Backtest).filter(Backtest.id==backtest_id).first()
        if not bt_obj:
            return

        bt_obj.status = "RUNNING"
        db.commit()

        # Preparar feed
        df = pd.read_sql(f"SELECT * FROM prices WHERE symbol_id=(SELECT id FROM symbols WHERE ticker='{bt_obj.ticker}') AND date BETWEEN '{bt_obj.start_date}' AND '{bt_obj.end_date}' ORDER BY date", db.bind)
        df.set_index("date", inplace=True)

        cerebro = bt.Cerebro()
        data_feed = bt.feeds.PandasData(dataname=df)
        cerebro.adddata(data_feed)
        cerebro.addstrategy(TrendFollowingStrategy,
                             initial_cash=bt_obj.initial_cash,
                             commission=bt_obj.commission)
        cerebro.broker.setcash(bt_obj.initial_cash)
        cerebro.run()

        
        bt_obj.status = "COMPLETED"
        db.commit()

    except Exception as e:
        bt_obj.status = "FAILED"
        bt_obj.message = str(e)
        db.commit()
    finally:
        db.close()

def save_backtest_result_json(backtest_id: int, metrics: dict, trades: list, daily_positions: list):
    result = {
        "backtest_id": backtest_id,
        "metrics": metrics,
        "trades": trades,
        "daily_positions": daily_positions
    }
    path = os.path.join(RESULTS_DIR, f"backtest_{backtest_id}.json")
    with open(path, "w") as f:
        json.dump(result, f, indent=4, default=str)  # default=str converte datas para string
    return path