import json
from pydantic.json import pydantic_encoder

from sqlalchemy import delete
from model.pydantic.queue_in_raw import QueueInRaw

from database.queue_db.database import Session
from model.queue_db.queue_in import QueueIn


def add_record(user_tg_id: int, chat_id: int, data: QueueInRaw) -> None:
    session = Session()
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
    session.commit()
    session.close()


def is_empty() -> bool:
    with Session() as session:
        data = session.query(QueueIn).first()
        return data is None
    

def is_not_empty() -> bool:
    with Session() as session:
        data = session.query(QueueIn).first()
        return data is not None
    

def get_first_record() -> QueueIn:
    with Session() as session:
        record = session.query(QueueIn).first()
        session.query(QueueIn).filter(
            QueueIn.id == record.id
        ).delete(synchronize_session='fetch')
        session.commit()
        return record
