import time
import asyncio
import websockets
import json

import pydantic
import requests
from celery import Celery

from fastapi import status

from src.database import get_session
from src.models import Exchange, Course
from src.schemas import Exchange as ExchangeSchema
from src.constants import ExchangerName, BinanceStream, Direction
from src.utils import get_coingecko_direction
from src.exceptions import ExchangeNoResponseError
from src.settings import settings
from src.logging import logger

broker_url = (f"amqp://{settings.RABBITMQ_DEFAULT_USER}:{settings.RABBITMQ_DEFAULT_PASS}@rabbitmq:5672/"
              f"{settings.RABBITMQ_DEFAULT_VHOST}")
redis_url = "redis://redis"

queue = Celery("tasks", broker=broker_url, backend=redis_url)
queue.conf.timezone = "Europe/Moscow"


async def get_binance():
    async with websockets.connect(
            f"wss://stream.binance.com:9443/stream?streams={BinanceStream.BTCUSDT}/{BinanceStream.ETHUSDT}"
    ) as ws:
        try:
            is_eth_set = False
            is_btc_set = False
            while True:
                response = await asyncio.wait_for(ws.recv(), timeout=2)
                response = json.loads(response)
                logger.info(response)
                if not is_btc_set and not is_eth_set:
                    exchange = Exchange(exchanger=ExchangerName.BINANCE)
                with next(get_session()) as session:
                    if response.get("stream") == BinanceStream.ETHUSDT:
                        direction = Direction.ETHUSD
                        is_eth_set = True
                    elif response.get("stream") == BinanceStream.BTCUSDT:
                        direction = Direction.BTCUSD
                        is_btc_set = True
                    course = Course(direction=direction, value=response.get("data").get("w"))
                    session.add(course)
                    exchange.courses.append(course)
                    if is_btc_set and is_eth_set:
                        session.add(exchange)
                        session.commit()
                        is_eth_set = False
                        is_btc_set = False
                    logger.debug(pydantic.parse_obj_as(ExchangeSchema, exchange))
                await asyncio.sleep(2)
        except (websockets.exceptions.ConnectionClosed, TimeoutError):
            raise ExchangeNoResponseError


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
        latest = asyncio.run(get_binance())
        logger.info("Latest exchange: " + latest.exchanger)
        time.sleep(2)
        update_courses.delay()
        return latest.exchanger
    except ExchangeNoResponseError:
        logger.warning("Binance does not respond.")
    try:
        latest = get_coingecko()
        logger.info("Latest exchange: " + latest.exchanger)
        time.sleep(2)
        update_courses.delay()
        return latest.exchanger
    except ExchangeNoResponseError:
        logger.warning("Coingecko does not respond.")
    time.sleep(2)
    update_courses.delay()
    logger.critical("All requests failed.")
