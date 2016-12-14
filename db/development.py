import os

ENVIRONMENT_PATH = os.path.join(os.path.dirname('..'), 'schema.py')
execfile(ENVIRONMENT_PATH)

MONGO_HOST = 'localhost'
MONGO_PORT = 27017

MONGO_DBNAME = 'materials'

ZIPKIN_DSN = 'http://localhost:9411/api/v1/spans'