import requests

from fastapi import FastAPI, Depends, status

from src.database import Session, get_session
from src.models import Exchange, Course
from src.schemas import Exchange as ExchangeSchema, Course as CourseSchema
from src.constants import ExchangerName, Symbol

app = FastAPI()


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


@app.get(
    "/binance",
    response_model=ExchangeSchema,
    status_code=status.HTTP_200_OK
)
def get_binance(session: Session = Depends(get_session)):
    response = requests.get(f"https://api1.binance.com/api/v3/ticker/price?symbols={symbols}").json()
    exchange = Exchange(exchanger=ExchangerName.BINANCE)
    for item in response:
        course = Course(direction=get_direction(item.get("symbol")), value=item.get("price"))
        session.add(course)
        exchange.courses.append(course)
    session.add(exchange)
    session.commit()
    return exchange
