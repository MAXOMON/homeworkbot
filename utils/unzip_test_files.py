import os
import shutil
from pathlib import Path
from zipfile import ZipFile


async def save_test_files(path_to_test: str, downloaded_file: bytes) -> None:
    """
        Функция распаковывает архив тестов по дисциплине

        :param path_to_test: корневая директория загрузки тестов по выбранной студентом дисциплине
        :param downloaded_file: сырое представление архива (набор байт)
    """
    path = Path.cwd()
    path = Path(path.joinpath(path_to_test))
    if os.listdir(path):
        for file_path in os.listdir(path):
            shutil.rmtree(file_path)

    with open(path.joinpath("archive.zip"), "wb") as new_file:
        new_file.write(downloaded_file)
    with ZipFile(path.joinpath("archive.zip")) as zipObj:
        zipObj.extractall(path=Path(path))
