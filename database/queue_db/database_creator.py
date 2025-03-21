"""
This module contains the function of creating a queue table in the database
"""
from database.queue_db.database import create_tables


def create_queue_tables() -> None:
    """
    Create a table in the database that runs the Queue tasks
    
    :param None:

    :return None:
    """
    create_tables()
