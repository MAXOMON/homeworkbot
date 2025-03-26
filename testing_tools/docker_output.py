"""
The module is copied to the directory from which 
the container will be launched.
Serves to transfer data on test results from the docker container
to the verification subsystem
"""
from logger.docker_logger import DockerLogger

logger = DockerLogger()

print(logger.to_json())
