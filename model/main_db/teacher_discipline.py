from sqlalchemy import Column, Integer, ForeignKey
from database.main_db.database import Base


class TeacherDiscipline(Base):
    __tablename__ = "teacher_discipline"

    id = Column(Integer, primary_key=True)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)

    def __repr__(self) -> str:
        return f"Discipline [grID: {self.group_id}, tID: {self.teacher_id}]"
    