import json
import uuid
from pathlib import Path

from python_on_whales import docker

from model.pydantic.test_settings import TestSettings


class DockerBuilder:
    """
    Класс формирования Dockerfile
    """
    def __init__(self, path_to_folder: Path, student_id: int, lab_number: int) -> None:
        """
        :param path_to_folder: путь до директории с файлами, которые будут отправлены в контейнер
        :param student_id: Telegram id студента
        :param lab_number: номер лабораторной (домашней) работы
        """
        self.test_dir = path_to_folder
        settings_path = path_to_folder.joinpath('settings.json')
        with open(settings_path, encoding='utf-8') as file:
            data = json.load(file)
        self.dependencies = TestSettings(**data).dependencies
        self.tag_name = f'{student_id}-{lab_number}-{uuid.uuid4()}'
        self.logs: str | None = None

    def _build_docker_file(self):
        file = [
            "FROM python:3.11\n",
            "WORKDIR /opt/\n"
            "COPY . /opt \n",
        ]

        dependencies = 'pytest pydantic'
        if self.dependencies:
            for it in self.dependencies:
                dependencies += f' {it}'

        file.append(f"RUN pip install {dependencies}\n")
        file.append('RUN ["pytest", "--tb=no"]\n')
        file.append('CMD ["python3", "docker_output.py"]\n')

        f = open(self.test_dir.joinpath('Dockerfile'), "w")
        f.writelines(file)
        f.close()

    def get_run_result(self) -> str:
        return self.logs

    def run_docker(self):
        self._build_docker_file()

        with docker.build(context_path=self.test_dir, tags=self.tag_name) as my_image:
            with docker.run(self.tag_name, name=self.tag_name, detach=True) as output:
                self.logs = docker.container.logs(output) or docker.container.logs(output.id)
