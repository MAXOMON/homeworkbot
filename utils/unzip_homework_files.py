"""
Contains functionality for unpacking an archive from 
a student containing answers, generating a path 
to the directory in which the archive will be saved.
"""
from pathlib import Path
from zipfile import ZipFile
from database.main_db.common_crud import get_group
from database.main_db.student_crud import get_student_by_tg_id


async def save_homework_file(
        file_name: str,
        downloaded_file: bytes,
        user_tg_id: int,
        lab_num: int,
        path_to_answer: str) -> list[str]:
    """
    Unzip and save the student's archive with answers to a specific task.

    :param file_name: name of the archive uploaded by the student
    :param downloaded_file: raw archive representation (byte set)
    :param user_tg_id: student Telegram ID
    :param lab_num: work number for which the archive 
        with completed tasks was loaded
    :param path_to_answer: root directory for loading answers,
        for the discipline chosen by the student

    :return: list of paths to unpacked response files
    """
    student = get_student_by_tg_id(user_tg_id)
    group = get_group(student.group_id)

    path = Path.cwd()
    path = path.joinpath(
        path_to_answer
    ).joinpath(
        group.group_name
    ).joinpath(
        str(lab_num)
    ).joinpath(
        f'{student.full_name}-{user_tg_id}'
    )

    Path(path).mkdir(parents=True, exist_ok=True)

    with open(path.joinpath(file_name), "wb") as new_file:
        new_file.write(downloaded_file)
    with ZipFile(path.joinpath(file_name),
                 "r",
                 metadata_encoding="cp866") as zipObj:
        zipObj.extractall(path=path)

    filelist = [str(path.joinpath(file.filename)) for file in zipObj.filelist]
    return filelist
