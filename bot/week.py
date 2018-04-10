import pendulum


class Week(object):
    def __init__(self):
        week_number = pendulum.now('Europe/Kiev').week_of_year
        if week_number % 2 == 0:
            self.week = True  # 1
        else:
            self.week = False  # 2

    def next(self):
        self.week = not self.week

    def __str__(self):
        if self.week:
            return '1'
        else:
            return '2'

    def __nonzero__(self):
        return self.week
