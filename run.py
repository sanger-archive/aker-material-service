#!/usr/bin/env python

import sys
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
from eve_swagger import swagger
from flask_swagger_ui import get_swaggerui_blueprint
from bson import json_util
from flask_zipkin import Zipkin
from pymongo import ReturnDocument
from addresser import Addresser
from flask_login import LoginManager, current_user
from jwt_auth import JWTAuth
from user import User
from datetime import datetime
from eve.utils import date_to_str, str_to_date

environment = os.getenv('EVE_ENV', 'development')

SETTINGS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', environment + '.py')
SWAGGER_URL = '/docs'  # URL for exposing Swagger UI (without trailing '/')
API_URL = '/api-docs'  # Our API url (can of course be a local resource)

def create_app(settings):
    app = Eve(settings=settings, json_encoder=UUIDEncoder, validator=CustomValidator, auth=JWTAuth)

    app.name = 'Materials service'

    # We are using a document in the counters collection to generate sequential ids to be
    # used for barcodes. Here we're "seeding" the collection with the inital document
    with app.app_context():
        current_app.data.driver.db \
            .get_collection('counters') \
            .update({'_id': 'barcode'}, {'$setOnInsert': {'seq': 0}}, upsert=True)

    # Create a swagger.json
    app.register_blueprint(swagger)

    # Configure swagger ui to display docs using swagger.json @ SWAGGER_URL
    app.register_blueprint(get_swaggerui_blueprint(SWAGGER_URL, API_URL), url_prefix=SWAGGER_URL)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(email):
        print email
        return User(email)

    # Application hooks
    def set_uuid(resource_name, items):
        for item in items:
            item['_id'] = str(uuid.uuid4())

    app.on_insert += set_uuid

    # Containers hooks
    def set_barcode_if_not_present(containers):
        for container in containers:
            if 'barcode' not in container:
                result = app.data.driver.db.counters.find_one_and_update(
                    {'_id': 'barcode'},
                    {'$inc': { 'seq': 1 }},
                    return_document=ReturnDocument.AFTER)

                container['barcode'] = 'AKER-%s'%result['seq']

    def insert_empty_slots(containers):
        for container in containers:
            addresser = Addresser(container['num_of_rows'], container['num_of_cols'],
                                                     bool(container.get('row_is_alpha')), bool(container.get('col_is_alpha')))
            slots = container.get('slots')
            if not slots:
                container['slots'] = [{ 'address': address } for address in addresser]
            else:
                definedaddresses = { slot['address'] for slot in container['slots'] }
                for address in addresser:
                    if address not in definedaddresses:
                        slots.append({'address': address})

    app.on_insert_containers += set_barcode_if_not_present
    app.on_insert_containers += insert_empty_slots

    # Materials hooks
    def set_owner_id(materials):
        for material in materials:
            if not material.get("owner_id"):
                material["owner_id"] = current_user.id

    app.on_insert_materials += set_owner_id

    # Very rudimentary validation method... just for development!
    @app.route('/materials/validate', methods=['POST'])
    def validate(**lookup):
        if 'materials' not in request.json:
            abort(422)

        if (validate_existence(request.json['materials'])):
            return "ok"
        else:
            return "not ok - some materials not found"

    def validate_existence(materials):
        validation_set = set(materials)
        result_set = set()

        for material in app.data.driver.db.materials.find({'_id': { '$in': materials } }, { '_id': 1}):
            result_set.add(material['_id'])

        difference = validation_set - result_set

        return not difference

    @app.route('/materials/verify_ownership', methods=['POST'])
    def verify_ownership(**lookup):
        materials = request.json.get('materials')
        owner_id = request.json.get('owner_id')

        if materials is None or not owner_id:
            abort(422)

        if len(materials)==0:
            # If materials is an empty list, then the check is logically successful
            return Response(status=200, mimetype="application/json")

        if not validate_existence(materials):
            abort(422, description="There was at least one material that did not exist")

        find_args = {
            '$and': [
                { '_id': { '$in': materials } },
                { 'owner_id': { '$ne': owner_id }}
            ]
        }

        materials_cursor = app.data.driver.db.materials.find(find_args)

        if materials_cursor.count() > 0:
            response_body = json.dumps({
                "_status": "ERR",
                "_error": "{0} material(s) do not belong to {1}".format(materials_cursor.count(), owner_id),
                "_issues": [material['_id'] for material in materials_cursor]
            })

            return Response(status=403, response=response_body, mimetype="application/json")

        return Response(status=200, mimetype="application/json")

    def cerberus_to_json_list(schema, quality):
        return [key for key, value in schema.iteritems() if value.get(quality)]

    def cerberus_to_json_change_type_for_datetime(schema):
        for value in schema.itervalues():
            if value['type'] == 'datetime':
                value['type'] = 'string'
                value['format'] = 'date'

    def cerberus_to_json_filter_parameters(schema, filter_list):
        for key in filter_list:
            schema.pop(key, None)

    def cerberus_to_json_change_allowed_with_one_of(schema):
        for value in schema.itervalues():
            if 'allowed' in value:
                value['enum'] = value['allowed']
                del value['enum']

    def cerberus_to_json_only_id_is_required(schema):
        for key, value in schema.iteritems():
            if key=='_id':
                value['required'] = True
            elif value.get('required'):
                value['required'] = False

    def amend_required_order(required):
        if 'supplier_name' in required and required[0]!='supplier_name':
            required.remove('supplier_name')
            required.insert(0, 'supplier_name')

    def cerberus_to_json_schema(schema_obj, patch=False):
        filter_list = ['meta', 'parent', 'ancestors']
        if not patch:
            filter_list.append('_id')
        schema = copy.deepcopy(schema_obj)
        cerberus_to_json_change_type_for_datetime(schema)
        cerberus_to_json_filter_parameters(schema, filter_list)
        if patch:
            cerberus_to_json_only_id_is_required(schema)
        cerberus_to_json_change_allowed_with_one_of(schema)
        required = cerberus_to_json_list(schema, 'required')
        searchable = cerberus_to_json_list(schema, 'searchable')
        amend_required_order(required)

        return {'type': 'object', 'properties': schema, 'required': required, 'searchable': searchable}

    @app.route('/containers/json_schema', methods=['GET'])
    def containers_json_schema(**lookup):
        return json_schema_request('containers')

    @app.route('/materials/json_schema', methods=['GET'])
    def materials_json_schema(**lookup):
        return json_schema_request('materials')

    # Deprecated in favour of json_schema
    @app.route('/materials/schema', methods=['GET'])
    def bulk_schema(**lookup):
        return json_schema_request('materials')

    @app.route('/materials/json_patch_schema', methods=['GET'])
    def materials_json_patch_schema(**lookup):
        return json_schema_request('materials', True)

    def json_schema_request(model_name, patch=False):
        schema_obj = cerberus_to_json_schema(current_app.config['DOMAIN'][model_name]['schema'], patch)
        schema_str = json.dumps(schema_obj, default=json_util.default)
        return Response(response=schema_str, status=200, mimetype="application/json")

    def process_where(where, in_date_value=False):
        if not where:
            return where
        if isinstance(where, dict):
            for k,v in where.iteritems():
                where[k] = process_where(v, in_date_value or k=='date_of_receipt')
        elif isinstance(where, (list, tuple)):
            return [process_where(x, in_date_value) for x in where]
        elif in_date_value and isinstance(where, basestring):
            try:
                return str_to_date(where)
            except ValueError:
                return where
        return where

    def _bulk_find(resource, args):

        find_args = {
          'filter': process_where(args.get('where')),
          'projection': args.get('projection'),
        }
        try:
            limit = max(int(args['max_results']), 0)
        except (ValueError, KeyError):
            limit = 0
        if limit:
            find_args['limit'] = limit

        try:
            page = max(int(args['page']), 1)
        except (ValueError, KeyError):
            page = 1
        if limit and page>1:
            find_args['skip'] = limit*(page-1)

        cursor = app.data.driver.db[resource].find(**find_args)
        total = cursor.count()
        pages = ((total + limit-1) // limit) if limit else 1
        items = list(cursor)

        meta = { 'max_results': limit, 'total': total, 'page': page }

        links = {}
        if page > 1:
            links['prev'] = { 'page': (page-1) }
        if page < pages:
            links['next'] = { 'page': (page+1) }
            links['last'] = { 'page': pages }

        for item in items:
            for k, v in item.iteritems():
                if isinstance(v, datetime):
                    # date_to_str converts a datetime value to the format defined in the configuration file
                    item[k] = date_to_str(v)
                if isinstance(v, unicode):
                    item[k] = str(v)

        msg = { '_items': items, '_meta': meta, '_links': links }

        msg_json = json.dumps(msg, default=json_util.default)

        return Response(response=msg_json,
                        status=200,
                        mimetype="application/json")

    @app.route('/materials/search', methods=['POST'])
    def bulk_find_materials(**lookup):
        return _bulk_find('materials', request.json)

    @app.route('/containers/search', methods=['POST'])
    def bulk_find_containers(**lookup):
        return _bulk_find('containers', request.json)

    return app


# enable logging to 'app.log' file
log_handlers = [
     logging.FileHandler('app.log'),
     logging.StreamHandler(sys.stdout),
]

# set a custom log format, and add request
# metadata to each log line
for handler in log_handlers:
    handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(filename)s:%(lineno)d] -- ip: %(clientip)s, '
            'url: %(url)s, method: %(method)s'))

app = create_app(SETTINGS_PATH)

# the default log level is set to WARNING, so
# we have to explictly set the logging level
# to INFO to get our custom message logged.
app.logger.setLevel(logging.INFO)

for handler in log_handlers:
    app.logger.addHandler(handler)

def log_request_start(resource, request, lookup=None):
    message = "%s resource=%r, request=%r"%(request.method, resource, request)
    app.logger.info(message)
    app.logger.info("Request data:\n"+request.data)

def log_request_end(resource, request, response):
    message = "%s resource=%r, request=%r, response=%r"%(request.method, resource, request, response)
    app.logger.info(message)
    if response:
        app.logger.debug("Response data:\n"+response.data)

for method in 'GET POST PATCH PUT DELETE'.split():
    events = getattr(app, 'on_pre_'+method)
    events += log_request_start
    events = getattr(app, 'on_post_'+method)
    events += log_request_end

zipkin = Zipkin(sample_rate=1)
zipkin.init_app(app)

if __name__ == '__main__':
    app.run()
