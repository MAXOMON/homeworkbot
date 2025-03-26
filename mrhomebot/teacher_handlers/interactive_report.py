"""
A module for processing teacher commands, in this case, 
receiving an interactive report on the academic performance 
of a specific student.
"""
import asyncio
from telebot.types import CallbackQuery, InlineKeyboardButton,\
    InlineKeyboardMarkup
from database.main_db import teacher_crud
from model.pydantic.student_report import StudentReport
from mrhomebot import bot
from reports.interactive_report_builder import run_interactive_report_builder


__report_prefix = [
    'interactiveGrRep_',
    'interactiveDisRep_',
    'interactiveStRep_'
]

def __is_interactive_prefix_callback(data: str) -> bool:
    """
    Check if such a prefix is ​in the list of commands available 
    for receiving an interactive report.

    :param data: eg message.text

    :param bool: True IF is a command ELSE False
    """
    for it in __report_prefix:
        if it in data:
            return True
    return False

@bot.callback_query_handler(
    func=lambda call: __is_interactive_prefix_callback(call.data)
)
async def callback_interactive_report(call: CallbackQuery):
    """
    Create a keyboard with a choice of group, discipline and specific student,
    and delegate the report generation to another function

    :param call: an object that extends a standard message.
        Contains information about the selected group and discipline.
    """
    type_callback = call.data.split("_")[0]
    match type_callback:
        case 'interactiveGrRep':
            await bot.edit_message_text(
                "Выберите предмет",
                call.message.chat.id,
                call.message.id
            )
            group_id = int(call.data.split("_")[1])
            disciplines = teacher_crud.get_assign_group_discipline(
                call.from_user.id,
                group_id
            )
            if len(disciplines) == 0:
                await bot.edit_message_text(
                    "За группой не числится дисциплин",
                    call.message.chat.id,
                    call.message.id
                )
            else:
                markup = InlineKeyboardMarkup()
                markup.row_width = 1
                markup.add(
                    *[InlineKeyboardButton(
                        it.short_name,
                        callback_data=f'interactiveDisRep_{group_id}_{it.id}'
                    ) for it in disciplines]
                )
                await bot.edit_message_text(
                    "Выберите дисциплину:",
                    call.message.chat.id,
                    call.message.id,
                    reply_markup=markup
                )
        case 'interactiveDisRep':
            group_id = int(call.data.split("_")[1])
            discipline_id = int(call.data.split("_")[2])
            students = teacher_crud.get_auth_students(group_id)
            if len(students) < 1:
                await bot.send_message(
                    call.message.chat.id,
                    "В группе нет авторизованных студентов"
                )
                return
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(
                *[InlineKeyboardButton(
                    it.full_name,
                    callback_data=f'interactiveStRep_{it.id}_{discipline_id}'
                ) for it in students]
            )
            await bot.edit_message_text(
                "Выберите студента:",
                call.message.chat.id,
                call.message.id,
                reply_markup=markup
            )
        case 'interactiveStRep':
            student_id = int(call.data.split("_")[1])
            discipline_id = int(call.data.split("_")[2])
            await __create_report(call, student_id, discipline_id)
        case _:
            await bot.edit_message_text(
                "Неизвестный формат для обработки данных",
                call.message.chat.id,
                call.message.id
            )

async def __create_report(
        call: CallbackQuery,
        student_id: int,
        discipline_id: int) -> None:
    """
    Run the interactive report generation function in a separate thread.

    :param call: an object that extends a standard message.
    :param student_id: ID of the student for whom 
        the report needs to be generated
    :param discipline_id: ID of the discipline for which 
        the report needs to be generated.
    """
    await bot.edit_message_text(
        "Начинаем формировать отчёт",
        call.message.chat.id,
        call.message.id
    )
    report = await asyncio.gather(
        asyncio.to_thread(run_interactive_report_builder,
                          student_id,
                          discipline_id
                          )
    )
    student_report: StudentReport = report[0]
    text_report = f'<i>Студент</i>: <b>{student_report.full_name}</b>\n'
    text_report += f'<i>Кол-во баллов</i>: {student_report.points}\n'
    text_report += f'<i>Пропущенных дедлайнов</i>: \
        {student_report.deadlines_fails}\n'
    text_report += f'<i>Полностью выполненных лаб</i>: \
        {student_report.lab_completed}\n'
    text_report += f'<i>Выполнено заданий</i>: \
        {student_report.task_completed}\n'
    text_report += f'<i>Task ratio</i>: {student_report.task_ratio}\n'
    await bot.edit_message_text(
        text_report,
        call.message.chat.id,
        call.message.id,
        parse_mode='HTML'
    )
