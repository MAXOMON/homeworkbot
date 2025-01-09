import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


load_dotenv()

engine = create_engine(f"sqlite:///{os.getenv('QUEUE_DB_NAME')}.sqlite")
Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass


def create_tables() -> None:
    Base.metadata.create_all(engine)
