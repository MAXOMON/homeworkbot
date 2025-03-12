import os
import shutil
from datetime import datetime
from pathlib import Path


def create_answers_archive(path_to_group_folder: Path) -> Path:
    """
    Функция формирования архива ответов группы

    :param path_to_group_folder: путь до директории группы, где хранятся ответы

    :return: путь до сформированного архива
    """
    path = Path(Path.cwd().joinpath(os.getenv("TEMP_REPORT_DIR")))
    file_name = f'data_{datetime.now().date()}'

    shutil.make_archive(
        str(path.joinpath(f'{file_name}')),
        'zip', path_to_group_folder
    )

    return path.joinpath(f'{file_name}.zip')
