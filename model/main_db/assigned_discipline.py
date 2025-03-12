from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.main_db.database import Base


class AssignedDiscipline(Base):
    """
    :param discipline_id: ID присвоенной дисциплины
    :param student_id: ID студента
    :param point: количество баллов
    :param home_work: выполненные работы, DisciplineHomeWorks,
     необходимо передать в формате JSON
    """
    __tablename__ = "assigned_discipline"

    id: Mapped[int] = mapped_column(primary_key=True)
    discipline_id: Mapped[int] = mapped_column(ForeignKey("disciplines.id"), nullable=False)
    student_id: Mapped[int] = mapped_column(
        ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )
    point: Mapped[float] = mapped_column(default=0)
    home_work: Mapped[str] = mapped_column(JSON, nullable=False)  # DisciplineHomeWorks

    student: Mapped["Student"] = relationship(
        back_populates='homeworks'
    )

    def __repr__(self) -> str:
        info: str = f"Дисциплина {self.discipline_id}, " \
            f"student_id: {self.student_id}, " \
            f"points: {self.point}, " \
            f"home_works: {self.home_work}"
        return info
