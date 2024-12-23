import json

from pydantic_core import to_jsonable_python

from model.pydantic.discipline_works import DisciplinesConfig, DisciplineWorksConfig


def load_disciplines_config(file_path: str) -> DisciplinesConfig:
    with open(file_path, encoding='utf-8') as json_file:
        data = json.load(json_file)
        return DisciplinesConfig(**data)
    

def disciplines_config_to_json(data: DisciplinesConfig) -> str:
    return json.dumps(
        data,
        sort_keys=False,
        indent=4,
        ensure_ascii=False,
        separators=(",", ":"),
        default=to_jsonable_python
    )

def disciplines_config_from_json(json_data: str) -> DisciplinesConfig:
    data = json.loads(json_data)
    return DisciplinesConfig(**data)

def disciplines_works_to_json(data: DisciplineWorksConfig) -> str:
    return json.dumps(
        data,
        sort_keys=False,
        indent=4,
        ensure_ascii=False,
        separators=(",", ":"),
        default=to_jsonable_python
    )

def load_discipline(downloaded_data: bytes) -> DisciplineWorksConfig:
    data = json.loads(downloaded_data)
    return DisciplineWorksConfig(**data)

def disciplines_works_from_json(json_data: str) -> DisciplineWorksConfig:
    data = json.loads(json_data)
    return DisciplineWorksConfig(**data)

def counting_tasks(discipline: DisciplineWorksConfig) -> int:
    result = 0
    for it in discipline.works:
        result += it.amount_tasks
    return result
