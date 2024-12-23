from model.queue_db.queue_in import QueueIn
from model.queue_db.queue_out import QueueOut
from model.queue_db.rejected import Rejected

from database.queue_db.database import create_db


def create_queue_db() -> None:
    create_db()