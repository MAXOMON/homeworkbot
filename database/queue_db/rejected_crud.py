import json

from pydantic.json import pydantic_encoder

from model.queue_db.rejected import Rejected
from database.queue_db.database import Session
from model.pydantic.test_rejected_files import TestRejectedFiles


def add_record(
        user_tg_id: int,
        chat_id: int,
        rejected: TestRejectedFiles
) -> None:
    session = Session()

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
    session.commit()
    session.close()


def is_empty() -> bool:
    with Session() as session:
        data = session.query(Rejected).first()
        return data is None


def is_not_empty() -> bool:
    with Session() as session:
        data = session.query(Rejected).first()
        return data is not None


def get_first_record() -> Rejected:
    with Session() as session:
        record = session.query(Rejected).first()
        session.query(Rejected).filter(
            Rejected.id == record.id
        ).delete(synchronize_session='fetch')
        session.commit()
        return record
