from sqlalchemy import Column, Integer, ForeignKey, Float, JSON

from database.main_db.database import Base


class AssignedDiscipline(Base):
    __tablename__ = "assigned_discipline"

    id = Column(Integer, primary_key=True)
    discipline_id = Column(Integer, ForeignKey("disciplines.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    point = Column(Float, default=0)
    home_work = Column(JSON, nullable=False)

    def __repr__(self) -> str:
        info = f"AssignedDiscipline [dID: {self.discipline_id}, "
        info += f"sID: {self.student_id}, point: {self.point}, "
        info += f"home_work: {self.home_work}]"
        return info
