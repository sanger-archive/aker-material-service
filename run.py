import os
import logging
import uuid

from uuid_encoder import UUIDEncoder
from uuid_validator import UUIDValidator
from eve import Eve
from flask_bootstrap import Bootstrap
from eve_docs import eve_docs

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.py')
app = Eve(settings=SETTINGS_PATH, json_encoder=UUIDEncoder, validator=UUIDValidator)
Bootstrap(app)
app.register_blueprint(eve_docs, url_prefix='/docs')

def set_uuid(resource_name, items):
  for item in items:
    item['_id'] = str(uuid.uuid4())

app.on_insert += set_uuid

if __name__ == '__main__':
  # enable logging to 'app.log' file
  handler = logging.FileHandler('app.log')

  # set a custom log format, and add request
  # metadata to each log line
  handler.setFormatter(logging.Formatter(
      '%(asctime)s %(levelname)s: %(message)s '
      '[in %(filename)s:%(lineno)d] -- ip: %(clientip)s, '
      'url: %(url)s, method:%(method)s'))

  # the default log level is set to WARNING, so
  # we have to explictly set the logging level
  # to INFO to get our custom message logged.
  app.logger.setLevel(logging.INFO)

  # append the handler to the default application logger
  app.logger.addHandler(handler)

  app.run()