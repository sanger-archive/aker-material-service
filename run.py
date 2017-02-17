import os
import logging
import uuid
import json
import copy
import pdb

from uuid_encoder import UUIDEncoder
from custom_validator import CustomValidator
from eve import Eve
from flask import request, jsonify, abort, Response, current_app
from flask_bootstrap import Bootstrap
from eve_swagger import swagger
from bson import json_util
from flask_zipkin import Zipkin

environment = os.getenv('EVE_ENV', 'development')

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', environment + '.py')

def create_app(settings):
  app = Eve(settings=settings, json_encoder=UUIDEncoder, validator=CustomValidator)

  Bootstrap(app)
  app.register_blueprint(swagger)

  def set_uuid(resource_name, items):
    for item in items:
      item['_id'] = str(uuid.uuid4())

  app.on_insert += set_uuid

  def set_barcode_if_not_present(containers):
    for container in containers:
      if 'barcode' not in container:
        container['barcode'] = 'AKER-' + str(uuid.uuid4())[:8]

  app.on_insert_containers += set_barcode_if_not_present

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

  def cerberus_to_json_add_required_to_obj(out_obj):
    schema_obj_copy = out_obj['properties']
    required_list = []
    for key in schema_obj_copy:
      if (('required' in schema_obj_copy[key]) and (schema_obj_copy[key]['required'])):
        required_list += [key]
    if len(required_list) > 0:
      out_obj['required'] = required_list

  def cerberus_to_json_change_type_for_datetime(out_obj):
    schema_obj_copy = out_obj['properties']
    for key in schema_obj_copy:
      if schema_obj_copy[key]['type']=='datetime':
        schema_obj_copy[key]['type'] = 'string'
        schema_obj_copy[key]['format'] = 'date'

  def cerberus_to_json_filter_parameters(out_obj, filter_list):
    schema_obj_copy = out_obj['properties']
    for key in filter_list:
      if schema_obj_copy[key]:
        del schema_obj_copy[key]

  def cerberus_to_json_change_allowed_with_one_of(out_obj):
    schema_obj_copy = out_obj['properties']
    for key in schema_obj_copy:
      if 'allowed' in schema_obj_copy[key]:
        schema_obj_copy[key]['enum'] = schema_obj_copy[key]['allowed']
        del schema_obj_copy[key]['allowed']

  def cerberus_to_json_schema(schema_obj):
    filter_list = ['meta', '_id', 'parent','ancestors']
    out_obj = {'type': 'object', 'properties': copy.deepcopy(schema_obj)}

    cerberus_to_json_change_type_for_datetime(out_obj)
    cerberus_to_json_filter_parameters(out_obj, filter_list)
    cerberus_to_json_add_required_to_obj(out_obj)
    cerberus_to_json_change_allowed_with_one_of(out_obj)

    return out_obj

  @app.route('/materials/schema', methods=['GET'])
  def bulk_schema(**lookup):
    schema_obj = cerberus_to_json_schema(current_app.config['DOMAIN']['materials']['schema'])

    schema_str = json.dumps(schema_obj, default=json_util.default)

    resp = Response(response=schema_str, status=200, mimetype="application/json")
    return (resp)

  @app.route('/materials/bulk_get', methods=['POST'])
  def bulk_get(**lookup):
    if not 'materials' in request.json:
      abort(422)

    materials = []

    for material in app.data.driver.db.materials.find({'_id': { '$in': request.json['materials'] } }):
      materials.append(material)

    materials = json.dumps(materials, default=json_util.default)

    resp = Response(response=materials,
        status=200, \
        mimetype="application/json")

    return (resp)

  return app

# enable logging to 'app.log' file
handler = logging.FileHandler('app.log')

# set a custom log format, and add request
# metadata to each log line
handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(filename)s:%(lineno)d] -- ip: %(clientip)s, '
    'url: %(url)s, method:%(method)s'))

app = create_app(SETTINGS_PATH)

# the default log level is set to WARNING, so
# we have to explictly set the logging level
# to INFO to get our custom message logged.
app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)

zipkin = Zipkin(sample_rate=1)
zipkin.init_app(app)

if __name__ == '__main__':
  app.run()