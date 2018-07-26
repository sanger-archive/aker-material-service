import os

ENVIRONMENT_PATH = os.path.join(os.path.dirname('..'), 'schema.py')
execfile(ENVIRONMENT_PATH)

LOGGING_LEVEL = 'INFO'

MONGO_URI = 'mongodb://localhost:27017/materials'

ZIPKIN_DISABLE = True

SECRET_KEY = 'development'
