from typing import Optional

import prometheus_client
from sqlalchemy import select, func
from fastapi import FastAPI, Depends, status, HTTPException, Response
from fastapi_utils.tasks import repeat_every
from prometheus_fastapi_instrumentator import Instrumentator

from src.database import get_session, AsyncSession, SessionLocal
from src.models import Exchange
from src.schemas import Exchange as ExchangeSchema
from src.constants import ExchangerName
from src.metrics import BINANCE_TOTAL, COINGECKO_TOTAL

from worker.tasks import update_courses

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
async def get_courses(
        exchanger: Optional[str] = None,
        session: AsyncSession = Depends(get_session)
):
    if exchanger is None:
        stmt = select(Exchange).order_by(Exchange.timestamp.desc())
    else:
        if exchanger == ExchangerName.BINANCE:
            stmt = select(Exchange).\
                where(Exchange.exchanger == ExchangerName.BINANCE).\
                order_by(Exchange.timestamp.desc())
        elif exchanger == ExchangerName.COINGECKO:
            stmt = select(Exchange). \
                where(Exchange.exchanger == ExchangerName.COINGECKO). \
                order_by(Exchange.timestamp.desc())
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid exchanger name")
    result = await session.execute(stmt)
    return result.scalars().first()


@app.on_event("startup")
@repeat_every(seconds=60)
async def minute_task() -> None:
    async with SessionLocal() as session:
        result = await session.execute(
            select(func.count(Exchange.id)).where(Exchange.exchanger == ExchangerName.BINANCE)
        )
        binance_total_val = result.scalar()
        result = await session.execute(
            select(func.count(Exchange.id)).where(Exchange.exchanger == ExchangerName.COINGECKO)
        )
        coingecko_total_val = result.scalar()
        BINANCE_TOTAL.labels("count").set(binance_total_val)
        COINGECKO_TOTAL.labels("count").set(coingecko_total_val)


@app.on_event("startup")
def startup():
    update_courses.delay()
