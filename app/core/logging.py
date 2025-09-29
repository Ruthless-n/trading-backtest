import logging
import structlog

logging.basicConfig(format="%(message)s", level=logging.INFO)
log = structlog.get_logger()

def get_logger(backtest_id=None, ticker=None, job_name=None):
    return log.bind(backtest_id=backtest_id, ticker=ticker, job_name=job_name)
