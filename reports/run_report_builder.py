"""
This module launches the Academic Performance Report Builder,
depending on the selected report type.
"""
from enum import Enum
from reports.base_report_builder import BaseReportBuilder
from reports.finish_report_builder import FinishReportBuilder
from reports.full_report_builder import FullReportBuilder
from reports.short_report_builder import ShortReportBuilder


class ReportBuilderTypeEnum(Enum):
    """The required type of report to be generated"""
    FINISH = 1
    FULL = 2
    SHORT = 3


async def run_report_builder(
        group_id: int,
        discipline_id: int,
        builder_type: ReportBuilderTypeEnum) -> str:
    """
    Start generating file report

    :param group_id: group id
    :param discipline_id: discipline id
    :param builder_type: type of report being generated (FINISH, FULL, SHORT)

    :return str: path to the generated report
    """
    report_builder: BaseReportBuilder | None = None
    match builder_type:
        case ReportBuilderTypeEnum.FINISH:
            report_builder = await FinishReportBuilder(group_id, discipline_id)
        case ReportBuilderTypeEnum.FULL:
            report_builder = await FullReportBuilder(group_id, discipline_id)
        case ReportBuilderTypeEnum.SHORT:
            report_builder = await ShortReportBuilder(group_id, discipline_id)

    await report_builder.build_report()
    report_builder.save_report()
    return report_builder.get_path_to_report()
