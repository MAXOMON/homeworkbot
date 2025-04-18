"""
This module contains functionality for compiling various reports 
(Full/Final/Brief) for groups of students, according to selected disciplines.
"""
import asyncio
import pathlib
from telebot.types import CallbackQuery, InlineKeyboardMarkup,\
    InlineKeyboardButton, InputFile
from database.main_db import admin_crud, common_crud, teacher_crud
from mrhomebot.configuration import bot
from reports.run_report_builder import ReportBuilderTypeEnum,\
    run_report_builder


__report_prefix = [
    'fullReport_',
    'fullGrReport_',
    'finishReport_',
    'finishGrReport_',
    'shortReport_',
    'shortGrReport_'
]

__next_step = {
    'fullReport': 'fullGrReport',
    'finishReport': 'finishGrReport',
    'shortReport': 'shortGrReport'
}

__reports_builder_type = {
    'fullGrReport': ReportBuilderTypeEnum.FULL,
    'finishGrReport': ReportBuilderTypeEnum.FINISH,
    'shortGrReport': ReportBuilderTypeEnum.SHORT
}

def __is_download_prefix_callback(data: str) -> bool:
    """
    Check if the transmitted data contains a prefix for receiving a report!

    :param data: is the object of the call, in the Telegram API, 
        generated when the administrator clicks on 
        the button in the Telegram bot chat.

    :return bool: True IF this is the report prefix ELSE False
    """
    for it in __report_prefix:
        if it in data:
            return True
    return False

@bot.callback_query_handler(
        func=lambda call: __is_download_prefix_callback(call.data)
        )
async def callback_download_full_report(call: CallbackQuery):
    """
    Pass the collected necessary information about the groups 
    and their disciplines for which a report needs to be generated 
    to the next report generation function.

    :param call: an object that extends the standard message. 
        It contains information about what report needs to be generated, 
        the selected group and discipline.
    """
    type_callback = call.data.split("_")[0]
    match type_callback:
        case 'fullReport' | 'finishReport' | 'shortReport':
            await bot.edit_message_text(
                "Выберите предмет",
                call.message.chat.id,
                call.message.id
            )
            group_id = int(call.data.split("_")[1])
            if await admin_crud.is_admin_no_teacher_mode(call.from_user.id):
                disciplines = await common_crud.get_group_disciplines(group_id)
            else:
                disciplines = await teacher_crud.get_assign_group_discipline(
                    call.from_user.id,
                    group_id
                    )
            if len(disciplines) == 0:
                await bot.edit_message_text(
                    "За группой не числится дисциплин",
                    call.message.chat.id,
                    call.message.id
                )
            elif len(disciplines) > 1:
                markup = InlineKeyboardMarkup()
                markup.row_width = 1
                markup.add(
                    *[
                        InlineKeyboardButton(
                            it.short_name,
                            callback_data=f"{__next_step[type_callback]}_\
                                {group_id}_{it.id}"
                        ) for it in disciplines
                    ]
                )
                await bot.edit_message_text(
                    "Выберите дисциплину:",
                    call.message.chat.id,
                    call.message.id,
                    reply_markup=markup
                )
            else:
                await __create_report(
                    call,
                    group_id,
                    disciplines[0].id,
                    __reports_builder_type[__next_step[type_callback]]
                )
        case 'fullGrReport' | 'finishGrReport' | 'shortGrReport':
            group_id = int(call.data.split("_")[1])
            discipline_id = int(call.data.split("_")[2])
            await __create_report(
                call,
                group_id,
                discipline_id,
                __reports_builder_type[type_callback]
                )
        case _:
            await bot.edit_message_text(
                "Неизвестный формат для обработки данных",
                call.message.chat.id,
                call.message.id
            )

async def __create_report(
        call: CallbackQuery,
        group_id: int,
        discipline_id: int,
        builder_type: ReportBuilderTypeEnum) -> None:
    """
    Run the report generation function in a separate thread.

    :param call: CallbackQuery for sending report and editing messages in chat
    :param group_id: ID of the group for which the report is generated
    :param discipline_id: ID of the discipline 
        for which the report is generated
    :param builder_type: type of report being generated
    """
    await bot.edit_message_text(
        "Начинаем формировать отчёт",
        call.message.chat.id,
        call.message.id
    )
    path_to_report = await asyncio.gather(
        await asyncio.to_thread(
            run_report_builder,
            group_id, discipline_id,
            builder_type)
    )
    await bot.edit_message_text(
        "Отчёт успешно сформирован",
        call.message.chat.id,
        call.message.id
    )
    await bot.send_document(
        call.message.chat.id,
        InputFile(pathlib.Path(path_to_report[0]))
    )
