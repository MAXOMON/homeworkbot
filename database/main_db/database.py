"""
In this module, a MAIN database instance is created,
as well as auxiliary functions for subsequent access to it.
"""
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase


load_dotenv()

engine = create_engine(f"sqlite:///{os.getenv('DATABASE_NAME')}.sqlite")
Session = sessionmaker(bind=engine)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """
    Enable correct operation of foreign keys in SQLite.

    This function is triggered when a connection
    to the database is established.
    It sets the SQLite pragma `foreign_keys` to `ON`,
    ensuring that foreign key 
    constraints are enforced.

    :param dbapi_connection: The database API connection object representing 
        the connection to the SQLite database.
    :param connection_record: The connection record object maintained by 
        SQLAlchemy, providing context for the current connection.

    :return None:
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


class Base(DeclarativeBase):
    """
    inherited from sqlalchemy.orm.DeclarativeBase
    necessary for correct operation of DB initialization
    """
    pass


def create_tables() -> None:
    """
    create a main database instance

    :param None:

    :return None:
    """
    Base.metadata.create_all(engine)
