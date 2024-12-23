from reports.base_report_builder import BaseReportBuilder


class FinishReportBuilder(BaseReportBuilder):
    def __init__(self, group_id: int, discipline_id: int):
        super().__init__(group_id, discipline_id, "finish_report")
