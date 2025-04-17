"""Contains functionality for initialization of the application"""
import os
from pathlib import Path
from dotenv import load_dotenv
from setuptools._distutils.util import strtobool
from sqlalchemy_utils import database_exists, create_database
from database.main_db.database import engine as main_engine
from database.main_db.database_creator import create_main_tables
from database.queue_db.database import engine as queue_engine
from database.queue_db.database_creator import create_queue_tables
from model.pydantic.db_creator_settings import DbCreatorSettings


async def init_app() -> None:
    """
    Creates the main and intermediate databases, 
    as well as a directory where various reports will be stored, 
    if they have not yet been created.

    :param None:
    :return None:
    """

    load_dotenv()

    if not database_exists(main_engine.url):
        create_database(main_engine.url)
        settings = DbCreatorSettings(
            bool(strtobool(os.getenv("REMOTE_CONFIGURATION"))),
            os.getenv("DEFAULT_ADMIN"),
            os.getenv("PATH_TO_DISCIPLINES_DATA"),
            os.getenv("PATH_TO_INITIALIZATION_DATA")
        )
        await create_main_tables(settings)

    if not database_exists(queue_engine.url):
        create_database(queue_engine.url)
        await create_queue_tables()

    path = Path.cwd()
    Path(path.joinpath(os.getenv("TEMP_REPORT_DIR"))).mkdir(
        parents=True, exist_ok=True)
