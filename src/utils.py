from src.constants import Symbol, Coin, Currency


def get_binance_direction(symbol: Symbol):
    if symbol == Symbol.BTCRUB:
        return "BTC-RUB"
    if symbol == Symbol.BTCUSDT:
        return "BTC-USD"
    if symbol == Symbol.ETHRUB:
        return "ETH-RUB"
    if symbol == Symbol.ETHUSDT:
        return "ETH-USD"


def get_coingecko_direction(coin: Coin, currency: Currency):
    if coin == Coin.BITCOIN:
        if currency == Currency.RUB:
            return "BTC-RUB"
        if currency == Currency.USD:
            return "BTC-USD"
    if coin == Coin.ETHEREUM:
        if currency == Currency.RUB:
            return "ETH-RUB"
        if currency == Currency.USD:
            return "ETH-USD"