"""
Contains a bot instance, various command handlers, 
filters and middleware for the correct operation of the bot in the system.
"""
__all__ = ["bot"]

from .configuration import bot
import mrhomebot.admin_handlers as admin_handlers
import mrhomebot.auth_handlers as auth_handlers
import mrhomebot.student_handlers as student_handlers
import mrhomebot.teacher_handlers as teacher_handlers
