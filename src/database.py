from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session

from src.settings import settings


Base = declarative_base()

engine = create_engine(settings.DATABASE_URL)
session_maker = sessionmaker(bind=engine)


def get_session() -> Session:
    session = session_maker()
    try:
        yield session
    finally:
        session.close()
