"""
This module is designed to generate a full report 
on the student's academic performance.
"""
import json
from database.main_db import common_crud
from model.pydantic.home_work import DisciplineHomeWorks
from reports.base_report_builder import BaseReportBuilder, ReportFieldEnum


class FullReportBuilder(BaseReportBuilder):
    """Class for generating a full report on student performance"""
    def __init__(self, group_id: int, discipline_id: int):
        """
        :param group_id: student group id
        :param discipline_id: student discipline id
        """
        super().__init__(group_id, discipline_id, "full_report")

    def build_report(self) -> None:
        """
        start creating and filling a full report
        
        :return: None
        """
        super().build_report()
        worksheet = self.wb.active

        students = common_crud.get_students_from_group(self.group_id)
        row = 1
        for student in students:
            assigned_discipline = common_crud.get_disciplines_assigned_to_student(
                student.id,
                self.discipline_id)
            home_works = DisciplineHomeWorks(
                **json.loads(assigned_discipline.home_work)
                ).home_works
            if row == 1:
                col = ReportFieldEnum.NEXT
                for number_lab, work in enumerate(home_works):
                    for number_task, task in enumerate(work.tasks):
                        worksheet.cell(
                            row=row, column=col
                        ).value = f"lab{number_lab+1}_Q{number_task+1}"
                        col += 1
                row += 1
            if row > 1:
                col = ReportFieldEnum.NEXT
                for number_lab, work in enumerate(home_works):
                    for number_task, task in enumerate(work.tasks):
                        worksheet.cell(
                            row=row, column=col
                        ).value = 1 if task.is_done else 0

                        if task.is_done:
                            worksheet.cell(
                                row=row, column=col
                            ).fill = BaseReportBuilder.GREEN_FILL
                        else:
                            worksheet.cell(
                                row=row, column=col
                            ).fill = BaseReportBuilder.RED_FILL

                        col += 1
            row += 1
