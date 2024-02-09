from strenum import StrEnum


class Symbol(StrEnum):
    BTCRUB = "BTCRUB"
    BTCUSDT = "BTCUSDT"
    ETHRUB = "ETHRUB"
    ETHUSDT = "ETHUSDT"


class ExchangerName(StrEnum):
    BINANCE = "binance"
    COINGECKO = "coingecko"