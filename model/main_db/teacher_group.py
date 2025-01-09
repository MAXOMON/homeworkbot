from sqlalchemy import Column, ForeignKey, Table
from database.main_db.database import Base

"""
class TeacherGroup(Base):
    __tablename__ = "teacher_group"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)

    def __repr__(self) -> str:
        return f"TeacherGroup [grID: {self.group_id}, tID: {self.teacher_id}]"
"""

association_teacher_to_group = Table(
    "teacher_group",
    Base.metadata,
    Column("teacher_id", ForeignKey("teachers.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
)
