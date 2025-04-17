"""
This module contains the basic operations with incoming data 
for their subsequent entry/extraction into the queue database rejected table.
"""
import json
from database.queue_db.database import Session
from model.pydantic.test_rejected_files import TestRejectedFiles
from model.queue_db.rejected import Rejected
from pydantic.json import pydantic_encoder
from sqlalchemy.future import select


async def add_record(
        user_tg_id: int,
        chat_id: int,
        rejected: TestRejectedFiles
) -> None:
    """
    Add a record to the rejected table with the answers
    that did not pass the check

    :param user_tg_id: user Telegram ID
    :param chat_id: chat ID
    :param rejected: rejected test files

    :return None:
    """
    async with Session() as session:
        async with session.begin():
            json_data = json.dumps(
                rejected,
                sort_keys=False,
                indent=4,
                ensure_ascii=False,
                separators=(',', ': '),
                default=pydantic_encoder
            )

            session.add(Rejected(
                telegram_id=user_tg_id,
                chat_id=chat_id,
                data=json_data
            ))
            await session.commit()

async def is_empty() -> bool:
    """
    Check if rejected table is empty

    :param None:

    :return bool: True IF is empty ELSE False
    """
    async with Session() as session:
        data = await session.scalar(select(Rejected))
        return data is None

async def is_not_empty() -> bool:
    """
    Check if there is some data in the rejected table

    :param None:

    :return bool: True IF there is data ELSE False
    """
    async with Session() as session:
        data = await session.scalar(select(Rejected))
        return data is not None

async def get_first_record() -> Rejected:
    """
    Get first record in from rejected table

    :param None:

    :return Rejected: object of class Rejected
    """
    async with Session() as session:
        record = await session.scalar(select(Rejected))
        await session.delete(record)
        await session.commit()
        return record
