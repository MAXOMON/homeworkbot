"""
In this module, a QUEUE database instance is created,
as well as auxiliary functions for subsequent access to it.
"""
import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncAttrs,
    AsyncSession
)
from sqlalchemy.orm import DeclarativeBase


load_dotenv()

engine = create_async_engine(
    f"postgresql+psycopg://{os.getenv('DB_USERNAME')}" +
    f":{os.getenv('DB_PASSWORD')}@localhost:5432/{os.getenv('QUEUE_DB_NAME')}"
)

Session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    """
    Inherited from sqlalchemy.orm.DeclarativeBase
    necessary for correct operation of DB initialization
    """


async def create_tables() -> None:
    """
    create a queue database instance

    :param None:

    :return None:
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
