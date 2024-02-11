from src.constants import Direction, Coin, Currency


def get_coingecko_direction(coin: Coin, currency: Currency):
    if coin == Coin.BITCOIN:
        if currency == Currency.RUB:
            return Direction.BTCRUB
        if currency == Currency.USD:
            return Direction.BTCUSD
    if coin == Coin.ETHEREUM:
        if currency == Currency.RUB:
            return Direction.ETHRUB
        if currency == Currency.USD:
            return Direction.ETHUSD
