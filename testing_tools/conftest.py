"""
Модуль копируется в директорию из которой будет запускаться контейнер
"""
import pytest
from logger.docker_logger import DockerLogger


@pytest.fixture(scope="session")
def logger() -> DockerLogger:
    return DockerLogger()


def pytest_sessionfinish(session, exitstatus):
    """
    Функция запускается после завершения всех тестов
    """
    logger = DockerLogger()
    logger.save()
