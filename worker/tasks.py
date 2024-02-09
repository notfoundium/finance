import pydantic
import requests
from celery import Celery

from fastapi import status

from src.database import get_session
from src.models import Exchange, Course
from src.schemas import Exchange as ExchangeSchema
from src.constants import ExchangerName
from src.utils import get_coingecko_direction, get_binance_direction
from src.exceptions import ExchangeNoResponseError
from src.settings import settings
from src.logging import logger

broker_url = (f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@rabbitmq:5672/"
              f"{settings.RABBITMQ_DEFAULT_VHOST}")
redis_url = "redis://redis"

queue = Celery("tasks", broker=broker_url, backend=redis_url)
queue.conf.timezone = "Europe/Moscow"
symbols = str(
    ["BTCRUB", "BTCUSDT", "ETHRUB", "ETHUSDT"]
).replace("\'", "\"").replace(" ", "")


@queue.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(5.0, update_courses.s(), name="update_courses")


def get_binance():
    response = requests.get(f"https://api1.binance.com/api/v3/ticker/price?symbols={symbols}")
    if response.status_code != status.HTTP_200_OK:
        raise ExchangeNoResponseError
    response = response.json()
    exchange = Exchange(exchanger=ExchangerName.BINANCE)
    with next(get_session()) as session:
        for item in response:
            course = Course(direction=get_binance_direction(item.get("symbol")), value=item.get("price"))
            session.add(course)
            exchange.courses.append(course)
        session.add(exchange)
        session.commit()
        session.refresh(exchange)
        logger.debug(pydantic.parse_obj_as(ExchangeSchema, exchange))
    return exchange


def get_coingecko():
    response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,rub")
    if response.status_code != status.HTTP_200_OK:
        raise ExchangeNoResponseError
    response = response.json()
    exchange = Exchange(exchanger=ExchangerName.COINGECKO)
    with next(get_session()) as session:
        for coin in response:
            for currency in response.get(coin):
                course = Course(direction=get_coingecko_direction(coin, currency), value=response.get(coin).get(currency))
                session.add(course)
                exchange.courses.append(course)
        session.add(exchange)
        session.commit()
        session.refresh(exchange)
        logger.debug(pydantic.parse_obj_as(ExchangeSchema, exchange))
    return exchange


@queue.task
def update_courses():
    latest: Exchange
    try:
        latest = get_coingecko()
        logger.info("Latest exchange: " + latest.exchanger)
        return latest.exchanger
    except ExchangeNoResponseError:
        logger.warning("Coingecko does not respond.")

    try:
        latest = get_binance()
        logger.info("Latest exchange: " + latest.exchanger)
        return latest.exchanger
    except ExchangeNoResponseError:
        logger.warning("Binance does not respond.")
    logger.critical("All requests failed.")
