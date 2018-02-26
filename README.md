# [Schedule](http://t.me/timetable_kpi_bot) telegram bot on [Heroku](https://www.heroku.com/)
The project was created as a coursework on the discipline 'Software Engineering'. Lecture schedule in a telegram using 
a bot.  
#### Features:
- Schedule of classes for your group by days and weeks.
- Teacher's schedule.
- Exam Schedule.

## Installing
You need the latest version of `pip` to deploy the project on the local machine.
Install virtualenv:
```commandline
$ pip install --upgrade virtualenv
```

Cloning repo:
```commandline
$ git clone git@github.com:TheInfinityProjects/Timetable-bot.git
$ cd Timetable-bot
```

Created virtualenv:
```commandline
$ virtualenv -p python3 venv
```
Open `/Timetable-bot/venv/bin/active` and add:
```commandline
TOKEN='Your bot token'
export TOKEN
  
DATABASE_URL='Your database URL'
export DATABASE_URL
```

Activate virtual environment:
```commandline
$ source venv/bin/activate
```

Now install required python packages:
```commandline
(venv) $ pip install -r UkrExpCompany/requirements.txt
```

Start bot polling:
```commandline
(venv) $ python manage.py --start polling
Bot start polling!
```