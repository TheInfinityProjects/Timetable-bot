import functools
import logging

import requests
import pendulum

from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (CommandHandler, RegexHandler, ConversationHandler)

from .database import UserDatabase
from .timetable import Timetable
from .week import Week


def group_exists(func):
    """Decorator for bot commands.

    For call the telegrams, the command without arguments will return
    the schedule for user's group, for call the command with the argument,
    it will check the group exists

    Returns:
        :obj:`function`: On success, decorated function `func` is returned.

    """
    @functools.wraps(func)
    def decorator(self, bot, update, args):
        try:
            group_name = self.format_group(str(args[0]))
            if not self.is_group(group_name):
                bot.send_message(update.message.chat_id,
                                 'Группы с таким именем не существует, '
                                 'проверьте корректность введенного имени.',
                                 parse_mode='Markdown')
                return
        except IndexError:
            user_id = update.message.from_user['id']
            group_name = self.user_db.get_group_name(user_id)
        return func(self, bot, update, group_name)
    return decorator


def is_registered(func):
    """Decorator for bot commands.

    For registered users returns `func`, for other users - information message.

    Returns:
        :obj:`function`: On success, decorated function `func` is returned.

    """
    @functools.wraps(func)
    def decorator(self, bot, update, *args, **kwargs):
        user_id = str(update.message.from_user['id'])
        if self.user_db.registry(user_id):
            return func(self, bot, update, *args, **kwargs)
        else:
            bot.send_message(update.message.chat_id, 'Используй /set <группа>, чтобы установить расписание, '
                                                     'например \'/set io61\'.', parse_mode='Markdown')

    return decorator


class BotCommand(object):
    """This class implements the custom bot commands

    Attributes:
        logger (:obj:`Logger`): .
        user_db (:obj:`class`): Instance of a class UserDatabase.
        timetable (:obj:`class`): Instance of a class Timetable.
        week (:obj:`class`): Week class.

    """

    def __init__(self):
        # Enable logging
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        self.user_db = UserDatabase()

        self.timetable = Timetable()

        self.week = Week

        self.CHOOSING, self.TYPING_REPLY, self.TYPING_CHOICE = range(3)

        reply_keyboard = [['Понедельник', 'Вторник'],
                          ['Среда', 'Четверг'],
                          ['Пятница', 'Суббота'],
                          ['Скрыть']]
        self.markup = ReplyKeyboardMarkup(reply_keyboard)

        self.conv_handler = ConversationHandler(
            entry_points=[CommandHandler('keyboard', self.keyboard_mode)],

            states={
                self.CHOOSING: [RegexHandler('^(Понедельник|Вторник|Среда|Четверг|Пятница|Суббота)$',
                                             self.regular_choice),
                                ],

            },
            fallbacks=[RegexHandler('^Скрыть$', self.done)]
        )

    @is_registered
    def keyboard_mode(self, bot, update):
        bot.send_message(update.message.chat_id,
                         'Режим "keyboard"  активирован.',
                         reply_markup=self.markup)

        return self.CHOOSING

    def regular_choice(self, bot, update):
        text = update.message.text
        self.lessons_on_day(bot, update, text)

        return self.CHOOSING

    @staticmethod
    def done(bot, update):
        bot.send_message(update.message.chat_id,
                         'Можешь снова использовать команды.',
                         reply_markup=ReplyKeyboardRemove())

        return ConversationHandler.END

    def is_group(self, group_name):
        """Verifies the existence of such a group.

        http://api.rozklad.org.ua/v2/groups/{group_name|group_id}
        Get a group by name or by ID.
        If "statusCode": 200 and "message": OK - group exists.

        Args:
            group_name (:obj:`str`): This object is the name of the group.

        Returns:
            :obj:`boolean`: Return True if group exists, else False.

        """

        try:
            r_json = requests.get(
                'https://api.rozklad.org.ua/v2/groups/{}'.format(group_name)).json()
            message_text = r_json['message']
            if message_text == 'Ok':
                return True
            elif message_text == 'Group not found':
                return False
            else:
                self.logger.error(message_text)
        except ConnectionError as error_text:
            self.logger.error(error_text)
        except IndexError as error_text:
            self.logger.error(error_text)

    @staticmethod
    def format_group(group):
        if '-' in group:
            group = group
        else:
            list_ = list(group)
            list_.insert(2, '-')
            group = ''.join(list_)
        return group

    @staticmethod
    def start(bot, update):
        """Beginning of communication between the bot and the user.

        Args:
            bot (:obj:`str`): This object represents a Telegram Bot.
            update (:class:`telegram.Update`): Incoming telegram update.

        """

        bot.send_message(update.message.chat_id,
                         text='*Привет!* Используй /set <группа>, чтобы установить расписание, '
                              'например \'/set io-61\'.', parse_mode='Markdown')

    @staticmethod
    def help_message(bot, update):
        with open('./timetable_bot/static/help_message') as file:
            text = file.read()
        bot.send_message(update.message.chat_id,
                         text=text, parse_mode='Markdown')

    def set_group(self, bot, update, args):
        """Add a new user to the database.

        #

        Args:
            bot (:obj:`str`): This object represents a Telegram Bot.
            update (:class:`telegram.Update`): Incoming telegram update.
            args (:obj:`str`, optional): Arguments passed by the handler

        """
        username = str(update.message.from_user['username'])
        chat_id = str(update.message.from_user['id'])

        try:
            group_name = self.format_group(str(args[0]))

            if self.is_group(group_name):
                self.user_db.add_new_user(username, group_name, chat_id)
                bot.send_message(update.message.chat_id,
                                 'Расписание для группы *{}* успешно установлено!\n'
                                 '/today\n'
                                 '/tomorrow\n'
                                 '/week\n'
                                 '/nextweek\n'
                                 '/full\n'
                                 '/timetable\n'
                                 '/keyboard\n'.format(group_name),
                                 parse_mode='Markdown')
            else:
                raise Exception("Group is not exists.")
        except (Exception, IndexError):
            bot.send_message(update.message.chat_id,
                             'Группы с таким именем не существует, проверьте корректность введенного имени.',
                             parse_mode='Markdown')

    @is_registered
    @group_exists
    def lessons_week(self, bot, update, group_name):
        week_number = self.week()
        bot.send_message(update.message.chat_id,
                         text='`{}`\n'.format(group_name) + self.timetable.lessons_week(group_name, week_number),
                         parse_mode='Markdown')

    @is_registered
    @group_exists
    def lessons_next_week(self, bot, update, group_name):
        week_number = self.week()
        week_number.next()

        bot.send_message(update.message.chat_id,
                         text='`{}`\n'.format(group_name) + self.timetable.lessons_week(group_name, week_number),
                         parse_mode='Markdown')

    @is_registered
    @group_exists
    def full_weeks(self, bot, update, group_name):
        week_number = self.week()
        bot.send_message(update.message.chat_id,
                         text='`{}`\n'.format(group_name) + self.timetable.lessons_week(group_name, week_number),
                         parse_mode='Markdown')
        week_number.next()
        bot.send_message(update.message.chat_id,
                         text=self.timetable.lessons_week(group_name, week_number),
                         parse_mode='Markdown')

    @is_registered
    @group_exists
    def lessons_today(self, bot, update, group_name):
        week_number = self.week()
        day_number = pendulum.now('Europe/Kiev')

        bot.send_message(update.message.chat_id,
                         text='`{}`\n{}'.format(group_name,
                                                self.timetable.lessons_per_day(group_name,
                                                                               day_number,
                                                                               week_number)),
                         parse_mode='Markdown')

    @is_registered
    @group_exists
    def lessons_tomorrow(self, bot, update, group_name):
        week_number = self.week()
        day_number = pendulum.now('Europe/Kiev').add(days=1)

        bot.send_message(update.message.chat_id,
                         text='`{}`\n{}'.format(group_name,
                                                self.timetable.lessons_per_day(group_name,
                                                                               day_number,
                                                                               week_number)),
                         parse_mode='Markdown')

    @is_registered
    def lessons_on_day(self, bot, update, day):
        user_id = update.message.from_user['id']
        group_name = self.user_db.get_group_name(user_id)
        week_number = self.week()

        bot.send_message(update.message.chat_id,
                         text='`{}`\n{}'.format(group_name,
                                                self.timetable.daily_timetable(group_name,
                                                                               day,
                                                                               week_number)),
                         parse_mode='Markdown',
                         reply_markup=self.markup)

    @is_registered
    def call_schedule(self, bot, update):
        """Send the timetable in `Markdown`.

        Args:
            bot (:obj:`str`): This object represents a Telegram Bot.
            update (:class:`telegram.Update`): Incoming telegram update.

        """
        bot.send_message(update.message.chat_id, '_1 пара_  08:30 - 10:05\n'
                                                 '_2 пара_  10:25 - 12:00\n'
                                                 '_3 пара_  12:20 - 13:55\n'
                                                 '_4 пара_  14:15 - 15:50\n'
                                                 '_5 пара_  16:10 - 17:45',
                         parse_mode='Markdown')

    @is_registered
    def week_number(self, bot, update):
        bot.send_message(update.message.chat_id,
                         text='Сейчас *{}* учебная неделя.'.format(self.week()),
                         parse_mode='Markdown')
