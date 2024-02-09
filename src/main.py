from typing import Optional

from fastapi import FastAPI, Depends, status, HTTPException

from src.database import Session, get_session
from src.models import Exchange
from src.schemas import Exchange as ExchangeSchema
from src.constants import ExchangerName

app = FastAPI()


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
                Exchange.timestamp).first()
        elif exchanger == ExchangerName.COINGECKO:
            return session.query(Exchange).filter(Exchange.exchanger == ExchangerName.COINGECKO).order_by(
                Exchange.timestamp).first()
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid exchanger name")
    return session.query(Exchange).order_by(Exchange.timestamp).first()
