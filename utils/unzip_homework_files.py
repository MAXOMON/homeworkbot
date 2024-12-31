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
    Функция распаковки архива студента с ответами по конкретной работе

    :param file_name: имя загруженного студентом архива
    :param downloaded_file: сырое представление архива (набор байт)
    :param user_tg_id: Telegram ID студента
    :param lab_num: номер работы, по которой загружен архив с выполненными заданиями
    :param path_to_answer: корневая директория загрузки ответов,
      по выбранной студентом дисциплине

    :return: список путей до распакованных файлов ответов
    """
    student = get_student_by_tg_id(user_tg_id)
    group = get_group(student.group)

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
    with ZipFile(path.joinpath(file_name), "r", metadata_encoding="cp866") as zipObj:
        zipObj.extractall(path=path)

    filelist = [str(path.joinpath(file.filename)) for file in zipObj.filelist]
    return filelist
