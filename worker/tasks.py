import time
import asyncio
import json

import websockets
import pydantic
import requests
from celery import Celery

from fastapi import status

from src.database import SessionLocal
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
    try:
        async with websockets.connect(
                f"wss://stream.binance.com:9443/stream?streams={BinanceStream.BTCUSDT}/{BinanceStream.ETHUSDT}"
        ) as ws:
            is_eth_set = False
            is_btc_set = False
            while True:
                response = await asyncio.wait_for(ws.recv(), timeout=2)
                response = json.loads(response)
                logger.debug(response)
                if not is_btc_set and not is_eth_set:
                    exchange = Exchange(exchanger=ExchangerName.BINANCE)
                async with SessionLocal() as session:
                    if response.get("stream") == BinanceStream.ETHUSDT:
                        direction = Direction.ETHUSD
                        is_eth_set = True
                    elif response.get("stream") == BinanceStream.BTCUSDT:
                        direction = Direction.BTCUSD
                        is_btc_set = True
                    value = response.get("data").get("w")
                    course = Course(direction=direction, value=str(value))
                    session.add(course)
                    exchange.courses.append(course)
                    if is_btc_set and is_eth_set:
                        session.add(exchange)
                        await session.commit()
                        is_eth_set = False
                        is_btc_set = False
                    logger.debug(pydantic.parse_obj_as(ExchangeSchema, exchange))
                await asyncio.sleep(2)
    except (websockets.exceptions.ConnectionClosed, TimeoutError):
        raise ExchangeNoResponseError


async def get_coingecko():
    response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,rub")
    if response.status_code != status.HTTP_200_OK:
        raise ExchangeNoResponseError
    response = response.json()
    exchange = Exchange(exchanger=ExchangerName.COINGECKO)
    async with SessionLocal() as session:
        for coin in response:
            for currency in response.get(coin):
                course = Course(
                    direction=get_coingecko_direction(coin, currency), value=str(response.get(coin).get(currency))
                )
                session.add(course)
                exchange.courses.append(course)
        session.add(exchange)
        await session.commit()
        logger.debug(pydantic.parse_obj_as(ExchangeSchema, exchange))


@queue.task
def update_courses():
    try:
        asyncio.get_event_loop().run_until_complete(get_binance())
        logger.info("Latest exchange: " + ExchangerName.BINANCE)
        time.sleep(2)
        update_courses.delay()
        return
    except ExchangeNoResponseError:
        logger.warning("Binance does not respond.")
    try:
        asyncio.get_event_loop().run_until_complete(get_coingecko())
        logger.info("Latest exchange: " + ExchangerName.COINGECKO)
        time.sleep(2)
        update_courses.delay()
        return
    except ExchangeNoResponseError:
        logger.warning("Coingecko does not respond.")
    logger.critical("All requests failed.")
    time.sleep(2)
    update_courses.delay()
