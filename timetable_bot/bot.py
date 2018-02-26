import logging
import os

from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler)

from .command import BotCommand
from .database import UserDatabase


class StartBot(object):
    def __init__(self):
        # Set these variable to the appropriate values
        self.TOKEN = os.environ.get('TOKEN')
        self.NAME = os.environ.get('NAME_APP')

        # Port is given by Heroku
        self.PORT = os.environ.get('PORT')

        self.bc = BotCommand()
        self.user_db = UserDatabase()

        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def bot_activation(self, flag):
        """"""
        # Create the EventHandler and pass it your bot's token.
        updater = Updater(self.TOKEN)

        # Get the dispatcher to register handlers
        dp = updater.dispatcher

        dp.add_handler(self.bc.conv_handler)

        # on different commands - answer in Telegram
        dp.add_handler(CommandHandler("start", self.bc.start))
        dp.add_handler(RegexHandler('^(Понедельник|Вторник|Среда|Четверг|Пятница|Суббота)$',
                                    self.bc.regular_choice))
        dp.add_handler(RegexHandler('^Скрыть$', self.bc.done))
        dp.add_handler(CommandHandler("help", self.bc.help_message))
        dp.add_handler(CommandHandler("set", self.bc.set_group, pass_args=True))
        dp.add_handler(CommandHandler("week", self.bc.lessons_week, pass_args=True))
        dp.add_handler(CommandHandler("nextweek", self.bc.lessons_next_week, pass_args=True))
        dp.add_handler(CommandHandler("full", self.bc.full_weeks, pass_args=True))
        dp.add_handler(CommandHandler("today", self.bc.lessons_today, pass_args=True))
        dp.add_handler(CommandHandler("tomorrow", self.bc.lessons_tomorrow, pass_args=True))
        dp.add_handler(CommandHandler(["timetable", "tt"], self.bc.call_schedule))
        dp.add_handler(CommandHandler("weeknumber", self.bc.week_number))
        dp.add_handler(CommandHandler("exams", self.bc.exams, pass_args=True))

        def error(bot, update, error_):
            """Log Errors caused by Updates."""
            self.logger.warning('Update "%s" caused error "%s"', update, error_)

        # log all errors
        dp.add_error_handler(error)

        if flag == 'webhooks':
            updater.start_webhook(listen="0.0.0.0",
                                  port=int(self.PORT),
                                  url_path=self.TOKEN)
            updater.bot.setWebhook("https://{}.herokuapp.com/{}".format(self.NAME, self.TOKEN))
        elif flag == 'polling':
            updater.start_polling()

        # If flag == 'polling'.
        # Run the bot until you press Ctrl-C or the process receives SIGINT,
        # SIGTERM or SIGABRT. This should be used most of the time, since
        # start_polling() is non-blocking and will stop the bot gracefully.
        updater.idle()


if __name__ == "__main__":
    polling = StartBot()
    polling.bot_activation(input('Flag: '))
