import backtrader as bt
from app.services.risk_management import calculate_position_size

class TrendFollowingStrategy(bt.Strategy):
    params = dict(
        initial_cash=100000,
        atr_multiplier=1.0,
        commission=0.0,
        position_risk=0.01
    )

    def __init__(self):
        self.order = None
        self.atr = bt.indicators.ATR(self.data, period=14)
        self.trades_log = []

    def next(self):
        entry_price = self.data.close[0]
        if not self.position:
            sma50 = getattr(self.data, "SMA50", None)
            if sma50 and entry_price > sma50[0]:
                stop_price = entry_price - self.atr[0] * self.params.atr_multiplier
                size, reason = calculate_position_size(
                    self.params.initial_cash, entry_price, stop_price, self.atr[0], self.params.atr_multiplier, self.params.commission
                )
                if size > 0:
                    self.buy(size=size)
                    self.trades_log.append({
                        "entry_date": self.data.datetime.date(0),
                        "entry_price": entry_price,
                        "size": size,
                        "stop_price": stop_price,
                        "side": "BUY"
                    })
