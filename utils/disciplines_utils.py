"""
Contains various converters for correct processing of the presented data
"""
import json
from pydantic.json import pydantic_encoder
from model.pydantic.discipline_works import DisciplinesConfig, DisciplineWorksConfig


def load_disciplines_config(file_path: str) -> DisciplinesConfig:
    """
    Return the config containing information about
        loaded disciplines in general form

    :param file_path: path to file

    :return DisciplinesConfig: The object of class DisciplinesConfig
        containing a list of DisciplinesWorksConfig
    """
    with open(file_path, encoding='utf-8') as json_file:
        data = json.load(json_file)
        return DisciplinesConfig(**data)


def disciplines_config_to_json(data: DisciplinesConfig) -> str:
    """
    Return converted data, from DisciplinesConfig to JSON-like string format
    
    :param data: object DisciplinesConfig

    :return str: json-like string format data
    """
    return json.dumps(
        data,
        sort_keys=False,
        indent=4,
        ensure_ascii=False,
        separators=(",", ":"),
        default=pydantic_encoder
    )

def disciplines_config_from_json(json_data: str) -> DisciplinesConfig:
    """
    Return the converted json data, in the DisciplinesConfig object format

    :param json_data: Comprehensive data on the discipline in json format

    :return DisciplinesConfig: converted discipline data 
        in DisciplinesConfig format
    """
    data = json.loads(json_data)
    return DisciplinesConfig(**data)

def disciplines_works_to_json(data: DisciplineWorksConfig) -> str:
    """
    Return in string-format the converted data
        from the object DisciplineWorksConfig

    :param data: object DisciplineWorksConfig

    :return str: json-like string format data
    """
    return json.dumps(
        data,
        sort_keys=False,
        indent=4,
        ensure_ascii=False,
        separators=(",", ":"),
        default=pydantic_encoder
    )

def load_discipline(downloaded_data: bytes) -> DisciplineWorksConfig:
    """
    Return the converted data, from the bytes format 
        in the DisciplineWorksConfig model object
    
    :param downloaded_data: data in byte format

    :return DisciplineWorksConfig: pydantic model object
    """
    data = json.loads(downloaded_data)
    return DisciplineWorksConfig(**data)

def disciplines_works_from_json(json_data: str) -> DisciplineWorksConfig:
    """
    Return the converted data, from the json format 
        in the DisciplineWorksConfig model object
    
    :param json_data: JSON-file on discipline

    :return DisciplineWorksConfig: pydantic model object
    """
    data = json.loads(json_data)
    return DisciplineWorksConfig(**data)

def counting_tasks(discipline: DisciplineWorksConfig) -> int:
    """
    Return the total number of tasks for this subject

    :param disciplpine: chosen discipline

    :return int: total count
    """
    result = 0
    for it in discipline.works:
        result += it.amount_tasks
    return result
