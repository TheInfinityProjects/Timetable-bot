#!/usr/bin/env python
import unittest

import pendulum

from bot.timetable import Timetable
from bot.week import Week
from bot.parsing import _exams


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.week = Week()
        self.tt = Timetable()
        self.group_1 = self.tt.timetable('io-61')
        self.group_2 = self.tt.timetable('io-51')

    def tearDown(self):
        pass

    def test_timetable(self):
        self.assertIsNotNone(self.group_1)
        self.assertIsNotNone(self.group_2)
        self.assertNotEqual(self.group_1, self.group_2)

    def test_lessons_week(self):
        lessons_week_1 = self.tt.lessons_week('io-61', week_number=1)
        lessons_week_2 = self.tt.lessons_week('io-61', week_number=2)
        self.assertNotEqual(lessons_week_1, lessons_week_2)

    def test_lessons_per_day(self):
        day_number_1 = pendulum.now('Europe/Kiev')
        day_number_2 = pendulum.now('Europe/Kiev')
        lessons_week_1_day1 = self.tt.lessons_per_day('io-61', day_number_1, self.week)
        lessons_week_2_day2 = self.tt.lessons_per_day('io-61', day_number_2, self.week)
        self.assertNotEqual(lessons_week_1_day1, lessons_week_2_day2)

    def test_daily_timetable(self):
        day_number_1 = 'Понедельник'
        day_number_2 = 'Вторник'
        lessons_week_1_day1 = self.tt.daily_timetable('io-61', day_number_1, self.week)
        lessons_week_2_day2 = self.tt.daily_timetable('io-61', day_number_2, self.week)
        self.assertNotEqual(lessons_week_1_day1, lessons_week_2_day2)

    def test_daily_timetable_v2(self):
        day_number_1 = 'Понедельник'
        day_number_2 = 'Суббота'
        lessons_week_1_day1 = self.tt.daily_timetable('io-61', day_number_1, self.week)
        lessons_week_2_day2 = self.tt.daily_timetable('io-61', day_number_2, self.week)
        lessons_week_2_day2 = lessons_week_2_day2.split('\n')
        del lessons_week_2_day2[0]
        lessons_week_2_day2 = '\n'.join(lessons_week_2_day2)
        self.assertNotEqual(lessons_week_1_day1, lessons_week_2_day2)

    def test_daily_timetable_v3(self):
        day_number_1 = 'Another days'
        lessons_week_1_day1 = self.tt.daily_timetable('io-61', day_number_1, self.week)
        self.assertEqual(lessons_week_1_day1, 'Неверное имя дня недели')

    def test_exams(self):
        list_exams = _exams('io-61')
        self.assertIsNotNone(list_exams)


if __name__ == '__main__':
    unittest.main(verbosity=2)
