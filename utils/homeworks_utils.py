"""
This module contains the necessary utilities for the correct processing 
of the data students "home works" presented in various formats.
"""
import json
from pydantic.json import pydantic_encoder
from model.pydantic.discipline_works import DisciplineWorksConfig
from model.pydantic.home_work import DisciplineHomeWorks, HomeWork, HomeTask


def create_homeworks(discipline: DisciplineWorksConfig) -> DisciplineHomeWorks:
    """
    Takes the selected discipline and from its "homework" parameter forms
        a pydantic HomeWork model for subsequent correct processing
    
    :param discipline: object of the selected discipline from the database,
        in the format of the DisciplineWorksConfig model

    :return DisciplineHomeWorks: list of homework assignments for the selected
        discipline, in the format of the DisciplineHomeWorks model object
    """
    home_works_list: list[HomeWork] = []
    for it in discipline.works:
        home_tasks_list = [HomeTask(number=i)
                           for i in range(1, it.amount_tasks + 1)]
        home_work = HomeWork(
            number=it.number,
            deadline=it.deadline,
            tasks=home_tasks_list,
        )
        home_works_list.append(home_work)
    return DisciplineHomeWorks(home_works=home_works_list)


def homeworks_from_json(json_data: str) -> DisciplineHomeWorks:
    """
    Takes a json-file and transforms it into 
        the DisciplineHomeWorks model format
    
    :param json_data: information about homework for a specific subject

    :return DisciplineHomeWorks: directly the list of homework, 
        presented by the pydantic model DisciplineHomeWorks
    """
    data = json.loads(json_data)
    return DisciplineHomeWorks(**data)


def homeworks_to_json(data: DisciplineHomeWorks) -> str:
    """
    Return transformed data from the DisciplineHomeWorks model's pydantic
        as a json-like string

    :param data: list of home works from a specific discipline

    :return str: json-like string format
    """
    return json.dumps(
        data,
        sort_keys=False,
        indent=4,
        ensure_ascii=False,
        separators=(",", ":"),
        default=pydantic_encoder
    )
