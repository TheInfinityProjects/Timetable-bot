import requests
import pendulum


class Timetable(object):
    @staticmethod
    def timetable(group_name):
        return requests.get('https://api.rozklad.org.ua/v2/groups/{}/timetable'.format(group_name)).json()

    def lessons_week(self, group_name, week_number):
        r_json = self.timetable(group_name)
        if r_json['statusCode'] == '404':
            return 'Расписания ещё нет :('

        days = []
        for i in r_json['data']['weeks'][str(week_number)]['days']:
            lessons = []
            for j in r_json['data']['weeks'][str(week_number)]['days'][i]['lessons']:
                lessons.append('{}) {} *{}* `{}`'.format(j['lesson_number'],
                                                         j['lesson_name'],
                                                         j['lesson_type'],
                                                         j['lesson_room']))
            if r_json['data']['weeks'][str(week_number)]['days'][i]['lessons']:
                lessons.insert(0, '*{}*'.format(r_json['data']['weeks'][str(week_number)]['days'][i]['day_name']))
                days.append('\n'.join(lessons))
        return '\n'.join(days)

    def lessons_per_day(self, group_name, day, week_number):
        r_json = self.timetable(group_name)
        if r_json['statusCode'] == '404':
            return 'Расписания ещё нет :('
        
        lessons = list()

        if str(day.day_of_week) == '0':
            lessons.append('*Воскресенье — пар нет*')
            week_number.next()
            day = day.add(days=1)

        day_name = '*{}*'.format(r_json['data']['weeks'][str(week_number)]['days'][str(day.day_of_week)]['day_name'])
        lessons.append(day_name)
        
        if not r_json['data']['weeks'][str(week_number)]['days'][str(day.day_of_week)]['lessons']:
            day = day.add(days=1)
            return '{} *— пар нет\n*'.format(day_name) + self.lessons_per_day(group_name, day, week_number)

        for i in r_json['data']['weeks'][str(week_number)]['days'][str(day.day_of_week)]['lessons']:
            lessons.append('{}) {} *{}* `{}`'.format(i['lesson_number'],
                                                     i['lesson_name'],
                                                     i['lesson_type'],
                                                     i['lesson_room']))
        return '\n'.join(lessons)

    def daily_timetable(self, group_name, day, week_number):
        r_json = self.timetable(group_name)
        if r_json['statusCode'] == '404':
            return 'Расписания ещё нет :('

        lessons = list()

        days = {
            'Понедельник': 1,
            'Вторник': 2,
            'Среда': 3,
            'Четверг': 4,
            'Пятница': 5,
            'Суббота': 6
        }

        day_name = '*{}*'.format(day)
        lessons.append(day_name)
        try:
            if not r_json['data']['weeks'][str(week_number)]['days'][str(days[day])]['lessons']:
                return '{} *— пар нет\n*'.format(day_name)

            for i in r_json['data']['weeks'][str(week_number)]['days'][str(days[day])]['lessons']:
                lessons.append('{}) {} *{}* `{}`'.format(i['lesson_number'],
                                                         i['lesson_name'],
                                                         i['lesson_type'],
                                                         i['lesson_room']))
        except KeyError:
            return 'Неверное имя дня недели'

        return '\n'.join(lessons)


if __name__ == '__main__':
    sc = Timetable()
    print(sc.lessons_week('io-61', '1'))
