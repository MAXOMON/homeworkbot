"""Ассоциативная таблица для групп преподавателя"""
from sqlalchemy import Column, ForeignKey, Table
from database.main_db.database import Base


association_teacher_to_group = Table(
    "teacher_group",
    Base.metadata,
    Column("teacher_id", ForeignKey("teachers.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True)
)
