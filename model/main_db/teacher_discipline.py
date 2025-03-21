"""
Describes 'teacher_discipline' table (many to many),
where the tables 'teachers' and 'disciplines' are connected
"""
from sqlalchemy import Column, ForeignKey, Table
from database.main_db.database import Base


association_teacher_to_discipline = Table(
    "teacher_discipline",
    Base.metadata,
    Column(
        "teacher_id",
        ForeignKey("teachers.id", ondelete="CASCADE"), primary_key=True
        ),
    Column(
        "discipline_id",
        ForeignKey("disciplines.id", ondelete="CASCADE"), primary_key=True
        )
)
