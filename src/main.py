from typing import Optional

import pydantic
import requests

from fastapi import FastAPI, Depends, status, HTTPException
from fastapi_utils.tasks import repeat_every

from src.database import Session, get_session
from src.models import Exchange, Course
from src.schemas import Exchange as ExchangeSchema, Course as CourseSchema
from src.constants import ExchangerName
from src.utils import get_coingecko_direction, get_binance_direction
from src.exceptions import ExchangeNoResponseError
from src.logging import logger

app = FastAPI()


symbols = str(
    ["BTCRUB", "BTCUSDT", "ETHRUB", "ETHUSDT"]
).replace("\'", "\"").replace(" ", "")


@app.get(
    "/courses",
    response_model=ExchangeSchema
)
def get_courses(
        exchanger: Optional[str],
        session: Session = Depends(get_session)
):
    if exchanger is not None:
        if exchanger == ExchangerName.BINANCE:
            return session.query(Exchange).filter(Exchange.exchanger == ExchangerName.BINANCE).order_by(
                Exchange.timestamp).first()
        elif exchanger == ExchangerName.COINGECKO:
            return session.query(Exchange).filter(Exchange.exchanger == ExchangerName.COINGECKO).order_by(
                Exchange.timestamp).first()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid exchanger name")
    return session.query(Exchange).order_by(Exchange.timestamp).first()


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


@app.on_event("startup")
@repeat_every(seconds=5, logger=logger)
def update_courses():
    latest: Exchange
    try:
        latest = get_coingecko()
        logger.info("Latest exchange: ", latest.exchanger)
        return
    except ExchangeNoResponseError:
        logger.warning("Coingecko does not respond.")

    try:
        latest = get_binance()
        logger.info("Latest exchange: ", latest.exchanger)
        return
    except ExchangeNoResponseError:
        logger.warning("Binance does not respond.")
    logger.critical("All requests failed.")
