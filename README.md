
# Trading Backtesting API

Descrição do Projeto

API REST para executar backtests de estratégias de trend following em ações usando dados históricos do Yahoo Finance. O projeto permite:

Persistir preços históricos e indicadores técnicos.

Executar backtests com estratégias configuráveis (ex.: SMA Cross, Breakout).

Salvar resultados de trades, daily positions e métricas de performance.

Consultar resultados via API.
Visualizar resultados em notebooks (Jupyter).


## Stack utilizada
- Python 3.10+
- FastAPI
- SQLAlchemy
- PostgreSQL (via Docker)
- Finance (dados históricos)
- Jupyter Notebook (visualização)


## Para rodar o projeto:

Clone o repositório

```bash
  git clone https://github.com/Ruthless-n/trading-backtest.git
```

Entre no diretório do projeto

```bash
  cd trading-backtest
```

Recomendo utilizar variavel de ambiente. Para isso:

```bash
  python -m venv venv
  source venv/scripts/activate
```

Instale as dependências necessárias:

```bash
  pip install -r requirements.txt
```

## Banco de dados

Crie um .env na raíz do projeto para o acesso ao banco. (Use o .env.example como referência)

Rodar o Docker para os containêrs do banco
```bash
  docker-compose up -d
```

Para rodar a API:
```bash
  uvicorn main:app
```

Acesso ao docs: http://localhost:8000/docs

## Endpoints Principais

### Results

- POST /backtests/run – Executa um backtest
```json
  {
    "ticker": "PETR4.SA",
    "start_date": "2021-01-01",
    "end_date": "2024-12-31",
    "strategy_type": "sma_cross",
    "strategy_params": {"fast": 50, "slow": 200},
    "initial_cash": 100000,
    "commission": 0.001,
    "timeframe": "1d"
    }
```
    
- GET /backtests/{backtest_id}/results – Retorna resultados do backtest
```json
  {
    "backtest_id": 23,
    "metrics": {
        "total_return": 0.27,
        "sharpe": 1.1,
        "max_drawdown": -0.12
    },
    "trades": [
        {"date": "2023-01-10", "side": "BUY", "price": 27.45, "size": 365}
    ],
    "daily_positions": [
        {
        "date": "2023-01-10",
        "position_size": 365,
        "cash": 89970.0,
        "equity": 100000.0,
        "drawdown": 0.0
        }
    ]
    }
```
### Prices
- POST /prices/fetch – Busca e persiste preços históricos
- GET /prices/{ticker} – Consulta preços de um ticker

### Indicators
- POST /data/indicators/update – Calcula indicadores técnicos
## Rodando os testes

Para rodar os testes, rode o seguinte comando

```bash
  npm run test
```

