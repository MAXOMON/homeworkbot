"""
Describes 'association_discipline_to_group' table (many to many), where the tables: 
'groups' (groups of students) and 'disciplines' (academic disciplines) are connected
"""
from sqlalchemy import ForeignKey, Table, Column
from database.main_db.database import Base


association_discipline_to_group = Table(
    "association_discipline_to_group",
    Base.metadata,
    Column(
        "group_id",
        ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True
        ),
    Column(
        "discipline_id",
        ForeignKey("disciplines.id", ondelete="CASCADE"), primary_key=True
        )
)