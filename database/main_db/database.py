"""Базовый модуль для создания таблиц"""
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase


load_dotenv()

engine = create_engine(f"sqlite:///{os.getenv('DATABASE_NAME')}.sqlite")
Session = sessionmaker(bind=engine)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Base(DeclarativeBase):
    pass


def create_tables() -> None:
    Base.metadata.create_all(engine)
