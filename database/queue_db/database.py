"""
In this module, a QUEUE database instance is created,
as well as auxiliary functions for subsequent access to it.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


load_dotenv()

engine = create_engine(
    f"postgresql+psycopg://{os.getenv('DB_USERNAME')}" +
    f":{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('QUEUE_DB_NAME')}"
)

Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    """
    Inherited from sqlalchemy.orm.DeclarativeBase
    necessary for correct operation of DB initialization
    """


def create_tables() -> None:
    """
    create a queue database instance

    :param None:

    :return None:
    """
    Base.metadata.create_all(engine)
