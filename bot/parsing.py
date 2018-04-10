import re

import requests
import pendulum

from bs4 import BeautifulSoup


def _exams(group_name):
    """"""
    r_json = requests.get(
        'https://api.rozklad.org.ua/v2/groups/{}'.format(group_name)).json()
    group_url = r_json['data']['group_url'].rsplit('g=', 1)
    html_text = requests.get(
        'http://rozklad.kpi.ua/Schedules/ViewSessionSchedule.aspx?g={}'.format(group_url[1])).text
    soup = BeautifulSoup(html_text, 'lxml')

    exams_list = soup.findAll('tr')

    number_exams = len(exams_list)
    exams = []
    result_l = []

    for i in range(number_exams):
        soup_2 = BeautifulSoup(str(exams_list[i]), 'lxml')
        if not soup_2.findAll('a'):
            continue

        exam = []
        date_list = str(soup_2.find('td').text).split('/')
        time_exam = re.findall(r'\d\d:\d\d', str(
            soup_2.findAll('td')[1]))[0].split(':')
        date_exam = pendulum.create(year=int(date_list[2]), month=int(date_list[0]), day=int(date_list[1]),
                                    hour=int(time_exam[0]),
                                    minute=int(time_exam[1]), tz='Europe/Kiev')
        date = date_exam.format(
            'dddd D MMMM YYYY о HH:mm', formatter='alternative', locale='uk').capitalize()
        for j in soup_2.findAll('a'):
            exam.append(str(j.text))
        exam.append(date)
        exams.append(exam)

    for i in exams:
        result_l.append(
            '*{}* `{}`\n{}\n{}'.format(i[0], i[2], i[1], i[3]))

    result = '\n'.join(result_l)
    if result:
        return result
    else:
        return 'Дата экзаменов ещё неизвестна, спи спокойно :)'
