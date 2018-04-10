import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ADMINS = ['maximov.echo@gmail.com']
    FLASK_DEBUG = os.environ.get('FLASK_DEBUG') or 0
