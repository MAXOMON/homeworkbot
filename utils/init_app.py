import os

from setuptools._distutils.util import strtobool
from pathlib import Path

from dotenv import load_dotenv

from database.main_db.database_creator import create_main_db
from database.queue_db.database_creator import create_queue_db
from model.pydantic.db_creator_settings import DbCreatorSettings


def init_app() -> None:
    load_dotenv()
    db_is_created = os.path.exists(os.getenv("DATABASE_NAME") + ".sqlite")
    
    if not db_is_created:
        settings = DbCreatorSettings(
            bool(strtobool(os.getenv("REMOTE_CONFIGURATION"))),
            os.getenv("DEFAULT_ADMIN"),
            os.getenv("PATH_TO_DISCIPLINES_DATA"),
            os.getenv("PATH_TO_INITIALIZATION_DATA")
        )
        create_main_db(settings)

    db_is_created = os.path.exists(os.getenv("QUEUE_DB_NAME") + ".sqlite")
    if not db_is_created:
        create_queue_db()

    path = Path.cwd()
    Path(path.joinpath(os.getenv("TEMP_REPORT_DIR"))).mkdir(parents=True, exist_ok=True)
