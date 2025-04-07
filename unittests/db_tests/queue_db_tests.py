"""
This module contains the basic functions for testing queries 
to the intermediate queue database.
"""
import unittest
from database.queue_db import queue_in_crud, queue_out_crud, rejected_crud
from model.pydantic.queue_in_raw import QueueInRaw
from model.pydantic.queue_out_raw import TaskResult, TestResult
from model.pydantic.test_rejected_files import RejectedType, TestRejectedFiles


class TestQueueDb(unittest.TestCase):
    """
    This class is designed to test the basic functions of adding, 
    deleting and changing data in the input, output, rejected tables 
    of the queue database.
    """
    def test_input_table(self):
        """
        Check the presence, addition, absence, deletion of data 
        from the INPUT table of the intermediate database.
        """
        user_tg_id = 6543210123456
        chat_id = -54321012345
        discipline_id = 5000
        lab_number = 1000
        data_in = QueueInRaw(discipline_id=discipline_id,
                             lab_number=lab_number,
                             files_path=["lab_1_file_path", "lab_2_file_path"])

        # is_empty
        self.assertTrue(queue_in_crud.is_empty())

        # add_record
        queue_in_crud.add_record(user_tg_id, chat_id, data_in)

        # is_not_empty
        self.assertTrue(queue_in_crud.is_not_empty())

        # get_first_record
        record = queue_in_crud.get_first_record()
        self.assertTrue(bool(record))
        self.assertTrue(queue_in_crud.is_empty())

    def test_output_table(self):
        """
        Check the presence, addition, absence, deletion of data 
        from the OUTPUT table of the intermediate database.
        """
        user_tg_id = 6543210123456
        chat_id = -54321012345
        discipline_id = 5000
        lab_number = 1000
        data_out = TestResult(discipline_id=discipline_id,
                              lab_number=lab_number,
                              successful_task=[TaskResult(
                                  task_id=1,
                                  file_name="lab_1.py",
                                  description=["OK"])],
                              failed_task=[TaskResult(
                                  task_id=2,
                                  file_name="lab_2.py",
                                  description=["Failed"])]
                            )

        # is_empty
        self.assertTrue(queue_out_crud.is_empty())

        # add_record
        queue_out_crud.add_record(user_tg_id, chat_id, data_out)

        # is_not_empty
        self.assertTrue(queue_out_crud.is_not_empty())

        # get_all_records
        record, *_ = queue_out_crud.get_all_records()
        self.assertTrue(bool(record))

        # delete_record
        queue_out_crud.delete_record(record.id)
        self.assertTrue(queue_out_crud.is_empty())

    def test_rejected_table(self):
        """
        Check the presence, addition, absence, deletion of data 
        from the REJECTED table of the intermediate database.
        """
        user_tg_id = 6543210123456
        chat_id = -54321012345
        data_rejected = TestRejectedFiles(type=RejectedType.KeyWordsError,
                                          description="failed_test_result",
                                          files=["lab_2.py"])

        # is_empty
        self.assertTrue(rejected_crud.is_empty())

        # add_record
        rejected_crud.add_record(user_tg_id, chat_id, data_rejected)

        # is_not_empty
        self.assertTrue(rejected_crud.is_not_empty())

        # get_first_record
        record = rejected_crud.get_first_record()
        self.assertTrue(bool(record))
        self.assertTrue(rejected_crud.is_empty())


if __name__ == "__main__":
    unittest.main()
