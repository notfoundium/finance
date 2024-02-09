from typing import Optional

import prometheus_client
from fastapi import FastAPI, Depends, status, HTTPException, Response
from fastapi_utils.tasks import repeat_every
from prometheus_fastapi_instrumentator import Instrumentator

from src.database import Session, get_session
from src.models import Exchange
from src.schemas import Exchange as ExchangeSchema
from src.constants import ExchangerName
from src.metrics import BINANCE_TOTAL, COINGECKO_TOTAL

app = FastAPI()


instrumentator = Instrumentator(
    should_group_status_codes=False,
    should_ignore_untemplated=True,
    should_respect_env_var=True,
    should_instrument_requests_inprogress=True,
    excluded_handlers=[".*admin.*", "/metrics"],
    env_var_name="ENABLE_METRICS",
    inprogress_name="inprogress",
    inprogress_labels=True,
)


@app.get("/metrics")
def metrics():
    return Response(
        content=prometheus_client.generate_latest(),
        media_type="text/plain"
    )


@app.get(
    "/courses",
    response_model=ExchangeSchema
)
def get_courses(
        exchanger: Optional[str] = None,
        session: Session = Depends(get_session)
):
    if exchanger is not None:
        if exchanger == ExchangerName.BINANCE:
            return session.query(Exchange).filter(Exchange.exchanger == ExchangerName.BINANCE).order_by(
                Exchange.timestamp.desc()).first()
        elif exchanger == ExchangerName.COINGECKO:
            return session.query(Exchange).filter(Exchange.exchanger == ExchangerName.COINGECKO).order_by(
                Exchange.timestamp.desc()).first()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid exchanger name")
    return session.query(Exchange).order_by(Exchange.timestamp.desc()).first()


@app.on_event("startup")
@repeat_every(seconds=60)
def minute_task() -> None:
    with next(get_session()) as session:
        BINANCE_TOTAL.labels("count").set(session.query(Exchange).filter(Exchange.exchanger == ExchangerName.BINANCE).count())
        COINGECKO_TOTAL.labels("count").set(
            session.query(Exchange).filter(Exchange.exchanger == ExchangerName.COINGECKO).count())
