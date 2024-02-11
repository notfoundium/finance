from strenum import StrEnum


class Symbol(StrEnum):
    BTCRUB = "BTCRUB"
    BTCUSDT = "BTCUSDT"
    ETHRUB = "ETHRUB"
    ETHUSDT = "ETHUSDT"


class Direction(StrEnum):
    BTCRUB = "BTC-RUB"
    BTCUSD = "BTC-USD"
    ETHRUB = "ETH-RUB"
    ETHUSD = "ETH-USD"


class Coin(StrEnum):
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"


class Currency(StrEnum):
    USD = "usd"
    RUB = "rub"


class ExchangerName(StrEnum):
    BINANCE = "binance"
    COINGECKO = "coingecko"


class BinanceStream(StrEnum):
    BTCUSDT = "btcusdt@avgPrice"
    ETHUSDT = "ethusdt@avgPrice"
