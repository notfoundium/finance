import requests

from strenum import StrEnum
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Symbol(StrEnum):
    BTCRUB = "BTCRUB"
    BTCUSDT = "BTCUSDT"
    ETHRUB = "ETHRUB"
    ETHUSDT = "ETHUSDT"


class CourseSchema(BaseModel):
    direction: str
    value: str

    class Config:
        orm_mode = True


class ExchangeSchema(BaseModel):
    exchanger: str
    courses: list[CourseSchema]

    class Config:
        orm_mode = True


def get_direction(symbol: Symbol):
    if symbol == Symbol.BTCRUB:
        return "BTC-RUB"
    if symbol == Symbol.BTCUSDT:
        return "BTC-USD"
    if symbol == Symbol.ETHRUB:
        return "ETH-RUB"
    if symbol == Symbol.ETHUSDT:
        return "ETH-USD"


symbols = str(
    ["BTCRUB", "BTCUSDT", "ETHRUB", "ETHUSDT"]
).replace("\'", "\"").replace(" ", "")


@app.get("/courses")
def get_courses():
    response = requests.get(f"https://api1.binance.com/api/v3/ticker/price?symbols={symbols}")
    # response = requests.get(f"https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd,rub")
    return response.text
