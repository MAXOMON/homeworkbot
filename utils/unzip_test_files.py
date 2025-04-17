"""
Contains functionality for unpacking an archive with tests on 
an academic subject (downloaded by the administrator) 
and saving it in a predefined directory.
"""
import os
import shutil
from pathlib import Path
from zipfile import ZipFile


async def save_test_files(path_to_test: str, downloaded_file: bytes) -> None:
    """
    unpack the test archive (downloaded by the administrator) 
    for a specific discipline.

    :param path_to_test: root directory for loading tests 
        for the subject chosen by the student
    :param downloaded_file: raw archive representation (byte set)
    """
    path = Path.cwd()
    path = Path(path.joinpath(path_to_test))
    if os.listdir(path):
        for file_name in os.listdir(path):
            file_path = path.joinpath(file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                shutil.rmtree(file_path)

    with open(path.joinpath("archive.zip"), "wb") as new_file:
        new_file.write(downloaded_file)
    with ZipFile(path.joinpath("archive.zip")) as zipObj:
        zipObj.extractall(path=Path(path))
