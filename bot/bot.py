import logging
import os

from queue import Queue

import telegram

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler, Dispatcher)

from .command import BotCommand
from .database import UserDatabase


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def error(bot, update, err):
    """Log Errors caused by Updates."""
    logger.warning('Update "{}" caused error "{}"'.format(update, err))


class Bot(BotCommand):
    def __init__(self, token=None):
        super().__init__()
        self.TOKEN = token or os.environ.get('TOKEN')
        self.telegram_bot = telegram.Bot(token=self.TOKEN)
        update_queue = Queue()
        self.dp = Dispatcher(self.telegram_bot, update_queue)

        self.dp = self.add_update_handlers(self.dp)

        # log all errors
        self.dp.add_error_handler(error)

    def add_update_handlers(self, dp):
        # Create the EventHandler and pass it your bot's token.
        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.start))
        dp.add_handler(RegexHandler('^(Понедельник|Вторник|Среда|Четверг|Пятница|Суббота)$',
                                    self.regular_choice))
        dp.add_handler(RegexHandler('^Скрыть$', self.done))
        dp.add_handler(CommandHandler("help", self.help_message))
        dp.add_handler(CommandHandler("set", self.set_group, pass_args=True))
        dp.add_handler(CommandHandler("week", self.lessons_week, pass_args=True))
        dp.add_handler(CommandHandler("nextweek", self.lessons_next_week, pass_args=True))
        dp.add_handler(CommandHandler("full", self.full_weeks, pass_args=True))
        dp.add_handler(CommandHandler("today", self.lessons_today, pass_args=True))
        dp.add_handler(CommandHandler("tomorrow", self.lessons_tomorrow, pass_args=True))
        dp.add_handler(CommandHandler(["timetable", "tt"], self.call_schedule))
        dp.add_handler(CommandHandler("weeknumber", self.week_number))
        dp.add_handler(CommandHandler("exams", self.exams, pass_args=True))
        dp.add_handler(CommandHandler('keyboard', self.keyboard_mode))

        return dp
