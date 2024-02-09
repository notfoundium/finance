from uuid import uuid4

from sqlalchemy import DateTime, func, String, Column, ForeignKey
from sqlalchemy.orm import relationship

from src.database import Base


class Course(Base):
    __tablename__ = "courses"

    id = Column("id", String, nullable=False, primary_key=True, server_default=str(uuid4()))
    direction = Column("direction", String, nullable=False)
    value = Column("value", String, nullable=False)

    exchange_id = Column("exchange_id", ForeignKey("exchanges.id", ondelete="CASCADE"), nullable=False)
    exchange = relationship(
        "Exchange", foreign_keys=[exchange_id], back_populates="courses"
    )


class Exchange(Base):
    __tablename__ = "exchanges"

    id = Column("id", String, nullable=False, primary_key=True, server_default=str(uuid4()))
    exchanger = Column("exchanger", String, nullable=False)
    timestamp = Column("timestamp", DateTime, server_default=func.now(), nullable=False)
    courses = relationship(
        "Course",
        back_populates="exchange",
        foreign_keys=[Course.exchange_id],
        cascade="all, delete"
    )
