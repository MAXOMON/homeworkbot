from pydantic import BaseModel


class Teacher(BaseModel):
    full_name: str
    telegram_id: int
    is_admin: bool
    assign_disciplines: list[str]
    assign_groups: list[str]