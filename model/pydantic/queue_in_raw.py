"""Contains the data structure for the queue database input table"""
from pydantic import BaseModel


class QueueInRaw(BaseModel):
    """structured data for subsequent processing in the testing system"""
    discipline_id: int
    lab_number: int
    files_path: list[str]
