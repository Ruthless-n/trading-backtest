def calculate_position_size(initial_cash, entry_price, stop_price, atr=0, atr_multiplier=1.0, commission_per_unit=0.0):
    risk_amount = initial_cash * 0.01
    stop_distance = abs(entry_price - stop_price)
    if stop_distance <= 0:
        return 0, "Stop muito próximo"
    size = risk_amount / (stop_distance + commission_per_unit)
    if size < 1:
        return 0, "Posição mínima < 1"
    return int(size), None
