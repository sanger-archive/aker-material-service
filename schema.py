# Enable reads (GET), inserts (POST) and DELETE for resources/collections
# (if you omit this line, the API will default to ['GET'] and provide
# read-only access to the endpoint).
RESOURCE_METHODS = ['GET', 'POST']

# Enable reads (GET), edits (PATCH), replacements (PUT) and deletes of
# individual items  (defaults to read-only item access).
ITEM_METHODS = ['GET', 'PATCH', 'PUT', 'DELETE']

# Disables concurrency control
# When enabled, ETag is required value within If-Match HTTP header
# Stops race conditions (which we'll ignore for now for testing purposes)
IF_MATCH = False

ITEM_URL = 'regex("[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12}")'

SWAGGER_INFO = {
  'title': 'Materials Service',
  'description': 'An RESTful web service for storing material data',
  'version': 'v1'
}

material_schema = {
  '_id': {
    'type': 'uuid'
  },
  'material_type': {
    'type': 'string',
    'allowed': ['blood', 'dna']
  },
  'supplier_name': {
    'type': 'string',
    'required': True
  },
  'donor_id': {
    'type': 'string',
    'required': True
  },
  'gender': {
    'type': 'string',
    'allowed': ['male', 'female', 'unknown'],
    'required': True
  },
  'common_name': {
    'type': 'string',
    'required': True,
    'allowed': ['Homo Sapiens', 'Mouse']
  },
  'phenotype': {
    'type': 'string',
    'required': True
  },
  'date_of_receipt': {
    'type': 'datetime',
  },
  'meta': {
    'type': 'dict',
    'allow_unknown': True,
  },
  'ancestors': {
    'type': 'list',
    'schema': {
      'type': 'uuid',
      'data_relation': {
        'resource': 'materials',
        'field': '_id',
        'embeddable': True
      }
    },
  },
  'parent': {
    'type': 'uuid'
  }
}

container_schema = {
  '_id': {
    'type': 'uuid'
  },
  'num_of_rows': {
    'type': 'integer',
    'min': 1,
    'max': 9999,
    'required': True,
    'row_alpha_range': True
  },
  'num_of_cols': {
    'type': 'integer',
    'min': 1,
    'max': 9999,
    'required': True,
    'col_alpha_range': True
  },
  'row_is_alpha': {
    'type': 'boolean',
    'required': True
  },
  'col_is_alpha': {
    'type': 'boolean',
    'required': True
  },
  'barcode': {
    'type': 'string',
    'unique': True,
    'minlength': 7,
    'non_aker_barcode': True,
  },
  'slots': {
    'type': 'list',
    'uniqueaddresses': True,
    'schema': {
      'type': 'dict',
      'schema': {
        'address': { 'type': 'string', 'address': True },
        'material': {
          'type': 'uuid',
          'data_relation': {
            'resource': 'materials',
            'field': '_id',
            'embeddable': True
          }
        }
      }
    }
  }
}

DOMAIN = {
  'materials': {
    'schema': material_schema
  },
  'containers': {
    'schema': container_schema
  }
}