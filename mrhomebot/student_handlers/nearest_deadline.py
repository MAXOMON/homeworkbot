"""
Module for processing student commands to generate 
a report on the nearest deadline for a specific student and his discipline
"""
import asyncio
from telebot.types import CallbackQuery
from database.main_db import student_crud
from mrhomebot import bot
from reports.deadline_report_builder import run_deadline_report_builder


@bot.callback_query_handler(func=lambda call: 'nearestDeadline_' in call.data)
async def callback_nearest_deadline(call: CallbackQuery):
    """
    go to the next function (create a report)
    if a request for the nearest deadline for a specific student is received.

    :param call: an object that extends a standard message.
        contains information about the student and the discipline number
    """
    type_callback = call.data.split("_")[0]
    match type_callback:
        case "nearestDeadline":
            discipline_id = int(call.data.split("_")[1])
            student = student_crud.get_student_by_tg_id(call.from_user.id)
            await __create_report(call, student.id, discipline_id)
        case _:
            await bot.edit_message_text(
                f"Ошибка nearest_deadline{call.data=}",
                call.message.chat.id,
                call.message.id
            )

async def __create_report(
        call: CallbackQuery,
        student_id: int,
        discipline_id: int):
    """
    Run the function of generating a report on the nearest deadline 
    of a specific student, in a separate thread.

    :param call: an object that extends a standard message.
    :param student_id: ID of the student for whom the report 
        needs to be generated
    :param discipline_id: discipline ID, in order to later understand 
    which group the student is studying in and what the deadlines are 
    for submitting the material in that group.
    """
    await bot.edit_message_text(
        "Начинаем формировать отчёт",
        call.message.chat.id,
        call.message.id
    )
    report = await asyncio.gather(
        asyncio.to_thread(run_deadline_report_builder,
                          student_id, discipline_id)
    )
    student_report = report[0]

    await bot.edit_message_text(
        f"<i>{student_report}</i>",
        call.message.chat.id,
        call.message.id,
        parse_mode='HTML'
    )
