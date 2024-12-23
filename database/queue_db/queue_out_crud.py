import json

from pydantic.json import pydantic_encoder

from database.queue_db.database import Session
from model.queue_db.queue_out import QueueOut
from model.pydantic.queue_out_raw import TestResult


def is_empty() -> bool:
    with Session() as session:
        data = session.query(QueueOut).first()
        return data is None


def is_not_empty() -> bool:
    with Session() as session:
        data = session.query(QueueOut).first()
        return data is not None


def get_all_records() -> list[QueueOut]:
    with Session() as session:
        data = session.query(QueueOut).all()
        return data


def delete_record(record_id: int) -> None:
    with Session() as session:
        session.query(QueueOut).filter(
            QueueOut.id == record_id
        ).delete(synchronize_session="fetch")
        session.commit()


def add_record(user_tg_id: int, chat_id: int, data: TestResult) -> None:
    session = Session()
    json_data = json.dumps(
        data,
        sort_keys=False,
        indent=4,
        ensure_ascii=False,
        separators=(',', ': '),
        default=pydantic_encoder
    )

    session.add(
        QueueOut(
            telegram_id=user_tg_id,
            chat_id=chat_id,
            data=json_data
        )
    )
    session.commit()
    session.close()
