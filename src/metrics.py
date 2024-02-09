from prometheus_client import Gauge

BINANCE_TOTAL = Gauge(
    "finance_binance_total",
    "Binance Total",
    labelnames=("count",)
)

COINGECKO_TOTAL = Gauge(
    "finance_coingecko_total",
    "Coingecko Total",
    labelnames=("count",)
)
