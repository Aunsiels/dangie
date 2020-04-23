import os


BASEDIR = os.path.abspath(os.path.dirname(__file__))


# pylint: disable=too-few-public-methods
class Config():

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                              'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FACTS_PER_PAGE = 20
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SESSION_TYPE = os.environ.get("SESSION_TYPE") or "filesystem"
    PREFERRED_URL_SCHEME = 'https'
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://'
