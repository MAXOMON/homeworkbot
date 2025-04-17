"""
This module is designed to generate a short report 
on the student's academic performance.
"""
from datetime import datetime
import json
from database.main_db import common_crud
from model.pydantic.home_work import DisciplineHomeWorks
from reports.base_report_builder import BaseReportBuilder, ReportFieldEnum


class ShortReportBuilder(BaseReportBuilder):
    """Class for generating a short report on student performance"""
    async def __init__(self, group_id: int, discipline_id: int):
        """
        :param group_id: student group id
        :param discipline_id: student discipline id
        """
        await super().__init__(group_id, discipline_id, "short_report")

    async def build_report(self) -> None:
        """
        start creating and filling a full report
        
        :return: None
        """
        await super().build_report()
        worksheet = self.wb.active

        students = await common_crud.get_students_from_group(self.group_id)
        row = 1
        for student in students:
            assigned_discipline = await common_crud.get_disciplines_assigned_to_student(
                student.id,
                self.discipline_id)
            home_works = DisciplineHomeWorks(
                **json.loads(assigned_discipline.home_work)
                ).home_works
            if row == 1:
                col = ReportFieldEnum.NEXT
                for number_lab, work in enumerate(home_works):
                    worksheet.cell(
                        row=row, column=col
                    ).value = f"lab{number_lab + 1}_ratio"
                    worksheet.cell(
                        row=row, column=col + 1
                    ).value = f'lab{number_lab + 1}_deadline'
                    col += 2
                row += 1
            if row > 1:
                col = ReportFieldEnum.NEXT
                for work in home_works:
                    cell = worksheet.cell(row=row, column=col+1)
                    if datetime.now().date() > work.deadline:
                        if work.end_time is not None:
                            if work.end_time.date() > work.deadline:
                                cell.value = 'bad'
                                cell.fill = BaseReportBuilder.RED_FILL
                            else:
                                cell.value = 'good'
                                cell.fill = BaseReportBuilder.GREEN_FILL
                        else:
                            cell.value = 'bad'
                            cell.fill = BaseReportBuilder.RED_FILL
                    else:
                        cell.value = 'good'
                        cell.fill = BaseReportBuilder.GREEN_FILL

                    tasks_in_lab = len(work.tasks)
                    tasks_completed = 0
                    for task in work.tasks:
                        if task.is_done:
                            tasks_completed += 1
                    worksheet.cell(
                        row=row, column=col
                    ).value = tasks_completed / tasks_in_lab

                    col += 2
            row += 1
