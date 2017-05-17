import os

ENVIRONMENT_PATH = os.path.join(os.path.dirname('..'), 'schema.py')
execfile(ENVIRONMENT_PATH)

MONGO_HOST = 'localhost'
MONGO_PORT = 27017

MONGO_DBNAME = 'materials_test'

ZIPKIN_DISABLE = True

SECRET_KEY = 'test'