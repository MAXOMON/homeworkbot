"""
The module is copied to the directory 
from which the container will be launched.
"""
import pytest
from logger.docker_logger import DockerLogger


@pytest.fixture(scope="session")
def logger() -> DockerLogger:
    """Returns an instance of the class required for logging test results"""
    return DockerLogger()

def pytest_sessionfinish(session, exitstatus):
    """
    The function runs after all tests are completed 
    and saves the result to the logs.
    """
    logger = DockerLogger()
    logger.save()
