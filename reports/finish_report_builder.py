"""
This module is designed to generate a final report 
on the student's academic performance.
"""
from reports.base_report_builder import BaseReportBuilder


class FinishReportBuilder(BaseReportBuilder):
    """Class for generating a final report on student performance"""
    def __init__(self, group_id: int, discipline_id: int):
        """
        :param group_id: student group id
        :param discipline_id: student discipline id
        """
        super().__init__(group_id, discipline_id, "finish_report")
