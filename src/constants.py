from strenum import StrEnum


class Symbol(StrEnum):
    BTCRUB = "BTCRUB"
    BTCUSDT = "BTCUSDT"
    ETHRUB = "ETHRUB"
    ETHUSDT = "ETHUSDT"


class Coin(StrEnum):
    BITCOIN = "bitcoin"
    ETHEREUM = "ethereum"


class Currency(StrEnum):
    USD = "usd"
    RUB = "rub"


class ExchangerName(StrEnum):
    BINANCE = "binance"
    COINGECKO = "coingecko"