import os
from envparse import env

__all__ = ['ROOT_DIR', 'DATA_DIR', 'DEBUG', 'SITE_HOST',
           'SITE_PORT', 'SECRET_KEY', 'MONGO_HOST', 'MONGO_DB_NAME']


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT_DIR, 'data')

if os.path.isfile('.env'):
    env.read_envfile('.env')

SITE_HOST = env.str('HOST')
SITE_PORT = env.int('PORT')
SECRET_KEY = env.str('SECRET_KEY')
MONGO_HOST = env.str('MONGO_HOST')
MONGO_DB_NAME = env.str('MONGO_DB_NAME')
MONGO_COLLECTION_NACK = env.str('MONGO_COLLECTION_NACK')
MONGO_COLLECTION_INTEREST = env.str('MONGO_COLLECTION_INTEREST')
MONGO_COLLECTION_DATA = env.str('MONGO_COLLECTION_DATA')
