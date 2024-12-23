from pydantic import BaseModel


class QueueInRaw(BaseModel):
    discipline_id: int
    lab_number: int
    files_path: list[str]
