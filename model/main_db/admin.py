from sqlalchemy.orm import mapped_column, Mapped

from database.main_db.database import Base


class Admin(Base):
    __tablename__ = "admin"

    telegram_id: Mapped[int] = mapped_column(primary_key=True)
    teacher_mode: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"Admin [ID: {self.telegram_id}, mode: {self.teacher_mode}]"
    