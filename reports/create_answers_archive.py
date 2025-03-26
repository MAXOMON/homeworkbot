"""
This is where the creation of an archive of students
answers takes place and the formation of a path to it.
"""
import os
import shutil
from datetime import datetime
from pathlib import Path


def create_answers_archive(path_to_group_folder: Path) -> Path:
    """
    Create an archive with the group's responses.

    :param path_to_group_folder: path to the group directory 
        where the answers are stored

    :return Path: path to the generated archive
    """
    path = Path(Path.cwd().joinpath(os.getenv("TEMP_REPORT_DIR")))
    file_name = f'data_{datetime.now().date()}'

    shutil.make_archive(
        str(path.joinpath(f'{file_name}')),
        'zip', path_to_group_folder
    )

    return path.joinpath(f'{file_name}.zip')
