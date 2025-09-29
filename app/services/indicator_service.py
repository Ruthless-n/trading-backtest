import pandas as pd
import talib
import hashlib
import json
from app.db.session import SessionLocal
from app.db.models import Indicator, Symbol

def calculate_indicators(ticker: str, indicators: list):
    db = SessionLocal()
    try:
        symbol = db.query(Symbol).filter(Symbol.ticker == ticker).first()
        if not symbol:
            return

        df = pd.read_sql(f"SELECT * FROM prices WHERE symbol_id={symbol.id} ORDER BY date", db.bind)
        if df.empty:
            return

        results = []
        for ind in indicators:
            name = ind["name"]
            params = ind.get("params", {})
            params_hash = hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()

            # Idempotência
            exists = db.query(Indicator).filter(
                Indicator.symbol_id==symbol.id,
                Indicator.name==name,
                Indicator.params_hash==params_hash
            ).first()
            if exists:
                continue

            if name == "SMA":
                df[name] = talib.SMA(df["close"], timeperiod=params.get("period", 14))
            elif name == "EMA":
                df[name] = talib.EMA(df["close"], timeperiod=params.get("period", 14))
            elif name == "RSI":
                df[name] = talib.RSI(df["close"], timeperiod=params.get("period", 14))
            # outros indicadores ...

            # Persistir em batch
            for row in df.itertuples():
                results.append(
                    Indicator(
                        symbol_id=symbol.id,
                        date=row.date,
                        name=name,
                        value=getattr(row, name),
                        params_hash=params_hash
                    )
                )

        if results:
            db.bulk_save_objects(results)
            db.commit()
    finally:
        db.close()
