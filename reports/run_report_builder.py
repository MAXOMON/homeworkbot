from enum import Enum

from reports.base_report_builder import BaseReportBuilder
from reports.finish_report_builder import FinishReportBuilder
from reports.full_report_builder import FullReportBuilder
from reports.short_report_builder import ShortReportBuilder


class ReportBuilderTypeEnum(Enum):
    FINISH = 1
    FULL = 2
    SHORT = 3


def run_report_builder(
        group_id: int,
        discipline_id: int,
        builder_type: ReportBuilderTypeEnum) -> str:
    """
    Функция запуска формирования файлового отчёта

    :param group_id: идентификатор группы
    :param discipline_id: идентификатор дисциплины
    :param builder_type: тип формируемого отчёта (FINISH, FULL, SHORT)

    :return: путь до сформированного отчёта
    """
    report_builder: BaseReportBuilder | None = None
    match builder_type:
        case ReportBuilderTypeEnum.FINISH:
            report_builder = FinishReportBuilder(group_id, discipline_id)
        case ReportBuilderTypeEnum.FULL:
            report_builder = FullReportBuilder(group_id, discipline_id)
        case ReportBuilderTypeEnum.SHORT:
            report_builder = ShortReportBuilder(group_id, discipline_id)

    report_builder.build_report()
    report_builder.save_report()
    return report_builder.get_path_to_report()
