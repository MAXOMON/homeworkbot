"""data structure for simplified database filling"""
from dataclasses import dataclass


@dataclass
class DbCreatorSettings:
    """configuration for initial database filling"""
    remote_configuration: bool
    default_admin: int | None = None
    disciplines_path: str = ""
    excel_data_path: str = ""
