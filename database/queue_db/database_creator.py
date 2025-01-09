from model.queue_db.queue_in import QueueIn
from model.queue_db.queue_out import QueueOut
from model.queue_db.rejected import Rejected

from database.queue_db.database import create_tables


def create_queue_tables() -> None:
    create_tables()