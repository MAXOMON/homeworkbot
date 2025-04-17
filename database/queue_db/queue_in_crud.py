"""
This module contains the basic operations with incoming data 
for their subsequent entry/extraction into the queue database input table.
"""
import json
from database.queue_db.database import Session
from model.pydantic.queue_in_raw import QueueInRaw
from model.queue_db.queue_in import QueueIn
from pydantic.json import pydantic_encoder
from sqlalchemy.future import select


async def add_record(user_tg_id: int, chat_id: int, data: QueueInRaw) -> None:
    """
    Add a data entry to the input table
    
    :param user_tg_id: user Telegram ID, eg message.from_user.id
    :param chat_id: chat ID, eg message.chat.id
    :param data: eg discipline_id, lab_number, filelist

    :return None:
    """
    async with Session() as session:
        async with session.begin():
            json_data = json.dumps(
                data,
                sort_keys=False,
                indent=4,
                ensure_ascii=False,
                separators=(",", ": "),
                default=pydantic_encoder
            )
            session.add(
                QueueIn(
                    telegram_id=user_tg_id,
                    chat_id=chat_id,
                    data=json_data
                    )
                )
            await session.commit()

async def is_empty() -> bool:
    """
    Check if input table is empty

    :param None:

    :return bool: True IF is empty ELSE False
    """
    async with Session() as session:
        data = await session.scalar(select(QueueIn))
        return data is None

async def is_not_empty() -> bool:
    """
    Check if there is some data in the input table

    :param None:

    :return bool: True IF there is data ELSE False
    """
    async with Session() as session:
        data = await session.scalar(
            select(QueueIn)
        )
        return data is not None

async def get_first_record() -> QueueIn:
    """
    Get first record in from input table

    :param None:

    :return QueueIn: object of class QueueIn
    """
    async with Session() as session:
        record = await session.scalar(
            select(QueueIn)
        )
        await session.delete(record)
        await session.commit()
        return record
