from sqlalchemy import Column, ForeignKey, Table

from database.main_db.database import Base

"""
class TeacherDiscipline(Base):
    __tablename__ = "teacher_discipline"

    id = Column(Integer, primary_key=True)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)

    def __repr__(self) -> str:
        return f"Discipline [grID: {self.group_id}, tID: {self.teacher_id}]"
"""

association_teacher_to_discipline = Table(
    "teacher_discipline",
    Base.metadata,
    Column("teacher_id", ForeignKey("teachers.id", ondelete="CASCADE"), primary_key=True),
    Column("discipline_id", ForeignKey("disciplines.id", ondelete="CASCADE"), primary_key=True)
)
