from sqlalchemy import Column, Integer, ForeignKey
from database.main_db.database import Base


class TeacherGroup(Base):
    __tablename__ = "teacher_group"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)

    def __repr__(self) -> str:
        return f"TeacherGroup [grID: {self.group_id}, tID: {self.teacher_id}]"
    