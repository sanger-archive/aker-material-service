import os
import logging
import uuid

from uuid_encoder import UUIDEncoder
from uuid_validator import UUIDValidator
from eve import Eve
from flask import request, jsonify, abort
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

# Very rudimentary validation method... just for development!
@app.route('/materials/validate', methods=['POST'])
def validate(**lookup):
  if not 'materials' in request.json:
    abort(422)

  validation_set = set(request.json['materials'])
  result_set = set()

  for material in app.data.driver.db.materials.find({'_id': { '$in': request.json['materials'] } }, { '_id': 1}):
    result_set.add(material['_id'])

  difference = validation_set - result_set
  diff_len = len(difference)

  if (diff_len == 0):
    return "ok"
  else:
    return "not ok - " + str(diff_len) + " materials not found"

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