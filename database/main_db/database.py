"""
In this module, a MAIN database instance is created,
as well as auxiliary functions for subsequent access to it.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


load_dotenv()

engine = create_engine(
    f"postgresql+psycopg://{os.getenv('DB_USERNAME')}" +
    f":{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('DATABASE_NAME')}"
)

Session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    """
    inherited from sqlalchemy.orm.DeclarativeBase
    necessary for correct operation of DB initialization
    """


def create_tables() -> None:
    """
    create a main database instance

    :param None:

    :return None:
    """
    Base.metadata.create_all(engine)
