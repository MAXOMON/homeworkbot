"""
Contains functionality for checking for the presence of a directory with tests.
"""
import os
from pathlib import Path
from database.main_db import common_crud


async def is_test_folder_exist(discipline_id: int, work_id: int) -> bool:
    """
    Check if such directory with tests exists

    :param discipline_id: discipline ID
    :param work_id: work number
    """
    discipline = await common_crud.get_discipline(discipline_id)
    return os.path.exists(Path.cwd().joinpath(
        discipline.path_to_test
    ).joinpath(str(work_id)))
