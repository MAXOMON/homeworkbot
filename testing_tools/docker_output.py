"""
Модуль копируется в директорию из которой будет запускаться контейнер.
Служит для передачи данных о результатах тестирования из docker-контейнера
в подсистему проверки
"""
from logger.docker_logger import DockerLogger

logger = DockerLogger()

print(logger.to_json())
